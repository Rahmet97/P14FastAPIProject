from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class BlogSchema(BaseModel):
    id: int
    title: str
    description: str
    date: datetime
    view_count: int


class SubcategorySchemaCreate(BaseModel):
    name: str
    subcategory: int


class SubcategoryScheme(BaseModel):
    id: int
    name: str
    subcategory: int


class CategorySchemaCreate(BaseModel):
    name: str
    category: str = Field(examples=['women', 'men', 'kids'])


class CategoryScheme(BaseModel):
    id: int
    name: str
    subcategories: List[SubcategoryScheme]
