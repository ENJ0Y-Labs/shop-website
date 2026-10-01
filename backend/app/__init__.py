from flask import Flask

from .config.settings import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    return app
