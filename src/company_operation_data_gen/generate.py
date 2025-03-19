# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
Inserts the customer data, the product data, and the customer activity data into source database.
"""


from typing import Type
import datetime as dt

import sqlalchemy as sa
from pydantic import RootModel
from sqlalchemy.orm import DeclarativeBase, Session

from .database import SBase, ds
from .models import (
    ProductSource,
    CustomerSource,
    CustomerBehaviorSource,
    TransactionSource,
)
from .schemas import (
    CustomerData,
    ProductData,
    PromotionConstants,
    CustomerActivityData,
    CustomerBehaviorData,
    TransactionData,
)
from .constants import CustomerCountConstants
from .customer import customer_gen
from .scrape import product_gen
from .promotion import promotion_choose
from .transaction import activity_gen
from .logging import LOGGER


def init_customer(env: str = "dev") -> None:
    """Inserts the initial customer data into source database."""
    t_start: dt.datetime = dt.datetime.now()
    init_customer: CustomerData = customer_gen.gen_init_customer(
        count=CustomerCountConstants.CUSTOMER_COUNT_INIT
    )
    with ds.get_db(env=env) as db:
        SBase.metadata.create_all(db.bind)
        db.commit()
        insert_table(db, CustomerSource, init_customer)
        db.commit()
    LOGGER.info(
        f"Finished generating {len(init_customer.root)} initial customer records. {dt.datetime.now() - t_start}."
    )


def daily_register_customer(env: str = "dev") -> None:
    """Inserts the customer data daily."""
    t_start: dt.datetime = dt.datetime.now()
    customer: CustomerData = customer_gen.gen_new_customer(
        min=CustomerCountConstants.CUSTOMER_COUNT_MIN,
        max=CustomerCountConstants.CUSTOMER_COUNT_MAX,
    )

    with ds.get_db(env=env) as db:
        SBase.metadata.create_all(db.bind)
        db.commit()
        insert_table(db, CustomerSource, customer)
        db.commit()
        LOGGER.info(
            f"Finished generating {len(customer.root)} new customer records. {dt.datetime.now() - t_start}."
        )


def weekly_scrape_product(env: str = "dev") -> None:
    """Inserts the product data weekly."""
    t_start: dt.datetime = dt.datetime.now()

    product_gen.scrape()
    product: ProductData = product_gen.get_data()

    with ds.get_db(env=env) as db:
        SBase.metadata.create_all(db.bind)
        db.commit()
        insert_table(db, ProductSource, product)
        db.commit()
        LOGGER.info(
            f"Finished generating {len(product.root)} new product records. {dt.datetime.now() - t_start}."
        )


def daily_behavior_transaction(env: str = "dev") -> None:
    """Inserts the customer behavior data and transaction data daily."""
    t_start: dt.datetime = dt.datetime.now()
    promotion: PromotionConstants = promotion_choose.get_promotion_constants()
    activity: CustomerActivityData = activity_gen.generate(promotion)
    behavior: CustomerBehaviorData = activity.customer_behavior
    transaction: TransactionData = activity.transaction

    with ds.get_db(env=env) as db:
        SBase.metadata.create_all(db.bind)
        db.commit()
        insert_table(db, CustomerBehaviorSource, behavior)
        insert_table(db, TransactionSource, transaction)
        db.commit()
    LOGGER.info(
        f"Finished generating {len(behavior.root)} customer behavior records and {len(transaction.root)} transaction records. {dt.datetime.now() - t_start}."
    )


def insert_table(db: Session, model: Type[DeclarativeBase], data: RootModel) -> None:
    """Populates the database table with data."""
    table: sa.Table = model.__table__
    records = [record.model_dump() for record in data.root]
    db.execute(sa.insert(table), records)
    db.commit()
