import itertools
from functools import wraps
from typing import Callable

from flask_cors import CORS

from adapters.flask.common import *
from adapters.flask.validate import *
from auth import *
from entities.student import Student
from google_auth import *

rest_api = Blueprint('rest_api', __name__)
CORS(rest_api, supports_credentials=True)


def api_error(code, message, status='error', extra=None):
    if extra is None:
        extra = dict()

    data = {
        'status': status,
        'code': code,
        'message': message
    }
    data.update(extra)

    return jsonify(data), code


def api_success(payload):
    data = {
        'status': 'ok',
        'code': 200
    }
    data.update(payload)
    return jsonify(data)


def api_error_unauthorized(err: Optional[str] = None):
    return api_error(401, 'Unauthorized (not logged in)', extra=None if err is None else {'error': err})


def api_bad_value(problem_key):
    return api_error(422, f'Invalid or missing value for "{problem_key}"')


def requires_api_auth(f):
    @wraps(f)
    def dec_fun(*args, **kwargs):
        handle = logged_handle()

        if handle is None:
            try:
                data = request.get_json()
                if data is None:
                    raise LookupError('missing id_token data')
                token = data['id_token']
                handle, name = validate_firebase_token_for_info(token)
                g.handle = handle
            except Exception as e:
                return api_error_unauthorized(str(e))
        else:
            g.handle = handle

        return f(*args, **kwargs)

    return dec_fun


# teacher: string
# block: string (letter)
# log-in required
@rest_api.route('/api/lunch/number', methods=['GET', 'POST'])
@requires_api_auth
def api_lunch_get():
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
        handle, _ = validate_ios_token_for_info(token)
        log_in(handle)
        return api_success({'handle': handle})

    except ValueError:
        try:
            handle, _ = validate_token_for_info(token)
            log_in(handle)
            return api_success({'handle': handle})

        except ValueError as e2:
            return api_error(403, str(e2))


# handle: string
# log-in required
@rest_api.route('/api/schedule', methods=['GET', 'POST'])
@requires_api_auth
def api_schedule():
    handle = request.args.get('handle')
    if handle is None:
        handle = g.handle

    student = adapt.student_repo.load(handle)
    if student is None or student.schedules is None:
        return api_error(404, 'Handle not found: ' + handle)
    if not student.is_public and student.handle != g.handle:
        return api_error(403, 'Cannot read private handle: ' + handle)

    output = {}
    for (semester, mapping) in student.schedules.items():
        for (block, teacher) in mapping.items():
            output[f'{block}{semester}'] = teacher

    return api_success(output)


# block: string
# semester: 1 or 2
@rest_api.route('/api/classmates')
@requires_api_auth
def api_classmates():
    block = request.args.get('block')
    semester = request.args.get('semester')
    user = adapt.student_repo.load(g.handle)

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


@rest_api.route('/api/student/search', methods=['POST'])
@requires_api_auth
def api_search_student():
    req_json = request.get_json(silent=True)
    if req_json is None:
        return api_bad_value('query')

    query: str = req_json.get('query')
    if query is None or query.strip() == '':
        return api_bad_value('query')

    results = list(map(lambda student: {'handle': student.handle, 'name': student.name},
                       sorted(itertools.islice(adapt.student_repo.search(query), 15), key=completion_distance(query))))
    return api_success({'results': results})


def completion_distance(query: str) -> Callable[[Student], int]:
    def string_dist(a: str, b: str) -> int:
        base_len = min(len(a), len(b))
        result = 0
        for i in range(base_len):
            if a[i] != b[i]:
                result += 1
        return result

    def dist(result: Student):
        return min(string_dist(result.handle, query), string_dist(result.name, query))

    return dist
