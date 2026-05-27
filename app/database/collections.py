"""
Sync PyMongo collections — used ONLY by background workers (APScheduler).
Connection is lazy: the client is only created when a collection is first accessed,
so an invalid URI does not crash the app at import time.
"""
import pymongo
from app.config.settings import settings

_sync_client = None
_sync_db = None


def _get_sync_db():
    global _sync_client, _sync_db
    if _sync_db is None:
        _sync_client = pymongo.MongoClient(settings.MONGO_URI)
        _sync_db = _sync_client[settings.MONGO_DB_NAME]
    return _sync_db


class _LazyCollection:
    """Proxy that defers the actual MongoClient creation until first use."""

    def __init__(self, name: str):
        self._name = name

    def __getattr__(self, item):
        return getattr(_get_sync_db()[self._name], item)

    def __getitem__(self, item):
        return _get_sync_db()[self._name][item]

    def find(self, *args, **kwargs):
        return _get_sync_db()[self._name].find(*args, **kwargs)

    def find_one(self, *args, **kwargs):
        return _get_sync_db()[self._name].find_one(*args, **kwargs)

    def insert_one(self, *args, **kwargs):
        return _get_sync_db()[self._name].insert_one(*args, **kwargs)

    def update_one(self, *args, **kwargs):
        return _get_sync_db()[self._name].update_one(*args, **kwargs)

    def delete_one(self, *args, **kwargs):
        return _get_sync_db()[self._name].delete_one(*args, **kwargs)


products_collection      = _LazyCollection("products")
store_prices_collection  = _LazyCollection("store_prices")
alerts_collection        = _LazyCollection("alerts")
wishlist_collection      = _LazyCollection("wishlist")
user_settings_collection = _LazyCollection("user_settings")
