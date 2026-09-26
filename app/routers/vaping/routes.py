# EUFit/app/routers/vaping/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.routers.vaping import vaping_bp
from app.routers.vaping.forms import LogForm
from app.routers.vaping import services


@vaping_bp.route("/")
@login_required
def home():
    form = LogForm()
    avg = services.get_daily_avg(current_user.id)
    history = services.get_history(current_user.id)[:5]   # últimos 5 no dashboard
    return render_template(
        "vaping/home.html",
        user=current_user,
        form=form,
        avg=avg,
        history=history,
    )


@vaping_bp.route("/log", methods=["POST"])
@login_required
def log():
    form = LogForm()
    if form.validate_on_submit():
        services.create_vape_record(current_user.id, form.puff_count.data)
        flash("Record saved.", "success")
    else:
        flash("Invalid value.", "error")
    return redirect(url_for("vaping.home"))


@vaping_bp.route("/history")
@login_required
def history():
    records = services.get_history(current_user.id)
    return render_template("vaping/history.html", user=current_user, history=records)


@vaping_bp.route("/edit/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit(record_id):
    record = services.get_record(record_id, current_user.id)
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("vaping.history"))

    form = LogForm(obj=record)
    if form.validate_on_submit():
        services.update_vape_record(record_id, current_user.id, form.puff_count.data)
        flash("Record updated.", "success")
        return redirect(url_for("vaping.history"))

    return render_template("vaping/edit.html", user=current_user, record=record, form=form)


@vaping_bp.route("/delete/<int:record_id>", methods=["POST"])
@login_required
def delete(record_id):
    ok = services.delete_vape_record(record_id, current_user.id)
    if ok:
        flash("Record deleted.", "success")
    else:
        flash("Record not found.", "error")
    return redirect(url_for("vaping.history"))


@vaping_bp.route("/api/daily-avg")
@login_required
def api_daily_avg():
    avg = services.get_daily_avg(current_user.id)
    return jsonify({"daily_avg": round(avg, 2), "window_days": services.WINDOW_DAYS})
