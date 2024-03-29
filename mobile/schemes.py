from datetime import datetime
from typing import List, Union

from decimal import Decimal
from fastapi import UploadFile

from pydantic import BaseModel, Field

from mobile.utils import decode_card_number
from schemas import SubcategoryScheme


class BrandScheme(BaseModel):
    id: int
    name: str


class CategorySchema(BaseModel):
    id: int
    name: str


class ProductScheme(BaseModel):
    id: int
    brand: dict
    name: str
    price: float
    discount_percent: int
    quantity: int
    created_at: datetime
    sold_quantity: int
    description: str
    subcategory: dict
    category: str


class ProductForFilterScheme(BaseModel):
    id: int
    brand_id: int
    name: str
    price: float
    discount_percent: int
    quantity: int
    created_at: datetime
    sold_quantity: int
    description: str
    subcategory_id: int
    category: str


class MainProductScheme(BaseModel):
    category_name: str
    products: List[ProductScheme]


class SubCategoryProductScheme(BaseModel):
    name: str
    brand: dict
    price: float
    description: str


class RequestDataScheme(BaseModel):
    min: Union[float, None]
    max: Union[float, None]
    sizes: Union[List[int], None]
    category: Union[str, None]
    brands: Union[List[int], None]


class SizeScheme(BaseModel):
    id: int
    size: str


class ShoppingCartScheme(BaseModel):
    id: int
    product: dict
    count: int
    added_at: datetime


class ShoppingSaveCartScheme(BaseModel):
    product_id: int
    count: Union[int, None] = Field(gte=0)


class UserCardScheme(BaseModel):
    card_number: str = Field(max_length=16, min_length=16)
    card_expiration: str = Field(max_length=4, min_length=4)
    card_cvc: Union[str, None]


class CardScheme(BaseModel):
    id: int
    card_number: str
    card_expiration: str


class ReviewScheme(BaseModel):
    star: int
    review: str
    product_id: int
