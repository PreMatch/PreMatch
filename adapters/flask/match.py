from typing import Optional

from flask import Blueprint, render_template, g, request

from adapters.flask.auth import requires_login, logged_handle
from adapters.flask.common import adapt
from use_cases.match import match_score

match_app = Blueprint("PreMatch Matchmaker", __name__, template_folder="templates")


@match_app.route('/match')
@requires_login
def show_match():
    visitor = adapt.student_repo.load(g.handle)
    return render_template('match.html', handle=g.handle, name=visitor.name)


@match_app.route('/match/rate', methods=['POST'])
def rate_match():
    if logged_handle() is None:
        return '-1', 401

    handle1: Optional[str] = request.form.get('handle1')
    handle2: Optional[str] = request.form.get('handle2')

    if handle1 is None or handle1.strip() == '' or handle2 is None or handle2.strip() == '':
        return '-1', 422

    student1 = adapt.student_repo.load(handle1)
    student2 = adapt.student_repo.load(handle2)

    if student1 is None or student2 is None:
        return '-1', 422

    return str(match_score(student1, student2)), 200
