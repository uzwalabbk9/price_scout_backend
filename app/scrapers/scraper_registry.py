from app.scrapers.amazon_scraper import AmazonProductScraper
from app.scrapers.argos_scraper import ArgosProductScraper
from app.scrapers.currys_scraper import CurrysProductScraper
from app.scrapers.ebay_scraper import EbayProductScraper
from app.scrapers.john_lewis_scraper import JohnLewisProductScraper
from app.scrapers.additional_scrapers import VeryProductScraper, AOProductScraper, ScanProductScraper

# Used by the background price-refresh worker
SCRAPERS = {
    "amazon":     AmazonProductScraper(),
    "argos":      ArgosProductScraper(),
    "currys":     CurrysProductScraper(),
    "ebay":       EbayProductScraper(),
    "johnlewis":  JohnLewisProductScraper(),
    "very":       VeryProductScraper(),
    "ao":         AOProductScraper(),
    "scan":       ScanProductScraper(),
}
