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
  query = get_db().query(kind='__Stat_Kind__')
  query.add_filter('kind_name', '=', 'Schedule')
  return list(query.fetch())[0]['count']


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


def in_roster_form(entity_iterator):
  return list(map(lambda row: (row['name'], row['handle']), entity_iterator))


def class_roster(period, teacher, sort=True):
  matrix = in_roster_form(users_in_class(period, teacher))

  return sorted(matrix, key=lambda row: row[0]) if sort else matrix


def search_user(search_query):
  query = db_query()
  users = list(query.fetch())

  return list(filter(lambda user:
                     search_query.lower() in user[
                       'name'].lower() or search_query.lower() in user[
                       'handle'], users))


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


def upsert_lunch(handle, lunch_numbers):
  if not handle_exists(handle):
    raise Exception(f'Schedule with handle {handle} does not exist')

  schedule = user_schedule(handle)

  for block in PERIODS[2:]:
    number = lunch_numbers.get(block)
    if number is not None:
      teacher = schedule[block]
      add_lunch_number(teacher, block, int(number))


def add_lunch_number(teacher, block, number):
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


def lunch_roster(block, number, sort=True):
  if number is None:
    return None

  query = get_db().query(kind='Lunch')
  query.add_filter(block, '=', number)
  applicable_teachers = map(
      lambda entity: entity['teacher'], query.fetch())

  roster = []
  for teacher in applicable_teachers:
    roster += class_roster(block, teacher, sort=False)

  return sorted(roster, key=lambda row: row[0]) if sort else roster


def lunch_number(block, teacher):
  key = get_db().key('Lunch', teacher)
  entity = get_db().get(key)

  return entity.get(block) if entity is not None else None


def lunch_numbers(handle):
  if not handle_exists(handle):
    return {}

  schedule = user_schedule(handle)
  return dict(map(
      lambda block: (block, lunch_number(block, schedule[block])), PERIODS[2:]))


def record_discord_assoc(handle, user_id):
  client = get_db()
  key = client.key('Discord', user_id)
  task = datastore.Entity(key)

  task.update({
    'handle': handle
  })

  client.put(task)


def get_assoc_discord_id(handle):
  query = get_db().query(kind='Discord')
  query.add_filter('handle', '=', handle)

  result = list(query.fetch())
  if len(result) == 0:
    return None

  return result[0].key.name


def missing_some_lunch(handle):
  schedule = user_schedule(handle)
  if schedule is None:
    return True

  for block in PERIODS[2:]:
    if lunch_number(block, schedule[block]) is None:
      return True

  return False


def is_admin(handle):
  return handle in [
    'hpeng2021',
    'divanovich2021'
  ]


def roster_of_all():
  return in_roster_form(get_db().query(kind='Schedule').fetch())