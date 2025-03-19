# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The product data scraper.
"""


import re
import time
import uuid
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .constants import CrawlerConstants
from .schemas import ProductData


class ProductScraper:
    """The product data scraper."""

    def __init__(self, keywords, pages, headers, url):
        self.keywords = keywords
        self.pages = pages
        self.headers = headers
        self.url = url
        self.brand_pattern = re.compile(r"【(.*?)】")
        self.products = []

    def scrape(self):
        for keyword in self.keywords:
            self._scrape_keyword(keyword)

    def _scrape_keyword(self, keyword):
        for page in range(1, self.pages + 1):
            self._scrape_page(keyword, page)

    def _scrape_page(self, keyword, page):
        url = self.url.format(page, keyword)
        print(f"Scraping URL: {url}")

        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            self._parse_products(soup, keyword)
            time.sleep(1)
        else:
            print(
                f"Failed to retrieve page {page} for keyword '{keyword}'. Status code: {resp.status_code}"
            )

    def _parse_products(self, soup, keyword):
        for item in soup.select("li.goodsItemLi"):
            product_id = str(uuid.uuid4())
            product_name = item.select_one(".prdName").get_text(strip=True)
            brand_match = self.brand_pattern.search(product_name)
            brand_name = brand_match.group(1) if brand_match else None
            product_name = re.sub(r"【.*?】|\(.*?\)|（.*?）", "", product_name).strip()
            promotion_price = self._extract_price(item.select_one(".ec-current-price"))
            price = self._extract_price(item.select_one(".ec-origin-price"))
            fetched_at = datetime.now()

            self.products.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "brand_name": brand_name,
                    "category": keyword,
                    "price": price,
                    "promotion_price": promotion_price,
                    "fetched_at": fetched_at,
                }
            )

    def _extract_price(self, price_element):
        if price_element:
            price = price_element.get_text(strip=True)
            cleaned_price = re.sub(r"[\$,]", "", price).strip()
            if cleaned_price.isdigit():
                return int(cleaned_price)
            else:
                return None

    def get_data(self) -> ProductData:
        return ProductData(root=self.products)


crawler_constants = CrawlerConstants()

product_gen: ProductScraper = ProductScraper(
    crawler_constants.KEYWORD,
    crawler_constants.PAGES,
    crawler_constants.HEADERS,
    crawler_constants.URL,
)
"""The product data generator."""
