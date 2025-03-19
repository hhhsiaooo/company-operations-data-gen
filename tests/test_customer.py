# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The customer data test cases.
"""


import datetime

from company_operation_data_gen.customer import customer_gen
from company_operation_data_gen.schemas import CustomerData
from company_operation_data_gen.constants import CustomerCountConstants


def test_customer_count():
    """Test generating a random number of customer data."""
    for _ in range(10):
        data = customer_gen.gen_new_customer(
            min=CustomerCountConstants.CUSTOMER_COUNT_MIN,
            max=CustomerCountConstants.CUSTOMER_COUNT_MAX,
        )
        assert isinstance(data, CustomerData)
        assert len(data.root) >= CustomerCountConstants.CUSTOMER_COUNT_MIN
        assert len(data.root) <= CustomerCountConstants.CUSTOMER_COUNT_MAX


def test_customer_data_content():
    """Test customer data content."""
    data = customer_gen.gen_new_customer(
        min=CustomerCountConstants.CUSTOMER_COUNT_MIN,
        max=CustomerCountConstants.CUSTOMER_COUNT_MAX,
    )
    customer = data.root[0]
    assert isinstance(customer.customer_name, str)
    assert customer.gender in ["M", "F"]
    assert isinstance(customer.birth, datetime.date)
    assert "@" in customer.email
    assert "縣" or "市" in customer.city
    assert isinstance(customer.registered_at, datetime.date)
