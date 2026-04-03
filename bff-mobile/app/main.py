from __future__ import annotations

import os

import requests
from flask import Flask, Response, jsonify, request

from app.jwt_validation import authorization_is_valid
from app.transforms import (
    is_book_detail_get_path,
    is_customer_mobile_get,
    strip_customer_location_fields,
    transform_book_genre_nonfiction,
)

app = Flask(__name__)

def _backend_base() -> str | None:
    base = os.getenv("URL_BASE_BACKEND_SERVICES", "").strip().rstrip("/")
    return base or None


@app.before_request
def require_client_and_jwt() -> tuple | None:
    raw = request.headers.get("X-Client-Type")
    if raw is None or not str(raw).strip():
        return jsonify({"message": "X-Client-Type header is required."}), 400

    auth = request.headers.get("Authorization")
    if auth is None or not auth.strip():
        return jsonify({"message": "Authorization header is required."}), 401
    if not authorization_is_valid(auth):
        return jsonify({"message": "Invalid or expired token."}), 401
    return None


def _maybe_transform_mobile_response(backend_resp: requests.Response) -> Response:
    if request.method != "GET" or backend_resp.status_code != 200:
        return _raw_backend_response(backend_resp)

    content_type = backend_resp.headers.get("Content-Type", "")
    if "application/json" not in content_type.lower():
        return _raw_backend_response(backend_resp)

    try:
        data = backend_resp.json()
    except ValueError:
        return _raw_backend_response(backend_resp)

    path = request.path
    user_id_q = request.args.get("userId")

    if is_book_detail_get_path(path):
        transformed = transform_book_genre_nonfiction(data)
        out = jsonify(transformed)
        out.status_code = 200
        return out

    if is_customer_mobile_get(path, user_id_q) and isinstance(data, dict):
        stripped = strip_customer_location_fields(data)
        out = jsonify(stripped)
        out.status_code = 200
        return out

    return _raw_backend_response(backend_resp)


def _raw_backend_response(backend_resp: requests.Response) -> Response:
    out_headers = {}
    if "Location" in backend_resp.headers:
        out_headers["Location"] = backend_resp.headers["Location"]
    return Response(
        backend_resp.content,
        status=backend_resp.status_code,
        headers=out_headers,
        content_type=backend_resp.headers.get("Content-Type"),
    )


def _proxy_to_backend() -> Response:
    base = _backend_base()
    if not base:
        return jsonify({"message": "Backend base URL is not configured."}), 503
    path = request.full_path
    if path.endswith("?"):
        path = path[:-1]
    url = f"{base}{path}"

    forward_headers: dict[str, str] = {}
    ct = request.headers.get("Content-Type")
    if ct:
        forward_headers["Content-Type"] = ct

    data = None
    if request.method in ("POST", "PUT", "PATCH"):
        data = request.get_data()

    try:
        backend_resp = requests.request(
            method=request.method,
            url=url,
            headers=forward_headers,
            data=data,
            timeout=120,
            allow_redirects=False,
        )
    except requests.RequestException:
        return jsonify({"message": "Upstream service unavailable."}), 502

    return _maybe_transform_mobile_response(backend_resp)


@app.route("/status", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/customers", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/customers/<path:sub>", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/books", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/books/<path:sub>", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(sub: str | None = None) -> Response:
    return _proxy_to_backend()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
