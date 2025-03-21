import uuid
from datetime import datetime, timedelta
from typing import Type
from faker import Faker
import numpy as np

import sqlalchemy as sa
from pydantic import RootModel
from sqlalchemy.orm import DeclarativeBase, Session

from .database import SBase, ds
from .scrape import product_gen

from .schemas import (
    CustomerData,
    CustomerRecord,
    ProductData,
)

from .models import (
    ProductSource,
    CustomerSource,
)


fake = Faker("zh-TW")


def insert_table(db: Session, model: Type[DeclarativeBase], data: RootModel) -> None:
    """Populates the database table with data."""
    table: sa.Table = model.__table__
    records = [record.model_dump() for record in data.root]
    db.execute(sa.insert(table), records)
    db.commit()


def history_customer(
    min_records: int, max_records: int, start_date: str, end_date: str
) -> None:

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    date_range = [start + timedelta(days=i) for i in range((end - start).days + 1)]

    record = []

    for date in date_range:
        count = np.random.randint(min_records, max_records)
        for _ in range(count):
            record.append(
                CustomerRecord(
                    customer_id=str(uuid.uuid4()),
                    customer_name=fake.name(),
                    gender=fake.random_element(elements=("M", "F")),
                    birth=fake.date_of_birth(minimum_age=16, maximum_age=70),
                    email=fake.email(),
                    phone_number=fake.phone_number(),
                    city=fake.city_name(),
                    registered_at=date,
                )
            )

    customer = CustomerData(root=record)

    with ds.get_db() as db:
        SBase.metadata.create_all(db.bind)
        db.commit()
        insert_table(db, CustomerSource, customer)
        db.commit()


def history_product(scrape_date: str) -> None:
    product_gen.scrape()
    product: ProductData = product_gen.get_data()
    init_date = datetime.strptime(scrape_date, "%Y-%m-%d")
    init_product = ProductData(
        root=[p.model_copy(update={"fetched_at": init_date}) for p in product.root]
    )
    with ds.get_db() as db:
        SBase.metadata.create_all(db.bind)
        db.commit()
        insert_table(db, ProductSource, init_product)
        db.commit()


history_customer(5, 15, "2025-03-15", "2025-03-18")
history_product("2025-01-01")
