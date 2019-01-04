from itertools import chain
from typing import Optional, List, Tuple, Iterable

from google.cloud import datastore

DATABASE = datastore.Client()

Roster = List[Tuple[str, str]]
PrivacyRoster = List[Tuple[str, str, bool]]


def get_db() -> datastore.Client:
    return DATABASE


def db_query() -> datastore.query.Query:
    query = get_db().query(kind="Schedule")
    return query


def get_row_from_handle(handle: str) -> Optional[datastore.Entity]:
    entity = get_db().get(get_db().key('Schedule', handle))
    return entity


def handle_exists(handle: str) -> bool:
    return get_row_from_handle(handle) is not None


def schedule_count() -> int:
    query = get_db().query(kind='__Stat_Kind__')
    query.add_filter('kind_name', '=', 'Schedule')
    return list(query.fetch())[0]['count']


def db_entry(block: str, semester: int) -> str:
    return f'{block}{semester}'


def users_in_class(block: str, semester: int, teacher: str) -> List[datastore.Entity]:
    query = db_query()
    query.add_filter(db_entry(block, semester), '=', teacher)

    return list(query.fetch())


def lunch_number(block: str, semester: int, teacher: str) -> Optional[int]:
    key = get_db().key('Lunch', teacher)
    entity = get_db().get(key)

    return entity.get(db_entry(block, semester)) if entity is not None else None


def users_in_lunch(block: str, number: int, semester: int) -> List[datastore.Entity]:
    query: datastore.Query = get_db().query(kind='Lunch')
    query.add_filter(db_entry(block, semester), '=', number)

    teachers = map(lambda n: n['teacher'], query.fetch())
    return list(chain.from_iterable(map(
        lambda t: users_in_class(block, semester, t), teachers)))


def class_student_count(block: str, semester: int, teacher: str) -> int:
    return len(users_in_class(block, semester, teacher))


def is_admin(handle: str) -> bool:
    return handle in [
        'hpeng2021',
        'divanovich2021'
    ]


def search(query: str) -> Iterable[datastore.Entity]:
    users = db_query().fetch()

    def predicate(user: datastore.Entity) -> bool:
        name_match = query.lower() in user['name'].lower()
        handle_match = query.lower() in user['handle']
        return name_match or handle_match

    return filter(predicate, users)
