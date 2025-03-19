# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The customer data generator.
"""


import uuid
import random
from datetime import datetime, timedelta

from faker import Faker
import numpy as np

from .schemas import (
    CustomerData,
    CustomerRecord,
)


fake = Faker("zh-TW")


class CustomerGenerator:
    """The customer data generator."""

    def gen_init_customer(self, count) -> CustomerData:
        """The initial customer data."""
        return self.__generate(count=count)

    def gen_new_customer(self, min, max) -> CustomerData:
        """A random count of new customer data."""
        return self.__generate(count=np.random.randint(min, max))

    def __generate(self, count: int) -> CustomerData:
        """Generates and returns customer data."""

        yesterday = datetime.now() - timedelta(days=1)
        """Generates customer data of previous day."""

        cities = [
            "臺北市",
            "新北市",
            "桃園市",
            "臺中市",
            "臺南市",
            "高雄市",
            "新竹縣",
            "苗栗縣",
            "彰化縣",
            "南投縣",
            "雲林縣",
            "嘉義縣",
            "屏東縣",
            "宜蘭縣",
            "花蓮縣",
            "臺東縣",
            "澎湖縣",
            "金門縣",
            "連江縣",
            "基隆市",
            "新竹市",
            "嘉義市",
        ]
        record = [
            CustomerRecord(
                customer_id=str(uuid.uuid4()),
                customer_name=fake.name(),
                gender=fake.random_element(elements=("M", "F")),
                birth=fake.date_of_birth(minimum_age=16, maximum_age=70),
                email=fake.email(),
                phone_number=fake.phone_number(),
                city=random.choice(cities),
                registered_at=yesterday,
            )
            for _ in range(count)
        ]

        return CustomerData(root=record)


customer_gen: CustomerGenerator = CustomerGenerator()
"""The customer data generator."""
