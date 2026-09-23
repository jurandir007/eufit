from flask import render_template
from flask_login import login_required, current_user
from app.routers.dashboard import dashboard_bp


@dashboard_bp.route("/")
@login_required
def home():
    return render_template("dashboard/home.html", user=current_user)
