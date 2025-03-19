# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The data model.
"""


import datetime as dt

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .database import SBase


class ProductSource(SBase):
    """The product record."""

    __tablename__ = "product"

    product_id: Mapped[str] = mapped_column(sa.VARCHAR(36), primary_key=True)
    product_name: Mapped[str] = mapped_column(sa.VARCHAR(255))
    brand_name: Mapped[str] = mapped_column(sa.VARCHAR(100), nullable=True)
    category: Mapped[str] = mapped_column(sa.VARCHAR(50))
    price: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    promotion_price: Mapped[int]
    fetched_at: Mapped[dt.datetime]


class CustomerSource(SBase):
    """The customer record."""

    __tablename__ = "customer"

    customer_id: Mapped[str] = mapped_column(sa.VARCHAR(36), primary_key=True)
    customer_name: Mapped[str] = mapped_column(sa.VARCHAR(50))
    gender: Mapped[str] = mapped_column(sa.VARCHAR(10))
    birth: Mapped[dt.datetime]
    email: Mapped[str] = mapped_column(sa.VARCHAR(255))
    phone_number: Mapped[str] = mapped_column(sa.VARCHAR(50))
    city: Mapped[str] = mapped_column(sa.VARCHAR(50))
    registered_at: Mapped[dt.datetime]


class CustomerBehaviorSource(SBase):
    """The customer behavior record."""

    __tablename__ = "customer_behavior"

    customer_id: Mapped[str] = mapped_column(sa.VARCHAR(36), primary_key=True)
    product_id: Mapped[str] = mapped_column(sa.VARCHAR(36), primary_key=True)
    action_type: Mapped[str] = mapped_column(sa.VARCHAR(20))
    device_type: Mapped[str] = mapped_column(sa.VARCHAR(20))
    referrer: Mapped[str] = mapped_column(sa.VARCHAR(20))
    action_at: Mapped[dt.datetime] = mapped_column(primary_key=True)


class TransactionSource(SBase):
    """The transaction record."""

    __tablename__ = "transaction"

    customer_id: Mapped[str] = mapped_column(sa.VARCHAR(36), primary_key=True)
    product_id: Mapped[str] = mapped_column(sa.VARCHAR(36), primary_key=True)
    quantity: Mapped[int]
    promotion_price: Mapped[int]
    amount: Mapped[int]
    discount: Mapped[int]
    gift: Mapped[str] = mapped_column(sa.VARCHAR(100), nullable=True)
    total: Mapped[int]
    transaction_at: Mapped[dt.datetime] = mapped_column(primary_key=True)


class PromotionDateSource(SBase):
    """The promotion everday."""

    __tablename__ = "promotion_date"

    day_of_week: Mapped[int] = mapped_column(primary_key=True)
    promotion_type: Mapped[str] = mapped_column(sa.VARCHAR(20))
    published_at: Mapped[dt.datetime] = mapped_column(primary_key=True)


class PromotionSource(SBase):
    """The promotion record."""

    __tablename__ = "promotion"

    promotion_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    promotion_name: Mapped[str] = mapped_column(sa.VARCHAR(50))
    promotion_type: Mapped[str] = mapped_column(sa.VARCHAR(20))
    cash_threshold: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    quantity_threshold: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    discount_rate: Mapped[float] = mapped_column(sa.Float, nullable=True)
    gift: Mapped[str] = mapped_column(sa.VARCHAR(20), nullable=True)
    published_at: Mapped[dt.datetime]
