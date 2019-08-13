from dataclasses import dataclass
from typing import Optional, Iterable

from entities.student import Student
from entities.types import *
from use_cases.types import StudentRepository, TeacherRepository


@dataclass
class MissingScheduleError(ValueError):
    student: Student


@dataclass
class ScheduleCase:
    student_repo: StudentRepository
    teacher_repo: TeacherRepository

    # May raise KeyError if semester invalid or schedule not defined
    @staticmethod
    def own_schedule(student: Student, semester: Semester) -> SemesterSchedule:
        output = student.semester_schedule(semester)
        if output is None:
            raise MissingScheduleError(student)
        return output

    @staticmethod
    def show_schedule(viewer: Student, target: Student, semester: Semester) -> SemesterSchedule:
        """ Missing blocks means 'Private'; MissingScheduleError means not available """
        schedule = target.semester_schedule(semester)
        if schedule is None:
            raise MissingScheduleError(target)

        if target.is_public:
            return schedule

        viewer_schedule = viewer.semester_schedule(semester)
        if viewer_schedule is None:
            return {}

        return dict(set(schedule.items()) & set(viewer_schedule.items()))

    def show_classmates(self, viewer: Student, semester: Semester, block: Block) -> Optional[Iterable[Student]]:
        schedule = viewer.semester_schedule(semester)
        if schedule is None:
            raise MissingScheduleError(viewer)

        roster = self.student_repo.students_in_class(semester, block, schedule[block])
        return roster

    def show_lunch_number(self, target: Student, semester: Semester, block: Block) -> Optional[LunchNumber]:
        """ None: teacher does not have this lunch recorded
        MissingScheduleError: viewer has no schedule """
        schedule = target.semester_schedule(semester)
        if schedule is None:
            raise MissingScheduleError(target)
        teacher = self.teacher_repo.load(schedule[block])
        return teacher.lunch_number(semester, block)

    # may raise ValueError or MissingScheduleError
    def show_lunchmates(self, viewer: Student, semester: Semester,
                        block: Block, number: LunchNumber) -> Iterable[Student]:
        schedule = viewer.semester_schedule(semester)
        if schedule is None:
            raise MissingScheduleError(viewer)

        own_teacher = self.teacher_repo.load(schedule[block])
        own_number = own_teacher.lunch_number(semester, block)

        teachers = self.teacher_repo.names_of_teachers_in_lunch(semester, block, number)

        for teacher in teachers:
            yield from self.student_repo.students_in_class(semester, block, teacher)
