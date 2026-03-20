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


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    address2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(128), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(16), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "address2": self.address2,
            "city": self.city,
            "state": self.state,
            "zipcode": self.zipcode,
        }
