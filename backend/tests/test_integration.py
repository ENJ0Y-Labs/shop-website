import uuid

import pytest
from werkzeug.security import generate_password_hash

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import CartItem, Order, Product, User
from backend.app.services import google_oauth
from backend.app.routes import auth as auth_routes


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = False
    CORS_ORIGINS = ["http://localhost:5173"]
    GOOGLE_CLIENT_ID = "test-client"
    GOOGLE_CLIENT_SECRET = "test-secret"
    GOOGLE_REDIRECT_URI = "http://localhost:5000/api/auth/google/callback"
    SUPABASE_URL = "https://example.supabase.co"
    SUPABASE_STORAGE_BUCKET = "product-images"
    MAILGUN_API_KEY = "test-api-key"
    MAILGUN_DOMAIN = "mg.example.com"
    MAILGUN_FROM_EMAIL = "enj0y Solution <orders@mg.example.com>"
    MAILGUN_API_BASE_URL = "https://api.mailgun.net"
    MAILGUN_TIMEOUT = 10


@pytest.fixture
def app(tmp_path):
    TestConfig.SESSION_FILE_DIR = str(tmp_path / "flask_session")
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        user_a = User(
            email="user@example.com",
            password_hash=generate_password_hash("password123"),
            name="User A",
        )
        user_b = User(
            email="other@example.com",
            password_hash=generate_password_hash("password123"),
            name="User B",
        )
        products = [
            Product(
                id=uuid.uuid4(),
                name="Alpha Shirt",
                description="Cotton shirt",
                price=1500000,
                category="Clothing",
                stock=5,
            ),
            Product(
                id=uuid.uuid4(),
                name="Beta Bag",
                description="Travel bag",
                price=2500000,
                category="Bags",
                stock=2,
            ),
            Product(
                id=uuid.uuid4(),
                name="Gamma Lamp",
                description="Desk lamp",
                price=500000,
                category="Home",
                stock=0,
            ),
        ]
        db.session.add_all([user_a, user_b, *products])
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def products(app):
    with app.app_context():
        return db.session.query(Product).order_by(Product.name).all()


def login(client, email="user@example.com"):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200
    return response


def checkout_payload():
    return {
        "name": "Customer Name",
        "email": "customer@example.com",
        "phone": "08012345678",
        "address": "12 Test Street",
        "city": "Port Harcourt",
        "state": "Rivers",
        "country": "Nigeria",
    }


def test_registration_login_logout_flow(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "new@example.com",
            "password": "password123",
            "name": "New User",
        },
    )
    assert response.status_code == 201
    assert response.json["user"]["email"] == "new@example.com"
    assert client.get("/api/auth/me").status_code == 200

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401

    response = client.post(
        "/api/auth/login",
        json={"email": "new@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert client.get("/api/auth/me").status_code == 200


def test_google_auth_callback_creates_verified_google_session(client, app, monkeypatch):
    class FakeGoogleClient:
        def authorize_access_token(self):
            return {
                "userinfo": {
                    "sub": "google-user-123",
                    "email": "google@example.com",
                    "email_verified": True,
                    "name": "Google User",
                    "picture": "https://example.com/avatar.jpg",
                }
            }

    monkeypatch.setattr(google_oauth, "get_google_client", lambda: FakeGoogleClient())

    response = client.get("/api/auth/google/callback", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost:5173/?auth=success"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json["user"]["email"] == "google@example.com"

    with app.app_context():
        user = db.session.query(User).filter_by(email="google@example.com").one()
        assert user.google_id == "google-user-123"


def test_google_auth_rejects_unverified_email(client, monkeypatch):
    class FakeGoogleClient:
        def authorize_access_token(self):
            return {
                "userinfo": {
                    "sub": "google-user-456",
                    "email": "unverified@example.com",
                    "email_verified": False,
                }
            }

    monkeypatch.setattr(google_oauth, "get_google_client", lambda: FakeGoogleClient())

    response = client.get("/api/auth/google/callback")

    assert response.status_code == 400
    assert response.json["error"]["code"] == "google_email_unverified"
    assert client.get("/api/auth/me").status_code == 401


def test_product_browsing_search_filter_and_sort(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json["pagination"]["total"] == 3

    response = client.get("/api/products?search=shirt&category=clothing")
    assert response.status_code == 200
    assert [item["name"] for item in response.json["products"]] == ["Alpha Shirt"]

    response = client.get("/api/products?sort=price_desc")
    assert response.status_code == 200
    assert [item["name"] for item in response.json["products"]] == [
        "Beta Bag",
        "Alpha Shirt",
        "Gamma Lamp",
    ]


def test_login_cart_merge_and_order_flow(client, app, products, monkeypatch):
    shirt, bag, _ = products

    login(client)

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
    assert response.json["cart"]["item_count"] == 3

    sent_orders = []

    def fake_send(order):
        sent_orders.append(order.order_number)
        return True

    monkeypatch.setattr(
        "backend.app.routes.orders.send_order_confirmation",
        fake_send,
    )

    response = client.post("/api/orders", json=checkout_payload())
    assert response.status_code == 201

    order_data = response.json["order"]
    assert order_data["status"] == "confirmed"
    assert order_data["total_amount"] == (shirt.price * 2) + bag.price
    assert sent_orders == [order_data["order_number"]]

    with app.app_context():
        refreshed_shirt = db.session.get(Product, shirt.id)
        refreshed_bag = db.session.get(Product, bag.id)
        assert refreshed_shirt.stock == 3
        assert refreshed_bag.stock == 1

        assert db.session.query(CartItem).count() == 0

    history = client.get("/api/orders")
    assert history.status_code == 200
    assert [item["id"] for item in history.json["orders"]] == [order_data["id"]]

    detail = client.get(f"/api/orders/{order_data['id']}")
    assert detail.status_code == 200
    assert detail.json["order"]["order_number"] == order_data["order_number"]


def test_insufficient_stock_does_not_create_order_or_reduce_inventory(client, app, products):
    shirt, _, _ = products
    login(client)

    response = client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 2},
    )
    assert response.status_code == 201

    with app.app_context():
        product = db.session.get(Product, shirt.id)
        product.stock = 1
        db.session.commit()

    response = client.post("/api/orders", json=checkout_payload())

    assert response.status_code == 409
    assert response.json["error"]["code"] == "insufficient_stock"

    with app.app_context():
        assert db.session.query(Order).count() == 0
        product = db.session.get(Product, shirt.id)
        assert product.stock == 1
        item = db.session.query(CartItem).one()
        assert item.quantity == 2


def test_order_authorization_blocks_user_b_from_user_a_order(client, app, products, monkeypatch):
    shirt, _, _ = products
    login(client)
    client.post(
        "/api/cart/items",
        json={"product_id": str(shirt.id), "quantity": 1},
    )

    monkeypatch.setattr(
        "backend.app.routes.orders.send_order_confirmation",
        lambda order: True,
    )
    response = client.post("/api/orders", json=checkout_payload())
    assert response.status_code == 201
    order_id = response.json["order"]["id"]

    client.post("/api/auth/logout")
    login(client, "other@example.com")

    history = client.get("/api/orders")
    assert history.status_code == 200
    assert history.json["orders"] == []

    detail = client.get(f"/api/orders/{order_id}")
    assert detail.status_code == 404


def test_google_service_links_existing_email_account(app):
    with app.app_context():
        user = User(
            email="linked@example.com",
            password_hash=generate_password_hash("password123"),
            name="Existing User",
        )
        db.session.add(user)
        db.session.commit()

        class FakeGoogleClient:
            def authorize_access_token(self):
                return {
                    "userinfo": {
                        "sub": "google-linked-123",
                        "email": "linked@example.com",
                        "email_verified": True,
                        "name": "Existing User",
                        "picture": "https://example.com/new-avatar.jpg",
                    }
                }

        from flask import session

        with app.test_request_context("/api/auth/google/callback"):
            monkeypatch = pytest.MonkeyPatch()
            monkeypatch.setattr(
                google_oauth,
                "get_google_client",
                lambda: FakeGoogleClient(),
            )
            linked = google_oauth.handle_google_callback(session)
            monkeypatch.undo()

        assert linked.id == user.id
        assert linked.google_id == "google-linked-123"
        assert linked.profile_picture_url == "https://example.com/new-avatar.jpg"
