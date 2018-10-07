from auth import *
from google_auth import *
from config import *
import database
from flask import *

rest_api = Blueprint('rest_api', __name__)


def api_error(code, message, status='error'):
  return jsonify({
    'status': status,
    'code': code,
    'message': message
  }), code


def api_success(**payload):
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

  if teacher not in teachers:
    return api_bad_value('teacher')
  if block not in lunch_blocks:
    return api_bad_value('block')

  number = database.lunch_number(block, teacher)

  if number is None:
    return api_error(404, 'No lunch number set', status='empty')
  else:
    return api_success(number=number)


# id_token: string
@rest_api.route('/api/login', methods=['GET'])
def api_login():
  token = request.args.get('id_token')

  if token is None:
    return api_bad_value('id_token')

  try:
    handle, name = validate_token_for_info(token)
    log_in(handle)
    return api_success(handle=handle)

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
  if not database.handle_exists(handle):
    return api_error(404, 'Handle not found: ' + handle)

  schedule = database.user_schedule(handle)
  response = dict(map(lambda blk: (blk, schedule.get(blk)), periods))

  return api_success(**response)