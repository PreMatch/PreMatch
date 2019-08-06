from entities.types import *

LUNCH_BLOCKS = list('CDEFG')
BLOCKS = list('ABCDEFG')


def valid_semester_string(sem: str) -> bool:
    return sem in list('12')


def valid_semester(sem: Semester) -> bool:
    return valid_semester_string(str(sem))


def valid_lunch_block(block: Block) -> bool:
    return block in LUNCH_BLOCKS


def valid_block(block: Block) -> bool:
    return block in BLOCKS
