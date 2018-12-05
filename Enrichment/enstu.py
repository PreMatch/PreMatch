import requests as req
from typing import Optional, Mapping, List

VALIDATE_TOKEN_ENDPOINT = 'https://app.enrichingstudents.com/LoginApi' \
                          '/ValidateGoogleToken'
FETCH_SCHEDULE_ENDPOINT = 'https://student.enrichingstudents.com' \
                          '/StudentViewScheduleApi/FetchSchedule'


class Session:
    def __init__(self, cookies: dict):
        self.cookies = cookies

    def fetch_schedule(self, date: str) -> Mapping[str, str]:
        fetch_res = req.post(FETCH_SCHEDULE_ENDPOINT,
                 cookies=self.cookies,
                 json={'scheduleDate': date})

        if not fetch_res.json()['CallSucceeded'] or fetch_res.status_code != 200:
            raise Exception(fetch_res.reason)

        result = fetch_res.json()
        try:
            return dict(
                map(lambda ap: (ap['ScheduleDate'],
                                ap['AppointmentDetails'][0]['InstructorLastName']),
                    result['ViewModel']['AppointmentsGroupedByScheduleDate']))
        except Exception as e:
            print(e)
            raise e


def login(id_token: str) -> Session:
    res = req.post(VALIDATE_TOKEN_ENDPOINT, json={'idToken': id_token}).json()
    if res.get('CallSucceeded'):
        jar = req.get(res.get('RedirectTo'))
        return Session(jar.cookies)
    else:
        raise Exception(res.reason)


