from app import create_app, db
from app.models import Book, Customer


app = create_app()


with app.app_context():
    db.session.query(Book).delete()
    db.session.query(Customer).delete()
    db.session.commit()
    print("Books and customers tables cleared.")
