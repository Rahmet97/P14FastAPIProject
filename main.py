from typing import List

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update

from auth.schemas import UserRead
from auth.utils import verify_token
from database import get_async_session
from mobile.schemes import ProductScheme
from models.models import category, subcategory, product, users
from schemas import CategorySchemaCreate, SubcategorySchemaCreate, CategoryScheme, ProductListSchema
from auth.auth import register_router
from mobile.mobile import mobile_router

app = FastAPI(title='P14Project', version='1.0.0')
router = APIRouter()


@router.get('/category', response_model=List[CategoryScheme])
async def get_categories(keyword: str, token: dict = Depends(verify_token),
                         session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    query = select(category).where(category.c.category == keyword)
    category__data = await session.execute(query)
    category_data = category__data.all()
    categories = []
    for single in category_data:
        query2 = select(subcategory).where(subcategory.c.subcategory == single.id)
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


app.include_router(register_router)
app.include_router(router)
app.include_router(mobile_router, prefix='/mobile')
