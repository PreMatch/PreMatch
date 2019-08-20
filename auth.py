import base64

from flask import session
from google.cloud import firestore


def set_secret_key(app):
    client = firestore.Client(project='prematch-db')
    app.secret_key = base64.b64decode(client.document('auth/key').get().get('encoded').encode())


def log_in(handle):
    session['handle'] = handle


def log_out():
    session.pop('handle', '')


def logged_handle():
    return session.get('handle', None)
