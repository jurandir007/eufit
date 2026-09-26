# EUFit/app/routers/auth/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.extensions import oauth, db
from app.routers.auth.models import User
from app.routers.auth import auth_bp


@auth_bp.route("/login", methods=["GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))
    return render_template("auth/login.html")


@auth_bp.route("/google-login")
def google_login():
    redirect_uri = url_for("auth.google_auth", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/google-auth")
def google_auth():
    token = oauth.google.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info:
        flash("Google authentication failed.", "danger")
        return redirect(url_for("auth.login"))

    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name")

    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
            user.name = name or user.name
            db.session.commit()
        else:
            user = User(
                email=email,
                name=name,
                google_id=google_id,
            )
            db.session.add(user)
            db.session.commit()

    login_user(user)
    flash("Login successful!", "success")
    return redirect(url_for("dashboard.home"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Session ended.", "success")
    return redirect(url_for("auth.login"))
