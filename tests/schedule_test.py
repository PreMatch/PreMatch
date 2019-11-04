from unittest.mock import MagicMock

import pytest

from entities.klass import Class
from entities.student import Student
from tests.mock_helper import require, switch
from use_cases.schedule import ScheduleCase, MissingScheduleError

student_repo = MagicMock()
class_repo = MagicMock()
case = ScheduleCase(student_repo, class_repo)


@pytest.fixture
def reset_mock():
    student_repo.reset_mock()
    class_repo.reset_mock()


def test_own_schedule_exists():
    student = Student('hpeng2021', 'Michael')
    student.schedules = {1: {'D': 'Yes'}}

    output = case.own_schedule(student, 1)

    assert output == {'D': 'Yes'}


def test_own_schedule_none():
    student = Student('hpeng2021', 'Michael')
    student.schedules = {}

    with pytest.raises(MissingScheduleError, match='hpeng2021'):
        case.own_schedule(student, 1)


def test_read_schedule_of_public():
    reader = Student('hpeng2021', 'Michael')
    student = Student('divanovich2021', 'Daniel')
    student.is_public = True
    student.schedules = {1: {'G': 'Ream'}}

    result = case.show_schedule(reader, student, 1)

    assert result == {'G': 'Ream'}


def test_read_schedule_of_private():
    reader = Student('hpeng2021', 'Michael')
    reader.schedules = {1: {'A': 'Holm-Andersen', 'D': 'Givens', 'E': 'Messina', 'F': 'Parsons', 'G': 'Hibino, Krista'}}

    student = Student('divanovich2021', 'Daniel')
    student.schedules = {1: {'A': 'Holm-Andersen', 'D': 'Givens', 'E': 'Reusch', 'F': 'Scarfo', 'G': 'Ream'}}
    student.is_public = False

    result = case.show_schedule(reader, student, 1)

    assert result == {'A': 'Holm-Andersen', 'D': 'Givens'}


def test_read_schedule_of_private_without_reader_schedule():
    reader = Student('hpeng2021', 'Michael')

    student = Student('divanovich2021', 'Daniel')
    student.schedules = {2: {'D': 'Givens'}}

    assert case.show_schedule(reader, student, 2) == {}


def test_read_no_schedule_student():
    reader = Student('a', 'A')
    student = Student('b', 'B')
    student.is_public = True
    student.schedules = None

    with pytest.raises(MissingScheduleError, match='B'):
        case.show_schedule(reader, student, 1)


def test_show_classmates(reset_mock):
    classmates = [
        Student('a', 'A'),
        Student('b', 'B'),
        Student('c', 'C')
    ]
    student_repo.students_in_class.return_value = classmates
    student = Student('hpeng2021', 'Michael')
    student.schedules = {1: {'D': 'Givens'}}

    output = case.show_classmates(student, 1, 'D')

    assert output == classmates
    student_repo.students_in_class.assert_called_once_with(1, 'D', 'Givens')


def test_show_classmates_without_schedule(reset_mock):
    student = Student('abush', 'Am Bush')

    with pytest.raises(MissingScheduleError, match='abush'):
        case.show_classmates(student, 1, 'C')


def test_show_lunch_number(reset_mock):
    viewer = Student('hpeng2021', 'Michael Peng')
    viewer.schedules = {
        1: {'C': 'Ream', 'D': 'DiBenedetto', 'E': 'Emery'},
        2: {'C': 'Ream', 'D': 'DiBenedetto', 'E': 'Messina'}
    }
    emery = Class('Emery', 'E', 1, lunch=2)
    messina = Class('Messina', 'E', 2, lunch=None)

    class_repo.load.side_effect = switch({('Emery', 'E', 1): emery, ('Messina', 'E', 2): messina})

    e1_out = case.show_lunch_number(viewer, 1, 'E')
    e2_out = case.show_lunch_number(viewer, 2, 'E')

    assert e1_out == 2
    assert e2_out is None


def test_show_lunch_number_no_schedule(reset_mock):
    viewer = Student('hpeng2021', 'Michael Peng')

    with pytest.raises(MissingScheduleError, match='hpeng2021'):
        case.show_lunch_number(viewer, 2, 'C')


def test_show_lunchmates_of_own_lunch(reset_mock):
    viewer = Student('hpeng2021', 'Michael Peng')
    viewer.schedules = {1: {'D': 'Smith'}}
    lunchmates = [
        Student('pcess', 'Pro Cess'),
        Student('azenith', 'Ayush Zenith'),
        Student('jmann', 'Jordan Mann')
    ]
    klass = Class('Smith', 'D', 1, lunch=3)

    class_repo.load.side_effect = require(('Smith', 'D', 1), klass)
    class_repo.names_of_teachers_in_lunch.side_effect = require((1, 'D', 3), ['Smith'])
    student_repo.students_in_class.side_effect = require((1, 'D', 'Smith'), lunchmates)

    output = case.show_lunchmates(viewer, 1, 'D', 3)

    assert list(output) == list(lunchmates)


def test_show_lunchmates_without_schedule():
    with pytest.raises(MissingScheduleError):
        viewer = Student('hpeng2021', 'Michael Peng')
        viewer.schedules = None
        list(case.show_lunchmates(viewer, 1, 'D', 1))


def test_show_lunchmates_of_external_lunch(reset_mock):
    # Current decision: show private students in another lunch
    # Can be blocked in frontend

    viewer = Student('hpeng2021', 'Michael Peng')
    viewer.schedules = {1: {'C': 'Smith', 'F': 'Shea'}}
    smith = Class('Smith', 'C', 1, lunch=2)
    shea = Class('Shea', 'F', 1, lunch=None)

    class_repo.load.side_effect = switch({('Smith', 'C', 1): smith, ('Shea', 'F', 1): shea})
    class_repo.names_of_teachers_in_lunch.side_effect = switch({
        (1, 'C', 2): ['Messina', 'Smith', 'Caveney'],
        (1, 'C', 4): ['Emery', 'Gonzalez', 'Parsons']
    })

    lunchmates = [Student('divanovich2021', 'Daniel', is_public=False),
                  Student('azenith2021', 'Ayush', is_public=True)]

    student_repo.students_in_class.side_effect = switch({
        (1, 'C', 'Emery'): [lunchmates[1]],
        (1, 'C', 'Parsons'): [lunchmates[0]],
        (1, 'C', 'Gonzalez'): []
    })

    output = case.show_lunchmates(viewer, 1, 'C', 4)

    assert set(output) == set(lunchmates)

# If we decide to block private ones here, then we need to also check number against own_number
