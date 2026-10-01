# EUFit/app/routers/scale/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.routers.scale import scale_bp
from app.routers.scale.forms import LogForm, EditForm
from app.routers.scale import services


@scale_bp.route("/")
@login_required
def home():
    form    = LogForm()
    history = services.get_history(current_user.id, limit=5)
    latest  = history[0] if history else None
    return render_template(
        "scale/home.html",
        user=current_user,
        form=form,
        history=history,
        latest=latest,
    )


@scale_bp.route("/log", methods=["POST"])
@login_required
def log():
    form = LogForm()
    if form.validate_on_submit():
        try:
            services.create_record(
                user_id=current_user.id,
                peso=form.peso.data,
                gordura=form.gordura.data,
                viceral=form.viceral.data,
                musculo=form.musculo.data,
                basal=form.basal.data,
                idade=form.idade.data,
            )
            flash("Measurement saved.", "success")
        except Exception as exc:
            flash(f"Error saving record: {exc}", "error")
    else:
        flash("Invalid values. Check required fields.", "error")
    return redirect(url_for("scale.home"))


@scale_bp.route("/history")
@login_required
def history():
    records = services.get_history(current_user.id)
    return render_template("scale/history.html", user=current_user, history=records)


@scale_bp.route("/edit/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit(record_id):
    record = services.get_record(record_id, current_user.id)
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("scale.history"))

    form = EditForm(obj=record)
    # Pré-preenche carimbo no formato esperado pelo DateTimeLocalField
    if request.method == "GET":
        form.carimbo.data = record.carimbo

    if form.validate_on_submit():
        services.update_record(
            record_id, current_user.id,
            carimbo=form.carimbo.data,
            peso=form.peso.data,
            gordura=form.gordura.data,
            viceral=form.viceral.data,
            musculo=form.musculo.data,
            basal=form.basal.data,
            idade=form.idade.data,
        )
        flash("Record updated.", "success")
        return redirect(url_for("scale.history"))

    return render_template("scale/edit.html", user=current_user, record=record, form=form)


@scale_bp.route("/delete/<int:record_id>", methods=["POST"])
@login_required
def delete(record_id):
    ok = services.delete_record(record_id, current_user.id)
    flash("Record deleted." if ok else "Record not found.", "success" if ok else "error")
    return redirect(url_for("scale.history"))


@scale_bp.route("/api/chart-data")
@login_required
def api_chart_data():
    days = request.args.get("days", 90, type=int)
    return jsonify(services.get_chart_data(current_user.id, days=days))
