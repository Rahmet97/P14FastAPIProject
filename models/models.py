from datetime import datetime

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    MetaData,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    DECIMAL,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

metadata = MetaData()

product_colors = Table(
    'product_colors',
    metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('color_id', Integer, ForeignKey('color.id'))
)

product_sizes = Table(
    'product_sizes',
    metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('size_id', Integer, ForeignKey('size.id'))
)

color = Table(
    'color',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String)
)

size = Table(
    'size',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('size', String)
)

product = Table(
    'product',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('brand_id', ForeignKey('brand.id')),
    Column('name', String),
    Column('price', DECIMAL(precision=10, scale=2)),
    Column('discount_percent', Integer, default=0),
    Column('quantity', Integer),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('sold_quantity', Integer),
    Column('description', Text),
    Column('subcategory_id', ForeignKey('subcategory.id'))
)

product_color_relationship = relationship("color", secondary=product_colors, backref="products")
product_size_relationship = relationship("size", secondary=product_sizes, backref="products")

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('first_name', String),
    Column('last_name', String),
    Column('email', String),
    Column('phone', String),
    Column('username', String),
    Column('password', String),
    Column('is_superuser', Boolean, default=False)
)

brand = Table(
    'brand',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String)
)

file = Table(
    'file',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('file', String),
    Column('product_id', ForeignKey('product.id'))
)

subcategory_enum = ENUM('men', 'women', 'kids', name='subcategory_enum')

category = Table(
    'category',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String),
    Column('category', subcategory_enum),
    UniqueConstraint('name', 'category', name='uniqNC')
)

subcategory = Table(
    'subcategory',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String),
    Column('subcategory', ForeignKey('category.id')),
    UniqueConstraint('name', 'subcategory', name='uniqNS')
)

status_enum = ENUM('delivered', 'processing', 'canceled', name='status_enum')

order = Table(
    'order',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('product_id', ForeignKey('product.id')),
    Column('user_id', ForeignKey('users.id')),
    Column('count', Integer),
    Column('ordered_at', TIMESTAMP, default=datetime.utcnow),
    Column('status', status_enum)
)

review = Table(
    'review',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('message', Text),
    Column('user_id', ForeignKey('users.id'), nullable=True),
    Column('product_id', ForeignKey('product.id')),
    Column('reviewed_at', TIMESTAMP, default=datetime.utcnow)
)
