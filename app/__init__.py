from flask import Flask


def create_app():
    """Application factory."""
    app = Flask(__name__)

    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def home():
        return {
            "message": "Welcome to the Enterprise Student Record "
                       "& Academic Management Platform",
            "api": "/api/students",
            "status": "running",
        }, 200

    return app
