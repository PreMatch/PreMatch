from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict

from entities.types import *

YearSchedule = Dict[Semester, SemesterSchedule]


@dataclass
class Student:
    handle: Handle
    name: Name
    discord_id: Optional[str] = None
    accepts_terms: bool = False
    accepts_privacy: bool = False
    schedules: Optional[YearSchedule] = None
    is_public: bool = False

    def semester_schedule(self, semester: Semester) -> Optional[SemesterSchedule]:
        if self.schedules is None:
            return None
        return self.schedules.get(semester)

    def __hash__(self):
        return hash(self.handle)