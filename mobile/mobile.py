from datetime import timedelta
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException

from auth.utils import verify_token
from database import get_async_session
from .schemes import ProductScheme, MainProductScheme, RequestDataScheme, ProductForFilterScheme, CategorySchema, \
    SizeScheme
from models.models import product, category, subcategory, brand, product_sizes, size

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


@mobile_router.get('/categories', response_model=List[CategorySchema])
async def get_category_filter(
        session: AsyncSession = Depends(get_async_session)
):
    query = select(category)
    category__data = await session.execute(query)
    category_data = category__data.all()
    return category_data


@mobile_router.get('/category-sizes', response_model=List[SizeScheme])
async def category_sizes(category_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(size).where(size.c.category_id == category_id).order_by('id')
    sizes__data = await session.execute(query)
    sizes_data = sizes__data.all()
    return sizes_data


@mobile_router.get('/filter', response_model=List[ProductForFilterScheme])
async def product_filter(
        request_data: RequestDataScheme,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(product)
    if request_data.min is not None and request_data.max is not None:
        if request_data.min <= request_data.max:
            query = query.where(and_(product.c.price >= request_data.min, product.c.price <= request_data.max)).order_by('id')
        else:
            raise HTTPException(status_code=400, detail="Min price should be less than or equal to max price.")

    if request_data.sizes is not None:
        if request_data.sizes:
            product_sizes_query = select(product_sizes).where(product_sizes.c.size_id.in_(request_data.sizes))
            product_datas = await session.execute(product_sizes_query)
            product_ids = [row.product_id for row in product_datas]
            if product_ids:
                query = query.where(product.c.id.in_(product_ids)).order_by('id')
            else:
                raise HTTPException(status_code=400, detail="No products found for the given size(s).")

    if request_data.category is not None:
        if request_data.category in ['women', 'men', 'kids']:
            query = query.where(product.c.category == request_data.category).order_by('id')
        else:
            raise HTTPException(status_code=400, detail="No products found for the given category.")

    if request_data.brands is not None:
        query = query.where(product.c.brand_id.in_(request_data.brands)).order_by('id')

    product__datas = await session.execute(query)
    product_datas = product__datas.all()
    print(product_datas)
    return product_datas
