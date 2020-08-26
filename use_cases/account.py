from dataclasses import dataclass
from typing import List

from entities.klass import Class
from entities.student import Student, YearSchedule
from entities.types import *
from use_cases.schedule import MissingScheduleError
from use_cases.types import AuthProvider, StudentRepository, DiscordVerifier, DiscordUser, ClassRepository


@dataclass
class AccountCase:
    auth_prov: AuthProvider
    student_repo: StudentRepository
    class_repo: ClassRepository
    discord_verifier: DiscordVerifier

    def login(self, token: str) -> (Handle, Name):
        return self.auth_prov.verify(token)

    def declare_public(self, student: Student):
        student.is_public = True
        self.student_repo.save(student)

    def declare_private(self, student: Student):
        student.is_public = False
        self.student_repo.save(student)

    def update_schedule(self, student: Student, new_schedule: YearSchedule):
        student.schedules = new_schedule
        self.student_repo.save(student)

    def update_lunches(self, student: Student, update: Dict[Semester, SemesterLunches]):
        batch_update: List[Class] = []

        for (semester, lunches) in update.items():
            schedule = student.semester_schedule(semester)
            if schedule is None:
                raise MissingScheduleError(student)
            for (block, number) in lunches.items():
                batch_update.append(Class(schedule[block], block, semester, lunch=number))

        self.class_repo.update_batch(batch_update)

    def integrate_discord(self, student: Student, code: str, state: str) -> DiscordUser:
        if student.schedules is None:
            raise MissingScheduleError(student)

        user = self.discord_verifier.verify(code, state)
        student.discord_id = user.id
        self.student_repo.save(student)

        return user
