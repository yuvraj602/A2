from app import create_app, db
from app.models import Book, Customer


app = create_app()


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

    existing_customer = Customer.query.filter_by(user_id="starlord2002@gmail.com").first()
    if not existing_customer:
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

    existing_customer_2 = Customer.query.filter_by(user_id="rocket.raccoon@gmail.com").first()
    if not existing_customer_2:
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
    print("Seed data inserted.")
