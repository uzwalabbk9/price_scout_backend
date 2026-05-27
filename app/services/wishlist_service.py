from typing import List
from datetime import datetime
from bson import ObjectId
from app.database.connection import get_db
from app.models.wishlist_model import WishlistItem


async def add_to_wishlist(user_id: str, product_id: str) -> WishlistItem:
    db = get_db()
    item = {
        "user_id": user_id,
        "product_id": product_id,
        "created_at": datetime.utcnow(),
    }
    result = await db.wishlist.insert_one(item)
    item["_id"] = str(result.inserted_id)
    return WishlistItem(**item)


async def get_wishlist(user_id: str) -> List[WishlistItem]:
    db = get_db()
    docs = await db.wishlist.find({"user_id": user_id}).to_list(100)
    items = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        items.append(WishlistItem(**doc))
    return items


async def delete_wishlist_item(item_id: str) -> dict:
    db = get_db()
    await db.wishlist.delete_one({"_id": ObjectId(item_id)})
    return {"deleted": True}
