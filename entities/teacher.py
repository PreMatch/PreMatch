from entities.types import *
from __future__ import annotations


class Teacher:
    handle: Handle
    name: Name
    lunches: dict[Semester, SemesterLunches]
