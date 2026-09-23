"""Hash, tokens e decorators auxiliares."""
from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(role: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or getattr(current_user, "role", None) != role:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
