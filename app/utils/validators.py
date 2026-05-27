def validate_query(query: str) -> str:
    if not query or len(query.strip()) < 2:
        raise ValueError("Search query must be at least 2 characters.")
    return query.strip()


def validate_price(price: float) -> float:
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    return price
