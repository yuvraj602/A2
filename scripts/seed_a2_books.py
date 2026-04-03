"""Seed books table. Run from repo root: python scripts/seed_a2_books.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "book-service"))

from app import create_app, db  # noqa: E402
from app.models import Book  # noqa: E402

app = create_app()


def main() -> None:
    with app.app_context():
        db.create_all()

        if not db.session.get(Book, "978-0136886099"):
            db.session.add(
                Book(
                    isbn="978-0136886099",
                    title="Software Architecture in Practice",
                    author="Bass, L.",
                    description="The definitive guide to architecting modern software",
                    genre="non-fiction",
                    price=59.95,
                    quantity=106,
                    summary=None,
                )
            )

        if not db.session.get(Book, "978-0201633610"):
            db.session.add(
                Book(
                    isbn="978-0201633610",
                    title="Design Patterns",
                    author="Gamma, E.",
                    description="Elements of reusable object-oriented software",
                    genre="non-fiction",
                    price=49.99,
                    quantity=50,
                    summary=None,
                )
            )

        db.session.commit()
        print("Book seed complete.")


if __name__ == "__main__":
    main()
