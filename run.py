import sqlite3
import flask
import re
import atexit
import database
import json
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

@app.route('/user/<handle>', methods=['GET'])
def show_user(handle):
    if not database.handle_exists(handle):
        return '404 Page not Found: no such handle', 404
    schedule = database.user_schedule(handle)
    name = database.user_name(handle)
    return flask.render_template('user.html', schedule=schedule, name=name, handle=handle, teachers=teachers)

@app.route('/add', methods=['GET'])
def do_add():
    return flask.render_template('add.html', teachers=teachers)
    
@app.route('/update', methods=['POST'])
def do_update():
    # Form key existence check
    if missing_form_field('id_token'):
        return 'Missing value for id_token', 400
    if any(map(missing_form_field, PERIODS)):
        return 'One or more periods missing', 400
    
    # Teacher validity check
    new_schedule = list(map(flask.request.form.get, PERIODS))
    for teacher in new_schedule:
        if teacher not in teachers:
            return 'Unknown teacher: ' + teacher, 400
    try:
        # Token validity check
        token = flask.request.form['id_token']
        handle, name = validate_token_for_info(token)

        if database.handle_exists(handle):
            database.update_schedule(handle, new_schedule)
        else:
            database.add_schedule(handle, name, new_schedule)
        return '{"status": "success"}'
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

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