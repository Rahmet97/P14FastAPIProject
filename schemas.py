from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SubcategorySchemaCreate(BaseModel):
    name: str
    subcategory: int


class SubcategoryScheme(BaseModel):
    id: int
    name: str
    subcategory: int


class CategorySchemaCreate(BaseModel):
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


class OrderDetailSchema(BaseModel):
    id: int
    tracking_number: str
    shipping_address: str
    delivery_method: str
