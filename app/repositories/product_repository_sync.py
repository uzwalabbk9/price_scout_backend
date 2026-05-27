from bson import ObjectId
from app.models.product_model import Product, StorePrice
from app.database.collections import products_collection

def _serialize_product(doc):
    doc["_id"] = str(doc["_id"])
    return Product(**doc)

def create_product(product_dict: dict) -> Product:
    # Insert product dict into MongoDB
    product_dict.pop("_id", None)
    result = products_collection.insert_one(product_dict)
    product_dict["_id"] = result.inserted_id
    return _serialize_product(product_dict)

def get_all_products():
    cursor = products_collection.find({})
    return [_serialize_product(doc) for doc in cursor]

def update_product_prices(product_id: str, store_prices: list[StorePrice]):
    products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"store_prices": [sp.dict() for sp in store_prices]}},
    )

def get_product_by_id(product_id: str):
    doc = products_collection.find_one({"_id": ObjectId(product_id)})
    if not doc:
        return None
    return _serialize_product(doc)

def delete_product(product_id: str) -> bool:
    result = products_collection.delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count == 1