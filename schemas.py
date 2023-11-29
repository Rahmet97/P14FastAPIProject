from datetime import datetime
from pydantic import BaseModel


class BlogSchema(BaseModel):
    id: int
    title: str
    description: str
    date: datetime
    view_count: int


class BlogSchemaCreate(BaseModel):
    title: str
    description: str
