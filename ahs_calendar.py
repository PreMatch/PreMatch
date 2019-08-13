import datetime
import json


def current_semester():
    return 1
    # TODO enable
    # def now_in_date_range(date_range):
    #     start, end = map(datetime.date.fromisoformat, date_range)
    #     now = datetime.date.today()
    #     return start <= now <= end
    #
    # with open('static/calendar.json') as the_file:
    #     objects = json.load(the_file)
    #     date_ranges = objects['semesters']
    #
    #     for i in range(len(date_ranges)):
    #         if now_in_date_range(date_ranges[i]):
    #             return i + 1


def before_schedule_release():
    with open('static/calendar.json') as the_file:
        objects = json.load(the_file)
        dt_iso = objects['schedule_release']

        release_time = datetime.datetime.fromisoformat(dt_iso)
        return datetime.datetime.now() < release_time
