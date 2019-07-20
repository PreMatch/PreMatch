from entities.types import *
from __future__ import annotations
from typing import Optional


class Student:
    handle: Handle
    name: Name
    discord_id: Optional[str]
    accepts_terms: bool
    accepts_privacy: bool
    schedules: dict[Semester, SemesterSchedule]
    is_public: bool
