import datetime
import secrets
import string
import re
from urllib.parse import urlparse

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.routers.url_shortener import shortener_bp
from app.routers.url_shortener.models import ShortenedUrl, UrlClick


RESERVED_SLUGS = {
    "login",
    "logout",
    "google-login",
    "google-auth",
    "guest",
    "dashboard",
    "vaping",
    "scale",
    "social",
    "static",
    "sobre",
    "shortener",
    "url",
}


def generate_unique_code(length=6) -> str:
    characters = string.ascii_letters + string.digits
    for _ in range(10):
        code = "".join(secrets.choice(characters) for _ in range(length))
        if not ShortenedUrl.query.filter_by(code=code).first() and code.lower() not in RESERVED_SLUGS:
            return code
    raise RuntimeError("Could not generate a unique code. Please try again.")


def clean_slug(slug: str) -> str:
    slug = slug.strip().lower()
    slug = re.sub(r"[^a-zA-Z0-9-_]", "", slug)
    return slug


def get_client_ip() -> str:
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or ""


def cleanup_expired_urls():
    """Remove expired URLs from database."""
    now = datetime.datetime.utcnow()
    expired_urls = ShortenedUrl.query.filter(
        ShortenedUrl.expires_at.isnot(None),
        ShortenedUrl.expires_at <= now,
    ).all()
    if expired_urls:
        for url in expired_urls:
            db.session.delete(url)
        db.session.commit()


@shortener_bp.route("/shortener", methods=["GET", "POST"])
@login_required
def index():
    cleanup_expired_urls()

    now = datetime.datetime.utcnow()

    if request.method == "POST":
        original_url = request.form.get("original_url", "").strip()
        custom_slug = request.form.get("custom_slug", "").strip()

        # URL validation
        if not original_url:
            flash("Please provide a valid URL to shorten.", "error")
            return redirect(url_for("shortener.index"))

        parsed = urlparse(original_url)
        if not parsed.scheme:
            original_url = "https://" + original_url
            parsed = urlparse(original_url)

        if not parsed.netloc:
            flash("The provided URL is invalid.", "error")
            return redirect(url_for("shortener.index"))

        # User quota rules
        if current_user.is_guest:
            # Guest: max 1 active link
            existing_count = ShortenedUrl.query.filter_by(user_id=current_user.id).count()
            if existing_count >= 1:
                flash(
                    "Guest limit reached: Guest users can only have 1 active shortened link at a time. "
                    "Wait for it to expire (15 min) or delete it to create a new one.",
                    "error",
                )
                return redirect(url_for("shortener.index"))
            expires_at = now + datetime.timedelta(minutes=15)
        else:
            # Authenticated user: max 10 links per day
            today_start = datetime.datetime(now.year, now.month, now.day)
            links_today = ShortenedUrl.query.filter(
                ShortenedUrl.user_id == current_user.id,
                ShortenedUrl.created_at >= today_start,
            ).count()

            if links_today >= 10:
                flash("Daily limit reached: You have already created 10 links today. Please try again tomorrow.", "error")
                return redirect(url_for("shortener.index"))
            expires_at = None

        # Custom code or auto-generation
        if custom_slug:
            code = clean_slug(custom_slug)
            if not code or len(code) < 3:
                flash("Custom code must have at least 3 characters (letters, numbers, '-' or '_').", "error")
                return redirect(url_for("shortener.index"))
            if code in RESERVED_SLUGS:
                flash("This alias is reserved by the system. Please choose another one.", "error")
                return redirect(url_for("shortener.index"))
            if ShortenedUrl.query.filter_by(code=code).first():
                flash("This alias is already taken. Please choose another one.", "error")
                return redirect(url_for("shortener.index"))
        else:
            code = generate_unique_code()

        new_short = ShortenedUrl(
            user_id=current_user.id,
            original_url=original_url,
            code=code,
            expires_at=expires_at,
        )
        db.session.add(new_short)
        db.session.commit()

        flash("URL shortened successfully!", "success")
        return redirect(url_for("shortener.index"))

    # GET: List user's URLs
    user_urls = ShortenedUrl.query.filter_by(user_id=current_user.id).order_by(ShortenedUrl.created_at.desc()).all()

    # Quota calculations
    today_start = datetime.datetime(now.year, now.month, now.day)
    urls_created_today = (
        ShortenedUrl.query.filter(
            ShortenedUrl.user_id == current_user.id,
            ShortenedUrl.created_at >= today_start,
        ).count()
        if not current_user.is_guest
        else len(user_urls)
    )

    return render_template(
        "shortener/index.html",
        urls=user_urls,
        urls_created_today=urls_created_today,
        now=now,
    )


@shortener_bp.route("/shortener/delete/<int:url_id>", methods=["POST"])
@login_required
def delete(url_id: int):
    short_url = ShortenedUrl.query.filter_by(id=url_id, user_id=current_user.id).first()
    if not short_url:
        flash("Link not found or permission denied.", "error")
        return redirect(url_for("shortener.index"))

    db.session.delete(short_url)
    db.session.commit()
    flash("Shortened link successfully deleted.", "info")
    return redirect(url_for("shortener.index"))


@shortener_bp.route("/<string:code>")
def redirect_to_url(code: str):
    """Direct root redirect route."""
    if code.lower() in RESERVED_SLUGS:
        abort(404)

    short_url = ShortenedUrl.query.filter_by(code=code).first()

    if not short_url:
        abort(404)

    # Check expiration
    if short_url.is_expired:
        db.session.delete(short_url)
        db.session.commit()
        return render_template("shortener/expired.html", code=code), 410

    # Track click and analytics
    short_url.clicks_count = (short_url.clicks_count or 0) + 1
    short_url.last_accessed_at = datetime.datetime.utcnow()

    click_log = UrlClick(
        shortened_url_id=short_url.id,
        ip_address=get_client_ip(),
        user_agent=request.headers.get("User-Agent", "")[:500],
    )
    db.session.add(click_log)
    db.session.commit()

    return redirect(short_url.original_url)
