from __future__ import annotations

from email_validator import EmailNotValidError, validate_email

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC",
}

CUSTOMER_REQUIRED_FIELDS = ["userId", "name", "phone", "address", "city", "state", "zipcode"]


def _is_missing_required_fields(payload: dict, required_fields: list[str]) -> bool:
    return not isinstance(payload, dict) or any(field not in payload for field in required_fields)


def validate_customer_payload(payload: dict) -> tuple[bool, dict | None]:
    if _is_missing_required_fields(payload, CUSTOMER_REQUIRED_FIELDS):
        return False, None

    if "address2" in payload and payload["address2"] is not None and not isinstance(payload["address2"], str):
        return False, None

    try:
        normalized_email = validate_email(str(payload.get("userId", "")), check_deliverability=False).email
    except EmailNotValidError:
        return False, None

    state = str(payload.get("state", "")).upper()
    if state not in US_STATES:
        return False, None

    for field in ["name", "phone", "address", "city", "zipcode"]:
        value = payload.get(field)
        if not isinstance(value, str):
            return False, None

    normalized = {
        "userId": normalized_email,
        "name": payload["name"],
        "phone": payload["phone"],
        "address": payload["address"],
        "address2": payload.get("address2"),
        "city": payload["city"],
        "state": state,
        "zipcode": payload["zipcode"],
    }
    return True, normalized
