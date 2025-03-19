# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The promotion constants.

Returns the promotion data based on the different weekday,
and the corresponding constants, including the number of customer behavior data and the quantity of products purchased.
"""


from datetime import datetime
from typing import Tuple

import sqlalchemy as sa

from .database import ds
from .models import PromotionDateSource, PromotionSource
from .schemas import PromotionRecord, PromotionData, PromotionConstants
from .constants import BehaviorCountConstants, QuantityCountConstants


class PromotionChoose:

    def get_promotion_constants(
        self,
        today_weekday: int = None,
        session: sa.orm.Session = None,
    ) -> PromotionConstants:
        """Returns the promotion data and the corresponding constants.

        :param today_weekday: Passes the weekday for testing purposes. If no parameters are provided, today's weekday will be used.
        :param session: Passes the test database for testing purposes. If no parameters are provided, the source database will be used.
        :return:
            - The promotion type.
            - The promotion data.
            - The constants based on the different promotion type.
        """

        today_weekday = (
            today_weekday if today_weekday is not None else datetime.now().weekday()
        )
        result = self.__get_today_promotion(
            today_weekday=today_weekday, session=session
        )
        today_promotion_type: str = result[0]
        latest_promotion_content: PromotionData = result[1]

        if today_promotion_type == "免運滿額贈":
            return PromotionConstants(
                promotion_type=today_promotion_type,
                promotion_detail=latest_promotion_content,
                behavior_avg=BehaviorCountConstants.GIFT_BEHAVIOR_AVG,
                behavior_sigma=BehaviorCountConstants.GIFT_BEHAVIOR_SIGMA,
                behavior_min=BehaviorCountConstants.GIFT_BEHAVIOR_MIN,
                behavior_max=BehaviorCountConstants.GIFT_BEHAVIOR_MAX,
                quantity_avg=QuantityCountConstants.GIFT_QUANTITY_AVG,
                quantity_sigma=QuantityCountConstants.GIFT_QUANTITY_SIGMA,
                quantity_min=QuantityCountConstants.GIFT_QUANTITY_MIN,
                quantity_max=QuantityCountConstants.GIFT_QUANTITY_MAX,
            )
        elif today_promotion_type == "滿額折扣":
            return PromotionConstants(
                promotion_type=today_promotion_type,
                promotion_detail=latest_promotion_content,
                behavior_avg=BehaviorCountConstants.DISCOUNT_BEHAVIOR_AVG,
                behavior_sigma=BehaviorCountConstants.DISCOUNT_BEHAVIOR_SIGMA,
                behavior_min=BehaviorCountConstants.DISCOUNT_BEHAVIOR_MIN,
                behavior_max=BehaviorCountConstants.DISCOUNT_BEHAVIOR_MAX,
                quantity_avg=QuantityCountConstants.DISCOUNT_QUANTITY_AVG,
                quantity_sigma=QuantityCountConstants.DISCOUNT_QUANTITY_SIGMA,
                quantity_min=QuantityCountConstants.DISCOUNT_QUANTITY_MIN,
                quantity_max=QuantityCountConstants.DISCOUNT_QUANTITY_MAX,
            )
        elif today_promotion_type == "多件優惠":
            return PromotionConstants(
                promotion_type=today_promotion_type,
                promotion_detail=latest_promotion_content,
                behavior_avg=BehaviorCountConstants.MULTI_BEHAVIOR_AVG,
                behavior_sigma=BehaviorCountConstants.MULTI_BEHAVIOR_SIGMA,
                behavior_min=BehaviorCountConstants.MULTI_BEHAVIOR_MIN,
                behavior_max=BehaviorCountConstants.MULTI_BEHAVIOR_MAX,
                quantity_avg=QuantityCountConstants.MULTI_QUANTITY_AVG,
                quantity_sigma=QuantityCountConstants.MULTI_QUANTITY_SIGMA,
                quantity_min=QuantityCountConstants.MULTI_QUANTITY_MIN,
                quantity_max=QuantityCountConstants.MULTI_QUANTITY_MAX,
            )

    def __get_today_promotion(
        self, today_weekday: int, session: sa.orm.Session
    ) -> Tuple[str, PromotionData]:
        """Returns the promotion type based on the weekday, then query the latest promotion data."""

        if session:
            db = session
        else:
            db = ds.get_db()

        with db:
            today_promotion_type = (
                db.query(PromotionDateSource.promotion_type)
                .filter(PromotionDateSource.day_of_week == today_weekday)
                .order_by(PromotionDateSource.published_at.desc())
                .first()
            )
            today_promotion_type = (
                today_promotion_type[0] if today_promotion_type else None
            )
            latest_promotion_date = db.scalar(sa.func.max(PromotionSource.published_at))

            latest_promotion_content = (
                db.query(PromotionSource)
                .filter(
                    PromotionSource.promotion_type == today_promotion_type,
                    PromotionSource.published_at == latest_promotion_date,
                )
                .all()
            )
            latest_promotion_content_models = [
                PromotionRecord.model_validate(promotion)
                for promotion in latest_promotion_content
            ]

        return today_promotion_type, PromotionData(root=latest_promotion_content_models)


promotion_choose: PromotionChoose = PromotionChoose()
"""Chooses the promotion data."""
