from unittest.mock import MagicMock

import pytest

from entities.student import Student
from entities.types import Name
from mock_helper import require
from use_cases.account import AccountCase
from use_cases.schedule import MissingScheduleError
from use_cases.types import *

auth = MagicMock()
student_repo = MagicMock()
teacher_repo = MagicMock()
discord_verifier = MagicMock()
account_case = AccountCase(auth, student_repo, teacher_repo, discord_verifier)

sample_schedule = {
    1: {
        'A': 'Aubrey',
        'B': 'Gaudiano',
        'C': 'Michaud',
        'D': 'Givens',
        'E': 'Emery',
        'F': 'Parsons',
        'G': 'Reidy'
    },
    2: {
        'A': 'Aubrey',
        'B': 'Gaudiano',
        'C': 'Michaud',
        'D': 'Givens',
        'E': 'Messina',
        'F': 'Parsons',
        'G': 'Reidy'
    }
}


@pytest.fixture
def mock_setup():
    auth.reset_mock()
    student_repo.reset_mock()
    teacher_repo.reset_mock()
    discord_verifier.reset_mock()


@pytest.fixture
def fill_teacher_repo():
    teacher_repo.load.return_value = Teacher("Desfosse", "bdesfosse")


def test_call_auth_verify(mock_setup):
    auth.verify.return_value = ("hpeng2021", "Michael Peng")

    res = account_case.login('token')

    assert res == auth.verify.return_value
    auth.verify.assert_called_once_with('token')


def test_declare_public_saves(mock_setup):
    student = Student('hpeng2021', 'Michael Peng')
    student.is_public = False

    account_case.declare_public(student)

    assert student.is_public
    student_repo.save.assert_called_with(student)


def test_declare_private_saves(mock_setup):
    student = Student('hpeng2021', 'Michael Peng')
    student.is_public = True

    account_case.declare_private(student)

    assert not student.is_public
    student_repo.save.assert_called_once_with(student)


def test_update_schedule_saves(mock_setup):
    student = Student('hpeng2021', 'Michael Peng')

    account_case.update_schedule(student, sample_schedule)

    assert student.schedules == sample_schedule
    student_repo.save.assert_called_once_with(student)


def test_update_lunch_bulk(mock_setup, fill_teacher_repo):
    student = Student('hpeng2021', 'Michael Peng')
    student.schedules = sample_schedule

    lunch_updates = {
        1: {
            'B': 1,
            'C': 3,
            'E': 2,
            'G': 1
        },
        2: {
            'E': 4,
            'G': 1
        }
    }
    account_case.update_lunches(student, lunch_updates)

    expected_batch_update: Dict[Name, Dict[Semester, SemesterLunches]] = {
        sample_schedule[1]['B']: {1: {'B': 1}},
        sample_schedule[1]['C']: {1: {'C': 3}},
        sample_schedule[1]['E']: {1: {'E': 2}},
        sample_schedule[1]['G']: {1: {'G': 1}, 2: {'G': 1}},
        sample_schedule[2]['E']: {2: {'E': 4}}
    }

    teacher_repo.update_batch_lunch.assert_called_once_with(expected_batch_update)


def test_update_lunch_without_schedule():
    student = Student('nschedule', 'None Schedule')
    with pytest.raises(MissingScheduleError, match='nschedule'):
        account_case.update_lunches(student, {1: {'C': 2, 'E': 4}})


def test_accept_terms():
    student: Student = Student('divanovich2021', 'Daniel Ivanovich')
    student.accepts_terms = False

    account_case.accept_terms(student)

    assert student.accepts_terms


def test_accept_privacy():
    student: Student = Student('divanovich2021', 'Daniel Ivanovich')
    student.accepts_privacy = False

    account_case.accept_privacy(student)

    assert student.accepts_privacy


def test_discord_user_init():
    user_info = {
        'id': '101391209481209312',
        'avatar': '190843fac09848fa-avatar',
        'username': 'Test User',
        'discriminator': '#4515'
    }
    user = DiscordUser(user_info)

    assert user.username == user_info['username']
    assert user.avatar == user_info['avatar']
    assert user.id == user_info['id']
    assert user.discriminator == user_info['discriminator']


def test_discord_avatar_url():
    user_info = {
        'id': '101391209481209312',
        'avatar': '190843fac09848fa-avatar',
        'username': 'Test User',
        'discriminator': '#4515'
    }
    user = DiscordUser(user_info)

    assert user.avatar_url() \
           == f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png'


def test_integrate_discord_without_schedule():
    student = Student('hpeng2021', 'Michael')
    with pytest.raises(MissingScheduleError, match=student.handle):
        account_case.integrate_discord(student, 'code', 'state')


def test_integrate_discord_passed_to_verifier(mock_setup):
    student = Student('hpeng2021', 'Michael')
    student.schedules = {1: {'A': 'Shea', 'B': 'Gaudiano', 'C': 'Ream'}}
    user = DiscordUser({
        'id': '101391209481209312',
        'avatar': '190843fac09848fa-avatar',
        'username': 'Test User',
        'discriminator': '#4515'
    })
    discord_verifier.verify.side_effect = require(('code', 'state'), user)

    output = account_case.integrate_discord(student, 'code', 'state')

    assert output == user


def test_integrate_discord_saves_association(mock_setup):
    student = Student('hpeng2021', 'Michael')
    student.schedules = {1: {'A': 'Holm-Andersen', 'B': 'Gonzalez', 'C': 'Caveney'}}
    user = DiscordUser({
        'id': '101391209481209312',
        'avatar': '190843fac09848fa-avatar',
        'username': 'Test User',
        'discriminator': '#4515'
    })
    discord_verifier.verify.return_value = user

    account_case.integrate_discord(student, 'code', 'state')

    assert student.discord_id == user.id
    student_repo.save.assert_called_once_with(student)
