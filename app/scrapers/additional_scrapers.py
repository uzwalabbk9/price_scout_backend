from typing import List, Optional
from app.scrapers.scraper_utils import fetch_html, fetch_page, safe_extract
from app.scrapers.scraper_interface import ScraperInterface
from app.models.product_model import StorePrice


# ─── Very ─────────────────────────────────────────────────────────────────────

class VeryScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://www.very.co.uk/search/results.aspx?sq={query.replace(' ', '+')}"
        soup = await fetch_html(url)
        results = []
        items = soup.select(".product-listing") or soup.select("[class*='product-item']")
        for item in items:
            title_el = item.select_one("[class*='product-title']") or item.select_one("h3")
            price_el = item.select_one("[class*='product-price']") or item.select_one(".price")
            link_el = item.select_one("a")
            title = safe_extract(title_el)
            price = safe_extract(price_el)
            if not title or not price or not link_el:
                continue
            href = link_el.get("href", "")
            results.append({
                "store": "Very",
                "title": title,
                "price": price,
                "url": "https://www.very.co.uk" + href if not href.startswith("http") else href,
            })
        return results


class VeryProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        price_el = soup.select_one("[class*='product-price']") or soup.select_one(".price")
        if not price_el:
            return None
        try:
            price = float(price_el.get_text(strip=True).replace("£", "").replace(",", "").strip())
        except ValueError:
            return None
        return StorePrice(
            store_name="Very",
            price=price,
            currency="GBP",
            delivery_cost=3.99,
            delivery_time="3–5 days",
            in_stock=True,
            affiliate_link=url,
        )


# ─── AO.com ───────────────────────────────────────────────────────────────────

class AOScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://ao.com/search?q={query.replace(' ', '+')}"
        soup = await fetch_html(url)
        results = []
        items = soup.select("[class*='product-tile']") or soup.select("[class*='product-card']")
        for item in items:
            title_el = item.select_one("[class*='product-title']") or item.select_one("h3")
            price_el = item.select_one("[class*='price']")
            link_el = item.select_one("a")
            title = safe_extract(title_el)
            price = safe_extract(price_el)
            if not title or not price or not link_el:
                continue
            href = link_el.get("href", "")
            results.append({
                "store": "AO",
                "title": title,
                "price": price,
                "url": "https://ao.com" + href if not href.startswith("http") else href,
            })
        return results


class AOProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        price_el = soup.select_one("[class*='price']") or soup.select_one(".product-price")
        if not price_el:
            return None
        try:
            price = float(price_el.get_text(strip=True).replace("£", "").replace(",", "").strip())
        except ValueError:
            return None
        return StorePrice(
            store_name="AO",
            price=price,
            currency="GBP",
            delivery_cost=0.0,
            delivery_time="Next day",
            in_stock=True,
            affiliate_link=url,
        )


# ─── Scan.co.uk ───────────────────────────────────────────────────────────────

class ScanScraper:
    @staticmethod
    async def search(query: str) -> List[dict]:
        url = f"https://www.scan.co.uk/search?q={query.replace(' ', '+')}"
        soup = await fetch_html(url)
        results = []
        items = soup.select(".productInfo") or soup.select("[class*='product-item']")
        for item in items:
            title_el = item.select_one(".description") or item.select_one("h3")
            price_el = item.select_one(".price") or item.select_one("[class*='price']")
            link_el = item.select_one("a")
            title = safe_extract(title_el)
            price = safe_extract(price_el)
            if not title or not price or not link_el:
                continue
            href = link_el.get("href", "")
            results.append({
                "store": "Scan",
                "title": title,
                "price": price,
                "url": "https://www.scan.co.uk" + href if not href.startswith("http") else href,
            })
        return results


class ScanProductScraper(ScraperInterface):
    def scrape(self, url: str) -> Optional[StorePrice]:
        soup = fetch_page(url)
        price_el = soup.select_one(".price") or soup.select_one("[class*='price']")
        if not price_el:
            return None
        try:
            price = float(price_el.get_text(strip=True).replace("£", "").replace(",", "").strip())
        except ValueError:
            return None
        return StorePrice(
            store_name="Scan",
            price=price,
            currency="GBP",
            delivery_cost=0.0,
            delivery_time="1–2 days",
            in_stock=True,
            affiliate_link=url,
        )
