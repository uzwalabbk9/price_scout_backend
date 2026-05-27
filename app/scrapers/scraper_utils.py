import httpx
from bs4 import BeautifulSoup
import requests

# Headers that mimic a real browser to avoid 403/bot blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def fetch_html(url: str) -> BeautifulSoup:
    """Async HTTP fetch → BeautifulSoup. Returns empty soup on failure."""
    try:
        async with httpx.AsyncClient(
            headers=HEADERS,
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"[fetch_html] Error fetching {url}: {e}")
        return BeautifulSoup("", "html.parser")


def fetch_page(url: str) -> BeautifulSoup:
    """Sync HTTP fetch for product-level scrapers."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"[fetch_page] Error fetching {url}: {e}")
        return BeautifulSoup("", "html.parser")


def safe_extract(element) -> str:
    """Safely extract text from a BeautifulSoup element."""
    if element is None:
        return ""
    return element.get_text(strip=True)
