from auth import logged_handle
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
    return api_error(422, f'No such teacher: {teacher}')
  if block not in lunch_blocks:
    return api_error(422, f'No such lunch block: {block}')

  number = database.lunch_number(block, teacher)

  if number is None:
    return api_error(404, 'No lunch number set', status='empty')
  else:
    return api_success(number=number)