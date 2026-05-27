from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.database.connection import get_db
from app.models.wishlist_model import WishlistItem


class WishlistRepository:

    @staticmethod
    async def add_item(item: WishlistItem) -> dict:
        db = get_db()
        doc = item.model_dump(by_alias=True, exclude={"id"})
        doc.pop("_id", None)
        doc["created_at"] = datetime.utcnow()
        doc["updated_at"] = datetime.utcnow()
        result = await db.wishlist.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    @staticmethod
    async def get_by_user(user_id: str) -> List[dict]:
        db = get_db()
        docs = await db.wishlist.find({"user_id": user_id}).to_list(200)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    async def update_item(user_id: str, product_id: str, fields: dict) -> Optional[dict]:
        db = get_db()
        fields["updated_at"] = datetime.utcnow()
        result = await db.wishlist.find_one_and_update(
            {"user_id": user_id, "product_id": product_id},
            {"$set": fields},
            return_document=True,
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    @staticmethod
    async def delete(user_id: str, product_id: str) -> bool:
        db = get_db()
        result = await db.wishlist.delete_one({"user_id": user_id, "product_id": product_id})
        return result.deleted_count > 0

    @staticmethod
    async def clear_all(user_id: str) -> int:
        db = get_db()
        result = await db.wishlist.delete_many({"user_id": user_id})
        return result.deleted_count

    @staticmethod
    async def exists(user_id: str, product_id: str) -> bool:
        db = get_db()
        doc = await db.wishlist.find_one({"user_id": user_id, "product_id": product_id})
        return doc is not None
