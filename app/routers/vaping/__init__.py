# EUFit/app/routers/vaping/__init__.py
from flask import Blueprint

vaping_bp = Blueprint(
    "vaping",
    __name__,
    url_prefix="/vaping",
    template_folder="../../templates/vaping",
)

from app.routers.vaping import routes  # noqa
