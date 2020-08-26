from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from entities.types import *

YearSchedule = Dict[Semester, SemesterSchedule]


@dataclass
class Student:
    handle: Handle
    name: Name
    discord_id: Optional[str] = None
    schedules: Optional[YearSchedule] = None
    is_public: bool = False
    cohort: Optional[Cohort] = None

    def semester_schedule(self, semester: Semester) -> Optional[SemesterSchedule]:
        if self.schedules is None:
            return None
        return self.schedules.get(semester)

    def graduating_year(self) -> Optional[int]:
        year_str = ''.join(filter(lambda char: char.isdigit(), self.handle))[:4]
        if len(year_str) == 0:
            return None
        return int(year_str)

    def __hash__(self):
        return hash(self.handle)
