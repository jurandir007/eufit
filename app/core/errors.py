from flask import render_template


def register(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("base.html", message="404 — Página não encontrada"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("base.html", message="500 — Erro interno"), 500
