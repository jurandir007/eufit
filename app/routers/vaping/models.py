# EUFit/app/routers/vaping/models.py
from app.extensions import db
from app.routers.auth.models import User  # noqa — garante que o User está registado


class RecordVape(db.Model):
    __tablename__ = "record_vape"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    puff_count = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
    )

    user = db.relationship(
        User,
        backref=db.backref("vape_records", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<RecordVape {self.id} - {self.puff_count} puffs>"
