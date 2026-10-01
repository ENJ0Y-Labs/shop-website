import uuid

import pytest
from werkzeug.security import generate_password_hash

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Cart, CartItem, Product, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = ".test_flask_session"
    SESSION_COOKIE_SECURE = False
    CORS_ORIGINS = ["http://localhost:5173"]
    GOOGLE_CLIENT_ID = None
    GOOGLE_CLIENT_SECRET = None
    GOOGLE_REDIRECT_URI = "http://localhost:5000/api/auth/google/callback"
    SUPABASE_URL = None
    SUPABASE_STORAGE_BUCKET = "product-images"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        user = User(
            email="user@example.com",
            password_hash=generate_password_hash("password123"),
            name="User",
        )
        other_user = User(
            email="other@example.com",
            password_hash=generate_password_hash("password123"),
            name="Other User",
        )
        products = [
            Product(
                id=uuid.uuid4(),
                name="Shirt",
                description="Cotton shirt",
                price=1000000,
                category="Clothing",
                stock=5,
            ),
            Product(
                id=uuid.uuid4(),
                name="Bag",
                description="Travel bag",
                price=2000000,
                category="Bags",
                stock=2,
            ),
            Product(
                id=uuid.uuid4(),
                name="Sold Out",
                description="Unavailable",
                price=3000000,
                category="Home",
                stock=0,
            ),
        ]
        db.session.add_all([user, other_user, *products])
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def products(app):
    return db.session.query(Product).order_by(Product.name).all()


def login(client, email="user@example.com"):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200


def test_unauthenticated_cart_is_rejected(client):
    assert client.get("/api/cart").status_code == 401


def test_add_item_and_increase(client, products):
    login(client)
    shirt = products[1]

    response = client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 2},
    )
    assert response.status_code == 201
    assert response.json["cart"]["item_count"] == 2
    assert response.json["cart"]["items"][0]["quantity"] == 2

    response = client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 2},
    )
    assert response.status_code == 201
    assert response.json["cart"]["items"][0]["quantity"] == 4


def test_decrease_and_remove(client, products):
    login(client)
    shirt = products[1]

    client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 3},
    )
    item_id = client.get("/api/cart").json["cart"]["items"][0]["id"]

    response = client.patch(
        f"/api/cart/items/{item_id}",
        json={"quantity": 1},
    )
    assert response.status_code == 200
    assert response.json["cart"]["items"][0]["quantity"] == 1

    response = client.delete(f"/api/cart/items/{item_id}")
    assert response.status_code == 200
    assert response.json["cart"]["items"] == []


def test_clear_cart(client, products):
    login(client)
    for product in products[:2]:
        client.post(
            "/api/cart/items",
            json={"product_id": str(product.id), "quantity": 1},
        )

    response = client.delete("/api/cart")
    assert response.status_code == 200
    assert response.json["cart"]["items"] == []
    assert response.json["cart"]["item_count"] == 0


def test_stock_limit_is_enforced(client, products):
    login(client)
    shirt = products[1]

    response = client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 6},
    )
    assert response.status_code == 409
    assert response.json["error"]["code"] == "insufficient_stock"

    response = client.post(
        "/api/cart/items",
        json={"product_id": str(products[2].id), "quantity": 1},
    )
    assert response.status_code == 409


def test_user_cannot_modify_another_users_item(client, app, products):
    login(client)
    shirt = products[1]
    client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 1},
    )
    item_id = client.get("/api/cart").json["cart"]["items"][0]["id"]

    client.post("/api/auth/logout")
    login(client, "other@example.com")

    response = client.patch(
        f"/api/cart/items/{item_id}",
        json={"quantity": 2},
    )
    assert response.status_code == 404


def test_merge_adds_to_existing_cart(client, products):
    login(client)
    bag, shirt, _ = products

    client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 1},
    )

    response = client.post(
        "/api/cart/merge",
        json={
            "items": [
                {"product_id": str(shirt.id), "quantity": 2},
                {"product_id": str(bag.id), "quantity": 1},
            ]
        },
    )
    assert response.status_code == 200

    items = {
        item["product"]["id"]: item["quantity"]
        for item in response.json["cart"]["items"]
    }
    assert items[str(shirt.id)] == 3
    assert items[str(bag.id)] == 1


def test_merge_is_atomic_when_stock_is_exceeded(client, products):
    login(client)
    bag, shirt, _ = products

    response = client.post(
        "/api/cart/merge",
        json={
            "items": [
                {"product_id": str(shirt.id), "quantity": 1},
                {"product_id": str(bag.id), "quantity": 3},
            ]
        },
    )
    assert response.status_code == 409

    cart = client.get("/api/cart").json["cart"]
    assert cart["items"] == []
