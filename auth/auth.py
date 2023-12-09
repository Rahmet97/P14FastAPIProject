import os
import secrets
from typing import Optional

import jwt
from datetime import datetime, timedelta

from .schemas import UserInfo, User, UserInDB, UserLogin
from database import get_async_session

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from passlib.context import CryptContext

from models.models import users

load_dotenv()
register_router = APIRouter()

secret_key = os.environ.get('SECRET')
algorithm = 'HS256'
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
security = HTTPBearer()


def generate_token(user_id: int):
    jti_access = str(secrets.token_urlsafe(32))
    jti_refresh = str(secrets.token_urlsafe(32))
    data_access_token = {
        'token_type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'user_id': user_id,
        'jti': jti_access
    }
    data_refresh_token = {
        'token_type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=1),
        'user_id': user_id,
        'jti': jti_refresh
    }
    access_token = jwt.encode(data_access_token, secret_key, algorithm)
    refresh_token = jwt.encode(data_refresh_token, secret_key, algorithm)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        secret_key = os.environ.get('SECRET')

        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@register_router.post('/register')
async def register(user: User, session: AsyncSession = Depends(get_async_session)):
    if user.password1 == user.password2:
        if not select(users).where(users.c.username == user.username).exists:
            return {'success': False, 'message': 'Username already exists!'}
        if not select(users).where(users.c.email == user.email).exists:
            return {'success': False, 'message': 'Email already exists!'}
        password = pwd_context.hash(user.password1)
        user_in_db = UserInDB(**dict(user), password=password)
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
    try:
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired!')
    except (jwt.InvalidTokenError, jwt.DecodeError):
        raise HTTPException(status_code=401, detail='Token invalid or malformed!')
