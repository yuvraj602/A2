"""Seed customers table. Run from repo root: python scripts/seed_a2_customers.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "customer-service"))

from app import create_app, db  # noqa: E402
from app.models import Customer  # noqa: E402

app = create_app()


def main() -> None:
    with app.app_context():
        db.create_all()

        if not Customer.query.filter_by(user_id="starlord2002@gmail.com").first():
            db.session.add(
                Customer(
                    user_id="starlord2002@gmail.com",
                    name="Star Lord",
                    phone="+14122144122",
                    address="48 Galaxy Rd",
                    address2="suite 4",
                    city="Fargo",
                    state="ND",
                    zipcode="58102",
                )
            )

        if not Customer.query.filter_by(user_id="rocket.raccoon@gmail.com").first():
            db.session.add(
                Customer(
                    user_id="rocket.raccoon@gmail.com",
                    name="Rocket",
                    phone="+14125550123",
                    address="1 Milano Way",
                    address2=None,
                    city="Fargo",
                    state="ND",
                    zipcode="58102",
                )
            )

        db.session.commit()
        print("Customer seed complete.")


if __name__ == "__main__":
    main()
