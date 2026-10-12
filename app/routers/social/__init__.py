# EUFit/app/routers/social/__init__.py
from flask import Blueprint

social_bp = Blueprint(
    "social",
    __name__,
    url_prefix="/social",
    template_folder="../../templates/social",
)

from app.routers.social import routes  # noqa
