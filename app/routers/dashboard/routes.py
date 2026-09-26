from flask import render_template
from flask_login import current_user
from app.routers.dashboard import dashboard_bp


@dashboard_bp.route("/")
def home():
    return render_template("dashboard/home.html", user=current_user)
