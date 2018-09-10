from google.oauth2 import id_token
from google.auth.transport import requests
import datetime

CLIENT_ID = '764760025104-is3262o216isl5tbfj4aakcel2tirl7n.apps.googleusercontent.com'
APS_DOMAIN = 'k12.andoverma.us'


def grad_year_of_handle(handle):
  year_str = ''.join(filter(lambda char: char.isdigit(), handle))[:4]
  if len(year_str) == 0:
    return None
  return int(year_str)


# returns (handle, name)
def validate_token_for_info(token):
  idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

  if idinfo['iss'] not in ['accounts.google.com',
                           'https://accounts.google.com']:
    raise ValueError('Wrong issuer')
  if 'hd' not in idinfo or idinfo['hd'] != APS_DOMAIN:
    raise ValueError('You need to use your k12.andoverma.us account')

  handle = idinfo['email'].split('@')[0]
  grad_year = grad_year_of_handle(handle)
  this_year = datetime.date.today().year

  if grad_year is not None and (grad_year < this_year or
                                grad_year - 4 > this_year):
    raise ValueError('You are not a current student of Andover High School')

  return handle, idinfo['name']
