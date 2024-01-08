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
    Enum, Float
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
    Column('code', String(length=7))
)

size = Table(
    'size',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('size', String),
    Column('category_id', ForeignKey('category.id'))
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
    Column('sold_quantity', Integer, default=0),
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
    Column('joined_at', TIMESTAMP, default=datetime.utcnow),
    Column('cash', Float, default=1000)
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
    Column('product_id', ForeignKey('product.id')),
    Column('hash', String, unique=True)
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


class PaymentMethodEnum(enum.Enum):
    cash = 'cash'
    card = 'card'


order_products = Table(
    'order_products',
    metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('order_id', Integer, ForeignKey('order.id'))
)

order = Table(
    'order',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('tracking_number', Text),
    Column('user_id', ForeignKey('users.id')),
    Column('ordered_at', TIMESTAMP, default=datetime.utcnow),
    Column('status', Enum(StatusEnum)),
    Column('payment_method', Enum(PaymentMethodEnum)),
    Column('shipping_address_id', ForeignKey('shipping_address.id')),
    Column('delivery_method_id', ForeignKey('delivery_method.id')),
    Column('user_card_id', ForeignKey('user_card.id'), nullable=True)
)

shipping_address = Table(
    'shipping_address',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('shipping_address', Text)
)

delivery_method = Table(
    'delivery_method',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('delivery_company', String),
    Column('delivery_day', String),
    Column('delivery_price', DECIMAL(precision=10, scale=2)),
)

user_card = Table(
    'user_card',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('card_number', String),
    Column('card_expiration', String),
    Column('cvc', Integer),
    Column('user_id', ForeignKey('users.id'))
)

review = Table(
    'review',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('message', Text),
    Column('user_id', ForeignKey('users.id'), nullable=True),
    Column('product_id', ForeignKey('product.id')),
    Column('star', Integer),
    Column('reviewed_at', TIMESTAMP, default=datetime.utcnow)
)

image = Table(
    'image_review',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('image', String),
    Column('review_id', Integer, ForeignKey('review.id'))
)

shopping_cart = Table(
    'shopping_cart',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('product_id', ForeignKey('product.id')),
    Column('count', Integer, default=1),
    Column('added_at', TIMESTAMP, default=datetime.utcnow),
    UniqueConstraint('user_id', 'product_id', name='uniqueSC')
)

bank_card = Table(
    'bank_card',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('card_number', String(length=32)),
    Column('card_expiration', String(length=4)),
    Column('card_cvc', String(length=3), nullable=True),
    Column('user_id', ForeignKey('users.id')),
    Column('token', String, nullable=True)
)
