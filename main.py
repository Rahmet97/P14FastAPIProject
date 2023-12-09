from typing import List

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from database import get_async_session
from models.models import blogs
from schemas import BlogSchema, BlogSchemaCreate
from auth.auth import register_router

app = FastAPI(title='P14Project', version='1.0.0')
router = APIRouter()


@router.post('/blogs')
async def add_blog(new_blog: BlogSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    query = insert(blogs).values(**dict(new_blog))
    await session.execute(query)
    await session.commit()
    return {'success': True}


@router.get('/blogs', response_model=List[BlogSchema])
async def blog_list(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(blogs)
        result = await session.execute(query)
        return result.all()
    except Exception:
        raise HTTPException(status_code=500)


@router.get('/blogs/{blog_id}', response_model=BlogSchema)
async def blog_detail(blog_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(blogs).where(blogs.c.id == blog_id)
    result = await session.execute(query)
    return result.one()


app.include_router(router)
app.include_router(register_router)
