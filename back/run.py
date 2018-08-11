import sqlite3
import flask
import re
import atexit
import database
from teachers import teachers
from google_auth import *

PERIODS = list(map(chr, range(65, 73)))

app = flask.Flask(__name__)

@app.route('/login', methods=['GET'])
def login():
    return flask.render_template('login.html')

@app.route('/edit', methods=['POST'])
def do_edit():
    # POST form will contain: id_token
    try:
        handle, name = validate_token_for_info(flask.request.form['id_token'])
        schedule = database.user_schedule(handle)
        return flask.render_template('edit.html', handle=handle, name=name, schedule=schedule, teachers=teachers)
    except Exception as e:
        return flask.render_template('auth_failed.html', error=str(e))

@app.route('/update', methods=['POST'])
def do_update():
    # form will contain: id_token, handle, name, A, B, ..., H
    forms = flask.request.form
    handle = forms['handle']
    periods = list(map(lambda i: forms[i], PERIODS))

    if database.handle_exists(handle):
        database.update_schedule(handle, periods)
        return 'Updated with great success'
    try:
        database.add_schedule(handle, forms['name'], periods)
        return 'Added with great success'
    except Exception as e:
        return flask.render_template('update_failed.html', error=str(e))

@app.route('/roster/<period>/<teacher>')
def show_roster(period, teacher):
    if period not in PERIODS:
        return 'Invalid period: ' + period
    
    roster = database.class_roster(period, teacher)
    if len(roster) == 0:
        return 'Empty class'

    return flask.render_template('roster.html', period=period, teacher=teacher, roster=roster)
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.commit()
        db.close()