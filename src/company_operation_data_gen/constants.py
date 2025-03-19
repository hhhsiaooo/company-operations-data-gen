# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""The constants.

include:
- The variables for web crawler.
- The number of customer data to generate.
- The number of customer behavior data for different promotion activities.
- The purchase quantity for different promotion activities.
- The product preferences for different promotion activities.
"""


from typing import List, Dict


class CrawlerConstants:
    """The variables for web crawler."""

    KEYWORD: List[str] = [
        "寵物零食",
        "潔牙骨",
        "寵物保健食品",
        "寵物清潔用品",
        "寵物凍乾",
        "寵物尿布墊",
        "狗飼料",
        "狗罐頭",
    ]
    PAGES: int = 2
    HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    URL: str = (
        "https://m.momoshop.com.tw/search.momo?_advFirst=N&_advCp=N&curPage={}&searchType=1&cateLevel=2&ent=k&searchKeyword={}&_advThreeHours=N&_isFuzzy=0&_imgSH=fourCardType"
    )


class CustomerCountConstants:
    """The number of customer data to generate."""

    CUSTOMER_COUNT_INIT: int = 100
    CUSTOMER_COUNT_MIN: int = 5
    CUSTOMER_COUNT_MAX: int = 15


class BehaviorCountConstants:
    """
    The number of customer behavior data for different promotion activities.
    GIFT：免運滿額贈，high transaction volume
    DISCOUNT：滿額折扣，medium transaction volume
    MULTI：多件優惠，low transaction volume
    """

    GIFT_BEHAVIOR_MIN = 60
    GIFT_BEHAVIOR_AVG = 80
    GIFT_BEHAVIOR_MAX = 100
    GIFT_BEHAVIOR_SIGMA = 6

    DISCOUNT_BEHAVIOR_MIN = 40
    DISCOUNT_BEHAVIOR_AVG = 60
    DISCOUNT_BEHAVIOR_MAX = 80
    DISCOUNT_BEHAVIOR_SIGMA = 6

    MULTI_BEHAVIOR_MIN = 20
    MULTI_BEHAVIOR_AVG = 40
    MULTI_BEHAVIOR_MAX = 60
    MULTI_BEHAVIOR_SIGMA = 6


class QuantityCountConstants:
    """
    The purchase quantity for different promotion activities.
    GIFT：免運滿額贈，low purchase quantity
    DISCOUNT：滿額折扣，medium purchase quantity
    MULTI：多件優惠，high purchase quantity
    """

    GIFT_QUANTITY_MIN = 1
    GIFT_QUANTITY_AVG = 3
    GIFT_QUANTITY_MAX = 5
    GIFT_QUANTITY_SIGMA = 1

    DISCOUNT_QUANTITY_MIN = 2
    DISCOUNT_QUANTITY_AVG = 5
    DISCOUNT_QUANTITY_MAX = 10
    DISCOUNT_QUANTITY_SIGMA = 2

    MULTI_QUANTITY_MIN = 5
    MULTI_QUANTITY_AVG = 8
    MULTI_QUANTITY_MAX = 15
    MULTI_QUANTITY_SIGMA = 2


"""The product preferences for different promotion activities."""
PROMO_PRODUCT_PREFERENCES = {
    "免運滿額贈": {
        "寵物零食": 0.3,
        "潔牙骨": 0.3,
        "寵物保健食品": 0.05,
        "寵物清潔用品": 0.05,
        "寵物凍乾": 0.05,
        "寵物尿布墊": 0.05,
        "狗飼料": 0.1,
        "狗罐頭": 0.1,
    },
    "滿額折扣": {
        "寵物零食": 0.05,
        "潔牙骨": 0.05,
        "寵物保健食品": 0.25,
        "寵物清潔用品": 0.25,
        "寵物凍乾": 0.25,
        "寵物尿布墊": 0.05,
        "狗飼料": 0.05,
        "狗罐頭": 0.05,
    },
    "多件優惠": {
        "寵物零食": 0.05,
        "潔牙骨": 0.05,
        "寵物保健食品": 0.05,
        "寵物清潔用品": 0.05,
        "寵物凍乾": 0.05,
        "寵物尿布墊": 0.25,
        "狗飼料": 0.25,
        "狗罐頭": 0.25,
    },
}
