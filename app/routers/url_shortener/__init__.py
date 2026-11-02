from flask import Blueprint

shortener_bp = Blueprint(
    "shortener",
    __name__,
    template_folder="../../templates/shortener",
)

from app.routers.url_shortener import routes  # noqa
