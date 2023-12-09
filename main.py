from typing import List

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from database import get_async_session
from schemas import BlogSchema, BlogSchemaCreate
from auth.auth import register_router

app = FastAPI(title='P14Project', version='1.0.0')
router = APIRouter()

app.include_router(register_router)
