from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Iterable

from entities.klass import Class
from entities.student import Student
from entities.types import *


class AuthProvider(ABC):
    # May raise ValueError
    @abstractmethod
    def verify(self, token: str) -> (Handle, Name):
        raise NotImplementedError()


class StudentRepository(ABC):
    @abstractmethod
    def save(self, student: Student):
        raise NotImplementedError()

    @abstractmethod
    def exists(self, handle: Handle) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def load(self, handle: Handle) -> Optional[Student]:
        raise NotImplementedError()

    @abstractmethod
    def students_in_class(self, semester: Semester, block: Block, teacher_name: Name) -> Iterable[Student]:
        raise NotImplementedError()

    @abstractmethod
    def search(self, query: str) -> Iterable[Student]:
        raise NotImplementedError()

    @abstractmethod
    def user_count(self) -> int:
        raise NotImplementedError()


class ClassRepository(ABC):
    @abstractmethod
    def save(self, klass: Class):
        raise NotImplementedError()

    @abstractmethod
    def exists(self, teacher: Name, block: Block, semester: Semester) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def load(self, teacher: Name, block: Block, semester: Semester) -> Optional[Class]:
        raise NotImplementedError()

    @abstractmethod
    def update_batch(self, classes: Iterable[Class]):
        raise NotImplementedError()

    @abstractmethod
    def names_of_teachers_in_lunch(self, semester: Semester,
                                   block: Block, number: LunchNumber) -> Iterable[Name]:
        raise NotImplementedError()

    @abstractmethod
    def list_teacher_names(self) -> Iterable[Name]:
        raise NotImplementedError()


class DiscordVerifier(ABC):
    # throws PermissionError if code/state validation failed, KeyError if state invalid
    @abstractmethod
    def verify(self, code: str, state: str) -> DiscordUser:
        raise NotImplementedError()


class DiscordUser:
    user_info: Dict[str, str]

    def __init__(self, user_info: dict):
        self.user_info = user_info

    def __getattr__(self, item):
        return self.user_info[item]

    def avatar_url(self) -> str:
        return f'https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png'
