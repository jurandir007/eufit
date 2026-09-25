#app/routers/auth/models.py
from flask_login import UserMixin
from app.extensions import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    google_id = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
