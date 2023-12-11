from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select, insert, and_
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException

from auth.utils import verify_token
from database import get_async_session
from .schemes import ProductScheme, MainProductScheme
from models.models import product

mobile_router = APIRouter()


@mobile_router.get('/main-products', response_model=MainProductScheme)
async def main_products(session: AsyncSession = Depends(get_async_session)):
    # sale
    query_sale = select(product).where(product.c.discount_percent > 0)
    product_sales__data = await session.execute(query_sale)
    product_sales_data = product_sales__data.all()

    # new
    query_new = select(product).where(
        product.c.created_at >= func.current_timestamp() - timedelta(days=3)
    )
    product_new__data = await session.execute(query_new)
    product_new_data = product_new__data.all()
    return {
        'sales': product_sales_data,
        'new': product_new_data
    }
