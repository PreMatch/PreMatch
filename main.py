import os
from urllib import parse

import sentry_sdk
from flask import *
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException

from adapters.flask.auth import auth_app
from adapters.flask.common import error, error_no_own_schedule, render_login_optional, ValidationError, \
    flash_ios_announcement, adapt
from adapters.flask.discovery import discovery_app
from adapters.flask.match import match_app
from adapters.flask.user import user_app
from apis import rest_api
from auth import *
from help import help_site
from use_cases.schedule import MissingScheduleError

if 'PREMATCH_DEV' not in os.environ:
    sentry_sdk.init(
        dsn="https://11b83f7d2a054364bf7883476e681eea@sentry.io/1536746",
        integrations=[FlaskIntegration()]
    )

app = Flask(__name__)
set_secret_key(app)

app.register_blueprint(help_site)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)


@app.before_request
def enforce_domain_https():
    url = parse.urlparse(request.url)
    is_http = 'prematch.org' in url.netloc.lower() and url.scheme == 'http'
    if 'appspot' in url.netloc or is_http:
        newurl = parse.ParseResult('https', 'prematch.org',
                                   url.path, url.params, url.query, url.fragment)
        return redirect(newurl.geturl(), code=301)


@app.errorhandler(ValidationError)
def validation_error_handler(err):
    sentry_sdk.capture_message(f'Validation error: {err.problem}')
    return error(422, err.problem)


@app.errorhandler(MissingScheduleError)
def schedule_missing_handler(err: MissingScheduleError):
    if g.handle == err.student.handle:
        return error_no_own_schedule()
    sentry_sdk.capture_message(f'Attempt to access nonexistent schedule of {err.student}')
    return render_template('profile_not_found.html', bad_handle=err.student.handle)


@app.errorhandler(HTTPException)
def generic_http_error(err):
    sentry_sdk.capture_exception(err)
    return render_template('error.html', error=err)


@app.route('/')
def front_page():
    flash_ios_announcement()
    return render_login_optional('index.html',
                                 schedule_count=adapt.student_repo.user_count())


@app.route('/about')
def show_about():
    flash_ios_announcement()
    return render_login_optional('about.html')


@app.route('/about/discord')
def show_about_discord():
    return render_login_optional('about_discord.html')


@app.route('/about/ios')
def show_about_app():
    return render_login_optional('about_ios.html')


@app.route('/countdown')
def show_countdown():
    return render_login_optional('countdown.html')


@app.route('/support')
def show_support_home():
    return render_login_optional('support_home.html')


@app.route('/support/feedback')
def show_feedback_page():
    return render_login_optional('support_feedback.html')


@app.route('/support/teachers')
def show_teachers_page():
    return render_login_optional('support_teachers.html')


blueprints = [
    rest_api,
    discovery_app,
    user_app,
    auth_app,
    match_app
]

for bp in blueprints:
    app.register_blueprint(bp)

if __name__ == "__main__":
    app.run()
