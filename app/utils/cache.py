import time

_cache = {}


def set_cache(key: str, value: any, ttl: int = 300):
    _cache[key] = {
        "value": value,
        "expires": time.time() + ttl
    }


def get_cache(key: str):
    item = _cache.get(key)
    if not item:
        return None

    if time.time() > item["expires"]:
        del _cache[key]
        return None

    return item["value"]