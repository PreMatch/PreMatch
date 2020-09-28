import datetime
from typing import Optional

from google.auth.transport import requests
from google.oauth2 import id_token

from entities.types import Handle, Name
from use_cases.types import AuthProvider

WEB_CLIENT_ID = '764760025104-is3262o216isl5tbfj4aakcel2tirl7n.apps.googleusercontent.com'
IOS_CLIENT_ID = '764760025104-70ao2s5vql3ldi54okdf9tbkd4chtama.apps.googleusercontent.com'
APS_DOMAIN = 'k12.andoverma.us'
CLIENT_IDS = [WEB_CLIENT_ID, IOS_CLIENT_ID]


# FIXME duplicated in Student
def grad_year_of_handle(handle) -> Optional[int]:
    year_str = ''.join(filter(lambda char: char.isdigit(), handle))[:4]
    if len(year_str) == 0:
        return None
    return int(year_str)


# Throws ValueError
def validate_for_handle_name(token, client_id):
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

    if idinfo['iss'] not in ['accounts.google.com',
                             'https://accounts.google.com']:
        raise ValueError('Wrong issuer')
    if 'hd' not in idinfo or idinfo['hd'] != APS_DOMAIN:
        raise ValueError('You need to use your k12.andoverma.us account!')

    handle = idinfo['email'].split('@')[0]
    grad_year = grad_year_of_handle(handle)
    this_year = datetime.date.today().year

    if grad_year is not None and (grad_year < this_year or
                                  grad_year - 4 > this_year) and handle != 'kdole2020':
        raise ValueError('You are not a current student of Andover High School')

    return handle, idinfo.get('name')


def validate_token_for_info(token):
    return validate_for_handle_name(token, WEB_CLIENT_ID)


def validate_ios_token_for_info(token):
    return validate_for_handle_name(token, IOS_CLIENT_ID)


class GoogleAuthProvider(AuthProvider):
    def verify(self, token: str) -> (Handle, Name):
        return validate_token_for_info(token)
