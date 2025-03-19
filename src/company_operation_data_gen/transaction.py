# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The transaction data generator.
"""


import random
from datetime import datetime, timedelta
from typing import Optional, Dict

import sqlalchemy as sa

from .database import ds
from .models import ProductSource, CustomerSource
from .schemas import (
    CustomerRecord,
    ProductRecord,
    CustomerActivityData,
    CustomerBehaviorData,
    CustomerBehaviorRecord,
    TransactionData,
    TransactionRecord,
    PromotionConstants,
    PromotionData,
    PromotionRecord,
)

from .constants import PROMO_PRODUCT_PREFERENCES


class CustomerActivityGenerator:
    """The customer behavior data and transaction data generator."""

    def generate(
        self, promotion_constants: PromotionConstants, session: sa.orm.Session = None
    ) -> CustomerActivityData:
        """Generates and returns the customer behavior data and transaction data.

        :param promotion_constants: The constants based on the different promotion type.
        :param session: Passes the test database for testing purposes. If no parameters are provided, the source database will be used.
        :return:
            - The customer behavior data.
            - The transaction data.
        """
        num_behavior: int = self.__gen_random_count(
            promotion_constants.behavior_avg,
            promotion_constants.behavior_sigma,
            promotion_constants.behavior_min,
            promotion_constants.behavior_max,
        )

        product_probabilities = self.__get_product_prob(
            promotion_constants.promotion_type
        )

        if session:
            db = session
        else:
            db = ds.get_db()

        with db:
            customers = db.query(CustomerSource).all()

        customer_behavior_record: CustomerBehaviorData = []
        transaction_record: TransactionData = []

        for _ in range(num_behavior):
            customer: CustomerRecord = random.choice(customers)
            product: ProductRecord = self.__get_product_based_on_prob(
                product_probabilities, db
            )

            view_behavior: CustomerBehaviorRecord = self.__gen_behavior(
                customer, product, action_type="view"
            )
            customer_behavior_record.append(view_behavior)

            device_type = view_behavior.device_type
            referrer = view_behavior.referrer
            last_action_time = view_behavior.action_at

            if random.choice([True, False]):
                add_to_cart_behavior: CustomerBehaviorRecord = self.__gen_behavior(
                    customer,
                    product,
                    action_type="add_to_cart",
                    device_type=device_type,
                    referrer=referrer,
                    action_at=self.__random_timestamp_after(last_action_time),
                )
                customer_behavior_record.append(add_to_cart_behavior)

                last_action_time = add_to_cart_behavior.action_at

                if random.choice([True, False]):
                    purchase_behavior: CustomerBehaviorRecord = self.__gen_behavior(
                        customer,
                        product,
                        action_type="purchase",
                        device_type=device_type,
                        referrer=referrer,
                        action_at=self.__random_timestamp_after(last_action_time),
                    )
                    customer_behavior_record.append(purchase_behavior)

                    num_quantity: int = self.__gen_random_count(
                        promotion_constants.quantity_avg,
                        promotion_constants.quantity_sigma,
                        promotion_constants.quantity_min,
                        promotion_constants.quantity_max,
                    )

                    transaction = self.__gen_transaction(
                        customer,
                        product,
                        purchase_behavior,
                        num_quantity,
                        promotion_constants,
                    )
                    transaction_record.append(transaction)

        customer_behavior_data = CustomerBehaviorData(root=customer_behavior_record)
        transaction_data = TransactionData(root=transaction_record)

        return CustomerActivityData(
            customer_behavior=customer_behavior_data,
            transaction=transaction_data,
        )

    def __gen_random_count(self, mu, sigma, minimum, maximum) -> int:
        """Generates a random customer behavior count within a defined minimum and maximum range."""
        num_behavior = int(random.normalvariate(mu, sigma))
        return max(minimum, min(num_behavior, maximum))

    def __get_product_prob(self, promotion_type: str) -> Dict[str, float]:
        """Returns the probabilities for choosing product according to the promotion type."""
        if promotion_type == "免運滿額贈":
            return PROMO_PRODUCT_PREFERENCES["免運滿額贈"]
        elif promotion_type == "滿額折扣":
            return PROMO_PRODUCT_PREFERENCES["滿額折扣"]
        elif promotion_type == "多件優惠":
            return PROMO_PRODUCT_PREFERENCES["多件優惠"]

    def __get_product_based_on_prob(
        self, product_probabilities: Dict[str, float], db: sa.orm.Session
    ) -> ProductRecord:
        products = list(product_probabilities.keys())
        probabilities = list(product_probabilities.values())

        category = random.choices(products, probabilities)[0]

        with db:
            selected_category = (
                db.query(ProductSource).filter(ProductSource.category == category).all()
            )
        selected_product = random.choice(selected_category)

        return selected_product

    def __random_timestamp_previous_day(self) -> datetime:
        """Generates a random timestamp from the previous day."""
        start_time = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_time = start_time.replace(hour=23, minute=59, second=59)
        random_time = start_time + timedelta(
            seconds=random.randint(0, int((end_time - start_time).total_seconds()))
        )
        return random_time

    def __random_timestamp_after(self, start_time) -> datetime:
        """Generates a random timestamp for customer behavior that follows a specific sequence.
        The time interval between customer behaviors is between five minutes and two hours.
        """
        random_time = start_time + timedelta(seconds=random.randint(300, 7200))
        return random_time

    def __gen_behavior(
        self,
        customer: CustomerRecord,
        product: ProductRecord,
        action_type: str,
        device_type: str = None,
        referrer: str = None,
        action_at: datetime = None,
    ) -> CustomerBehaviorRecord:
        """Generates and returns the customer behavior record.
        When 'action_type' is 'add to cart' or 'purchase',
        the 'device_type' and 'referrer' of the record should be the same as the customer's behavioe record when they viewed,
        and the 'action_at' must occur after the 'view' action.

        :return: The customer behavior record.
        """
        device_list = ["mobile", "tablet", "desktop", "laptop", "unknown"]
        referrer_list = [
            "direct",
            "search_engine",
            "social_media",
            "email",
            "paid_ads",
            "referral",
            "unknown",
        ]

        if device_type is None:
            """When a customer view a product for the first time, meaning the action_type is 'view', the device_type will be null."""
            device_type = random.choice(device_list)

        if referrer is None:
            """When a customer view a product for the first time, meaning the action_type is 'view', the referrer will be null."""
            referrer = random.choice(referrer_list)

        if action_at is None:
            """When a customer view a product for the first time, meaning the action_type is 'view', the action_at will be null."""
            action_at = self.__random_timestamp_previous_day()

        customer_id = customer.customer_id
        product_id = product.product_id

        behavior_record = CustomerBehaviorRecord(
            customer_id=customer_id,
            product_id=product_id,
            action_type=action_type,
            device_type=device_type,
            referrer=referrer,
            action_at=action_at,
        )
        return behavior_record

    def __gen_transaction(
        self,
        customer: CustomerRecord,
        product: ProductRecord,
        behavior: CustomerBehaviorRecord,
        quantity: int,
        promotion_constants: PromotionConstants,
    ) -> TransactionRecord:
        """Generates and returns the transaction record."""
        customer_id = customer.customer_id
        product_id = product.product_id
        quantity = quantity
        promotion_price = product.promotion_price
        amount = quantity * promotion_price
        transaction_at = behavior.action_at

        applied_promotion = self.__select_promotion(
            promotion_constants.promotion_type,
            promotion_constants.promotion_detail,
            quantity,
            amount,
        )
        if applied_promotion is None:
            transaction_record = {
                "customer_id": customer_id,
                "product_id": product_id,
                "quantity": quantity,
                "promotion_price": promotion_price,
                "amount": amount,
                "discount": 0,
                "gift": None,
                "total": amount,
                "transaction_at": transaction_at,
            }
            return transaction_record

        elif applied_promotion.promotion_type in ["滿額折扣", "多件優惠"]:
            transaction_record = {
                "customer_id": customer_id,
                "product_id": product_id,
                "quantity": quantity,
                "promotion_price": promotion_price,
                "amount": amount,
                "discount": int(round(amount * applied_promotion.discount_rate)),
                "gift": None,
                "total": amount - int(round(amount * applied_promotion.discount_rate)),
                "transaction_at": transaction_at,
            }
            return transaction_record

        elif applied_promotion.promotion_type == "免運滿額贈":
            transaction_record = {
                "customer_id": customer_id,
                "product_id": product_id,
                "quantity": quantity,
                "promotion_price": promotion_price,
                "amount": amount,
                "discount": 0,
                "gift": applied_promotion.gift,
                "total": amount,
                "transaction_at": transaction_at,
            }
            return transaction_record

    def __select_promotion(
        self,
        promotion_type: str,
        promotion_detail: PromotionData,
        quantity: int,
        amount: int,
    ) -> Optional[PromotionRecord]:
        """根據促銷類型選擇要用購買金額或購買數量，排序促銷活動，以擇優選擇促銷活動(可能無適用活動)"""

        if promotion_type == "滿額折扣" or promotion_type == "免運滿額贈":
            sorted_promotions = sorted(
                promotion_detail.root,
                key=lambda promo: promo.cash_threshold,
                reverse=True,
            )
        elif promotion_type == "多件優惠":
            sorted_promotions = sorted(
                promotion_detail.root,
                key=lambda promo: promo.quantity_threshold,
                reverse=True,
            )
        else:
            sorted_promotions = []

        for promotion in sorted_promotions:
            if promotion_type == "免運滿額贈" and amount >= promotion.cash_threshold:
                return promotion
            elif promotion_type == "滿額折扣" and amount >= promotion.cash_threshold:
                return promotion
            elif (
                promotion_type == "多件優惠"
                and quantity >= promotion.quantity_threshold
            ):
                return promotion

        return None


activity_gen: CustomerActivityGenerator = CustomerActivityGenerator()
"""The customer activity data generator."""
