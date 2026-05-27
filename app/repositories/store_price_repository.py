from typing import List
from app.database.connection import get_db
from app.models.store_price_model import StorePriceRecord


class StorePriceRepository:

    @staticmethod
    async def upsert_price(price: StorePriceRecord) -> StorePriceRecord:
        db = get_db()
        await db["store_prices"].update_one(
            {"product_id": price.product_id, "store_name": price.store_name},
            {"$set": price.model_dump(by_alias=True)},
            upsert=True,
        )
        return price

    @staticmethod
    async def get_prices_for_product(product_id: str) -> List[StorePriceRecord]:
        db = get_db()
        cursor = db["store_prices"].find({"product_id": product_id})
        docs = await cursor.to_list(length=100)
        results = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            results.append(StorePriceRecord(**doc))
        return results
