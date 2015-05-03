from functools import wraps

from flask import request
from flask.ext.restful import abort
from flask.ext.stormpath import user

def role_required(func):
    """
    Check if user has specified role for this sub page
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        role = request.view_args.get('location')
        groups = [g.group.name for g in user.group_memberships]
        if groups is None or role not in groups:
            abort(403, message='"%s" role required' % role)
        return func(*args, **kwargs)
    return wrapped
