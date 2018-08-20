from google.oauth2 import id_token
from google.auth.transport import requests

CLIENT_ID = '764760025104-is3262o216isl5tbfj4aakcel2tirl7n.apps.googleusercontent.com'
APS_DOMAIN = 'k12.andoverma.us'


# returns (handle, name)
def validate_token_for_info(token):
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer')
    if 'hd' not in idinfo or idinfo['hd'] != APS_DOMAIN:
        raise ValueError('You need to use your k12.andoverma.us account')

    return idinfo['email'].split('@')[0], idinfo['name']
