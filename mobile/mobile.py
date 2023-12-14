from datetime import timedelta, datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException

from auth.utils import verify_token
from database import get_async_session
from .schemes import ProductScheme, MainProductScheme, SubCategoryProductScheme
from models.models import product, category, subcategory, brand

mobile_router = APIRouter()


@mobile_router.get('/main-products', response_model=List[MainProductScheme])
async def main_products(session: AsyncSession = Depends(get_async_session)):
    try:
        query_sale = select(product).where(product.c.discount_percent > 0)
        product_sales_data = await session.execute(query_sale)
        product_sales_data = product_sales_data.all()[:5]

        query_new = select(product).where(
            product.c.created_at >= func.current_timestamp() - timedelta(days=3)
        )
        product_new_data = await session.execute(query_new)
        product_new_data = product_new_data.all()[:5]

        query_categories = select(category)
        categories_data = await session.execute(query_categories)
        categories = categories_data.all()

        data = [
            {
                'category_name': 'sales',
                'products': product_sales_data
            },
            {
                'category_name': 'new',
                'products': product_new_data
            },
        ]

        for category_data in categories:
            query_products = select(product).where(product.c.category_id == category_data.id)
            category_products_data = await session.execute(query_products)
            category_products = category_products_data.scalars().all()[:5]
            data_dict = {
                'category_name': category_data.name,
                'products': category_products
            }
            data.append(data_dict)

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mobile_router.get('/products/{product_id}', response_model=ProductScheme)
async def product_detail(
        product_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(product).where(product.c.id == product_id)
    product__data = await session.execute(query)
    try:
        product_data = product__data.one()
        product_data = product_data._asdict()
        subcategory_query = select(subcategory).where(subcategory.c.id == product_data.get('subcategory_id'))
        brand_query = select(brand).where(brand.c.id == product_data.get('brand_id'))
        subcategory__data = await session.execute(subcategory_query)
        brand__data = await session.execute(brand_query)
        product_data['subcategory'] = subcategory__data.one()._asdict()
        product_data['brand'] = brand__data.one()._asdict()
        return product_data
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Product not found!')


@mobile_router.get('/subcategory_products_sort/{subcategory_id}', response_model=List[SubCategoryProductScheme])
async def get_subcategory_products(
        subcategory_id: int, keyword: str,
        session: AsyncSession = Depends(get_async_session)):
    lowest_price_query = (
        select(product).where(product.c.subcategory_id == subcategory_id).order_by(product.c.price))
    product__data = await session.execute(lowest_price_query)
    product_data = []
    try:
        for data in product__data.all():
            data = data._asdict()
            brand_query = select(brand).where(brand.c.id == data.get('brand_id'))
            brand__data = await session.execute(brand_query)
            data['brand'] = brand__data.one()._asdict()
            product_data.append(data)
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Product not found')
    if keyword == 'lth':
        return product_data
    elif keyword == 'htl':
        return product_data[::-1]
    elif keyword == 'nst':
        query_products = select(product).where(product.c.subcategory_id == subcategory_id).where(
            product.c.created_at >= func.current_timestamp() - timedelta(days=3))
        products = await session.execute(query_products)
        products_data = []
        try:
            for data in products.all():
                data = data._asdict()
                brand_query = select(brand).where(brand.c.id == data.get('brand_id'))
                brand__data = await session.execute(brand_query)
                data['brand'] = brand__data.one()._asdict()
                products_data.append(data)
                print(products_data)
            return products_data
        except NoResultFound:
            raise HTTPException(status_code=404, detail='Product not found')
    else:
        raise HTTPException(status_code=404, detail="Keyword not found")


@mobile_router.get('/subcategory_products/{subcategory_id}', response_model=List[SubCategoryProductScheme])
async def get_subcategory_products(
        subcategory_id: int,
        session: AsyncSession = Depends(get_async_session)):
    query = (
        select(product).where(product.c.subcategory_id == subcategory_id))
    product__data = await session.execute(query)
    product_data = []
    try:
        for data in product__data.all():
            data = data._asdict()
            brand_query = select(brand).where(brand.c.id == data.get('brand_id'))
            brand__data = await session.execute(brand_query)
            data['brand'] = brand__data.one()._asdict()
            product_data.append(data)
        return product_data
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Product not found')
