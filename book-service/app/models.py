from __future__ import annotations

from app import db


class Book(db.Model):
    __tablename__ = "books"

    isbn = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.Text, nullable=True)

    def to_dict(self, include_summary: bool = True) -> dict:
        payload = {
            "ISBN": self.isbn,
            "title": self.title,
            "Author": self.author,
            "description": self.description,
            "genre": self.genre,
            "price": float(self.price),
            "quantity": self.quantity,
        }
        if include_summary:
            payload["summary"] = self.summary
        return payload
