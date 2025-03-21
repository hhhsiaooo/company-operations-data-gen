import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Type

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
from .constants import PROMO_PRODUCT_PREFERENCES
from .promotion import promotion_choose
from .schemas import (
    CustomerRecord,
    ProductRecord,
    CustomerBehaviorData,
    CustomerBehaviorRecord,
    TransactionData,
    TransactionRecord,
    PromotionConstants,
    PromotionData,
    PromotionRecord,
)


class CustomerActivityHistory:
    def generate(self, start_date: str, end_date: str) -> None:

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        date_range = [start + timedelta(days=i) for i in range((end - start).days + 1)]

        for date in date_range:
            weekday = (date - timedelta(days=1)).weekday()
            promotion_constants: PromotionConstants = (
                promotion_choose.get_promotion_constants(yesterday_weekday=weekday)
            )

            num_behavior: int = self.__gen_random_count(
                promotion_constants.behavior_avg,
                promotion_constants.behavior_sigma,
                promotion_constants.behavior_min,
                promotion_constants.behavior_max,
            )

            product_probabilities = self.__get_product_prob(
                promotion_constants.promotion_type
            )

            with ds.get_db() as db:
                customers = (
                    db.query(CustomerSource)
                    .filter(CustomerSource.registered_at < date)
                    .all()
                )

            customer_behavior_record: CustomerBehaviorData = []
            transaction_record: TransactionData = []

            for _ in range(num_behavior):
                customer: CustomerRecord = random.choice(customers)
                product: ProductRecord = self.__get_product_based_on_prob(
                    product_probabilities, db
                )

                view_action_at = self.__random_timestamp_previous_day(date)

                view_behavior: CustomerBehaviorRecord = self.__gen_behavior(
                    customer, product, action_type="view", action_at=view_action_at
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

            with ds.get_db() as db:
                SBase.metadata.create_all(db.bind)
                db.commit()
                self.__insert_table(db, CustomerBehaviorSource, customer_behavior_data)
                self.__insert_table(db, TransactionSource, transaction_data)
                db.commit()

            print("finish {}".format(date))

    def __insert_table(
        self, db: Session, model: Type[DeclarativeBase], data: RootModel
    ) -> None:
        table: sa.Table = model.__table__
        records = [record.model_dump() for record in data.root]
        db.execute(sa.insert(table), records)
        db.commit()

    def __gen_random_count(self, mu, sigma, minimum, maximum) -> int:
        num_behavior = int(random.normalvariate(mu, sigma))
        return max(minimum, min(num_behavior, maximum))

    def __get_product_prob(self, promotion_type: str) -> Dict[str, float]:
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

    def __random_timestamp_previous_day(self, date) -> datetime:
        start_time = (date - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_time = start_time.replace(hour=23, minute=59, second=59)
        random_time = start_time + timedelta(
            seconds=random.randint(0, int((end_time - start_time).total_seconds()))
        )
        return random_time

    def __random_timestamp_after(self, start_time) -> datetime:
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
            device_type = random.choice(device_list)

        if referrer is None:
            referrer = random.choice(referrer_list)

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


activity_gen: CustomerActivityHistory = CustomerActivityHistory()
activity_gen.generate(start_date="2025-03-17", end_date="2025-03-17")
