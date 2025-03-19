# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The promotion data test cases.
"""


import os
import yaml

import pytest

from company_operation_data_gen.promotion import promotion_choose
from company_operation_data_gen.database import ds, SBase
from company_operation_data_gen.models import PromotionDateSource, PromotionSource
from company_operation_data_gen.schemas import (
    PromotionDateRecord,
    PromotionDateData,
    PromotionRecord,
    PromotionData,
    PromotionConstants,
)
from company_operation_data_gen.constants import (
    BehaviorCountConstants,
    QuantityCountConstants,
)


@pytest.fixture
def setup_test_db():
    """Sets up the SQLite in memory database for testing."""
    session = ds.get_db(env="test")
    SBase.metadata.create_all(session.get_bind())

    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "fixtures", "test_data.yaml")
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)

    promotion_date = PromotionDateData(
        root=[PromotionDateRecord(**record) for record in data["promotion_date"]]
    )
    orm_promotion_date = [
        PromotionDateSource(**record.model_dump()) for record in promotion_date.root
    ]
    session.bulk_save_objects(orm_promotion_date)

    promotion = PromotionData(
        root=[PromotionRecord(**record) for record in data["promotion"]]
    )
    orm_promotion = [
        PromotionSource(**record.model_dump()) for record in promotion.root
    ]
    session.bulk_save_objects(orm_promotion)
    session.commit()

    yield session

    session.close()


def test_promotion_choose(setup_test_db):
    test_weekday = 5
    promotion_constants = promotion_choose.get_promotion_constants(
        today_weekday=test_weekday, session=setup_test_db
    )

    assert isinstance(promotion_constants, PromotionConstants)
    assert promotion_constants.promotion_type == "免運滿額贈"
    assert promotion_constants.behavior_avg == BehaviorCountConstants.GIFT_BEHAVIOR_AVG
    assert promotion_constants.behavior_min == BehaviorCountConstants.GIFT_BEHAVIOR_MIN
    assert promotion_constants.behavior_max == BehaviorCountConstants.GIFT_BEHAVIOR_MAX
    assert promotion_constants.quantity_avg == QuantityCountConstants.GIFT_QUANTITY_AVG
    assert promotion_constants.quantity_min == QuantityCountConstants.GIFT_QUANTITY_MIN
    assert promotion_constants.quantity_max == QuantityCountConstants.GIFT_QUANTITY_MAX
    assert isinstance(promotion_constants.promotion_detail, PromotionData)

    expected_promotion_names = {"滿1000送零食", "滿2000送毛毯"}
    promotion_data = promotion_constants.promotion_detail.root
    actual_promotion_names = {promotion.promotion_name for promotion in promotion_data}
    assert actual_promotion_names == expected_promotion_names
