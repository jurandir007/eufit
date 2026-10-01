# EUFit/app/routers/scale/services.py
from datetime import datetime
from app.extensions import db
from app.routers.scale.models import ScaleRecord


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_str_comb(gordura, musculo, basal, idade, viceral) -> str:
    """Cria a 'digital' de campos ausentes. '0' = registo completo."""
    s = ""
    if gordura  is None: s += "f"
    if musculo  is None: s += "m"
    if basal    is None: s += "b"
    if idade    is None: s += "a"
    if viceral  is None: s += "v"
    return s if s else "0"


# ---------------------------------------------------------------------------
# ML Predictor (sklearn · regressão linear · cold-start seguro)
# ---------------------------------------------------------------------------

def _predict_missing(user_id: int, peso: float, gordura: float, viceral: float) -> dict:
    """
    Tenta prever musculo / basal / idade via regressão linear treinada
    com o histórico do próprio utilizador.

    Regras de segurança:
    - Mínimo 5 registos completos para treinar (cold-start).
    - Valores negativos são clipados para 0.
    - Exceções são capturadas silenciosamente — retorna {} em caso de falha.
    """
    try:
        import pandas as pd
        from sklearn.linear_model import LinearRegression

        records = (
            ScaleRecord.query
            .filter_by(fk_user_id=user_id)
            .all()
        )

        data = [
            {
                "peso":    r.peso,
                "gordura": r.gordura,
                "viceral": r.viceral,
                "musculo": r.musculo,
                "basal":   r.basal,
                "idade":   r.idade,
            }
            for r in records
        ]

        df = pd.DataFrame(data)
        X_cols = ["peso", "gordura", "viceral"]
        y_cols = ["musculo", "basal", "idade"]
        df_clean = df[X_cols + y_cols].dropna()

        if len(df_clean) < 5:
            return {}

        X = df_clean[X_cols]
        preds = {}
        input_row = pd.DataFrame([[peso, gordura, viceral]], columns=X_cols)

        for target in y_cols:
            model = LinearRegression()
            model.fit(X, df_clean[target])
            val = float(model.predict(input_row)[0])
            preds[target] = round(max(0.0, val), 2)

        if "idade" in preds:
            preds["idade"] = int(round(preds["idade"]))

        return preds

    except Exception as exc:
        print(f"[scale.services] ML prediction skipped: {exc}")
        return {}


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_record(user_id: int, peso: float, gordura: float, viceral: float,
                  musculo=None, basal=None, idade=None) -> ScaleRecord:
    """
    Insere novo registo de pesagem.
    Campos opcionais (musculo, basal, idade) são preenchidos por ML
    se o utilizador não os fornecer e já houver histórico suficiente.
    """
    if musculo is None or basal is None or idade is None:
        preds = _predict_missing(user_id, peso, gordura, viceral)
        if musculo is None: musculo = preds.get("musculo")
        if basal   is None: basal   = preds.get("basal")
        if idade   is None: idade   = preds.get("idade")

    str_comb = _build_str_comb(gordura, musculo, basal, idade, viceral)

    record = ScaleRecord(
        fk_user_id=user_id,
        carimbo=datetime.now(),
        peso=peso,
        gordura=gordura,
        viceral=viceral,
        musculo=musculo,
        basal=basal,
        idade=idade,
        str_comb=str_comb,
    )
    db.session.add(record)
    db.session.commit()
    return record


def get_history(user_id: int, limit: int | None = None):
    """Histórico do utilizador, do mais recente para o mais antigo."""
    q = (
        ScaleRecord.query
        .filter_by(fk_user_id=user_id)
        .order_by(ScaleRecord.carimbo.desc())
    )
    return q.limit(limit).all() if limit else q.all()


def get_record(record_id: int, user_id: int) -> ScaleRecord | None:
    """Devolve um registo específico (só do próprio utilizador)."""
    return ScaleRecord.query.filter_by(id=record_id, fk_user_id=user_id).first()


def update_record(record_id: int, user_id: int, **fields) -> bool:
    """Actualiza campos de um registo existente."""
    record = get_record(record_id, user_id)
    if not record:
        return False
    for key, val in fields.items():
        if hasattr(record, key):
            setattr(record, key, val)
    record.str_comb = _build_str_comb(
        record.gordura, record.musculo, record.basal, record.idade, record.viceral
    )
    db.session.commit()
    return True


def delete_record(record_id: int, user_id: int) -> bool:
    """Apaga um registo (só do próprio utilizador)."""
    record = get_record(record_id, user_id)
    if not record:
        return False
    db.session.delete(record)
    db.session.commit()
    return True


def get_chart_data(user_id: int, days: int = 90) -> list[dict]:
    """
    Devolve os registos dos últimos N dias formatados para o Chart.js.
    Ordenados do mais antigo para o mais recente (eixo temporal crescente).
    """
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    records = (
        ScaleRecord.query
        .filter_by(fk_user_id=user_id)
        .filter(ScaleRecord.carimbo >= cutoff)
        .order_by(ScaleRecord.carimbo.asc())
        .all()
    )
    return [
        {
            "date":    r.carimbo.strftime("%Y-%m-%d"),
            "peso":    r.peso,
            "gordura": r.gordura,
            "musculo": r.musculo,
            "viceral": r.viceral,
            "basal":   r.basal,
            "idade":   r.idade,
        }
        for r in records
    ]
