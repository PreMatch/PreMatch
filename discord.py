import requests
import hmac
import json

API_ENDPOINT = 'https://discordapp.com/api'
CLIENT_ID = '418089369942097921'
CLIENT_SECRET = 'IIx8xkGg52On9-EkZrxm0OiIGoyOHBkv'
# REDIRECT_URI = 'https://prematch.org/discord'
# TODO remove before deployment
REDIRECT_URI = 'http://localhost:5000/discord'


def state_valid(state, id_from_api):
  hmac_obj = hmac.new(CLIENT_SECRET.encode(), id_from_api.encode(), 'SHA1')
  return hmac.compare_digest(hmac_obj.hexdigest(), state)


def get(endpoint, access_token):
  result = requests.get(API_ENDPOINT + endpoint,
                        headers={
                          'Authorization': access_token['token_type'] + ' ' +
                                           access_token['access_token']})
  return result.json()


def avatar_url(user_info):
  return f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png'

def exchange_code(code):
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI,
    'scope': 'identify'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % API_ENDPOINT, data, headers)
  r.raise_for_status()
  return r.json()
