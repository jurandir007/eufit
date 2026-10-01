# EUFit/app/routers/scale/models.py
# Mapeia a tabela existente 'Eu_2016' do banco de dados Neon (2 027 registos).
# Os nomes das colunas são os originais do Google Forms/projeto antigo.
from app.extensions import db
from app.routers.auth.models import User  # noqa — garante que User está registado


class ScaleRecord(db.Model):
    __tablename__ = "Eu_2016"

    id          = db.Column("id",                   db.Integer,           primary_key=True, autoincrement=True)
    carimbo     = db.Column("Carimbo de data/hora", db.DateTime,          nullable=False)
    peso        = db.Column("Peso",                 db.Float,             nullable=False)
    gordura     = db.Column("Gordura",              db.Float,             nullable=False)
    viceral     = db.Column("viceral",              db.Float,             nullable=False)
    musculo     = db.Column("Musculo",              db.Float,             nullable=True)
    basal       = db.Column("basal",                db.Float,             nullable=True)
    idade       = db.Column("Idade",                db.Float,             nullable=True)
    str_comb    = db.Column("str_comb",             db.String(10),        nullable=True)
    fk_user_id  = db.Column(
        "fk_user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = db.relationship(
        User,
        backref=db.backref("scale_records", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<ScaleRecord {self.id} — {self.carimbo:%Y-%m-%d} {self.peso}kg>"
