import enum
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
    UniqueConstraint,
    Enum
)
from sqlalchemy.orm import relationship

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


class CategoryEnum(enum.Enum):
    men = 'Men'
    women = 'Women'
    kids = 'Kids'


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
    Column('category_id', ForeignKey('category.id')),
    Column('subcategory_id', ForeignKey('subcategory.id')),
    Column('category', Enum(CategoryEnum))
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
    Column('is_superuser', Boolean, default=False),
    Column('joined_at', TIMESTAMP, default=datetime.utcnow)
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

category = Table(
    'category',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String)
)

subcategory = Table(
    'subcategory',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String),
    Column('category_id', ForeignKey('category.id')),
    UniqueConstraint('name', 'category_id', name='uniqNS')
)


class StatusEnum(enum.Enum):
    delivered = 'delivered'
    processing = 'processing'
    canceled = 'canceled'


order = Table(
    'order',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('tracking_number', Text),
    Column('product_id', ForeignKey('product.id')),
    Column('user_id', ForeignKey('users.id')),
    Column('count', Integer),
    Column('ordered_at', TIMESTAMP, default=datetime.utcnow),
    Column('status', Enum(StatusEnum))
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

shipping_address = Table(
    'shipping_address',
    metadata,
    Column('order_id', ForeignKey('order.id')),
    Column('user_id', ForeignKey('user.id')),
    Column('shipping address', Text),
)

delivery_method = Table(
    'delivery_method',
    metadata,
    Column('delivery_company', String),
    Column('delivery_day', String),
    Column('delivery_price', DECIMAL(precision=10, scale=2)),
)

order_detail = Table(
    'order_detail',
    metadata,
    Column('tracking_number', ForeignKey('order.tracking_number')),
    Column('shipping_address_id', ForeignKey('shipping_address.id')),
    Column('delivery_method_id', ForeignKey('delivery_method.id')),
)