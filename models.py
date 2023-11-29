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
