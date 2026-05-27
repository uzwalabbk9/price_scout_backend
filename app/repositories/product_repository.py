from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from app.database.connection import get_db
from app.models.product_model import Product, ProductCreate
from app.database.collections import products_collection  # sync, for workers


# ─── Async repository (used by routers) ────────────────────────────────────

class ProductRepository:

    @staticmethod
    async def create(product_data: dict) -> dict:
        """Insert a product dict and return it with the new _id."""
        db = get_db()
        product_data.pop("_id", None)   # never insert with a client-set _id
        result = await db["products"].insert_one(product_data)
        product_data["_id"] = str(result.inserted_id)
        return product_data

    @staticmethod
    async def get_by_id(product_id: str) -> Optional[Product]:
        db = get_db()
        try:
            data = await db["products"].find_one({"_id": ObjectId(product_id)})
        except InvalidId:
            return None
        if not data:
            return None
        data["_id"] = str(data["_id"])
        return Product(**data)

    @staticmethod
    async def search_by_title(query: str) -> List[Product]:
        """Case-insensitive title search. Returns serialised Product list."""
        db = get_db()
        cursor = db["products"].find(
            {"title": {"$regex": query, "$options": "i"}}
        )
        docs = await cursor.to_list(length=100)
        products = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            try:
                products.append(Product(**doc))
            except Exception:
                continue
        return products

    @staticmethod
    async def delete(product_id: str) -> bool:
        db = get_db()
        try:
            result = await db["products"].delete_one(
                {"_id": ObjectId(product_id)}
            )
            return result.deleted_count == 1
        except InvalidId:
            return False


# ─── Sync helpers (used only by APScheduler background workers) ───────────

def _serialize(doc: dict) -> Product:
    doc["_id"] = str(doc["_id"])
    return Product(**doc)


def get_all_products() -> List[Product]:
    return [_serialize(doc) for doc in products_collection.find({})]


def get_product_by_id(product_id: str) -> Optional[Product]:
    try:
        doc = products_collection.find_one({"_id": ObjectId(product_id)})
    except InvalidId:
        return None
    return _serialize(doc) if doc else None


def update_product_prices(product_id: str, store_prices: list):
    try:
        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"store_prices": [sp.dict() for sp in store_prices]}},
        )
    except InvalidId:
        pass
