from adapters.flask.common import *
from adapters.flask.validate import *
from auth import *
from google_auth import *

rest_api = Blueprint('rest_api', __name__)


def api_error(code, message, status='error'):
    return jsonify({
        'status': status,
        'code': code,
        'message': message
    }), code


def api_success(payload):
    data = {
        'status': 'ok',
        'code': 200
    }
    data.update(payload)
    return jsonify(data)


def api_error_unauthorized():
    return api_error(401, 'Unauthorized (not logged in)')


def api_bad_value(problem_key):
    return api_error(422, f'Invalid or missing value for "{problem_key}"')


# teacher: string
# block: string (letter)
# log-in required
@rest_api.route('/api/lunch/number', methods=['GET'])
def api_lunch_get():
    if logged_handle() is None:
        return api_error_unauthorized()

    teacher = request.args.get('teacher')
    block = request.args.get('block')
    semester = request.args.get('semester')

    if not adapt.class_repo.exists(teacher, block, semester):
        return api_error(422, 'Class does not exist')

    number = adapt.class_repo.load(teacher, block, semester).lunch

    if number is None:
        return api_error(404, 'No lunch number set', status='empty')
    else:
        return api_success({'number': number})


# id_token: string
@rest_api.route('/api/login', methods=['GET'])
def api_login():
    token = request.args.get('id_token')

    if token is None:
        return api_bad_value('id_token')

    try:
        handle, name = validate_ios_token_for_info(token)
        log_in(handle)
        return api_success({'handle': handle})

    except ValueError as e:
        return api_error(403, str(e))


# handle: string
# log-in required
@rest_api.route('/api/schedule', methods=['GET'])
def api_schedule():
    if logged_handle() is None:
        return api_error_unauthorized()

    handle = request.args.get('handle')
    if handle is None:
        return api_bad_value('handle')
    student = adapt.student_repo.load(handle)
    if student is None or student.schedules is None:
        return api_error(404, 'Handle not found: ' + handle)
    if not student.is_public and student.handle != logged_handle():
        return api_error(403, 'Cannot read private handle: ' + handle)

    output = {}
    for (semester, mapping) in student.schedules.items():
        for (block, teacher) in mapping.items():
            output[f'{block}{semester}'] = teacher

    return api_success(output)

# block: string
# semester: 1 or 2
@rest_api.route('/api/classmates')
def api_classmates():
    handle = logged_handle()
    if handle is None:
        return api_error_unauthorized()

    block = request.args.get('block')
    semester = request.args.get('semester')
    user = adapt.student_repo.load(handle)

    if block is None or not valid_block(block):
        return api_bad_value('block')
    if semester is None or not valid_semester_string(semester):
        return api_bad_value('semester')
    if user is None:
        return api_error_unauthorized()

    # End of validation

    students = app.schedule.show_classmates(user, int(semester), block)
    students = list(map(lambda student: {'name': student.name, 'handle': student.handle}, students))

    return api_success({'students': students})
