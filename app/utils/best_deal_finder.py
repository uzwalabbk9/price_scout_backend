from app.utils.price_normalizer import normalize_price


def find_best_deal(results: list) -> dict:
    """Return the item with the lowest price from a list of dicts."""
    if not results:
        return {}
    try:
        return min(results, key=lambda x: normalize_price(x.get("price", 0)))
    except Exception:
        return results[0] if results else {}
