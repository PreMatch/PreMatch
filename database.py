from typing import Optional, List, Iterable, Tuple, Mapping, Union, cast

from google.cloud import datastore

from config import periods

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


def add_schedule(handle: str, name: str, sched_list: List[str], public: bool) -> None:
    if handle_exists(handle):
        raise Exception('Schedule with handle {} already exists'.format(handle))

    key = get_db().key('Schedule', handle)
    data = {
        'handle': handle,
        'name': name,
        'public': public
    }

    for i in range(len(sched_list)):
        data[periods[i]] = sched_list[i]

    task = datastore.Entity(key)
    task.update(data)

    get_db().put(task)


def update_schedule(handle: str, sched_list: List[str], public: Optional[bool]) -> None:
    client = get_db()
    with client.transaction():
        key = client.key('Schedule', handle)
        task = client.get(key)

        if task:
            for i in range(len(sched_list)):
                task[periods[i]] = sched_list[i]
            if public is not None:
                task['public'] = public
            client.put(task)


def can_read(viewer_handle: str, handle: str) -> bool:
    target = get_row_from_handle(handle)
    return target is not None and (target.get('public') or viewer_handle == handle)


def user_schedule(viewer_handle: str, handle: str) -> Optional[datastore.Entity]:
    row = get_row_from_handle(handle)
    if can_read(viewer_handle, handle):
        return row


def user_name(handle: str) -> Optional[str]:
    row = get_row_from_handle(handle)

    return None if row is None else row['name']


def users_in_class(block: str, teacher: str) -> List[datastore.Entity]:
    query = db_query()
    query.add_filter(block, '=', teacher)

    return list(query.fetch())


def in_roster_form(entity_iterator: Iterable[datastore.Entity]) -> Roster:
    return list(map(lambda row: (row['name'], row['handle']), entity_iterator))


def class_roster(period: str, teacher: str, sort: bool = True) -> Roster:
    matrix = in_roster_form(users_in_class(period, teacher))

    return sorted(matrix, key=lambda row: row[0]) if sort else matrix


def search_user(searcher: str, search_query: str) -> PrivacyRoster:
    query = db_query()
    users = list(query.fetch())

    def predicate(user: datastore.Entity) -> bool:
        name_match = search_query.lower() in user['name'].lower()
        handle_match = search_query.lower() in user['handle']

        return name_match or handle_match

    return inject_privacy(searcher, in_roster_form(filter(predicate, users)))


def user_in_roster(user_handle: str, roster: Roster) -> bool:
    return any(map(lambda entry: user_handle == entry[1], roster))


def upsert_lunch(handle: str, lunch_numbers: Mapping[str, int]) -> None:
    if not handle_exists(handle):
        raise Exception(f'Schedule with handle {handle} does not exist')

    schedule = cast(datastore.Entity, get_row_from_handle(handle))

    for block in periods[2:]:
        number = lunch_numbers.get(block)
        if number is not None:
            teacher = schedule[block]
            add_lunch_number(teacher, block, int(number))


def add_lunch_number(teacher: str, block: str, number: int) -> None:
    client = get_db()
    key = client.key('Lunch', teacher)
    task = client.get(key)

    if task:
        task[block] = int(number)
    else:
        task = datastore.Entity(key)
        task.update({
            'teacher': teacher,
            block: int(number)
        })

    client.put(task)


def lunch_roster(block: str, number: int, sort=True) -> Roster:
    query: datastore.Query = get_db().query(kind='Lunch')
    query.add_filter(block, '=', number)

    applicable_teachers: Iterable[str] = map(
        lambda entity: entity['teacher'], query.fetch())

    roster: Roster = []
    for teacher in applicable_teachers:
        roster += class_roster(block, teacher, sort=False)

    return sorted(roster, key=lambda row: row[0]) if sort else roster


def lunch_number(block: str, teacher: str) -> Optional[int]:
    key = get_db().key('Lunch', teacher)
    entity = get_db().get(key)

    return entity.get(block) if entity is not None else None


def lunch_numbers(viewer_handle: str, handle: str) -> Mapping[str, Optional[int]]:
    if user_schedule(viewer_handle, handle) is None:
        return {}

    schedule = cast(datastore.Entity, get_row_from_handle(handle))
    return dict(map(
        lambda block: (block, lunch_number(block, schedule[block])), periods[2:]))


def record_discord_assoc(handle: str, user_id: Union[int, str]) -> None:
    client = get_db()
    key: datastore.Key = client.key('Discord', str(user_id))
    task = datastore.Entity(key)

    task.update({
        'handle': handle
    })

    client.put(task)


def get_assoc_discord_id(handle: str) -> Optional[str]:
    query = get_db().query(kind='Discord')
    query.add_filter('handle', '=', handle)

    result = list(query.fetch())
    if len(result) == 0:
        return None

    return result[0].key.name


def missing_some_lunch(handle: str) -> bool:
    schedule = get_row_from_handle(handle)
    if schedule is None:
        return True

    for block in periods[2:]:
        if lunch_number(block, schedule[block]) is None:
            return True

    return False


def is_admin(handle: str) -> bool:
    return handle in [
        'hpeng2021',
        'divanovich2021'
    ]


def roster_of_all() -> Roster:
    return in_roster_form(get_db().query(kind='Schedule').fetch())


def restrict_roster(viewer: str, roster: Roster) -> Roster:
    if user_in_roster(viewer, roster):
        return roster
    else:
        return list(filter(lambda entry: can_read(viewer, entry[1]), roster))


def inject_privacy(viewer: str, roster: Roster) -> PrivacyRoster:
    return list(map(lambda entry: (entry[0], entry[1], can_read(viewer, entry[1])), roster))


def has_public_schedule(handle: str) -> bool:
    schedule = get_row_from_handle(handle)
    if schedule is None:
        return False
    return schedule.get('public')
