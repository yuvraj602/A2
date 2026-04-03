from __future__ import annotations

import base64
import json
import time
from typing import Any

ALLOWED_SUBJECTS = frozenset({"starlord", "gamora", "drax", "rocket", "groot"})


def _decode_jwt_payload(token: str) -> dict[str, Any] | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None
    payload_b64 = parts[1]
    padding = (4 - len(payload_b64) % 4) % 4
    payload_b64 += "=" * padding
    try:
        raw = base64.urlsafe_b64decode(payload_b64.encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def authorization_is_valid(authorization_header: str | None) -> bool:
    if not authorization_header or not authorization_header.startswith("Bearer "):
        return False
    token = authorization_header[7:].strip()
    if not token:
        return False
    payload = _decode_jwt_payload(token)
    if payload is None:
        return False
    sub = payload.get("sub")
    if sub not in ALLOWED_SUBJECTS:
        return False
    if payload.get("iss") != "cmu.edu":
        return False
    exp = payload.get("exp")
    if not isinstance(exp, (int, float)):
        return False
    if exp <= time.time():
        return False
    return True
