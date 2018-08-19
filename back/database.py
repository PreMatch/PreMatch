import sqlite3
from flask import g

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('users.db')
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    get_db().execute(query, args)
    get_db().commit()

def handle_exists(handle):
    return query_db('select A from schedule where handle is ?', [handle], one=True) is not None

def remove_schedule(handle):
    modify_db('delete from schedule where handle is ?', [handle])

def add_schedule(handle, name, sched_list):
    if (handle_exists(handle)):
        raise Exception('Schedule with handle {} already exists'.format(handle))
    modify_db('insert into schedule values (?,?,?,?,?,?,?,?,?,?)', [handle, name] + sched_list)

def update_schedule(handle, sched_list):
    modify_db('update schedule set A=?,B=?,C=?,D=?,E=?,F=?,G=?,H=? where handle is ?',
        list(sched_list) + [handle])

def user_schedule(handle):
    return query_db('select A,B,C,D,E,F,G,H from schedule where handle is ?', [handle], one=True)

def user_auth(handle):
    return query_db('select name,salt,pepper,passhash from auth where handle is ?', [handle], one=True)

def class_roster(period, teacher):
    result = query_db('select name,handle from schedule where {} is ?'.format(period), (teacher,))
    return list(map(lambda i: i.values, result))

def search_user(query):
    pattern = '%' + query + '%'
    return query_db('select name,handle from schedule where name like ? or handle like ?', (pattern, pattern))