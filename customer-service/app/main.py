from __future__ import annotations

from flask import Response, jsonify, request, url_for
from email_validator import EmailNotValidError, validate_email

from app import create_app, db
from app.models import Customer
from app.validators import validate_customer_payload

app = create_app()

with app.app_context():
    db.create_all()


@app.get("/status")
def status() -> Response:
    return Response("OK", status=200, content_type="text/plain")


def _customer_bad_request():
    return jsonify({"message": "Illegal, missing, or malformed input."}), 400


@app.get("/customers")
def get_customer_by_userid():
    user_id = request.args.get("userId")
    if not user_id:
        return _customer_bad_request()

    try:
        normalized_user_id = validate_email(user_id, check_deliverability=False).email
    except EmailNotValidError:
        return _customer_bad_request()

    customer = Customer.query.filter_by(user_id=normalized_user_id).first()
    if customer is None:
        return "", 404

    return jsonify(customer.to_dict()), 200


@app.post("/customers")
def add_customer():
    payload = request.get_json(silent=True)
    valid, normalized = validate_customer_payload(payload)
    if not valid:
        return _customer_bad_request()

    existing = Customer.query.filter_by(user_id=normalized["userId"]).first()
    if existing is not None:
        return jsonify({"message": "This user ID already exists in the system."}), 422

    customer = Customer(
        user_id=normalized["userId"],
        name=normalized["name"],
        phone=normalized["phone"],
        address=normalized["address"],
        address2=normalized["address2"],
        city=normalized["city"],
        state=normalized["state"],
        zipcode=normalized["zipcode"],
    )
    db.session.add(customer)
    db.session.commit()

    response = jsonify(customer.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("customer_path_tail", tail=str(customer.id), _external=True)
    return response


@app.route("/customers/<path:tail>", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"])
def customer_path_tail(tail: str):
    if request.method not in ("GET", "HEAD"):
        return _customer_bad_request()

    if "/" in tail or not tail.isdigit():
        return _customer_bad_request()

    customer = db.session.get(Customer, int(tail))
    if customer is None:
        return "", 404

    if request.method == "HEAD":
        return Response(status=200, mimetype="application/json")
    return jsonify(customer.to_dict()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
