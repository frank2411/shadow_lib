from functools import wraps

from flask import g, request
from flask_restful import abort

from shadow_lib.models import Token


def check_bearer_token(fn):
    """Decorator that checks if authorization header is present and validates token"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("authorization", None)

        if not auth_header:
            abort(403, message="Missing Authorization Header")

        auth_header = auth_header.split(" ")

        error_msg = "Bad {} header. Expected value '{} <API_KEY>'".format(
            "Authorization", "Bearer"
        )

        if len(auth_header) != 2:
            abort(403, message=error_msg)

        if auth_header[0] != "Bearer":
            abort(403, message=error_msg)

        return fn(*args, **kwargs)

    return wrapper


# Modify this decorator accordingly to your auth flow
def authenticate_user(fn):
    """Decorator that check token against the DB and then set the current user for the application"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("authorization", None)
        auth_header = auth_header.split(" ")
        token = auth_header[1]
        Token.set_current_user(token)
        return fn(*args, **kwargs)

    return wrapper


def redirect_if_not_superadmin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.current_user.role.value != "superadmin":
            abort(403, message="Access forbidden")
        return fn(*args, **kwargs)

    return wrapper
