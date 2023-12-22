import os
from datetime import datetime, date
from typing import List

import aiofiles
import secrets
from fastapi import FastAPI, Depends, HTTPException, APIRouter, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, func

from auth.schemas import UserRead
from auth.utils import verify_token
from database import get_async_session
from models.models import category, subcategory, product, users, order, file
from schemas import CategorySchemaCreate, SubcategorySchemaCreate, CategoryScheme, ProductListSchema, OrderScheme
from auth.auth import register_router
from mobile.mobile import mobile_router

app = FastAPI(title='P14Project', version='1.0.0')
router = APIRouter()


@router.get('/category', response_model=List[CategoryScheme])
async def get_categories(token: dict = Depends(verify_token),
                         session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    query = select(category)
    category__data = await session.execute(query)
    category_data = category__data.all()
    categories = []
    for single in category_data:
        query2 = select(subcategory).where(subcategory.c.category_id == single.id)
        subcategory__data = await session.execute(query2)
        subcategory_data = subcategory__data.all()
        data = {
            'id': single.id,
            'name': single.name,
            'subcategories': subcategory_data
        }
        categories.append(data)
    return categories


@router.get('/categories-filter', response_model=List[CategorySchemaCreate])
async def get_category_filter(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    query = select(category)
    category__data = await session.execute(query)
    category_data = category__data.all()
    return category_data


@router.post('/category')
async def add_category(
        new_category: CategorySchemaCreate,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    try:
        query = insert(category).values(**dict(new_category))
        await session.execute(query)
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Category already exists!')
    return {'success': True}


@router.post('/subcategory')
async def add_subcategory(
        new_subcategory: SubcategorySchemaCreate,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    try:
        query = insert(subcategory).values(**dict(new_subcategory))
        await session.execute(query)
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Subcategory already exists!')
    return {'success': True}


@router.patch('/category')
async def update_category(
        id: int,
        new_name: str,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    query = update(category).where(category.c.id == id).values(name=new_name)
    await session.execute(query)
    await session.commit()
    return {'success': True}


@router.patch('/subcategory')
async def update_subcategory(
        id: int,
        new_name: str,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    query = update(subcategory).where(subcategory.c.id == id).values(name=new_name)
    await session.execute(query)
    await session.commit()
    return {'success': True}


@router.get('/products', response_model=List[ProductListSchema])
async def product_list(
        category_id: int | None,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    if category_id is None:
        query = select(product).order_by('id')
    else:
        query = select(product).where(product.c.subcategory_id.category_id == category_id).order_by('id')
    product__data = await session.execute(query)
    product_data = product__data.all()
    return product_data


@router.get('/user-list', response_model=List[UserRead])
async def user_list(token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(users)
    users_list = await session.execute(query)
    result = users_list.all()
    return result


@router.get('/order', response_model=List[OrderScheme])
async def order_list(
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        status: str | None = None,
        today: bool = False,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(order)

    if start_date is not None and end_date is not None:
        query = query.where(order.c.ordered_at >= start_date).where(order.c.ordered_at <= end_date)
    elif start_date is not None and end_date is None:
        query = query.where(order.c.ordered_at == start_date)

    if status is not None:
        query = query.where(order.c.status == status)

    if today:
        query = query.where(func.date(order.c.ordered_at) == datetime.utcnow().date())

    query = query.order_by('id')

    order__data = await session.execute(query)
    order_data = order__data.all()
    return order_data


@router.post('/upload-file')
async def upload_file(
        upload__file: UploadFile,
        product_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        out_file = f'files/{upload__file.filename}'
        async with aiofiles.open(f'media/{out_file}', 'wb') as f:
            content = await upload__file.read()
            await f.write(content)
        hashcode = secrets.token_hex(32)
        query = insert(file).values(product_id=product_id, file=out_file, hash=hashcode)
        await session.execute(query)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    return {'success': True, 'message': 'Uploaded successfully'}


@router.get('/download-file/{hashcode}')
async def download_file(
        hashcode: str,
        session: AsyncSession = Depends(get_async_session)
):
    if hashcode is None:
        raise HTTPException(status_code=400, detail='Invalid hashcode')

    query = select(file).where(file.c.hash == hashcode)
    file__data = await session.execute(query)
    file_data = file__data.one()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(BASE_DIR)
    file_url = os.path.join(BASE_DIR, f'media/{file_data.file}')
    file_name = file_data.file.split('/')[-1]
    return FileResponse(path=file_url, media_type="application/octet-stream", filename=file_name)


app.include_router(register_router)
app.include_router(router)
app.include_router(mobile_router, prefix='/mobile')
app.mount('/media', StaticFiles(directory='media'),'files')