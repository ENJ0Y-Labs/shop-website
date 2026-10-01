import pytest
import uuid

from werkzeug.security import generate_password_hash

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Cart, CartItem, Order, Product, User


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
        product = Product(
            id=uuid.uuid4(),
            name="Test Shirt",
            description="Cotton shirt",
            price=1500000,
            category="Clothing",
            stock=5,
        )
        second_product = Product(
            id=uuid.uuid4(),
            name="Test Bag",
            description="Travel bag",
            price=2000000,
            category="Bags",
            stock=2,
        )
        db.session.add_all([user, product, second_product])
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def products(app):
    return db.session.query(Product).order_by(Product.name).all()


def login(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 200


def add_to_cart(client, product_id, quantity=1):
    response = client.post(
        "/api/cart/items",
        json={"product_id": str(product_id), "quantity": quantity},
    )
    assert response.status_code == 201


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


def test_checkout_requires_authentication(client):
    response = client.post("/api/orders", json=checkout_payload())
    assert response.status_code == 401


def test_checkout_rejects_empty_cart(client):
    login(client)

    response = client.post("/api/orders", json=checkout_payload())

    assert response.status_code == 400
    assert response.json["error"]["code"] == "empty_cart"


def test_checkout_creates_order_with_price_snapshots_and_clears_cart(client, app, products):
    login(client)
    shirt = products[1]
    bag = products[0]

    add_to_cart(client, shirt.id, 2)
    add_to_cart(client, bag.id, 1)

    response = client.post(
        "/api/orders",
        json={**checkout_payload(), "total_amount": 1},
    )

    assert response.status_code == 201
    order_data = response.json["order"]
    assert order_data["order_number"] == "ORD-000001"
    assert order_data["status"] == "confirmed"
    assert order_data["total_amount"] == 2 * shirt.price + bag.price
    assert order_data["customer"]["email"] == "customer@example.com"

    items = {
        item["product_name"]: item
        for item in order_data["items"]
    }
    assert items[shirt.name]["unit_price"] == shirt.price
    assert items[shirt.name]["quantity"] == 2
    assert items[shirt.name]["subtotal"] == shirt.price * 2

    with app.app_context():
        order = db.session.query(Order).filter_by(order_number="ORD-000001").one()
        assert len(order.items) == 2

        refreshed_shirt = db.session.get(Product, shirt.id)
        refreshed_bag = db.session.get(Product, bag.id)
        assert refreshed_shirt.stock == 3
        assert refreshed_bag.stock == 1

        cart = db.session.query(Cart).filter_by(user_id=order.user_id).one()
        assert db.session.query(CartItem).filter_by(cart_id=cart.id).count() == 0


def test_checkout_uses_current_price_not_cart_total(client, app, products):
    login(client)
    shirt = products[1]
    add_to_cart(client, shirt.id, 1)

    with app.app_context():
        product = db.session.get(Product, shirt.id)
        product.price = 1750000
        db.session.commit()

    response = client.post(
        "/api/orders",
        json={**checkout_payload(), "email": "buyer@example.com"},
    )

    assert response.status_code == 201
    assert response.json["order"]["total_amount"] == 1750000
    assert response.json["order"]["items"][0]["unit_price"] == 1750000


def test_checkout_rejects_insufficient_stock_without_creating_order(client, app, products):
    login(client)
    shirt = products[1]
    add_to_cart(client, shirt.id, 2)

    with app.app_context():
        product = db.session.get(Product, shirt.id)
        product.stock = 1
        db.session.commit()

    response = client.post("/api/orders", json=checkout_payload())

    assert response.status_code == 409
    assert response.json["error"]["code"] == "insufficient_stock"

    with app.app_context():
        assert db.session.query(Order).count() == 0
        cart = db.session.query(Cart).join(User).filter(User.email == "user@example.com").one()
        item = db.session.query(CartItem).filter_by(cart_id=cart.id).one()
        assert item.quantity == 2


def test_checkout_validates_required_customer_fields(client, products):
    login(client)
    add_to_cart(client, products[1].id)

    payload = checkout_payload()
    del payload["address"]

    response = client.post("/api/orders", json=payload)

    assert response.status_code == 400
    assert response.json["error"]["code"] == "validation_error"


def test_order_history_returns_only_authenticated_users_orders(client, app, products):
    login(client)
    add_to_cart(client, products[1].id, 1)

    response = client.post("/api/orders", json=checkout_payload())
    assert response.status_code == 201
    order_id = response.json["order"]["id"]

    history = client.get("/api/orders")
    assert history.status_code == 200
    assert [order["id"] for order in history.json["orders"]] == [order_id]

    detail = client.get(f"/api/orders/{order_id}")
    assert detail.status_code == 200
    assert detail.json["order"]["id"] == order_id


def test_order_detail_rejects_invalid_or_other_order(client, app, products):
    login(client)
    add_to_cart(client, products[1].id, 1)
    response = client.post("/api/orders", json=checkout_payload())
    order_id = response.json["order"]["id"]

    assert client.get("/api/orders/not-a-uuid").status_code == 400

    with app.app_context():
        other_user = User(
            email="other@example.com",
            password_hash=generate_password_hash("password123"),
            name="Other",
        )
        db.session.add(other_user)
        db.session.commit()

    with client.session_transaction() as active_session:
        active_session["user_id"] = str(other_user.id)

    assert client.get(f"/api/orders/{order_id}").status_code == 404
