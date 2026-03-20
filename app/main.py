from __future__ import annotations

from flask import Response, jsonify, request, url_for
from email_validator import EmailNotValidError, validate_email

from app import create_app, db
from app.llm import generate_book_summary
from app.models import Book, Customer
from app.validators import validate_book_payload, validate_customer_payload

app = create_app()

with app.app_context():
    db.create_all()

@app.get("/status")
def status() -> Response:
    return Response("OK", status=200, content_type="text/plain")


@app.post("/books")
def add_book():
    payload = request.get_json(silent=True)
    valid, normalized = validate_book_payload(payload)
    if not valid:
        return jsonify({"message": "Illegal, missing, or malformed input."}), 400

    existing = db.session.get(Book, normalized["ISBN"])
    if existing is not None:
        return jsonify({"message": "This ISBN already exists in the system."}), 422

    summary = generate_book_summary(normalized)

    book = Book(
        isbn=normalized["ISBN"],
        title=normalized["title"],
        author=normalized["Author"],
        description=normalized["description"],
        genre=normalized["genre"],
        price=normalized["price"],
        quantity=normalized["quantity"],
        summary=summary,
    )
    db.session.add(book)
    db.session.commit()

    response = jsonify(book.to_dict(include_summary=False))
    response.status_code = 201
    response.headers["Location"] = url_for("get_book", isbn=book.isbn, _external=True)
    return response


@app.put("/books/<string:isbn>")
def update_book(isbn: str):
    payload = request.get_json(silent=True)
    valid, normalized = validate_book_payload(payload)
    if not valid:
        return jsonify({"message": "Illegal, missing, or malformed input."}), 400

    book = db.session.get(Book, isbn)
    if book is None:
        return "", 404

    book.title = normalized["title"]
    book.author = normalized["Author"]
    book.description = normalized["description"]
    book.genre = normalized["genre"]
    book.price = normalized["price"]
    book.quantity = normalized["quantity"]

    db.session.commit()

    return jsonify(book.to_dict(include_summary=False)), 200


@app.get("/books/<string:isbn>")
def get_book(isbn: str):
    book = db.session.get(Book, isbn)
    if book is None:
        return "", 404
    return jsonify(book.to_dict(include_summary=True)), 200


@app.get("/books/isbn/<string:isbn>")
def get_book_by_isbn(isbn: str):
    return get_book(isbn)


@app.post("/customers")
def add_customer():
    payload = request.get_json(silent=True)
    valid, normalized = validate_customer_payload(payload)
    if not valid:
        return jsonify({"message": "Illegal, missing, or malformed input."}), 400

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
    response.headers["Location"] = url_for("get_customer_by_id", customer_id=customer.id, _external=True)
    return response


@app.get("/customers/<string:customer_id>")
def get_customer_by_id(customer_id: str):
    if not customer_id.isdigit():
        return jsonify({"message": "Illegal, missing, or malformed input."}), 400

    customer = db.session.get(Customer, int(customer_id))
    if customer is None:
        return "", 404

    return jsonify(customer.to_dict()), 200


@app.get("/customers")
def get_customer_by_userid():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"message": "Illegal, missing, or malformed input."}), 400

    try:
        normalized_user_id = validate_email(user_id, check_deliverability=False).email
    except EmailNotValidError:
        return jsonify({"message": "Illegal, missing, or malformed input."}), 400

    customer = Customer.query.filter_by(user_id=normalized_user_id).first()
    if customer is None:
        return "", 404

    return jsonify(customer.to_dict()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)