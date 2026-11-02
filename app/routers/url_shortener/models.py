from app.extensions import db
from app.models.base import TimestampMixin
from app.routers.auth.models import User
import datetime


class ShortenedUrl(TimestampMixin, db.Model):
    __tablename__ = "shortened_urls"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    original_url = db.Column(db.Text, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    clicks_count = db.Column(db.Integer, default=0, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    last_accessed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship(
        User,
        backref=db.backref("shortened_urls", lazy=True, cascade="all, delete-orphan"),
    )

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<ShortenedUrl {self.code} -> {self.original_url[:30]}>"


class UrlClick(db.Model):
    __tablename__ = "url_clicks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shortened_url_id = db.Column(
        db.Integer,
        db.ForeignKey("shortened_urls.id", ondelete="CASCADE"),
        nullable=False,
    )
    clicked_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False,
    )
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)

    shortened_url = db.relationship(
        ShortenedUrl,
        backref=db.backref("clicks", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<UrlClick {self.id} for url {self.shortened_url_id}>"
