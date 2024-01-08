import secrets
from datetime import timedelta, datetime
from typing import List

import aiofiles
from starlette import status
from sqlalchemy import select, and_, insert, update, delete
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException, UploadFile

from auth.utils import verify_token
from database import get_async_session
from .schemes import ProductScheme, MainProductScheme, SubCategoryProductScheme
from models.models import product, category, subcategory, brand, review, image
from schemas import ShippingAddressScheme, ShippingAddressGetScheme
from .schemes import ProductScheme, MainProductScheme, RequestDataScheme, ProductForFilterScheme, CategorySchema, \
    SizeScheme, ShoppingSaveCartScheme, ShoppingCartScheme, UserCardScheme, CardScheme, ReviewScheme
from models.models import product, category, subcategory, brand, product_sizes, size, shopping_cart, shipping_address, \
    bank_card
from .utils import step_3, collect_to_list

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
            query = query.where(
                and_(product.c.price >= request_data.min, product.c.price <= request_data.max)).order_by('id')
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


@mobile_router.post('/shopping-cart')
async def shopping_cart_data(
        data: ShoppingSaveCartScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(shopping_cart).where(
        (shopping_cart.c.user_id == token.get('user_id')) & (shopping_cart.c.product_id == data.product_id))
    shopping__data = await session.execute(query)
    try:
        shopping_data = shopping__data.one()
        if data.count == 0:
            query3 = delete(shopping_cart).where(shopping_cart.c.id == shopping_data.id)
            await session.execute(query3)
            await session.commit()
            return {'success': True, 'message': 'Product removed'}
        count = shopping_data.count + 1 if data.count is None else data.count
        query3 = update(shopping_cart).where(shopping_cart.c.id == shopping_data.id).values(count=count)
        await session.execute(query3)
        await session.commit()
    except NoResultFound:
        count = 1 if data.count is None else data.count
        query2 = insert(shopping_cart).values(user_id=token.get('user_id'), product_id=data.product_id, count=count)
        await session.execute(query2)
        await session.commit()
    return {'success': True, 'message': 'Added to shopping cart'}


@mobile_router.get('/shopping-cart', response_model=List[ShoppingCartScheme])
async def get_shopping_cart(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(shopping_cart).where(shopping_cart.c.user_id == token.get('user_id')).order_by('id')
    shopping__data = await session.execute(query)
    shopping_data = shopping__data.all()

    shopping_list = []
    for data in shopping_data:
        query_product = select(product).where(product.c.id == data.product_id)
        product__detail = await session.execute(query_product)
        product_detail = product__detail.one()._asdict()
        shopping_dict = {
            'id': data.id,
            'product': product_detail,
            'count': data.count,
            'added_at': data.added_at
        }
        shopping_list.append(shopping_dict)
    return shopping_list


@mobile_router.post('/shipping-address')
async def post_shipping_address(
        shipping_address_data: ShippingAddressScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(shipping_address).where(
        (
                shipping_address.c.shipping_address == shipping_address_data.shipping_address
        ) &
        (
                shipping_address.c.user_id == token.get('user_id')
        )
    )
    shipping__data = await session.execute(query)
    shipping_data = shipping__data.one_or_none()
    if shipping_data is None:
        query2 = insert(shipping_address).values(
            user_id=token.get('user_id'),
            shipping_address=shipping_address_data.shipping_address
        )
        await session.execute(query2)
        await session.commit()
    else:
        raise HTTPException(status_code=400, detail='Shipping address already exists!')
    return {'success': True, 'message': 'Added shipping address'}


@mobile_router.get('/shipping-address', response_model=List[ShippingAddressGetScheme])
async def get_user_shipping_addresses(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    query = select(shipping_address).where(shipping_address.c.user_id == token.get('user_id'))
    user_shipping__data = await session.execute(query)
    user_shipping_data = user_shipping__data.all()
    return user_shipping_data


@mobile_router.post('/add-card')
async def add_card(
        card_detail: UserCardScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')

    card_number = step_3(card_detail.card_number)
    query = select(bank_card).where(bank_card.c.card_number == card_number)
    card__data = await session.execute(query)
    card_data = card__data.one_or_none()
    if card_data:
        raise HTTPException(status_code=400, detail='Card already exists!')
    else:
        query2 = insert(bank_card).values(
            card_number=card_number,
            card_expiration=card_detail.card_expiration,
            card_cvc=card_detail.card_cvc,
            user_id=token.get('user_id')
        )
        await session.execute(query2)
        await session.commit()
    return {'success': True, 'message': 'Successfully added'}


@mobile_router.get('/user-cards', response_model=List[CardScheme])
async def get_user_cards(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    query = select(bank_card).where(bank_card.c.user_id == token.get('user_id'))
    card__data = await session.execute(query)
    card_data = card__data.all()
    cards_data = collect_to_list(card_data)
    return cards_data


@mobile_router.post('/review')
async def product_review(
        image_data: UploadFile,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session),
        review_data: ReviewScheme = Depends(),
):
    if token is None:
        raise HTTPException(status_code=403, detail='Forbidden')
    user_id = token.get('user_id')
    try:
        out_file = f'images/{image_data.filename}'
        async with aiofiles.open(f'media/{out_file}', 'wb') as f:
            content = await image_data.read()
            await f.write(content)

        insert_review_query = insert(review).values(
            message=review_data.review,
            user_id=user_id,
            star=review_data.star,
            product_id=review_data.product_id,
        )

        review_result = await session.execute(insert_review_query)
        review_id = review_result.scalars().first()

        insert_image_review_query = insert(image).values(
            image=out_file,
            review_id=review_id,
        )
        await session.execute(insert_image_review_query)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {'success': True, 'message': 'Reviewed !!!'}
