# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The transaction data test cases.
"""


import os
import yaml
import random
from datetime import datetime, timedelta
from typing import List

import pytest

from company_operation_data_gen.transaction import activity_gen
from company_operation_data_gen.database import ds, SBase
from company_operation_data_gen.models import (
    ProductSource,
    CustomerSource,
)
from company_operation_data_gen.schemas import (
    CustomerRecord,
    CustomerData,
    ProductRecord,
    ProductData,
    CustomerActivityData,
    CustomerBehaviorData,
    CustomerBehaviorRecord,
    TransactionData,
    PromotionConstants,
    PromotionData,
    PromotionRecord,
)
from company_operation_data_gen.constants import (
    BehaviorCountConstants,
    QuantityCountConstants,
)


current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "fixtures", "test_data.yaml")
with open(file_path, "r") as f:
    data = yaml.safe_load(f)

test_promotion_type = "多件優惠"

promotion_detail = PromotionData(
    root=[
        PromotionRecord(**record)
        for record in data["promotion"]
        if record["promotion_type"] == test_promotion_type
    ]
)

promotion_constants = PromotionConstants(
    promotion_type=test_promotion_type,
    promotion_detail=promotion_detail,
    behavior_avg=BehaviorCountConstants.MULTI_BEHAVIOR_AVG,
    behavior_sigma=BehaviorCountConstants.MULTI_BEHAVIOR_SIGMA,
    behavior_min=BehaviorCountConstants.MULTI_BEHAVIOR_MIN,
    behavior_max=BehaviorCountConstants.MULTI_BEHAVIOR_MAX,
    quantity_avg=QuantityCountConstants.MULTI_QUANTITY_AVG,
    quantity_sigma=QuantityCountConstants.MULTI_QUANTITY_SIGMA,
    quantity_min=QuantityCountConstants.MULTI_QUANTITY_MIN,
    quantity_max=QuantityCountConstants.MULTI_QUANTITY_MAX,
)


@pytest.fixture
def setup_test_db():
    """Sets up the SQLite in memory database for testing."""
    session = ds.get_db(env="test")
    SBase.metadata.create_all(session.get_bind())

    customers = CustomerData(
        root=[CustomerRecord(**record) for record in data["customers"]]
    )
    orm_customer = [CustomerSource(**record.model_dump()) for record in customers.root]
    session.bulk_save_objects(orm_customer)

    products = ProductData(
        root=[ProductRecord(**record) for record in data["products"]]
    )
    orm_product = [ProductSource(**record.model_dump()) for record in products.root]
    session.bulk_save_objects(orm_product)
    session.commit()

    yield session

    session.close()


class TestGenerate:
    def test_generate(self, setup_test_db):
        activity: CustomerActivityData = activity_gen.generate(
            promotion_constants=promotion_constants, session=setup_test_db
        )
        customer_behavior_data: CustomerBehaviorData = activity.customer_behavior
        transaction_data: TransactionData = activity.transaction

        self.__test_data_count(
            promotion_constants, customer_behavior_data, transaction_data
        )
        self.__test_data_datetime(customer_behavior_data, transaction_data)
        self.__test_transaction_process(customer_behavior_data, transaction_data)
        self.__test_discount_calcu(promotion_detail, transaction_data)

    def __test_data_count(
        self,
        promotion_constants: PromotionConstants,
        customer_behavior_data: CustomerBehaviorData,
        transaction_data: TransactionData,
    ):
        """Test the number of views is between the specified maximum and minimum values
        ,and greater than the number of transaction."""
        view_actions: List[CustomerBehaviorRecord] = [
            behavior
            for behavior in customer_behavior_data.root
            if behavior.action_type == "view"
        ]
        view_count = len(view_actions)
        assert promotion_constants.behavior_min <= view_count
        assert view_count <= promotion_constants.behavior_max
        assert len(transaction_data.root) <= view_count

    def __test_data_datetime(
        self,
        customer_behavior_data: CustomerBehaviorData,
        transaction_data: TransactionData,
    ):
        """Test the customer behavior data and transaction data correspond to the previous day's date."""
        now = datetime.now()
        yesterday = datetime(now.year, now.month, now.day) - timedelta(days=1)
        for record in customer_behavior_data.root:
            assert record.action_at >= yesterday
        for record in transaction_data.root:
            assert record.transaction_at >= yesterday

    def __test_transaction_process(
        self,
        customer_behavior_data: CustomerBehaviorData,
        transaction_data: TransactionData,
    ):
        """Test the transaction record follows the sequence of browsing, adding to the cart, and purchasing."""
        transaction_record = random.choice(transaction_data.root)
        correspond_behavior = [
            record
            for record in customer_behavior_data.root
            if record.customer_id == transaction_record.customer_id
            and record.product_id == transaction_record.product_id
            and record.action_at == transaction_record.transaction_at
        ]
        related_behavior = [
            record
            for record in customer_behavior_data.root
            if record.customer_id == correspond_behavior[0].customer_id
            and record.product_id == correspond_behavior[0].product_id
            and record.device_type == correspond_behavior[0].device_type
            and record.referrer == correspond_behavior[0].referrer
        ]
        action_types = [record.action_type for record in related_behavior]
        assert "view" in action_types
        assert "add_to_cart" in action_types
        assert "purchase" in action_types

    def __test_discount_calcu(
        self, promotion_detail: PromotionData, transaction_data: TransactionData
    ):
        """Test the correct promotion is applied, and the discount calculation is accurate."""
        sorted_promotions = sorted(
            promotion_detail.root,
            key=lambda promo: promo.quantity_threshold,
            reverse=True,
        )

        for record in transaction_data.root:
            for promo in sorted_promotions:
                if record.quantity >= promo.quantity_threshold:
                    return promo
            discount = int(round(record.amount * promo.discount_rate))
            assert record.discount == discount
            assert record.total == record.amount - discount
