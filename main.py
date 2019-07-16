import requests
from flask import *

import discord
import database
import ahs_calendar
import traceback
from config import *
from urllib import parse
from auth import *
from google_auth import validate_token_for_info
from user import User, Reader


def default_home():
    return '/dashboard'


def empty(string):
    return str(string).strip() == ''


def missing_form_field(key):
    return key not in request.form or empty(request.form[key])


def error(code, message):
    return render_template('error.html', code=code, error=message), code


def error_not_logged_in():
    flash('You must be logged in to view this page.', 'error')
    return redirect('/login?redirect=' + escape(request.path))


def render_login_optional(template, **kwargs):
    return render_template(template, logged_in=logged_handle() is not None,
                           user=User.from_db(logged_handle()), **kwargs)


def error_no_own_schedule():
    flash('You need to enter your schedule first', 'error')
    return redirect('/update')


def error_private(handle):
    flash(f'The user {handle} has decided to make their schedule private')
    return redirect('/')


def should_countdown():
    return ahs_calendar.current_semester() is None and ahs_calendar.before_schedule_release()


app = Flask(__name__)
set_secret_key(app)


@app.before_request
def enforce_domain_https():
    url = parse.urlparse(request.url)
    is_http = 'prematch.org' in url.netloc.lower() and url.scheme == 'http'
    if 'appspot' in url.netloc or is_http:
        newurl = parse.ParseResult('https', 'prematch.org',
                                   url.path, url.params, url.query, url.fragment)
        return redirect(newurl.geturl(), code=301)


class ValidationError(Exception):
    def __init__(self, problem):
        self.problem = problem


def demand(truth, message):
    if not truth:
        raise ValidationError(message)


@app.errorhandler(ValidationError)
def validation_error_handler(err):
    return error(422, err.problem)


@app.route('/')
def front_page():
    return render_login_optional('index.html',
                                 schedule_count=database.schedule_count())


@app.route('/about')
def show_about():
    return render_login_optional('about.html')


@app.route('/about/discord')
def show_about_discord():
    return render_login_optional('about_discord.html')


@app.route('/about/app')
def show_about_app():
    return render_login_optional('about_app.html')


@app.route('/countdown')
def show_countdown():
    return render_login_optional('countdown.html')


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
            return redirect(request.args.get('redirect', default_home()))
        return render_template('login.html',
                               redirect=request.args.get('redirect', ''))

    # expected form argument: id_token, redirect (optional)
    if missing_form_field('id_token'):
        return error(422, 'Missing token from Google sign-in')

    try:
        handle, name = validate_token_for_info(request.form['id_token'])
        log_in(handle)
        user = User.from_db(handle)

        if user is not None and user.missing_some_lunch():
            flash('You are missing some lunch numbers. ' +
                  'To enter them, please visit the Update page.')
        else:
            flash('Successfully logged in as ' + name)

        default = default_home()

        if user is None:
            session['name'] = name
            default = '/update'

        if missing_form_field('redirect'):
            return redirect(default)
        return redirect(request.form.get('redirect', default))

    except ValueError as e:
        return error(403, 'Authentication failed: ' + str(e))


@app.route('/logout')
def do_logout():
    if logged_handle() is not None:
        flash('You were successfully logged out')

    log_out()
    return redirect('/')


@app.route('/user')
def show_self_current_semester():
    return show_user_current_semester(logged_handle())


@app.route('/user/<handle>')
def show_user_current_semester(handle):
    return show_user(handle, str(ahs_calendar.current_semester()))


@app.route('/user/<handle>/<semester>', methods=['GET'])
def show_user(handle, semester):
    own_handle = logged_handle()
    if own_handle is None:
        return error_not_logged_in()

    if should_countdown():
        return redirect('/countdown', code=307)

    target = User.from_db(handle)
    if target is None:
        if own_handle == handle:
            return error_no_own_schedule()
        return render_template('profile_not_found.html', bad_handle=handle)

    demand(semester in semesters, f'Invalid semester: {semester}')
    semester = int(semester)

    reader = Reader(own_handle)
    if not reader.can_read(target):
        return error_private(handle)

    return render_template('user.html', schedule=target.semester_mapping(semester), name=target.name,
                           handle=handle, teachers=teachers,
                           lunch_numbers=target.lunch_numbers(semester),
                           lunch_blocks=lunch_blocks,
                           semester=semester)


@app.route('/dashboard')
def show_own_dashboard_current_semester():
    return show_dashboard(logged_handle(), str(ahs_calendar.current_semester()))


@app.route('/dashboard/<semester_or_handle>')
def show_own_dashboard_current_semester_or_handle(semester_or_handle):
    if semester_or_handle in semesters:
        return show_dashboard(logged_handle(), semester_or_handle)
    else:
        return show_dashboard(semester_or_handle, str(ahs_calendar.current_semester()))


@app.route('/dashboard/<handle>/<semester>')
def show_dashboard(handle, semester):
    user_handle = logged_handle()
    if user_handle is None:
        return error_not_logged_in()

    if should_countdown():
        return redirect('/countdown', code=307)

    reader = Reader(user_handle)
    target = User.from_db(handle)
    if target is None:
        if user_handle == handle:
            return error_no_own_schedule()
        return render_template('profile_not_found.html', bad_handle=handle)

    demand(semester in semesters, f'Invalid semester: {semester}')
    semester = int(semester)

    if not reader.can_read(target):
        return error_private(handle)

    rosters = {}
    class_sizes = {}
    for period in periods:
        students = database.users_in_class(period, semester, target.teacher(period, semester))

        class_sizes[period] = len(students)
        rosters[period] = list(reader.read_entities(students))

    # Lunch rosters on dashboard not implemented
    # lunch_rosters = {}
    # for block in lunch_blocks:
    #     num = database.lunch_number(block, schedule[block])
    #     lunch_rosters[block] = database.lunch_roster(block, num) \
    #         if num is not None else None

    return render_template('dashboard.html',
                           handle=handle, name=target.name, schedule=target.semester_mapping(semester),
                           rosters=rosters, sizes=class_sizes,
                           semester=semester)


@app.route('/update', methods=['GET', 'POST'])
def do_update():
    handle = logged_handle()
    if handle is None:
        return error_not_logged_in()

    if request.method == 'GET':
        user = User.from_db(handle)

        if user is None and 'name' not in session:
            flash('Sorry, but you need to log in again', 'error')
            return redirect('/login')

        if should_countdown():
            return redirect('/countdown', code=307)

        if user is None:
            empty_lunch_numbers = {}
            for semester in semesters:
                for blk in lunch_blocks:
                    empty_lunch_numbers[blk + semester] = None
            return render_template('update.html',
                                   handle=handle,
                                   name=session.get('name'),
                                   schedule=None,
                                   teachers=teachers,
                                   lunch_periods=lunch_blocks, lunches=[1, 2, 3, 4],
                                   lunch_numbers=empty_lunch_numbers,
                                   user_public=False)
        else:
            return render_template('update.html',
                                   handle=handle,
                                   name=session.get('name', user.name),
                                   schedule=user.teachers,
                                   teachers=teachers,
                                   lunch_periods=lunch_blocks, lunches=[1, 2, 3, 4],
                                   lunch_numbers=user.full_lunch_mapping(),
                                   user_public=user.public)
    else:
        # Redirect path reading from args
        redirect_path = request.args.get('from', default_home())
        if empty(redirect_path):
            redirect_path = default_home()

        for required_field in all_block_keys():
            demand(not missing_form_field(required_field), f'Missing field {required_field}')

        # Teacher validity check
        new_schedule = dict(map(lambda x: (x, request.form.get(x)), all_block_keys()))
        for teacher in new_schedule.values():
            demand(teacher in teachers, f'Unknown teacher: {teacher}')

        # Read lunches (optional)
        lunches = {}
        for semester in semesters:
            for block in lunch_blocks:
                nbr = request.form.get(f'lunch{block}{semester}')
                if nbr is not None:
                    demand(nbr in list('1234'), f'Invalid lunch number: {nbr}')
                    lunches[block + semester] = int(nbr)

        # Schedule publicly accessible?
        make_public = request.form.get('public') == 'true'

        try:
            user = User.from_db(handle)
            if user is None:
                if 'name' not in session:
                    return error(417, 'Name unknown because not in user session')
                user = User(handle, session.pop('name'), new_schedule,
                            make_public, False)

                flash('Schedule added successfully')
            else:
                user.teachers = new_schedule
                user.public = make_public

                flash('Schedule updated successfully')
            # TODO add (I accept) field ^

            user.put_into_db()
            user.put_lunch(lunches)

            return redirect(redirect_path)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return error(500, str(e))


@app.route('/roster/<period>/<teacher>')
def show_roster_current_semester(period, teacher):
    return show_roster(str(ahs_calendar.current_semester()), period, teacher)


@app.route('/roster/<semester_str>/<period>/<teacher>')
def show_roster(semester_str, period, teacher):
    handle = logged_handle()
    if handle is None:
        return error_not_logged_in()

    if should_countdown():
        return redirect('/countdown', code=307)

    demand(period in periods, f'Invalid block: {period}')
    demand(teacher in teachers, f'Invalid teacher: {teacher}')
    demand(semester_str in semesters, f'Invalid semester: {semester_str}')
    semester = int(semester_str)

    entities = database.users_in_class(period, semester, teacher)
    users = list(Reader(handle).read_entities(entities))

    if len(entities) == 0:
        flash('That class is either empty or nonexistent', 'error')
        return redirect('/')

    user_in_class = handle in list(map(lambda row: row.handle, users))
    return render_template('roster.html', period=period, teacher=teacher,
                           roster=users, handle=handle,
                           lunch_number=database.lunch_number(period, semester, teacher),
                           lunch_periods=lunch_blocks,
                           size=len(entities),
                           user_in_class=user_in_class,
                           semester=semester)


@app.route('/lunch/<block>/<number>')
def show_lunch_current_semester(block, number):
    return show_lunch(str(ahs_calendar.current_semester()), block, number)


@app.route('/lunch/<semester_str>/<block>/<number>')
def show_lunch(semester_str, block, number):
    handle = logged_handle()
    if handle is None:
        return error_not_logged_in()

    if should_countdown():
        return redirect('/countdown', code=307)

    demand(block in lunch_blocks, f'Invalid lunch block: {block}')
    demand(number in list('1234'), f'Invalid lunch number: {number}')
    demand(semester_str in semesters, f'Invalid semester: {semester_str}')
    semester = int(semester_str)
    number = int(number)

    entities = database.users_in_lunch(block, number, semester)
    roster = list(Reader(handle).read_entities(entities))

    if len(entities) == 0:
        flash('No applicable classes were found', 'error')
        return redirect(default_home())

    return render_template('lunch.html', handle=handle, roster=roster,
                           block=block, number=number, size=len(entities), semester=semester)


@app.route('/search')
def do_search():
    handle = logged_handle()
    if handle is None:
        return error_not_logged_in()

    if should_countdown():
        return redirect('/countdown', code=307)

    query = request.args.get('query')
    if query is None or query.strip() == '':
        return render_template('search-new.html', handle=handle)

    results = list(map(User.from_entity, database.search(query.strip())))
    return render_template('search-result.html', query=query, results=results,
                           handle=handle)


@app.route('/discord')
def discord_entry_point():
    code = request.args.get('code')
    state = request.args.get('state')

    if code is not None and state is not None:
        return redirect(f'/discord/{code}/{state}')

    if code is None:
        flash('No code was supplied from Discord. Not our fault!', 'error')
    if state is None:
        flash('No state was supplied from Discord. Is this request legit?',
              'error')

    return redirect('/')


@app.route('/discord/<code>/<state>')
def verify_discord(code, state):
    handle = logged_handle()
    if handle is None:
        return error_not_logged_in()

    user = User.from_db(handle)
    if user is None:
        flash('You need to enter your schedule before integration', 'error')
        return redirect('/update')

    try:
        access_token = discord.exchange_code(code)
        user_info = discord.get('/users/@me', access_token)
        user_id = user_info.get('id')

        if not discord.state_valid(state, user_id):
            return "Did you use a link from someone else? Please use $$personalize to get a link, just for you."

        if user.get_discord_id() is None:
            user.put_discord_id(user_id)

        return render_template('discord_integration.html',
                               avatar_src=discord.avatar_url(user_info),
                               user_name=user_info['username'],
                               user_discriminator=user_info['discriminator'],
                               handle=handle, name=user.name)

    except requests.exceptions.HTTPError as e:
        print(e)
        return error(401, 'Discord authorization failed!')


@app.route('/privacy')
def show_privacy():
    return render_template('privacy.html',
                           is_logged_in=logged_handle() is not None)


def let_handle_read(handle, entities):
    users = list(map(User.from_entity, entities))

    if handle in map(lambda u: u.handle, users):
        return users
    else:
        return list(filter(lambda u: u.can_be_read_by_handle(handle), users))


from apis import rest_api

app.register_blueprint(rest_api)

if __name__ == "__main__":
    app.run()
