from __future__ import annotations

import config
import database as db
from google.cloud import datastore
from typing import Mapping, Optional, List, Union, Iterable


class Reader:
    handle: str

    def __init__(self, handle: str):
        self.handle = handle

    def can_read(self, other: User) -> bool:
        return other.can_be_read_by_handle(self.handle)

    def read_class_roster(self, block: str, teacher: str) -> Iterable[User]:
        return self.read_entities(db.users_in_class(block, teacher))

    def read_lunch_roster(self, block: str, number: int) -> Iterable[User]:
        return self.read_entities(db.users_in_lunch(block, number))

    def search(self, query: str) -> List[User]:
        return list(filter(self.can_read,
                           map(User.from_entity,
                               db.search(query))))

    def read_entities(self, entities: Iterable[datastore.Entity]) \
            -> Iterable[User]:
        students = list(map(User.from_entity, entities))
        if self.handle in map(lambda u: u.handle, students):
            return students
        else:
            return filter(self.can_read, students)


class User(Reader):
    name: str
    teachers: Mapping[str, str]
    public: bool
    accepts_privacy: bool

    @staticmethod
    def from_db(handle: str) -> Optional[User]:
        if handle is None:
            return None
        row = db.get_row_from_handle(handle)
        return None if row is None else User.from_entity(row)

    @staticmethod
    def from_entity(row: datastore.Entity) -> User:
        teachers = dict(map(lambda p: (p, row.get(p)), config.all_block_keys()))
        return User(row['handle'], row['name'],
                    teachers, row['public'], row['accepts_privacy'])

    @staticmethod
    def all() -> Iterable[User]:
        return map(User.from_entity, db.db_query().fetch())

    def __init__(self, handle: str, name: str, teachers: Mapping[str, str], public: bool, accepts_privacy: bool):
        super().__init__(handle)
        self.name = name
        self.teachers = teachers
        self.public = public
        self.accepts_privacy = accepts_privacy

    def put_into_db(self):
        with db.get_db().transaction():
            db.get_db().put(self.db_entity())

    def db_entity(self) -> datastore.Entity:
        key = db.get_db().key('Schedule', self.handle)
        task = datastore.Entity(key=key)

        mapping = {
            'handle': self.handle,
            'name': self.name,
            'public': self.public,
            'accepts_privacy': self.accepts_privacy
        }
        mapping.update(self.teachers)
        task.update(mapping)

        return task

    def __eq__(self, other):
        return type(other) == User and other.handle == self.handle

    # == Privacy ==

    def can_be_read_by(self, reader: User) -> bool:
        return self.can_be_read_by_handle(reader.handle)

    def can_be_read_by_handle(self, handle: str) -> bool:
        return self.public or handle == self.handle

    # == Access ==

    def teacher(self, block: str, semester: int) -> str:
        return self.teachers[f'{block}{semester}']

    def semester_mapping(self, semester: int) -> Mapping[str, str]:
        mapping = {}
        for block in config.periods:
            mapping[block] = self.teacher(block, semester)
        return mapping

    # == Lunch ==

    def put_lunch(self, lunch_numbers: Mapping[str, int]) -> None:
        client = db.get_db()
        tasks: List[datastore.Entity] = []

        for semester in config.semesters:
            for block in config.lunch_blocks:
                number = lunch_numbers.get(block + semester)
                if number is not None:
                    task = self.db_lunch_task(block, int(semester), number)
                    tasks.append(task)

        if tasks:
            client.put_multi(tasks)

    def db_lunch_task(self, block, semester: int, number) -> datastore.Entity:
        key = db.get_db().key('Lunch', self.teacher(block, semester))
        task = db.get_db().get(key)
        if task:
            task[block] = int(number)
        else:
            task = datastore.Entity(key)
            task.update({
                'teacher': self.teacher(block, semester),
                f'{block}{semester}': int(number)
            })
        return task

    def lunch_number(self, block: str, semester: int) -> Optional[int]:
        return db.lunch_number(block, semester, self.teacher(block, semester))

    def lunch_numbers(self, semester: int) -> Mapping[str, Optional[int]]:
        return dict(map(lambda p: (p, self.lunch_number(p, semester)),
                        config.lunch_blocks))

    def full_lunch_mapping(self) -> Mapping[str, Optional[int]]:
        mapping = {}
        for semester in config.semesters:
            for block in config.periods:
                mapping[block + semester] = self.lunch_number(block, semester)
        return mapping

    def missing_some_lunch(self) -> bool:
        for semester in config.semesters:
            if None in self.lunch_numbers(int(semester)):
                return True
        return False

    # == Discord ==

    def put_discord_id(self, user_id: Union[int, str]) -> None:
        client = db.get_db()
        key: datastore.Key = client.key('Discord', str(user_id))

        task = datastore.Entity(key)
        task.update({'handle': self.handle})
        client.put(task)

    def get_discord_id(self) -> Optional[str]:
        query = db.get_db().query(kind='Discord')
        query.add_filter('handle', '=', self.handle)

        result = list(query.fetch())
        if len(result) == 0:
            return None
        return result[0].key.name
