# app/routers/main/routes.py
from flask import redirect, url_for, render_template
from flask_login import current_user
from app.routers.main import main_bp


@main_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@main_bp.route("/sobre")
def about():
    return render_template("main/index.html")
