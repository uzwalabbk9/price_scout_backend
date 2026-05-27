from apscheduler.schedulers.background import BackgroundScheduler
from app.repositories.product_repository import get_all_products, update_product_prices
from app.scrapers.scraper_registry import SCRAPERS

scheduler = BackgroundScheduler()


def refresh_all_prices():
    """Sync job run by APScheduler every 3 hours to refresh store prices."""
    products = get_all_products()
    for product in products:
        updated_prices = []
        for sp in product.store_prices:
            scraper = SCRAPERS.get(sp.store_name.lower())
            if scraper and sp.affiliate_link:
                new_price = scraper.scrape(sp.affiliate_link)
                if new_price:
                    updated_prices.append(new_price)
        if updated_prices:
            update_product_prices(product.id, updated_prices)


def start_price_refresh_worker():
    scheduler.add_job(refresh_all_prices, "interval", hours=3)
    scheduler.start()
