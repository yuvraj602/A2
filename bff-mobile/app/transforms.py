from __future__ import annotations

from typing import Any

MOBILE_CUSTOMER_OMIT = frozenset({"address", "address2", "city", "state", "zipcode"})


def transform_book_genre_nonfiction(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: transform_book_genre_nonfiction(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [transform_book_genre_nonfiction(v) for v in obj]
    if obj == "non-fiction":
        return 3
    return obj


def strip_customer_location_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if k not in MOBILE_CUSTOMER_OMIT}


def is_book_detail_get_path(path: str) -> bool:
    p = path.rstrip("/") or "/"
    segments = [s for s in p.split("/") if s]
    if len(segments) == 3 and segments[0] == "books" and segments[1] == "isbn":
        return True
    if len(segments) == 2 and segments[0] == "books" and segments[1] != "isbn":
        return True
    return False


def is_customer_mobile_get(path: str, user_id_query: str | None) -> bool:
    segments = [s for s in path.rstrip("/").split("/") if s]
    if len(segments) == 2 and segments[0] == "customers" and segments[1].isdigit():
        return True
    if len(segments) == 1 and segments[0] == "customers" and user_id_query:
        return True
    return False
