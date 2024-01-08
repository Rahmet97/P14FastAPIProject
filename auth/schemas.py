from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import TIMESTAMP


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    username: str
    password1: str
    password2: str


class UserInDB(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    username: str
    joined_at: datetime
    password: str = Field(required=False)


class UserInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    first_name: str
    last_name: str
    email: str
    joined_at: datetime
