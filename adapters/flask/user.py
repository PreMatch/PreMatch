import datetime
import traceback

import secrets
from adapters.flask.auth import requires_login, logged_handle
from adapters.flask.common import *
from adapters.flask.validate import *
from entities.student import Student, YearSchedule
from entities.types import Semester, SemesterLunches
from use_cases import ap
from use_cases.calendar import IcsCalendarCase
from use_cases.schedule import MissingScheduleError

user_app = Blueprint("PreMatch User Management", __name__, template_folder="templates")


@user_app.route('/user')
@requires_login
def show_self_current_semester():
    return show_user_current_semester(g.handle)


@user_app.route('/user/<handle>')
@requires_login
def show_user_current_semester(handle):
    return show_user(handle, str(ahs_calendar.current_semester()))


@user_app.route('/user/<handle>/<semester>')
@requires_login
def show_user(handle, semester):

    target = adapt.student_repo.load(handle)
    if target is None:
        raise MissingScheduleError(Student(handle, '<unknown>'))
    if target.schedules is None:
        flash(f'The user {handle} has not entered their schedule yet', 'error')
        return redirect(DEFAULT_HOME)

    demand(valid_semester_string(semester), f'Invalid semester: {semester}')
    semester = int(semester)

    flash_ios_announcement()

    viewer = adapt.student_repo.load(g.handle)
    result = app.schedule.show_schedule(viewer, target, semester)

    lunch_numbers = {}
    for block in result:
        lunch_numbers[block] = app.schedule.show_lunch_number(target, semester, block)

    return render_template('user.html', schedule=result, name=target.name,
                           handle=handle,
                           lunch_numbers=lunch_numbers,
                           semester=semester)


@user_app.route('/dashboard')
@requires_login
def show_own_dashboard_current_semester():
    return show_dashboard(g.handle, str(ahs_calendar.current_semester()))


@user_app.route('/dashboard/<semester_or_handle>')
@requires_login
def show_own_dashboard_current_semester_or_handle(semester_or_handle):
    if valid_semester_string(semester_or_handle):
        return show_dashboard(g.handle, semester_or_handle)
    else:
        return show_dashboard(semester_or_handle, str(ahs_calendar.current_semester()))


@user_app.route('/dashboard/<handle>/<semester>')
@requires_login
def show_dashboard(handle, semester):

    target = adapt.student_repo.load(handle)
    if target is None or target.schedules is None:
        raise MissingScheduleError(target)

    demand(valid_semester_string(semester), f'Invalid semester: {semester}')
    semester = int(semester)

    if not target.is_public and target.handle != g.handle:
        return error_private(handle)

    flash_ios_announcement()

    rosters = {}
    class_sizes = {}
    for block in BLOCKS:
        students = list(adapt.student_repo.students_in_class(
            semester, block, target.semester_schedule(semester)[block]))

        class_sizes[block] = len(students)
        rosters[block] = students

    return render_template('dashboard.html',
                           handle=handle, name=target.name, schedule=target.semester_schedule(semester),
                           rosters=rosters, sizes=class_sizes,
                           semester=semester,
                           user=target)


@user_app.route('/update', methods=['GET', 'POST'])
@requires_login
def do_update():
    teacher_names = list(adapt.class_repo.list_teacher_names())
    if request.method == 'GET':
        user = adapt.student_repo.load(g.handle)

        if user is None and 'name' not in session:
            flash('Sorry, but you need to log in again', 'error')
            return redirect('/login')

        if user.schedules is None:
            return render_template('update.html',
                                   handle=g.handle,
                                   name=session.get('name', user.name),
                                   schedule=None,
                                   teachers=teacher_names,
                                   lunch_periods=LUNCH_BLOCKS, lunches=[1, 2, 3, 4],
                                   lunch_numbers=lambda a, b: None,
                                   user_public=False)
        else:
            schedule = lambda sem, b: user.semester_schedule(int(sem))[b]

            def lunch_number(sem, b):
                return app.schedule.show_lunch_number(user, int(sem), b)

            return render_template('update.html',
                                   handle=g.handle,
                                   name=session.get('name', user.name),
                                   schedule=schedule,
                                   teachers=teacher_names,
                                   lunch_periods=LUNCH_BLOCKS, lunches=[1, 2, 3, 4],
                                   lunch_numbers=lunch_number,
                                   user_public=user.is_public)
    else:
        # Redirect path reading from args
        redirect_path = request.args.get('from', DEFAULT_HOME)
        if empty(redirect_path):
            redirect_path = DEFAULT_HOME

        new_schedule: YearSchedule = {}
        teachers = set()
        for block in BLOCKS:
            for semester in SEMESTER_STRINGS:
                required_field = f'{block}{semester}'
                demand(not missing_form_field(required_field), f'Missing field {required_field}')

                teacher = request.form.get(required_field)
                new_schedule.setdefault(int(semester), {})[block] = teacher
                demand(teacher in teacher_names, f'Unknown teacher: {teacher}')

        # Read lunches (optional)
        lunches: Dict[Semester, SemesterLunches] = {}
        for semester in SEMESTER_STRINGS:
            for block in LUNCH_BLOCKS:
                nbr = request.form.get(f'lunch{block}{semester}')
                if nbr is not None:
                    demand(nbr in list('1234'), f'Invalid lunch number: {nbr}')
                    lunches.setdefault(int(semester), {})[block] = int(nbr)

        # Schedule publicly accessible?
        make_public = request.form.get('public') == 'true'

        try:
            user = adapt.student_repo.load(g.handle)
            user.schedules = new_schedule
            user.is_public = make_public

            flash('Schedule updated successfully')
            # TODO add (I accept) field ^

            app.account.update_lunches(user, lunches)
            adapt.student_repo.save(user)

            return redirect(redirect_path)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return error(500, str(e))


@user_app.route('/privacy')
def show_privacy():
    return render_template('embedded_document.html',
                           is_logged_in=logged_handle() is not None, title='Privacy Policy',
                           document_path='privacy-policy.md')


@user_app.route('/terms')
def show_terms():
    return render_template('embedded_document.html',
                           is_logged_in=logged_handle() is not None, title='Terms and Conditions of Service',
                           document_path='terms-and-conditions.md')


@user_app.route('/open_house')
@requires_login
def open_house_table():
    user = adapt.student_repo.load(g.handle)
    schedule = user.semester_schedule(ahs_calendar.current_semester())
    if schedule is None:
        flash('You must enter your schedule to get your customized open house table', 'error')
        return redirect('/')

    times = [
        {'time': '6:30 – 6:40', 'block': 'H1'},
        {'time': '6:45 – 6:55', 'block': 'A'},
        {'time': '7:00 – 7:10', 'block': 'B'},
        {'time': '7:15 – 7:25', 'block': 'C'},
        {'time': '7:30 – 7:40', 'block': 'D'},
        {'time': '7:45 – 7:55', 'block': 'E'},
        {'time': '8:00 – 8:10', 'block': 'F'},
        {'time': '8:15 – 8:25', 'block': 'G'}
    ]

    return render_template('openhouse-table.html', user=user,
                           schedule=schedule, blocks=times,
                           time=datetime.datetime.now())


@user_app.route('/calendar')
@requires_login
def download_ahs_at_home_ics():
    user = adapt.student_repo.load(g.handle)
    calendar = IcsCalendarCase.generate_calendar_except_break(user)
    if hasattr(secrets, 'process_calendar'):
        secrets.process_calendar(calendar, g.handle)
    print(f'event download_calendar_except_break {g.handle}')
    ics = IcsCalendarCase.generate_ics(calendar)

    ics.seek(0)
    return send_file(ics, mimetype='text/calendar', as_attachment=True, attachment_filename='classes-with-break.ics')


@user_app.route('/calendar/until-june')
@requires_login
def download_ahs_at_home_ics_until_june():
    user = adapt.student_repo.load(g.handle)
    calendar = IcsCalendarCase.generate_calendar(user, start_date=datetime.date(2020, 5, 4),
                                                 end_date=datetime.date(2020, 5, 29))
    ics = IcsCalendarCase.generate_ics(calendar)
    print(f'event download_calendar_until_june {g.handle}')

    ics.seek(0)
    return send_file(ics, mimetype='text/calendar', as_attachment=True, attachment_filename='classes-may.ics')


@user_app.route('/ap-exam/events', methods=['GET', 'POST'])
def ap_exam_events():
    if request.method == 'GET':
        return render_template('ap_events.html', handle=logged_handle(), subjects=ap.AP_TEST_DESCRIPTIONS.keys())

    payload = request.form
    try:
        subjects = dict(payload)
        makeup = subjects.pop('__makeup', False)
        calendar = ap.calendar_of_exams(ap.exam_events(subjects.keys(), makeup))
        ics = IcsCalendarCase.generate_ics(calendar)
        print(f'event exam_events_download makeup={payload.get("makeup")} len={len(calendar.events)} '
              f'handle={logged_handle()}')

        ics.seek(0)
        return send_file(ics, mimetype='text/calendar', as_attachment=True, attachment_filename='ap-exams.ics')
    except KeyError as key:
        return error(422, f'Unknown subject: {key}')