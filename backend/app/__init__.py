import os

from flask import Flask
from flask_cors import CORS
from flask_session import Session
from sqlalchemy import text

from .config.settings import Config
from .errors import register_error_handlers
from .extensions import db, migrate
from .services.google_oauth import init_google_oauth


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(
        app,
        db,
        directory=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "migrations")
        ),
    )
    Session(app)

    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
    )

    from . import models  # noqa: F401
    from .routes.auth import auth_bp
    from .routes.cart import cart_bp
    from .routes.products import products_bp
    from .routes.orders import orders_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    init_google_oauth(app)
    register_error_handlers(app)

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/api/health/db")
    def database_health_check():
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}

    return app
