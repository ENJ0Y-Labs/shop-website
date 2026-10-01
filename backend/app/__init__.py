import os

from flask import Flask
from sqlalchemy import text

from .config.settings import Config
from .extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    migrations_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "migrations")
    )
    migrate.init_app(app, db, directory=migrations_dir)

    from . import models  # noqa: F401

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/api/health/db")
    def database_health_check():
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}

    return app
