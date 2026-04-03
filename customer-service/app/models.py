from __future__ import annotations

from app import db


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
