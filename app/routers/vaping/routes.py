# EUFit/app/routers/vaping/routes.py
from flask import render_template
from flask_login import login_required, current_user
from app.routers.vaping import vaping_bp


@vaping_bp.route("/")
@login_required
def home():
    return render_template("vaping/home.html", user=current_user)
