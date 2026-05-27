from typing import List, Optional
from app.scrapers.scraper_utils import fetch_html, fetch_page, safe_extract
from app.scrapers.scraper_interface import ScraperInterface
from app.models.product_model import StorePrice


class AmazonScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://www.amazon.co.uk/s?k={query.replace(' ', '+')}"
        soup = await fetch_html(url)
        results = []
        items = soup.select("div[data-component-type='s-search-result']")
        for item in items:
            title_el = item.select_one("h2 a span")
            price_el = item.select_one("span.a-price > span.a-offscreen")
            link_el = item.select_one("h2 a")
            if not title_el or not price_el or not link_el:
                continue
            results.append({
                "store": "Amazon",
                "title": safe_extract(title_el),
                "price": safe_extract(price_el),
                "url": "https://www.amazon.co.uk" + link_el.get("href", ""),
            })
        return results


class AmazonProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        title = soup.select_one("#productTitle")
        price_el = soup.select_one("span.a-price-whole")
        if not title or not price_el:
            return None
        try:
            price = float(
                price_el.get_text(strip=True).replace(",", "").replace("£", "")
            )
        except ValueError:
            return None
        return StorePrice(
            store_name="Amazon",
            price=price,
            currency="GBP",
            delivery_cost=0.0,
            delivery_time="1–3 days",
            in_stock=True,
            affiliate_link=url,
        )
