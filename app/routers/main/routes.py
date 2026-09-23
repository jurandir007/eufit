from flask import render_template
from app.routers.main import main_bp


@main_bp.route("/")
def index():
    return render_template("main/index.html")


@main_bp.route("/sobre")
def about():
    return render_template("main/index.html")
