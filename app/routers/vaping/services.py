# EUFit/app/routers/vaping/services.py
from datetime import datetime, timedelta
from app.extensions import db
from app.routers.vaping.models import RecordVape

WINDOW_DAYS = 15


def create_vape_record(user_id, puff_count):
    """Insere um novo registo. Data/hora automática pelo Neon."""
    try:
        record = RecordVape(user_id=user_id, puff_count=puff_count)
        db.session.add(record)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        raise


def update_vape_record(record_id, user_id, puff_count, recorded_at):
    try:
        record = RecordVape.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return False
        record.puff_count = puff_count
        record.recorded_at = recorded_at
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        raise


def delete_vape_record(record_id, user_id):
    """Apaga um registo (só do próprio user)."""
    try:
        record = RecordVape.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return False
        db.session.delete(record)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        raise


def get_history(user_id):
    """Todos os registos do user, do mais recente para o mais antigo."""
    return (
        RecordVape.query
        .filter_by(user_id=user_id)
        .order_by(RecordVape.recorded_at.desc())
        .all()
    )


def get_daily_avg(user_id, days=WINDOW_DAYS):
    """
    Média móvel de puffs/dia.

    Regras:
    - Janela máxima: 15 dias
    - Contas novas: divisor = dias desde o primeiro registo (+1)
    - Sem registos: devolve 0
    - Dias sem registo contam como 0 na soma
    """
    now = datetime.utcnow()
    start = now - timedelta(days=days)

    records = (
        RecordVape.query
        .filter(RecordVape.user_id == user_id)
        .filter(RecordVape.recorded_at >= start)
        .filter(RecordVape.recorded_at < now)
        .all()
    )

    if not records:
        return 0

    total = sum(r.puff_count for r in records)

    # Divisor: dias desde o primeiro registo, com teto máximo de 15
    first_record = (
        RecordVape.query
        .filter_by(user_id=user_id)
        .order_by(RecordVape.recorded_at.asc())
        .first()
    )

    if first_record:
        dias_de_vida = (now - first_record.recorded_at).days + 1
        divisor = min(days, dias_de_vida)
    else:
        divisor = days

    return total / divisor if divisor > 0 else 0
    
def get_record(record_id, user_id):
    """Vai buscar 1 registo específico (só do próprio user)."""
    return RecordVape.query.filter_by(id=record_id, user_id=user_id).first()
