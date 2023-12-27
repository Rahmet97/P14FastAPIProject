from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SubcategorySchemaCreate(BaseModel):
    name: str
    category_id: int


class SubcategoryScheme(BaseModel):
    id: int
    name: str
    category_id: int


class CategorySchemaCreate(BaseModel):
    name: str


class CategorySchema(BaseModel):
    id: int
    name: str


class CategoryScheme(BaseModel):
    id: int
    name: str
    subcategories: List[SubcategoryScheme]


class ProductListSchema(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    sold_quantity: int


class OrderScheme(BaseModel):
    id: int
    user_id: int
    tracking_number: str
    ordered_at: datetime
    status: str


class ShippingAddressScheme(BaseModel):
    shipping_address: str


class ShippingAddressGetScheme(BaseModel):
    id: int
    shipping_address: str
    user_id: int


class BrandScheme(BaseModel):
    id: int
    name: str


class ProductAddScheme(BaseModel):
    brand_id: int
    name: str
    price: float
    discount_percent: int
    quantity: int
    description: str
    category_id: int
    subcategory_id: int
    category: str
    sizes: List[int]
    colors: List[int]


class AddColor(BaseModel):
    code: str


class SizeSchema(BaseModel):
    size: str
    category_id: int


class BrandAddSchema(BaseModel):
    name: str


class ColorListSchema(BaseModel):
    id: int
    code: str
