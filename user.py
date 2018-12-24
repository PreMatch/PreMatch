from __future__ import annotations

import database as db
from google.cloud import datastore
from typing import Mapping, Optional, List, Union, Iterable
import config


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
        teachers = dict(map(lambda p: (p, row.get(p)), config.periods))
        return User(row['handle'], row['name'],
                    teachers, row['public'], row['accepts_privacy'])

    @staticmethod
    def all() -> Iterable[User]:
        return map(User.from_entity, db.db_query().fetch())

    def __init__(self, handle: str, name: str, teachers: Mapping[str, str],
        public: bool, accepts_privacy: bool):
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

    # == Lunch ==

    def put_lunch(self, lunch_numbers: Mapping[str, int]) -> None:
        client = db.get_db()
        tasks: List[datastore.Entity] = []

        for block in config.lunch_blocks:
            number = lunch_numbers.get(block)
            if number is not None:
                task = self.db_lunch_task(block, number)
                tasks.append(task)

        if tasks:
            client.put_multi(tasks)

    def db_lunch_task(self, block, number) -> datastore.Entity:
        key = db.get_db().key('Lunch', self.teachers[block])
        task = db.get_db().get(key)
        if task:
            task[block] = int(number)
        else:
            task = datastore.Entity(key)
            task.update({
                'teacher': self.teachers[block],
                block: int(number)
            })
        return task

    def lunch_number(self, block: str) -> Optional[int]:
        return db.lunch_number(block, self.teachers[block])

    def lunch_numbers(self) -> Mapping[str, Optional[int]]:
        return dict(map(lambda p: (p, self.lunch_number(p)),
                        config.lunch_blocks))

    def missing_some_lunch(self) -> bool:
        return None in self.lunch_numbers().values()

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
