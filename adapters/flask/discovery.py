from adapters.flask.auth import requires_login
from adapters.flask.common import *
from adapters.flask.validate import valid_block, valid_semester_string, valid_lunch_block

discovery_app = Blueprint("PreMatch Discovery", __name__, template_folder='templates')


@discovery_app.route('/roster/<period>/<teacher>')
@requires_login
def show_roster_current_semester(period, teacher):
    return show_roster(str(ahs_calendar.current_semester()), period, teacher)


@discovery_app.route('/roster/<semester_str>/<period>/<teacher>')
@requires_login
def show_roster(semester_str, period, teacher):
    flash_ios_announcement()

    demand(valid_block(period), f'Invalid block: {period}')
    demand(teacher in adapt.class_repo.list_teacher_names(), f'Invalid teacher: {teacher}')
    demand(valid_semester_string(semester_str), f'Invalid semester: {semester_str}')
    semester = int(semester_str)

    classmates = list(adapt.student_repo.students_in_class(semester, period, teacher))

    if len(classmates) == 0:
        flash('That class is either empty or nonexistent', 'error')
        return redirect('/')

    user_in_class = g.handle in list(map(lambda student: student.handle, classmates))
    klass = adapt.class_repo.load(teacher, period, semester)
    lunch_number = klass.lunch if klass is not None else None

    return render_template('roster.html', period=period, teacher=teacher,
                           roster=classmates, handle=g.handle,
                           lunch_number=lunch_number,
                           size=len(classmates),
                           user_in_class=user_in_class,
                           semester=semester)


@discovery_app.route('/lunch/<block>/<number>')
@requires_login
def show_lunch_current_semester(block, number):
    return show_lunch(str(ahs_calendar.current_semester()), block, number)


@discovery_app.route('/lunch/<semester_str>/<block>/<number>')
@requires_login
def show_lunch(semester_str, block, number):
    demand(valid_lunch_block(block), f'Invalid lunch block: {block}')
    demand(number in list('1234'), f'Invalid lunch number: {number}')
    demand(valid_semester_string(semester_str), f'Invalid semester: {semester_str}')
    semester = int(semester_str)
    number = int(number)

    viewer = adapt.student_repo.load(g.handle)
    lunchmates = list(app.schedule.show_lunchmates(
        viewer, semester, block, number))

    if len(lunchmates) == 0:
        flash('No applicable classes were found', 'error')
        return redirect(DEFAULT_HOME)

    viewer_in_lunch = app.schedule.show_lunch_number(viewer, semester, block) == number

    return render_template('lunch.html', handle=g.handle, roster=lunchmates,
                           block=block, number=number, size=len(lunchmates), semester=semester,
                           viewer_in_lunch=viewer_in_lunch)


@discovery_app.route('/search')
@requires_login
def do_search():
    flash_ios_announcement()

    query = request.args.get('query')
    if query is None or query.strip() == '':
        return render_template('search-new.html', handle=g.handle)

    results = list(app.search.perform_search(query))
    return render_template('search-result.html', query=query, results=results,
                           handle=g.handle)
