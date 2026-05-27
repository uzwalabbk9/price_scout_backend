from typing import List, Optional
from app.scrapers.scraper_utils import fetch_html, fetch_page, safe_extract
from app.scrapers.scraper_interface import ScraperInterface
from app.models.product_model import StorePrice


class JohnLewisScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://www.johnlewis.com/search?search-term={query.replace(' ', '+')}"
        soup = await fetch_html(url)
        results = []
        items = soup.select("[class*='product-card']") or soup.select("[data-component='product-card']")
        for item in items:
            title_el = item.select_one("[class*='product-card__title']") or item.select_one("h2")
            price_el = item.select_one("[class*='price']") or item.select_one("[data-test='product-price']")
            link_el = item.select_one("a")
            title = safe_extract(title_el)
            price = safe_extract(price_el)
            if not title or not price or not link_el:
                continue
            href = link_el.get("href", "")
            results.append({
                "store": "John Lewis",
                "title": title,
                "price": price,
                "url": "https://www.johnlewis.com" + href if not href.startswith("http") else href,
            })
        return results


class JohnLewisProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        price_el = soup.select_one("[data-test='product-price']") or soup.select_one("[class*='price']")
        if not price_el:
            return None
        try:
            price = float(
                price_el.get_text(strip=True).replace("£", "").replace(",", "").strip()
            )
        except ValueError:
            return None
        return StorePrice(
            store_name="John Lewis",
            price=price,
            currency="GBP",
            delivery_cost=0.0,
            delivery_time="2–5 days",
            in_stock=True,
            affiliate_link=url,
        )
