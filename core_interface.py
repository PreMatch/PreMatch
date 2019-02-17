from abc import ABC, abstractmethod
from user import User, Reader
from typing import Iterable, Mapping, Optional, Iterator


class Roster(Iterable[User]):
    students: list[User]

    def __init__(self, students: list[User]):
        self.students = students

    def __iter__(self) -> Iterator[User]:
        for student in students:
            if self.visible(student):
                yield student

    def count(self):
        return len(self.students)

    def visible(self, student: User) -> bool:
        return

class IPreMatchCore(ABC):
    @abstractmethod
    def search(self, searcher: Reader, term: str) -> Iterable[User]:
        pass

    @abstractmethod
    def view_schedule(self, viewer: Reader, user: User, semester: int) -> Optional[Mapping[str, str]]:
        pass

    @abstractmethod
    def view_roster(self, viewer: Reader, teacher: str, block: str, semester: int) -> Roster: