from typing import List
from unittest.mock import MagicMock

import pytest

from tests.mock_helper import require
from use_cases.account import AccountCase
from use_cases.schedule import MissingScheduleError
from use_cases.types import *

auth = MagicMock()
student_repo = MagicMock()
class_repo = MagicMock()
discord_verifier = MagicMock()
account_case = AccountCase(auth, student_repo, class_repo, discord_verifier)

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
    class_repo.reset_mock()
    discord_verifier.reset_mock()


@pytest.fixture
def fill_class_repo():
    class_repo.load.return_value = Class('Desfosse', 'D', 1)


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


def test_update_lunch_bulk(mock_setup, fill_class_repo):
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

    expected_batch_update: List[Class] = [
        Class(sample_schedule[1]['B'], 'B', 1, lunch=1),
        Class(sample_schedule[1]['C'], 'C', 1, lunch=3),
        Class(sample_schedule[1]['E'], 'E', 1, lunch=2),
        Class(sample_schedule[1]['G'], 'G', 1, lunch=1),
        Class(sample_schedule[2]['E'], 'E', 2, lunch=4),
        Class(sample_schedule[1]['G'], 'G', 2, lunch=1)
    ]

    class_repo.update_batch.assert_called_once_with(expected_batch_update)


def test_update_lunch_without_schedule():
    student = Student('nschedule', 'None Schedule')
    with pytest.raises(MissingScheduleError, match='nschedule'):
        account_case.update_lunches(student, {1: {'C': 2, 'E': 4}})


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
