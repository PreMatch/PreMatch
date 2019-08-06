from adapters.flask.auth import requires_login
from adapters.flask.common import *
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
    if target is None or target.schedules is None:
        raise MissingScheduleError(handle)

    demand(valid_semester_string(semester), f'Invalid semester: {semester}')
    semester = int(semester)

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
    reader = adapt.student_repo.load(g.handle)
    target = adapt.student_repo.load(handle)
    if target is None or target.schedules is None:
        raise MissingScheduleError(handle)

    demand(valid_semester_string(semester), f'Invalid semester: {semester}')
    semester = int(semester)

    if not target.is_public:
        return error_private(handle)

    rosters = {}
    class_sizes = {}
    for block in BLOCKS:
        students = list(adapt.student_repo.students_in_class(
            semester, block, target.semester_schedule(semester)[block]))

        class_sizes[block] = len(students)
        rosters[block] = students

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
@requires_login
def do_update():
    if request.method == 'GET':
        user = adapt.student_repo.load(g.handle)

        if user is None and 'name' not in session:
            flash('Sorry, but you need to log in again', 'error')
            return redirect('/login')

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
