# EUFit/app/__init__.py
from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate, oauth
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    oauth.init_app(app)

    # Registo do cliente OAuth do Google
    oauth.register(
        name="google",
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    # Routers (blueprints)
    from app.routers.main import main_bp
    from app.routers.auth import auth_bp
    from app.routers.dashboard import dashboard_bp
    from app.routers.vaping import vaping_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vaping_bp)

    # Handlers de erro
    from app.core import errors
    errors.register(app)

    return app
