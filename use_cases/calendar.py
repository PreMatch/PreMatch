import datetime
import io
from typing import List

import arrow
from arrow import Arrow
from ics import Calendar, Event, AudioAlarm

from entities.student import Student
from entities.types import Block, Name

BLOCK_SEQ = ['ACEG', 'BDF', [], 'ACEG', 'BDF']
BLOCK_LEN = datetime.timedelta(minutes=45)
START_TIME = datetime.time(8, 30, 0)
START_DATE = datetime.date(2020, 4, 6)
BLOCK_SPACING = datetime.timedelta(minutes=15)
TIMEZONE = datetime.timezone(-datetime.timedelta(hours=4))


class IcsCalendarCase:

    @staticmethod
    def generate_ics(calendar: Calendar) -> io.BytesIO:
        data = io.BytesIO()
        data.write(str(calendar).encode())
        return data

    @staticmethod
    def generate_april_break_calendar(student: Student) -> Calendar:
        return IcsCalendarCase.generate_calendar(student, start_date=datetime.date(2020, 4, 20),
                                                 end_date=datetime.date(2020, 4, 24))

    @staticmethod
    def generate_calendar_except_break(student: Student) -> Calendar:
        events = IcsCalendarCase.generate_calendar(student, end_date=datetime.date(2020, 4, 17)).events
        events.update(IcsCalendarCase.generate_calendar(student, start_date=datetime.date(2020, 4, 27)).events)

        cal = Calendar()
        cal.events = events
        return cal

    # end_date is included, if applicable
    @staticmethod
    def generate_calendar(student: Student, start_date: datetime.date = START_DATE,
                          end_date: datetime.date = datetime.date(2020, 5, 1)) -> Calendar:
        cal = Calendar()
        date = start_date
        while date <= end_date:
            if date.weekday() < len(BLOCK_SEQ):
                cal.events.update(IcsCalendarCase._generate_day_events(student, date))
            date += datetime.timedelta(days=1)

        return cal

    @staticmethod
    def _generate_day_events(student: Student, day: datetime.date) -> List[Event]:
        output = []
        time = arrow.get(datetime.datetime.combine(day, START_TIME, TIMEZONE))
        for block in BLOCK_SEQ[time.weekday()]:
            output.append(IcsCalendarCase._generate_event(
                block, teacher=student.semester_schedule(2)[block], begin=time))
            time += BLOCK_LEN + BLOCK_SPACING
        return output

    @staticmethod
    def _generate_event(block: Block, teacher: Name, begin: Arrow) -> Event:
        return Event(name=f'{block} Block with {teacher}',
                     begin=begin,
                     end=begin + BLOCK_LEN,
                     categories=['AHS at home', f'AHS at home: {block} Block'],
                     alarms=[AudioAlarm(-datetime.timedelta(minutes=5))])
