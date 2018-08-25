from google.cloud import datastore
from flask import g

PERIODS = 'ABCDEFG'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = datastore.Client()
    return db


def db_query():
    query = get_db().query(kind="Schedule")
    return query


def get_row_from_handle(handle):
    entity = get_db().get(get_db().key('Schedule', handle))
    return entity


def handle_exists(handle):
    return get_row_from_handle(handle) is not None


def schedule_count():
    return len(list(get_db().query(kind="Schedule").fetch()))


def add_schedule(handle, name, sched_list):
    if handle_exists(handle):
        raise Exception('Schedule with handle {} already exists'.format(handle))

    key = get_db().key('Schedule', handle)
    data = {
        'handle': handle,
        'name': name
    }

    for i in range(len(sched_list)):
        data[PERIODS[i]] = sched_list[i]

    task = datastore.Entity(key)
    task.update(data)

    get_db().put(task)


def update_schedule(handle, sched_list):
    client = get_db()
    with client.transaction():
        key = client.key('Schedule', handle)
        task = client.get(key)

        if task:
            for i in range(len(sched_list)):
                task[PERIODS[i]] = sched_list[i]
            client.put(task)


def user_schedule(handle):
    return get_row_from_handle(handle)


def user_name(handle):
    row = get_row_from_handle(handle)

    return None if row is None else row['name']


def class_roster(period, teacher):
    query = db_query()
    query.add_filter(period, '=', teacher)

    return list(map(lambda row: (row['name'], row['handle']), list(query.fetch())))


def search_user(search_query):
    query = db_query()
    users = list(query.fetch())

    return list(filter(lambda user:
                       search_query.lower() in user['name'].lower() or search_query.lower() in user['handle'], users))
