from typing import List, Optional
from app.scrapers.scraper_utils import fetch_html, fetch_page, safe_extract
from app.scrapers.scraper_interface import ScraperInterface
from app.models.product_model import StorePrice


class EbayScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://www.ebay.co.uk/sch/i.html?_nkw={query.replace(' ', '+')}"
        soup = await fetch_html(url)
        results = []
        items = soup.select(".s-item")
        for item in items:
            title = safe_extract(item.select_one(".s-item__title"))
            price = safe_extract(item.select_one(".s-item__price"))
            link = item.select_one("a.s-item__link")
            # eBay injects a dummy first item with "Shop on eBay"
            if not title or not price or not link or "Shop on eBay" in title:
                continue
            results.append({
                "store": "eBay",
                "title": title,
                "price": price,
                "url": link.get("href", ""),
            })
        return results


class EbayProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        price_el = (
            soup.select_one("#prcIsum")
            or soup.select_one(".x-price-primary")
            or soup.select_one(".notranslate")
        )
        if not price_el:
            return None
        try:
            price = float(
                price_el.get_text(strip=True)
                .replace("£", "").replace(",", "").replace("GBP", "").strip()
            )
        except ValueError:
            return None
        return StorePrice(
            store_name="eBay",
            price=price,
            currency="GBP",
            delivery_cost=0.0,
            delivery_time="3–7 days",
            in_stock=True,
            affiliate_link=url,
        )
