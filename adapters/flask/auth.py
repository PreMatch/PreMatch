from functools import wraps
from html import escape

from flask import request, flash, redirect, render_template, Blueprint, session, g

from adapters.flask.common import missing_form_field, adapt, DEFAULT_HOME, error, app
from entities.student import Student


def requires_login(f):
    @wraps(f)
    def dec_fun(*args, **kwargs):

        # todo enable
        # if should_countdown():
        #     return redirect('/countdown', code=307)

        handle = logged_handle()
        if handle is None:
            flash('You must be logged in to view this page.', 'error')
            return redirect('/login?redirect=' + escape(request.path))
        g.handle = handle

        return f(*args, **kwargs)

    return dec_fun


def session_log_in(handle):
    session['handle'] = handle


def session_log_out():
    session.pop('handle', '')


def logged_handle():
    return session.get('handle', None)


# Endpoints

auth_app = Blueprint("PreMatch Authentication", __name__, template_folder="templates")


@auth_app.route('/login', methods=['GET', 'POST'])
def do_login():
    if request.method == 'GET':
        if logged_handle() is not None:
            flash('You are already logged in')
            return redirect(request.args.get('redirect', DEFAULT_HOME))
        return render_template('login.html',
                               redirect=request.args.get('redirect', ''))

    # expected form argument: id_token, redirect (optional)
    if missing_form_field('id_token'):
        return error(422, 'Missing token from Google sign-in')

    try:
        (handle, name) = adapt.google.verify(request.form['id_token'])
        session_log_in(handle)
        have_user = adapt.student_repo.exists(handle)

        flash('Successfully logged in as ' + name)

        default = DEFAULT_HOME

        if not have_user:
            session['name'] = name
            default = '/update'
            new = Student(handle, name)
            adapt.student_repo.save(new)
            # Fact: if user is logged in, then the user must have a database entry

        if missing_form_field('redirect'):
            return redirect(default)
        return redirect(request.form.get('redirect', default))

    except ValueError as e:
        return error(403, 'Authentication failed: ' + str(e))


@auth_app.route('/logout')
def do_logout():
    if logged_handle() is not None:
        flash('You were successfully logged out')

    session_log_out()
    return redirect('/')


@auth_app.route('/discord')
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


@auth_app.route('/discord/<code>/<state>')
@requires_login
def verify_discord(code, state):
    user = adapt.student_repo.load(g.handle)

    try:
        discord_user = app.account.integrate_discord(user, code, state)

        return render_template('discord_integration.html',
                               avatar_src=discord_user.avatar_url(),
                               user_name=discord_user.username,
                               user_discriminator=discord_user.discriminator,
                               handle=g.handle, name=user.name)

    except PermissionError as e:
        print(e)
        return error(401, 'Discord authorization failed!')
    except KeyError:
        flash('Your state appears to be invalid. Please use $$personalize to get a link for yourself.', 'error')
        return redirect('/')
