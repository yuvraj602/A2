from __future__ import annotations

from decimal import Decimal, InvalidOperation

BOOK_REQUIRED_FIELDS = ["ISBN", "title", "Author", "description", "genre", "price", "quantity"]


def _is_missing_required_fields(payload: dict, required_fields: list[str]) -> bool:
    return not isinstance(payload, dict) or any(field not in payload for field in required_fields)


def validate_price(value: object) -> Decimal | None:
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None

    if dec < 0:
        return None

    if dec.as_tuple().exponent < -2:
        return None

    return dec.quantize(Decimal("0.01"))


def validate_book_payload(payload: dict) -> tuple[bool, dict | None]:
    if _is_missing_required_fields(payload, BOOK_REQUIRED_FIELDS):
        return False, None

    price = validate_price(payload.get("price"))
    if price is None:
        return False, None

    try:
        quantity = int(payload.get("quantity"))
    except (TypeError, ValueError):
        return False, None

    for field in ["ISBN", "title", "Author", "description", "genre"]:
        value = payload.get(field)
        if not isinstance(value, str):
            return False, None

    normalized = {
        "ISBN": payload["ISBN"],
        "title": payload["title"],
        "Author": payload["Author"],
        "description": payload["description"],
        "genre": payload["genre"],
        "price": price,
        "quantity": quantity,
    }
    return True, normalized
