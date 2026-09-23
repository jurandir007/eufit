from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Routers (blueprints)
    from app.routers.main import main_bp
    from app.routers.auth import auth_bp
    from app.routers.dashboard import dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Handlers de erro
    from app.core import errors
    errors.register(app)

    return app
