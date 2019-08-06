from dataclasses import dataclass
from typing import Iterable

from entities.student import Student
from use_cases.types import StudentRepository


@dataclass
class SearchCase:
    student_repo: StudentRepository

    def perform_search(self, query: str) -> Iterable[Student]:
        return self.student_repo.search(query)
