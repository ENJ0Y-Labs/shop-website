from app import create_app
from app.extensions import db
from app.models import Product

PRODUCTS = [
    {"name": "Classic Cotton T-Shirt", "description": "Everyday cotton t-shirt with a clean, comfortable fit.", "price": 1250000, "category": "Clothing", "stock": 25, "image_url": None},
    {"name": "Minimal Canvas Backpack", "description": "Lightweight everyday backpack for school, work, and travel.", "price": 2200000, "category": "Bags", "stock": 12, "image_url": None},
    {"name": "Wireless Desk Lamp", "description": "Rechargeable LED desk lamp with adjustable brightness.", "price": 1850000, "category": "Home", "stock": 18, "image_url": None},
    {"name": "Everyday Sneakers", "description": "Casual sneakers designed for daily wear.", "price": 3500000, "category": "Footwear", "stock": 10, "image_url": None},
]


def seed_products():
    app = create_app()
    with app.app_context():
        for data in PRODUCTS:
            if Product.query.filter_by(name=data["name"]).first() is None:
                db.session.add(Product(**data))
        db.session.commit()


if __name__ == "__main__":
    seed_products()
