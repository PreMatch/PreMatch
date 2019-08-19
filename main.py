from urllib import parse

from flask import *
from werkzeug.exceptions import HTTPException

from adapters.flask.auth import auth_app
from adapters.flask.common import error, error_no_own_schedule, render_login_optional, ValidationError
from adapters.flask.discovery import discovery_app
from adapters.flask.user import user_app
from apis import rest_api
from auth import *
from help import help_site
from use_cases.schedule import MissingScheduleError

app = Flask(__name__)
set_secret_key(app)

app.register_blueprint(help_site)


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
    return error(422, err.problem)


@app.errorhandler(MissingScheduleError)
def schedule_missing_handler(err: MissingScheduleError):
    if g.handle == err.student.handle:
        return error_no_own_schedule()
    return render_template('profile_not_found.html', bad_handle=err.student.handle)


@app.errorhandler(HTTPException)
def generic_http_error(err):
    return render_template('error.html', error=err)


@app.route('/')
def front_page():
    return render_login_optional('index.html',
                                 schedule_count=0)  # FIXME


@app.route('/about')
def show_about():
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
]

for bp in blueprints:
    app.register_blueprint(bp)

if __name__ == "__main__":
    app.run()
