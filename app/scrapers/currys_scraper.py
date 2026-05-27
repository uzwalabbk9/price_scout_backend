from typing import List, Optional
from app.scrapers.scraper_utils import fetch_html, fetch_page, safe_extract
from app.scrapers.scraper_interface import ScraperInterface
from app.models.product_model import StorePrice


class CurrysScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://www.currys.co.uk/search?q={query.replace(' ', '+')}"
        soup = await fetch_html(url)
        results = []
        # Try new layout first, fall back to old
        items = soup.select(".product-card") or soup.select(".product")
        for item in items:
            title = (
                safe_extract(item.select_one(".product-card__title"))
                or safe_extract(item.select_one(".productTitle"))
            )
            price = (
                safe_extract(item.select_one(".product-card__price"))
                or safe_extract(item.select_one(".price"))
            )
            link = item.select_one("a")
            if not title or not price or not link:
                continue
            href = link.get("href", "")
            results.append({
                "store": "Currys",
                "title": title,
                "price": price,
                "url": "https://www.currys.co.uk" + href
                if not href.startswith("http") else href,
            })
        return results


class CurrysProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        price_el = (
            soup.select_one(".product-card__price")
            or soup.select_one(".price")
            or soup.select_one(".product-price")
        )
        if not price_el:
            return None
        try:
            price = float(
                price_el.get_text(strip=True)
                .replace("£", "").replace(",", "")
            )
        except ValueError:
            return None
        return StorePrice(
            store_name="Currys",
            price=price,
            currency="GBP",
            delivery_cost=0.0,
            delivery_time="3–5 days",
            in_stock=True,
            affiliate_link=url,
        )
