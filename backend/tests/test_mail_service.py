import uuid

import pytest
from werkzeug.security import generate_password_hash

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Cart, CartItem, Order, OrderItem, Product, User
from backend.app.services import mail_service


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
        user = User(
            email="customer@example.com",
            password_hash=generate_password_hash("password123"),
            name="Customer Name",
        )
        product = Product(
            id=uuid.uuid4(),
            name="Test Shirt",
            description="Cotton shirt",
            price=1500000,
            category="Clothing",
            stock=5,
        )
        db.session.add_all([user, product])
        db.session.flush()
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.flush()
        db.session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=2))
        db.session.commit()
        yield app
        db.drop_all()


def _create_order():
    user = db.session.query(User).filter_by(email="customer@example.com").one()
    product = db.session.query(Product).one()
    order = Order(
        user_id=user.id,
        order_number="ORD-000001",
        total_amount=3000000,
        status="confirmed",
        customer_name="Customer Name",
        customer_email="customer@example.com",
        customer_phone="08012345678",
        shipping_address="12 Test Street",
        shipping_city="Port Harcourt",
        shipping_state="Rivers",
        shipping_country="Nigeria",
    )
    db.session.add(order)
    db.session.flush()
    db.session.add(
        OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            quantity=2,
            unit_price=1500000,
            subtotal=3000000,
        )
    )
    db.session.commit()
    return order


def test_send_order_confirmation_posts_expected_mailgun_payload(app, monkeypatch):
    with app.app_context():
        order = _create_order()
        captured = {}

        class FakeResponse:
            def raise_for_status(self):
                captured["raised"] = True

        def fake_post(url, **kwargs):
            captured["url"] = url
            captured["kwargs"] = kwargs
            return FakeResponse()

        monkeypatch.setattr(mail_service.requests, "post", fake_post)

        assert mail_service.send_order_confirmation(order) is True

        assert captured["url"] == "https://api.mailgun.net/v3/mg.example.com/messages"
        assert captured["kwargs"]["auth"] == ("api", "test-api-key")
        assert captured["kwargs"]["data"]["to"] == "customer@example.com"
        assert captured["kwargs"]["data"]["subject"] == "Order confirmation - ORD-000001"
        assert "Test Shirt" in captured["kwargs"]["data"]["text"]
        assert "Quantity: 2" in captured["kwargs"]["data"]["text"]
        assert "₦15,000.00" in captured["kwargs"]["data"]["text"]
        assert "₦30,000.00" in captured["kwargs"]["data"]["text"]
        assert "confirmed" in captured["kwargs"]["data"]["html"]


def test_mailgun_failure_does_not_raise_or_rollback_order(app, monkeypatch):
    with app.app_context():
        order = _create_order()

        def fake_post(*args, **kwargs):
            raise mail_service.requests.RequestException("Mailgun unavailable")

        monkeypatch.setattr(mail_service.requests, "post", fake_post)

        assert mail_service.send_order_confirmation(order) is False
        assert db.session.query(Order).filter_by(order_number="ORD-000001").one()


def test_mailgun_missing_configuration_skips_send(app, monkeypatch):
    with app.app_context():
        order = _create_order()
        app.config["MAILGUN_API_KEY"] = None
        called = False

        def fake_post(*args, **kwargs):
            nonlocal called
            called = True

        monkeypatch.setattr(mail_service.requests, "post", fake_post)

        assert mail_service.send_order_confirmation(order) is False
        assert called is False
