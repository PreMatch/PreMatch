import datetime

from arrow import arrow
from ics.alarm import AudioAlarm

from use_cases.ap import APTest, AP_TESTS, AP_TEST_DESCRIPTIONS, exam_events

ahs_timezone = 'America/New_York'


def test_generate_calendar():
    test = APTest('Latin', (5, 12), (12, 0), 'idk')
    cal = test.calendar_entry()

    assert cal.name == 'AP Latin Exam'
    assert cal.begin == arrow.Arrow(2020, 5, 12, 12, 0, 0, tzinfo=ahs_timezone)
    assert cal.end == arrow.Arrow(2020, 5, 12, 12, 45, 0, tzinfo=ahs_timezone)
    assert list(cal.categories) == ['AP Exams 2020']
    assert cal.description == 'idk'
    assert list(cal.alarms) == [AudioAlarm(-datetime.timedelta(minutes=30)),
                                AudioAlarm(-datetime.timedelta(minutes=45))]


def test_generate_from_grid():
    grid = AP_TESTS

    physics_c_mechanics = grid['Physics C: Mechanics']
    assert physics_c_mechanics.subject == 'Physics C: Mechanics'
    assert physics_c_mechanics.description == AP_TEST_DESCRIPTIONS['Physics C: Mechanics']
    assert physics_c_mechanics.date == (5, 11)
    assert physics_c_mechanics.time == (12, 0)

    music_theory = grid['Music Theory']
    assert music_theory.subject == 'Music Theory'
    assert music_theory.description == AP_TEST_DESCRIPTIONS['Music Theory']
    assert music_theory.date == (5, 19)
    assert music_theory.time == (12, 0)

    italian = grid['Italian Language and Culture']
    assert italian.subject == 'Italian Language and Culture'
    assert italian.description == AP_TEST_DESCRIPTIONS['Italian Language and Culture']
    assert italian.date == (5, 19)
    assert italian.time == (16, 0)

    stats = grid['Statistics']
    assert stats.subject == 'Statistics'
    assert stats.description == AP_TEST_DESCRIPTIONS['Statistics']
    assert stats.date == (5, 22)
    assert stats.time == (14, 0)


def test_exam_events_non_makeup():
    events = list(exam_events(['Latin', 'Physics 2', 'Biology', 'Chemistry']))

    assert events[0].subject == 'Latin'
    assert events[0].date == (5, 12)
    assert events[0].time == (12, 0)
    assert events[1].subject == 'Physics 2'
    assert events[2].subject == 'Biology'
    assert events[3].subject == 'Chemistry'
    assert events[3].time == (14, 0)


def test_exam_events_makeup():
    events = list(exam_events(['Calculus BC', 'Environmental Science',
                               'English Language and Composition'], makeup=True))

    assert events[0].subject == 'Calculus BC'
    assert events[0].date == (6, 1)
    assert events[0].time == (16, 0)

    assert events[1].subject == 'Environmental Science'
    assert events[1].date == (6, 3)
    assert events[1].time == (14, 0)

    assert events[2].subject == 'English Language and Composition'
    assert events[2].date == (6, 5)
    assert events[2].time == (12, 0)
