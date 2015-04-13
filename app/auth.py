from functools import wraps

from flask import session, request
from flask.ext.restful import abort

def login_required(func):
    """
    Check if user is logged in
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('username'):
            abort(401)
        return func(*args, **kwargs)
    return wrapper

def role_required(func):
    """
    Check if user has specified role for this sub page
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        role = request.view_args.get('location')
        session_roles = session.get('roles')
        if session_roles is None or not role in session_roles:
            abort(403, message='"%s" role required' % role)
        return func(*args, **kwargs)
    return wrapped
