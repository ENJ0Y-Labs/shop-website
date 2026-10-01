import pytest

from backend.app import create_app
from backend.app.extensions import db


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


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_creates_user_and_session(client, app):
    response = client.post("/api/auth/register", json={
        "email": "Noble@example.com",
        "password": "password123",
        "name": "Noble",
    })
    assert response.status_code == 201
    assert response.json["user"]["email"] == "noble@example.com"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json["user"]["name"] == "Noble"


def test_duplicate_email_is_rejected(client):
    payload = {"email": "user@example.com", "password": "password123", "name": "User"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_login_and_logout(client):
    payload = {"email": "user@example.com", "password": "password123", "name": "User"}
    client.post("/api/auth/register", json=payload)

    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401

    response = client.post("/api/auth/login", json={
        "email": "USER@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert client.get("/api/auth/me").status_code == 200


def test_invalid_login_is_rejected(client):
    client.post("/api/auth/register", json={
        "email": "user@example.com",
        "password": "password123",
        "name": "User",
    })
    response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
