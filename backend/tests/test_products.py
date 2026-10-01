import uuid

import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Product


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
    SUPABASE_URL = "https://example.supabase.co"
    SUPABASE_STORAGE_BUCKET = "product-images"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        products = [
            Product(
                id=uuid.uuid4(),
                name="Alpha Shirt",
                description="Cotton shirt",
                price=1000000,
                category="Clothing",
                stock=10,
                variants={"size": ["S", "M", "L"]},
                image_url="products/alpha.jpg",
            ),
            Product(
                id=uuid.uuid4(),
                name="Beta Bag",
                description="Travel bag",
                price=2000000,
                category="Bags",
                stock=0,
            ),
            Product(
                id=uuid.uuid4(),
                name="Gamma Lamp",
                description="Desk lamp",
                price=500000,
                category="Home",
                stock=5,
            ),
        ]
        db.session.add_all(products)
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_list_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json["pagination"]["total"] == 3
    assert len(response.json["products"]) == 3


def test_search_and_category_filter(client):
    response = client.get("/api/products?search=shirt&category=clothing")
    assert response.status_code == 200
    assert [item["name"] for item in response.json["products"]] == ["Alpha Shirt"]


def test_sort_and_pagination(client):
    response = client.get("/api/products?sort=price_desc&page=1&per_page=2")
    assert response.status_code == 200
    assert [item["name"] for item in response.json["products"]] == ["Beta Bag", "Alpha Shirt"]
    assert response.json["pagination"]["has_next"] is True


def test_product_detail(client):
    product_id = Product.query.first().id
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json["product"]["name"] == "Alpha Shirt"
    assert response.json["product"]["variants"]["size"] == ["S", "M", "L"]
    assert response.json["product"]["image_url"] == "https://example.supabase.co/storage/v1/object/public/product-images/products/alpha.jpg"


def test_invalid_product_id(client):
    response = client.get("/api/products/not-a-uuid")
    assert response.status_code == 400
    assert response.json["error"]["code"] == "invalid_product_id"


def test_missing_product(client):
    response = client.get(f"/api/products/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json["error"]["code"] == "product_not_found"


def test_invalid_query_parameters(client):
    assert client.get("/api/products?sort=unknown").status_code == 400
    assert client.get("/api/products?page=0").status_code == 400
    assert client.get("/api/products?per_page=101").status_code == 400
