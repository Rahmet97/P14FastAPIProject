from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from schemas import SubcategoryScheme


class BrandScheme(BaseModel):
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


class MainProductScheme(BaseModel):
    category_name: str
    products: List[ProductScheme]

