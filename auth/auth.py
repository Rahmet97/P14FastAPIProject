import json

import redis
import secrets
from datetime import datetime

import requests
from pydantic import EmailStr

from config import GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URL, GOOGLE_CLIENT_SECRET_KEY, REDIS_HOST, REDIS_PORT
from tasks import send_mail_for_forget_password
from .schemas import UserInfo, User, UserInDB, UserLogin
from database import get_async_session

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException
from dotenv import load_dotenv
import starlette.status as status
from passlib.context import CryptContext

from models.models import users
from .utils import verify_token, generate_token

load_dotenv()
register_router = APIRouter()
redis_client = redis.StrictRedis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, decode_responses=True)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@register_router.post('/register')
async def register(user: User, session: AsyncSession = Depends(get_async_session)):
    if user.password1 == user.password2:
        username_exist_query = select(users).where(users.c.username == user.username)
        username__data = await session.execute(username_exist_query)
        username_data = username__data.scalar()
        if username_data:
            return {'success': False, 'message': 'Username already exists!'}
        email_exist_query = select(users).where(users.c.email == user.email)
        email__data = await session.execute(email_exist_query)
        email_data = email__data.scalar()
        if email_data:
            return {'success': False, 'message': 'Email already exists!'}
        password = pwd_context.hash(user.password1)
        user_in_db = UserInDB(**dict(user), password=password, joined_at=datetime.utcnow())
        query = insert(users).values(**dict(user_in_db))
        await session.execute(query)
        await session.commit()
        user_info = UserInfo(**dict(user_in_db))
        return dict(user_info)


@register_router.post('/login')
async def login(user: UserLogin, session: AsyncSession = Depends(get_async_session)):
    query = select(users).where(users.c.username == user.username)
    userdata = await session.execute(query)
    user_data = userdata.one()
    if pwd_context.verify(user.password, user_data.password):
        token = generate_token(user_data.id)
        return token
    else:
        return {'success': False, 'message': 'Username or password is not correct!'}


@register_router.get('/user-info', response_model=UserInfo)
async def user_info(token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401, detail='Token not provided!')

    user_id = token.get('user_id')

    query = select(users).where(users.c.id == user_id)
    user = await session.execute(query)
    try:
        result = user.one()
        return result
    except NoResultFound:
        raise HTTPException(status_code=404, detail='User not found!')


@register_router.get('/forget-password/{email}')
async def forget_password(
        email: EmailStr,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        user = select(users).where(users.c.email == email)
        user_data = await session.execute(user)
        if user_data.fetchone() is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Invalid Email address")
        token = secrets.token_urlsafe(32)

        redis_client.set(f'{token}', json.dumps({'email': email}))
        send_mail_for_forget_password(email, token)
        return {"detail": "Check your email"}
    except Exception as e:
        raise HTTPException(detail=f'{e}', status_code=status.HTTP_400_BAD_REQUEST)


@register_router.post('/reset-password/{token}')
async def reset_password(
        token: str,
        new_password: str,
        confirm_password: str,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if new_password != confirm_password:
            raise HTTPException(detail="Passwords are not same!!!", status_code=status.HTTP_400_BAD_REQUEST)
        user_data_json = redis_client.get(token)
        if user_data_json is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

        user_data = json.loads(user_data_json)
        email = user_data.get('email')

        update_password = update(users).where(users.c.email == email).values(
            password=pwd_context.hash(new_password))
        await session.execute(update_password)
        await session.commit()

        redis_client.delete(token)

        return {"detail": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(detail=f'{e}', status_code=status.HTTP_400_BAD_REQUEST)


@register_router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URL}&scope=openid%20profile%20email&access_type=offline"
    }


@register_router.get("/auth/google")
async def auth_google(code: str, session: AsyncSession = Depends(get_async_session)):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET_KEY,
        "redirect_uri": GOOGLE_REDIRECT_URL,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info_data = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                  headers={"Authorization": f"Bearer {access_token}"})
    user_data = {
        'first_name': user_info_data.json().get('name'),
        'last_name': user_info_data.json().get('name'),
        'username': user_info_data.json().get('email'),
        'email': user_info_data.json().get('email'),
        'password': pwd_context.hash(user_info_data.json().get('email')),
        'phone': user_info_data.json().get('email')
    }

    user_exist_query = select(users).where(users.c.username == user_info_data.json().get('email'))
    user_exist_data = await session.execute(user_exist_query)
    try:
        result = user_exist_data.scalars().one()
    except NoResultFound:
        try:
            query = insert(users).values(**user_data)
            await session.execute(query)

            user_data = await session.execute(
                select(users).where(users.c.username == user_info_data.json().get('email')))
            user_data = user_data.one()

            token = generate_token(user_data.id)
            await session.commit()
            return token
        except Exception as e:
            raise HTTPException(detail=f'{e}', status_code=status.HTTP_400_BAD_REQUEST)
    finally:
        await session.close()
