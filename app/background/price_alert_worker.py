import asyncio
from app.repositories.alerts_repository import AlertsRepository
from app.repositories.store_price_repository import StorePriceRepository
from app.services.search_service import SearchService
from app.utils.price_normalizer import normalize_price
from app.utils.logger import logger
from app.models.store_price_model import StorePriceRecord


class PriceAlertWorker:
    CHECK_INTERVAL = 60 * 30  # 30 minutes

    @staticmethod
    async def check_alerts_once():
        logger.info("Checking active price alerts...")
        alerts = await AlertsRepository.get_active_alerts()
        if not alerts:
            logger.info("No active alerts found.")
            return
        logger.info(f"Found {len(alerts)} active alert(s).")
        for alert in alerts:
            try:
                await PriceAlertWorker.process_alert(alert)
            except Exception as e:
                logger.error(f"Error processing alert {alert.id}: {e}")

    @staticmethod
    async def process_alert(alert):
        logger.info(f"Processing alert for product {alert.product_id}")

        # Use the search_query field if present, otherwise fall back to product_id
        query = getattr(alert, "search_query", None) or alert.product_id
        results = await SearchService.search_all_stores(query)

        if not results:
            logger.info(f"No results found for alert {alert.id}")
            return

        lowest_price = min(normalize_price(r["price"]) for r in results)
        logger.info(
            f"Alert {alert.id}: lowest={lowest_price}, target={alert.target_price}"
        )

        if lowest_price <= alert.target_price:
            await PriceAlertWorker.trigger_notification(alert, lowest_price)
            await AlertsRepository.deactivate_alert(alert.id)

        # Persist the latest store prices
        for r in results:
            price_model = StorePriceRecord(
                product_id=alert.product_id,
                store_name=r.get("store", "Unknown"),
                price=normalize_price(r["price"]),
                url=r.get("url", ""),
            )
            await StorePriceRepository.upsert_price(price_model)

    @staticmethod
    async def trigger_notification(alert, price: float):
        # Placeholder – replace with email/push notification logic
        logger.info(
            f"🔔 ALERT TRIGGERED: user={alert.user_id} "
            f"product={alert.product_id} dropped to £{price:.2f}"
        )

    @staticmethod
    async def start_worker():
        logger.info("Price Alert Worker started.")
        while True:
            await PriceAlertWorker.check_alerts_once()
            await asyncio.sleep(PriceAlertWorker.CHECK_INTERVAL)
