import hmac

import requests

from secrets import DISCORD_CLIENT_SECRET as CLIENT_SECRET
from use_cases.types import DiscordVerifier, DiscordUser

API_ENDPOINT = 'https://discordapp.com/api'
CLIENT_ID = '418089369942097921'
REDIRECT_URI = 'https://prematch.org/discord'


def state_valid(state, id_from_api):
    hmac_obj = hmac.new(CLIENT_SECRET.encode(), id_from_api.encode(), 'SHA1')
    return hmac.compare_digest(hmac_obj.hexdigest(), state)


def get(endpoint, access_token):
    result = requests.get(API_ENDPOINT + endpoint,
                          headers={
                              'Authorization': access_token['token_type'] + ' ' +
                                               access_token['access_token']})
    return result.json()


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


class DiscordVerifierImpl(DiscordVerifier):
    def verify(self, code: str, state: str) -> DiscordUser:
        try:
            token = exchange_code(code)
            user_info = get('/users/@me', token)
            user = DiscordUser(user_info)

            if not state_valid(state, user_info.get('id')):
                raise KeyError('bad state. get one for yourself?')

            return user
        except requests.exceptions.HTTPError as e:
            print(e)
            raise PermissionError(e)
