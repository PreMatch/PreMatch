import os
from flask import session


def set_secret_key(app):
    app.secret_key = os.urandom(16)


def log_in(handle):
    session['handle'] = handle


def log_out():
    session.pop('handle', '')


def logged_handle():
    return session.get('handle', None)
