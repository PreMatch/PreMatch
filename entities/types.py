from typing import Dict

Block = str
Handle = str
Name = str
# 1 <= LunchNumber <= 4
LunchNumber = int
# 1 <= Semester <= 2
Semester = int
# Location is either XXX (room number) or GYM/FIELD HOUSE, etc.
Location = str

SemesterSchedule = Dict[Block, Name]
SemesterLunches = Dict[Block, LunchNumber]

from enum import Enum

class Cohort(Enum):
    remote = 'remote'
    blue = 'blue'
    gold = 'gold'