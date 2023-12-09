from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Text, MetaData, TIMESTAMP

metadata = MetaData()

blogs = Table(
    'blogs',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String, nullable=False),
    Column('description', Text, nullable=False),
    Column('date', TIMESTAMP, default=datetime.utcnow()),
    Column('view_count', Integer, default=0)
)

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('first_name', String),
    Column('last_name', String),
    Column('email', String),
    Column('phone', String),
    Column('username', String),
    Column('password', String)
)
