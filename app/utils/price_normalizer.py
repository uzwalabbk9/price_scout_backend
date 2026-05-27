def normalize_price(price) -> float:
    """Accept a string like '£199.99' or a float and return a clean float."""
    if isinstance(price, (int, float)):
        return float(price)
    try:
        cleaned = (
            str(price)
            .replace("£", "")
            .replace(",", "")
            .replace("GBP", "")
            .strip()
        )
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0
