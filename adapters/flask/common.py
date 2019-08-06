from dataclasses import dataclass
from typing import Any

from flask import *

import ahs_calendar
from use_cases.account import AccountCase
from use_cases.schedule import ScheduleCase
from use_cases.search import SearchCase
from use_cases.types import DiscordVerifier, StudentRepository, TeacherRepository, AuthProvider

DEFAULT_HOME = '/dashboard'


def error(code, message):
    return render_template('error.html', code=code, error=message), code


def error_private(handle):
    flash(f'The user {handle} has decided to make their schedule private')
    return redirect('/')


def error_no_own_schedule():
    flash('You need to enter your schedule first', 'error')
    return redirect('/update')


def demand(truth: bool, message: str):
    if not truth:
        raise ValidationError(message)


def missing_form_field(key: str) -> bool:
    return key not in request.form or empty(request.form[key])


def empty(string: Any) -> bool:
    return str(string).strip() == ''


class ValidationError(Exception):
    def __init__(self, problem):
        self.problem = problem


def should_countdown():
    return ahs_calendar.current_semester() is None and ahs_calendar.before_schedule_release()


@dataclass
class App:
    account: AccountCase
    schedule: ScheduleCase
    search: SearchCase


@dataclass
class Adapters:
    discord: DiscordVerifier
    student_repo: StudentRepository
    teacher_repo: TeacherRepository
    google: AuthProvider


adapt: Adapters
app: App
