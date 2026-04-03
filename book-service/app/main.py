from __future__ import annotations

from flask import Response, jsonify, request, url_for

from app import create_app, db
from app.llm import generate_book_summary
from app.models import Book
from app.validators import validate_book_payload

app = create_app()

with app.app_context():
    db.create_all()


def _resolve_book_summary(normalized: dict) -> str:
    s = generate_book_summary(normalized)
    if s and str(s).strip():
        return str(s).strip()
    desc = normalized.get("description") or ""
    if isinstance(desc, str) and desc.strip():
        return (desc[:1200] + "…") if len(desc) > 1200 else desc
    return "No summary is available for this book."


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

    summary = _resolve_book_summary(normalized)

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

    if normalized["ISBN"] != isbn:
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
    book.summary = _resolve_book_summary(normalized)

    db.session.commit()

    return jsonify(book.to_dict(include_summary=False)), 200


@app.get("/books/<string:isbn>")
def get_book(isbn: str):
    book = db.session.get(Book, isbn)
    if book is None:
        return "", 404
    if not book.summary or not str(book.summary).strip():
        book.summary = _resolve_book_summary(
            {
                "ISBN": book.isbn,
                "title": book.title,
                "Author": book.author,
                "description": book.description,
                "genre": book.genre,
            }
        )
        db.session.commit()
    return jsonify(book.to_dict(include_summary=True)), 200


@app.get("/books/isbn/<string:isbn>")
def get_book_by_isbn(isbn: str):
    return get_book(isbn)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
