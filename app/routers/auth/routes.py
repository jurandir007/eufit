# EUFit/app/routers/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from app.extensions import oauth, db
from app.routers.auth.models import User
from app.routers.auth import auth_bp
from app.routers.auth.forms import LoginForm, RegisterForm


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login efetuado com sucesso!", "success")
            return redirect(url_for("dashboard.home"))
        flash("E-mail ou palavra-passe incorretos.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/google-login")
def google_login():
    redirect_uri = url_for("auth.google_auth", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/google-auth")
def google_auth():
    token = oauth.google.authorize_access_token()
    user_info = token.get("userinfo")
    
    if not user_info:
        flash("Falha na autenticação com o Google.", "danger")
        return redirect(url_for("auth.login"))

    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name")

    # Verificar se o utilizador já existe pelo google_id ou pelo e-mail
    user = User.query.filter_by(google_id=google_id).first()
    
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            # Se o utilizador já existe com o e-mail mas sem o google_id associado
            user.google_id = google_id
            user.name = name or user.name
            db.session.commit()
        else:
            # Criar novo utilizador via Google
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                password_hash=None
            )
            db.session.add(user)
            db.session.commit()

    # Iniciar sessão com Flask-Login
    login_user(user)
    flash("Login efetuado com sucesso!", "success")
    return redirect(url_for("dashboard.home"))
    
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Este e-mail já está registado.", "danger")
            return redirect(url_for("auth.register"))

        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registo efetuado com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Sessão terminada.", "success")
    return redirect(url_for("main.index"))
