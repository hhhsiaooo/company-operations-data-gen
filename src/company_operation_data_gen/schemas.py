# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The Pydantic schemas.
"""


import datetime as dt
from typing import Literal, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductRecord(BaseModel):
    """The product record."""

    product_id: str
    product_name: str
    brand_name: str | None
    category: str
    price: int | None
    promotion_price: int = Field(gt=0, description="售價必須大於0")
    fetched_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class ProductData(BaseModel):
    """The product data."""

    root: List[ProductRecord]


class CustomerRecord(BaseModel):
    """The customer record."""

    customer_id: str
    customer_name: str
    gender: str
    birth: dt.datetime
    email: str
    phone_number: str
    city: str
    registered_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerData(BaseModel):
    """The customer data."""

    root: List[CustomerRecord]


class CustomerBehaviorRecord(BaseModel):
    """The customer behavior record."""

    customer_id: str
    product_id: str
    action_type: Literal["view", "add_to_cart", "purchase"]
    device_type: Optional[Literal["mobile", "tablet", "desktop", "laptop", "unknown"]]
    referrer: Optional[
        Literal[
            "direct",
            "search_engine",
            "social_media",
            "email",
            "paid_ads",
            "referral",
            "unknown",
        ]
    ]
    action_at: dt.datetime


class CustomerBehaviorData(BaseModel):
    """The customer behavior data."""

    root: List[CustomerBehaviorRecord]


class TransactionRecord(BaseModel):
    """The transaction record."""

    customer_id: str
    product_id: str
    quantity: int = Field(gt=0, description="購買數量必須大於0")
    promotion_price: int = Field(gt=0, description="售價必須大於0")
    amount: int = Field(gt=0, description="總金額必須大於0")
    discount: int = Field(ge=0, description="折扣金額必須大於等於0")
    gift: str | None
    total: int = Field(gt=0, description="折扣後金額必須大於0")
    transaction_at: dt.datetime


class TransactionData(BaseModel):
    """The transaction data."""

    root: List[TransactionRecord]


class CustomerActivityData(BaseModel):
    """The customer activity data."""

    customer_behavior: CustomerBehaviorData
    """The customer behavior data."""
    transaction: TransactionData
    """The transaction data."""


class PromotionDateRecord(BaseModel):
    """The promotion dates record."""

    day_of_week: int
    promotion_type: str
    published_at: dt.datetime


class PromotionDateData(BaseModel):
    """The promotion dates data."""

    root: List[PromotionDateRecord]


class PromotionRecord(BaseModel):
    """The promotion record."""

    promotion_id: int
    promotion_name: str
    promotion_type: str
    cash_threshold: int | None
    quantity_threshold: int | None
    discount_rate: float | None
    gift: str | None
    published_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class PromotionData(BaseModel):
    """The promotion data."""

    root: List[PromotionRecord]


class PromotionConstants(BaseModel):
    """The constants for each promotion."""

    promotion_type: str
    promotion_detail: PromotionData
    behavior_avg: int
    behavior_sigma: float
    behavior_min: int
    behavior_max: int
    quantity_avg: int
    quantity_sigma: float
    quantity_min: int
    quantity_max: int
