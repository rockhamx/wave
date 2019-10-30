from functools import wraps
from flask import abort
from flask_login import current_user


def admin_require():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_administrator:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator
