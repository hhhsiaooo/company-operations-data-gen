# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The data generation test cases.
"""


import pytest

from company_operation_data_gen.database import ds
from company_operation_data_gen.constants import CustomerCountConstants
from company_operation_data_gen.models import (
    ProductSource,
    CustomerSource,
    CustomerBehaviorSource,
    TransactionSource,
)
from company_operation_data_gen.generate import (
    init_customer,
    weekly_scrape_product,
    daily_behavior_transaction,
)


@pytest.fixture
def setup_test_db():
    """Sets up the SQLite in memory database for testing."""
    session = ds.get_db(env="test")

    yield session

    session.query(CustomerSource).delete()
    session.query(ProductSource).delete()
    session.commit()
    session.close()


def test_init_customer(setup_test_db):
    init_customer(env="test")
    count_customer = setup_test_db.query(CustomerSource).all()
    assert len(count_customer) == CustomerCountConstants.CUSTOMER_COUNT_INIT


def test_weekly_product(setup_test_db):
    weekly_scrape_product(env="test")
    count_product = setup_test_db.query(ProductSource).all()
    assert len(count_product) > 0


def test_daily_behavior_transaction(setup_test_db):
    daily_behavior_transaction(env="test")
    count_behavior = setup_test_db.query(CustomerBehaviorSource).all()
    count_transaction = setup_test_db.query(TransactionSource).all()
    assert len(count_behavior) > 0
    assert len(count_transaction) > 0
