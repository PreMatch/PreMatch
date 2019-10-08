from typing import Dict

Block = str
Handle = str
Name = str
# 1 <= LunchNumber <= 4
LunchNumber = int
# 1 <= Semester <= 2
Semester = int

SemesterSchedule = Dict[Block, Name]
SemesterLunches = Dict[Block, LunchNumber]
