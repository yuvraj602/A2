from __future__ import annotations

import os

import requests
from flask import Flask, Response, jsonify, request

from app.jwt_validation import authorization_is_valid

app = Flask(__name__)
app.url_map.strict_slashes = False


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


def _proxy_to_backend() -> Response:
    base = _backend_base()
    if not base:
        return jsonify({"message": "Backend base URL is not configured."}), 503
    path = request.full_path
    if path.endswith("?"):
        path = path[:-1]
    url = f"{base}{path}"

    forward_headers: dict[str, str] = {}
    content_type = request.headers.get("Content-Type")
    if content_type:
        forward_headers["Content-Type"] = content_type

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

    out_headers = {}
    if "Location" in backend_resp.headers:
        out_headers["Location"] = backend_resp.headers["Location"]

    return Response(
        backend_resp.content,
        status=backend_resp.status_code,
        headers=out_headers,
        content_type=backend_resp.headers.get("Content-Type"),
    )


@app.route("/status", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/customers", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/customers/<path:sub>", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/books", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/books/<path:sub>", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(sub: str | None = None) -> Response:
    return _proxy_to_backend()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
