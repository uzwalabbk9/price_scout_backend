from typing import List, Optional
from app.scrapers.scraper_utils import fetch_html, fetch_page, safe_extract
from app.scrapers.scraper_interface import ScraperInterface
from app.models.product_model import StorePrice


class ArgosScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://www.argos.co.uk/search/{query.replace(' ', '-')}/"
        soup = await fetch_html(url)
        results = []
        # Argos frequently changes class names – try multiple selectors
        items = soup.select("[class*='Title']") or soup.select("[data-test='component-product-card']")
        for item in items:
            title = safe_extract(item)
            parent = item.parent
            if parent:
                parent = parent.parent or parent
            price_el = (
                parent.select_one("[class*='PriceText']") if parent else None
            )
            price = safe_extract(price_el)
            link = parent.select_one("a") if parent else None
            if not title or not price or not link:
                continue
            href = link.get("href", "")
            results.append({
                "store": "Argos",
                "title": title,
                "price": price,
                "url": "https://www.argos.co.uk" + href
                if not href.startswith("http") else href,
            })
        return results


class ArgosProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        price_el = soup.select_one("[class*='Price']") or soup.select_one(".price")
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
            store_name="Argos",
            price=price,
            currency="GBP",
            delivery_cost=0.0,
            delivery_time="2–5 days",
            in_stock=True,
            affiliate_link=url,
        )
