from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

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


class RequestDataScheme(BaseModel):
    min: float | None
    max: float | None
    sizes: List[int] | None
    category: str | None
    brands: List[int] | None


class SizeScheme(BaseModel):
    id: int
    size: str
