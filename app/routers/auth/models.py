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

    @property
    def is_guest(self) -> bool:
        return bool(self.email and self.email.endswith("@eufit.internal"))

    @property
    def guest_tier(self) -> str | None:
        if not self.is_guest:
            return None
        if "iniciante" in self.email:
            return "iniciante"
        elif "fiel" in self.email:
            return "fiel"
        return "pleno"

    @property
    def guest_tier_label(self) -> str:
        tier = self.guest_tier
        if tier == "iniciante":
            return "Iniciante (até 50 dados)"
        elif tier == "fiel":
            return "Fiel (+300 dados)"
        return "Pleno (50 a 300 dados)"


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
