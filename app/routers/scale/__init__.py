# EUFit/app/routers/scale/__init__.py
from flask import Blueprint

scale_bp = Blueprint(
    "scale",
    __name__,
    url_prefix="/scale",
    template_folder="../../templates/scale",
)

from app.routers.scale import routes  # noqa
