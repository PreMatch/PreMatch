import datetime
from typing import Iterable

from arrow.arrow import Arrow
from ics import Event, AudioAlarm

from entities.student import Student
from entities.types import SemesterSchedule
from use_cases.calendar import IcsCalendarCase

student_schedule: SemesterSchedule = {
    'A': 'Aubrey',
    'B': 'Bach',
    'C': 'Conrad',
    'D': 'Donovan',
    'E': 'Emery',
    'F': 'Frisk',
    'G': 'Gonzalez'
}
student: Student = Student('hpeng2021', 'Michael Peng', schedules={2: student_schedule})
case = IcsCalendarCase()

ahs_timezone = 'America/New_York'
expected_events = {
    Event(name='A Block with Aubrey',
          begin=Arrow(2020, 4, 6, 8, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 6, 9, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: A Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='C Block with Conrad',
          begin=Arrow(2020, 4, 6, 9, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 6, 10, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: C Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='E Block with Emery',
          begin=Arrow(2020, 4, 6, 10, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 6, 11, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: E Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='G Block with Gonzalez',
          begin=Arrow(2020, 4, 6, 11, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 6, 12, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: G Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='B Block with Bach',
          begin=Arrow(2020, 4, 7, 8, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 7, 9, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: B Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='D Block with Donovan',
          begin=Arrow(2020, 4, 7, 9, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 7, 10, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: D Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='F Block with Frisk',
          begin=Arrow(2020, 4, 7, 10, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 7, 11, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: F Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='A Block with Aubrey',
          begin=Arrow(2020, 4, 9, 8, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 9, 9, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: A Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='C Block with Conrad',
          begin=Arrow(2020, 4, 9, 9, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 9, 10, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: C Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='E Block with Emery',
          begin=Arrow(2020, 4, 9, 10, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 9, 11, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: E Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='G Block with Gonzalez',
          begin=Arrow(2020, 4, 9, 11, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 9, 12, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: G Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='B Block with Bach',
          begin=Arrow(2020, 4, 10, 8, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 10, 9, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: B Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='D Block with Donovan',
          begin=Arrow(2020, 4, 10, 9, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 10, 10, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: D Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))]),

    Event(name='F Block with Frisk',
          begin=Arrow(2020, 4, 10, 10, 30, tzinfo=ahs_timezone),
          end=Arrow(2020, 4, 10, 11, 15, tzinfo=ahs_timezone),
          categories=['AHS at home', 'AHS at home: F Block'],
          alarms=[AudioAlarm(datetime.timedelta(minutes=5))])

}


def test_generate_ics_one_week():
    calendar = case.generate_calendar(student, end_date=datetime.date(2020, 4, 10))
    assert_events_equal(expected_events, calendar.events)


def shift_event_weeks(weeks: int):
    def shift(event: Event):
        new_event = event.clone()
        new_event.end += datetime.timedelta(weeks=weeks)
        new_event.begin += datetime.timedelta(weeks=weeks)
        return new_event
    return shift


def test_generate_ics_two_weeks():
    calendar = case.generate_calendar(student, end_date=datetime.date(2020, 4, 19))
    expected = list(expected_events) + list(map(shift_event_weeks(1), expected_events))

    assert_events_equal(expected, calendar.events)


def test_generate_ics_break():
    calendar = case.generate_april_break_calendar(student)
    expected = list(map(shift_event_weeks(2), expected_events))

    assert_events_equal(expected, calendar.events)


def test_generate_ics_non_break():
    calendar = case.generate_calendar_except_break(student)
    expected = list(expected_events)
    expected += list(map(shift_event_weeks(1), expected_events))
    expected += list(map(shift_event_weeks(3), expected_events))

    assert_events_equal(expected, calendar.events)


def assert_events_equal(expected: Iterable[Event], actual: Iterable[Event]):
    expected_list = sorted(expected, key=lambda ev: ev.begin)
    actual_list = sorted(actual, key=lambda ev: ev.begin)

    assert len(expected_list) == len(actual_list)

    for i in range(len(expected_list)):
        exp_event, act_event = expected_list[i], actual_list[i]
        assert exp_event == act_event, f'index {i}'
