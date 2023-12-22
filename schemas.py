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
    product_id: int
    user_id: int
    count: int
    ordered_at: datetime
    status: str
