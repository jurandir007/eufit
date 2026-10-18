"""
Seed script to create and populate 3 demo visitor profiles in the Neon database:
1. Iniciante (< 50 registros)  -> 25 registros de Scale, 15 de Vape
2. Pleno (50 a 300 registros)  -> 120 registros de Scale, 60 de Vape
3. Fiel (> 300 registros)      -> 350 registros de Scale, 100 de Vape
"""
import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.routers.auth.models import User
from app.routers.scale.models import ScaleRecord
from app.routers.scale.services import _build_str_comb
from app.routers.vaping.models import RecordVape


DEMO_PROFILES = [
    {
        "email": "demo_iniciante@eufit.internal",
        "name": "Visitante Iniciante",
        "google_id": "guest_iniciante",
        "scale_count": 25,
        "vape_count": 15,
        "start_weight": 82.5,
        "end_weight": 79.8,
        "start_fat": 22.0,
        "end_fat": 19.5,
        "start_visceral": 9.0,
        "end_visceral": 8.0,
        "start_muscle": 34.5,
        "end_muscle": 36.2,
        "start_basal": 1750,
        "end_basal": 1720,
        "start_age": 32,
        "end_age": 30,
        "vape_start": 260,
        "vape_end": 170,
    },
    {
        "email": "demo_pleno@eufit.internal",
        "name": "Visitante Pleno",
        "google_id": "guest_pleno",
        "scale_count": 120,
        "vape_count": 60,
        "start_weight": 88.0,
        "end_weight": 78.4,
        "start_fat": 26.5,
        "end_fat": 18.2,
        "start_visceral": 11.0,
        "end_visceral": 7.0,
        "start_muscle": 32.0,
        "end_muscle": 38.0,
        "start_basal": 1860,
        "end_basal": 1710,
        "start_age": 38,
        "end_age": 31,
        "vape_start": 380,
        "vape_end": 110,
    },
    {
        "email": "demo_fiel@eufit.internal",
        "name": "Visitante Fiel",
        "google_id": "guest_fiel",
        "scale_count": 350,
        "vape_count": 100,
        "start_weight": 96.0,
        "end_weight": 76.5,
        "start_fat": 31.0,
        "end_fat": 16.5,
        "start_visceral": 13.0,
        "end_visceral": 6.0,
        "start_muscle": 30.5,
        "end_muscle": 39.5,
        "start_basal": 1950,
        "end_basal": 1690,
        "start_age": 42,
        "end_age": 29,
        "vape_start": 500,
        "vape_end": 0,
    },
]


def seed_profiles():
    app = create_app()
    with app.app_context():
        now = datetime.now()
        random.seed(42)  # determinístico

        for prof in DEMO_PROFILES:
            user = User.query.filter_by(email=prof["email"]).first()
            if not user:
                user = User(
                    email=prof["email"],
                    name=prof["name"],
                    google_id=prof["google_id"],
                )
                db.session.add(user)
                db.session.flush()
                print(f"Created user: {user.name} (id={user.id})")
            else:
                user.name = prof["name"]
                user.google_id = prof["google_id"]
                print(f"User already exists: {user.name} (id={user.id})")

            # Remove registros existentes para regenerar de forma limpa
            ScaleRecord.query.filter_by(fk_user_id=user.id).delete()
            RecordVape.query.filter_by(user_id=user.id).delete()
            db.session.flush()

            # Gerar registros de Scale
            count = prof["scale_count"]
            for i in range(count):
                # Do mais antigo ao mais recente
                frac = i / max(1, count - 1)
                days_ago = count - 1 - i
                carimbo = now - timedelta(days=days_ago, hours=random.randint(6, 9), minutes=random.randint(0, 59))

                # Interpolação linear com pequeno ruído natural
                noise_peso = random.uniform(-0.4, 0.4)
                peso = round(prof["start_weight"] + (prof["end_weight"] - prof["start_weight"]) * frac + noise_peso, 1)

                noise_fat = random.uniform(-0.3, 0.3)
                gordura = round(prof["start_fat"] + (prof["end_fat"] - prof["start_fat"]) * frac + noise_fat, 1)

                viceral = round(prof["start_visceral"] + (prof["end_visceral"] - prof["start_visceral"]) * frac, 1)

                # Opcionais com chance de ausência em alguns dias para simular entradas manuais reais
                has_opt = random.random() > 0.15
                if has_opt:
                    noise_mus = random.uniform(-0.3, 0.3)
                    musculo = round(prof["start_muscle"] + (prof["end_muscle"] - prof["start_muscle"]) * frac + noise_mus, 1)
                    basal = round(prof["start_basal"] + (prof["end_basal"] - prof["start_basal"]) * frac + random.uniform(-15, 15))
                    idade = round(prof["start_age"] + (prof["end_age"] - prof["start_age"]) * frac)
                else:
                    musculo = None
                    basal = None
                    idade = None

                str_comb = _build_str_comb(gordura, musculo, basal, idade, viceral)

                rec = ScaleRecord(
                    fk_user_id=user.id,
                    carimbo=carimbo,
                    peso=peso,
                    gordura=gordura,
                    viceral=viceral,
                    musculo=musculo,
                    basal=basal,
                    idade=idade,
                    str_comb=str_comb,
                )
                db.session.add(rec)

            # Gerar registros de Vape
            v_count = prof["vape_count"]
            for i in range(v_count):
                frac = i / max(1, v_count - 1)
                days_ago = v_count - 1 - i
                carimbo = now - timedelta(days=days_ago, hours=random.randint(18, 22))

                puffs = int(max(0, round(prof["vape_start"] + (prof["vape_end"] - prof["vape_start"]) * frac + random.uniform(-15, 15))))
                v_rec = RecordVape(
                    user_id=user.id,
                    recorded_at=carimbo,
                    puff_count=puffs,
                )
                db.session.add(v_rec)

            db.session.commit()
            print(f"Seeded {prof['name']}: {count} ScaleRecords, {v_count} RecordVapes")

        print("All demo profiles successfully seeded!")


if __name__ == "__main__":
    seed_profiles()
