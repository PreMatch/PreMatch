from database import *
from pprint import pprint


def a(n, blk, ln):
    res = search_user(n)
    pprint(list(enumerate(map(lambda l: l['name'], res))))
    ent = res[int(input('index:'))]

    if lunch_number(blk, ent[blk]) == ln:
        print('Already in')
    else:
        add_lunch_number(ent[blk], blk, ln)
