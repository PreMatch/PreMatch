import sqlite3
import flask
import re
import atexit
import database
from teachers import teachers
from google_auth import *

PERIODS = list(map(chr, range(65, 73)))

def empty(string):
    return str(string).strip() == ''

def missing_form_field(key):
    return key not in flask.request.form or empty(flask.request.form[key])

app = flask.Flask(__name__)

@app.route('/')
def frontpage():
    return flask.render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    return flask.render_template('login.html')

@app.route('/edit', methods=['POST'])
def do_edit():
    # POST form will contain: id_token
    if missing_form_field('id_token'):
        return 'Missing value for id_token', 400
    try:
        token = flask.request.form['id_token']
        handle, name = validate_token_for_info(token)
        schedule = database.user_schedule(handle)
        return flask.render_template('edit.html', token=token, name=name, schedule=schedule, teachers=teachers)
    except Exception as e:
        return flask.render_template('auth_failed.html', error=str(e))

@app.route('/update', methods=['POST'])
def do_update():
    for key in ['id_token'] + PERIODS:
        if missing_form_field(key):
            return "Missing value for {}".format(key), 400
    for key in PERIODS:
        if flask.request.form[key] not in teachers:
            return "Unknown teacher: {}".format(flask.request.form[key]), 400
    try:
        # form will contain: id_token, A, B, ..., H
        periods = list(map(flask.request.form.get, PERIODS))
        handle, name = validate_token_for_info(flask.request.form['id_token'])

        if database.handle_exists(handle):
            database.update_schedule(handle, periods)
            return 'Updated with great success'
        else:
            database.add_schedule(handle, name, periods)
            return 'Added with great success'
    except Exception as e:
        return flask.render_template('update_failed.html', error=str(e)), 500

@app.route('/roster/<period>/<teacher>')
def show_roster(period, teacher):
    if period not in PERIODS:
        return 'Invalid period: ' + period, 400
    if teacher not in teachers:
        return 'Invalid teacher: ' + teacher, 400

    roster = database.class_roster(period, teacher)
    if len(roster) == 0:
        return 'Empty or nonexistent class'

    return flask.render_template('roster.html', period=period, teacher=teacher, roster=roster)

@app.route('/search')
def do_search():
    query = flask.request.args.get('query')
    if query is None:
        return flask.render_template('search-new.html')
    
    results = database.search_user(str(query))
    return flask.render_template('search-result.html', results=results)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.commit()
        db.close()