from google.cloud import datastore

PERIODS = 'ABCDEFG'
DATABASE = datastore.Client()


def get_db():
    return DATABASE


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


def users_in_class(period, teacher):
    query = db_query()
    query.add_filter(period, '=', teacher)

    return list(query.fetch())


def class_roster(period, teacher):
    return list(map(lambda row: (row['name'], row['handle']), users_in_class(period, teacher)))


def search_user(search_query):
    query = db_query()
    users = list(query.fetch())

    return list(filter(lambda user:
                       search_query.lower() in user['name'].lower() or search_query.lower() in user['handle'], users))


def most_common_classmates(handle):
    frequency = {}
    max_hit_rate = 0
    max_users = []

    schedule = user_schedule(handle)

    for period in PERIODS:
        for classmate in users_in_class(period, schedule[period]):
            u_handle = classmate['handle']
            if u_handle != handle:

                if u_handle not in frequency:
                    frequency[u_handle] = 1
                else:
                    frequency[u_handle] += 1

                new_freq = frequency[u_handle]
                if new_freq > max_hit_rate:
                    max_hit_rate = new_freq
                    max_users = [classmate]
                elif new_freq == max_hit_rate:
                    max_users.append(classmate)

    if max_hit_rate < 2:
        return None

    return list(max_users), max_hit_rate


def lunch_exists_for_handle(handle):
    key = get_db().key('Lunch', handle)

    return get_db().get(key) is not None


def upsert_lunch(handle, lunch):
    if not handle_exists(handle):
        raise Exception(f'Schedule with handle {handle} does not exist')

    client = get_db()

    key = client.key('Lunch', handle)
    task = datastore.Entity(key=key)

    contents = {
        'handle': handle
    }
    for block in PERIODS[2:]:
        contents[block] = lunch[block]

    task.update(contents)
    client.put(task)