from flask import *
import database
from auth import *
from teachers import teachers
from google_auth import validate_token_for_info

PERIODS = list(map(chr, range(65, 73)))


def empty(string):
    return str(string).strip() == ''


def missing_form_field(key):
    return key not in request.form or empty(request.form[key])


def error(code, message):
    return render_template('error.html', code=code, error=message), code


def json_success(message):
    return jsonify({'status': 'success', 'message': str(message)})


def json_failure(code, message):
    return jsonify({'status': 'failure', 'message': str(message)}), code


def error_not_logged_in():
    flash('You must be logged in to view this page.')
    return redirect('/')


app = Flask(__name__)
set_secret_key(app)


@app.route('/')
def front_page():
    return render_template('index.html')


@app.route('/about')
def show_about():
    return render_template('about.html')


@app.route('/home')
def show_home():
    handle = logged_handle()
    if handle is None:
        return error_not_logged_in()

    if not database.handle_exists(handle):
        return redirect('/add')

    schedule = database.user_schedule(handle)
    name = database.user_name(handle)
    return render_template('home.html', handle=handle, name=name, schedule=schedule, teachers=teachers)


# Relaying final redirect (after log-in) from originator of /login GET to /login POST
# 1. Originator sends user to /login?redirect=<desired_url>
# 2. login.html is rendered with redirect (template variable) set to the value above, or '' if there wasn't one
# 3. Form submission from login.html sends redirect as form key in POST form to /login
# 4. /login POST logic acknowledges URL and redirects the user to it upon success
@app.route('/login', methods=['GET', 'POST'])
def do_login():
    if request.method == 'GET':
        if logged_handle() is not None:
            flash('You are already logged in')
            return redirect(request.args.get('redirect', '/home'))
        return render_template('login.html', redirect=request.args.get('redirect', ''))

    # expected form argument: id_token, redirect (optional)
    if missing_form_field('id_token'):
        return error(400, 'Missing token from Google sign-in')

    try:
        handle, name = validate_token_for_info(request.form['id_token'])
        log_in(handle)

        flash('Logged in successfully as ' + name)
        default = '/home' if database.handle_exists(handle) else '/add?name=' + escape(name)

        if missing_form_field('redirect'):
            return redirect(default)
        return redirect(request.form.get('redirect', default))

    except ValueError as e:
        return error(400, 'Authentication failed: ' + str(e))


@app.route('/logout')
def do_logout():
    handle = logged_handle()
    if handle is None:
        return error(400, 'Cannot log out when not logged in')

    log_out()
    return render_template('logout.html')


@app.route('/user/<handle>', methods=['GET'])
def show_user(handle):
    if logged_handle() is None:
        return error_not_logged_in()

    if not database.handle_exists(handle):
        return error(404, 'No schedule exists for ' + str(handle))

    schedule = database.user_schedule(handle)
    name = database.user_name(handle)
    return render_template('user.html', schedule=schedule, name=name, handle=handle, teachers=teachers)


@app.route('/add', methods=['GET'])
def do_add():
    if logged_handle() is None:
        return error_not_logged_in()

    return render_template('add.html', teachers=teachers, name=request.args.get('name', ''))


@app.route('/update', methods=['POST'])
def do_update():
    # Form key existence check
    handle = logged_handle()
    if handle is None:
        return error_not_logged_in()

    if any(map(missing_form_field, PERIODS)):
        flash('One or more periods missing', 'error')
        return redirect('/home')

    # Teacher validity check
    new_schedule = list(map(request.form.get, PERIODS))
    for teacher in new_schedule:
        if teacher not in teachers:
            flash('Unknown teacher: ' + teacher, 'error')
            return redirect('/home')
    try:
        # Token validity check
        token = request.form['id_token']
        handle, name = validate_token_for_info(token)

        if database.handle_exists(handle):
            database.update_schedule(handle, new_schedule)
            flash('Schedule updated successfully')
        else:
            database.add_schedule(handle, name, new_schedule)
            flash('Schedule added successfully')

        return redirect('/home')
    except Exception as e:
        return error(500, str(e))


@app.route('/roster/<period>/<teacher>')
def show_roster(period, teacher):
    if logged_handle() is None:
        return error_not_logged_in()

    if period not in PERIODS:
        return error(400, 'Invalid period: ' + period)
    if teacher not in teachers:
        return error(400, 'Invalid teacher: ' + teacher)

    roster = database.class_roster(period, teacher)
    if len(roster) == 0:
        return error(400, 'Empty or nonexistent class')

    return render_template('roster.html', period=period, teacher=teacher, roster=roster)


@app.route('/search')
def do_search():
    if logged_handle() is None:
        return error_not_logged_in()

    query = request.args.get('query')
    if query is None:
        return render_template('search-new.html')

    results = database.search_user(str(query))
    return render_template('search-result.html', results=results)


@app.teardown_appcontext
def close_connection(_):
    db = getattr(g, '_database', None)
    if db is not None:
        db.commit()
        db.close()


if __name__ == "__main__":
    app.run()
