import datetime
from dataclasses import dataclass
from itertools import chain
from typing import Tuple, Optional, List, Iterable, Dict

from arrow import Arrow
from ics import Event, AudioAlarm, Calendar

from use_cases.calendar import TIMEZONE


@dataclass
class APTest:
    subject: str
    date: Tuple[int, int]
    time: Tuple[int, int]
    # a brief description of what's covered on the exam. For example, 'DBQ with 5 documents covering units 3-7'
    description: Optional[str] = None

    def calendar_entry(self) -> Event:
        return Event(
            name=f'AP {self.subject} Exam',
            begin=Arrow(2020, self.date[0], self.date[1],
                        self.time[0], self.time[1], tzinfo=TIMEZONE),
            duration=datetime.timedelta(minutes=45),
            description=self.description,
            categories=['AP Exams 2020'],
            alarms=[
                AudioAlarm(-datetime.timedelta(minutes=30)),
                AudioAlarm(-datetime.timedelta(minutes=45))
            ])


AP_TIMES = [(12, 0), (14, 0), (16, 0)]
AP_BEGIN_DATE = (5, 11)
AP_MAKEUP_BEGIN_DATE = (6, 1)


# Entry: tuple(subject, description (optional))
def process_day_subjects(date: Tuple[int, int], entries: List[List[str]]) -> List[APTest]:
    assert len(entries) == len(AP_TIMES)
    return [APTest(subject, date, time, AP_TEST_DESCRIPTIONS[subject])
            for (blk_entries, time) in zip(entries, AP_TIMES) for subject in blk_entries]


def exam_dates(begin: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
    date = Arrow(2020, begin[0], begin[1], tzinfo=TIMEZONE)
    while True:
        yield date.date().month, date.date().day
        while True:
            date = date.shift(days=1)
            if date.isoweekday() < 6:
                break


def process_schedule_table(table: List[List[List[str]]], begin: Tuple[int, int]) -> List[APTest]:
    return list(chain.from_iterable([process_day_subjects(date, day_entries)
                                     for (day_entries, date) in zip(table, exam_dates(begin))]))


AP_TEST_DESCRIPTIONS = {
    'Art History': 'Two essays (FRQ 1 and FRQ 6) covering Units 1-6',
    'Biology': 'Two FRQs (FRQ 1 and FRQ 4) covering Units 1-6',
    'Calculus AB': 'Two Multi-focus FRQs covering Units 1-7',
    'Calculus BC': 'Two Multi-focus FRQs covering Units 1-8, 10.2, 10.5, 10.7, '
                   '10.8, and 10.11',
    'Chemistry': 'Two long FRQs covering Units 1-7',
    'Chinese Language and Culture': 'Conversation and Cultural Presentation covering Units 1-4',
    'Comparative Government and Politics': 'An Argument Essay and Quantitative Analysis covering Units 1-3',
    'Computer Science A (Java)': 'An FRQ on Array/ArrayList and an FRQ on Methods '
                                 'and Control Structures covering Units 1-7',
    'English Language and Composition': 'Rhetorical Analysis covering Units 1-7',
    'English Literature and Composition': 'A Prose Fiction Analysis covering '
                                          'Units 1-7',
    'Environmental Science': 'Two FRQs (FRQ 1 and FRQ 2) covering Units 1-7',
    'European History': 'A modified DBQ with 5 sources covering Units 1-7',
    'French Language and Culture': 'Conversation and Cultural Comparison covering Units 1-4',
    'German Language and Culture': 'Conversation and Cultural Comparison covering Units 1-4',
    'Human Geography': 'A Two-Stimulus FRQ and a One-Stimulus FRQ covering Units '
                       '1-5',
    'Italian Language and Culture': 'Conversation and Cultural Comparison covering Units 1-4',
    'Japanese Language and Culture': 'Conversation and Cultural Perspective Presentation '
                                     'covering Units 1-4',
    'Latin': 'Two Short Answer Questions covering Units 1-4',
    'Macroeconomics': 'Two short FRQs and one long FRQ covering Units 1-5',
    'Microeconomics': 'Two short FRQs and one long FRQ (FRQ 1) covering Units 1-5',
    'Music Theory': '2 Part-Writing Questions and Sight-singing covering Units 1-6',
    'Physics 1': 'A Qualitative/Quantitative Translation and a Paragraph Argument '
                 'Short Answer covering Units 1-7',
    'Physics 2': 'A Qualitative/Quantitative Translation and a Paragraph Argument '
                 'Short Answer covering Units 1-5',
    'Physics C: Electricity and Magnetism': 'Two FRQs covering Units 1-3',
    'Physics C: Mechanics': 'Two FRQs covering Units 1-5',
    'Psychology': 'Concept Application and Research Methods covering Units 1-7',
    'Spanish Language and Culture': 'Conversation and Cultural Comparison covering Units 1-4',
    'Spanish Literature and Culture': 'A Text Comparison Essay and a Text & Art '
                                      'Comparison Short Answer covering Units 1-6',
    'Statistics': 'Two Multi-focus FRQs covering Units 1-7',
    'U.S. Government and Politics': 'An Argument Essay and a Concept Application '
                                    'covering Units 1-3',
    'U.S. History': 'A modified DBQ with 5 sources covering Units 3-7',
    'World History: Modern': 'A modified DBQ with 5 sources covering Units 1-6'
}

AP_TEST_TABLE = [
    [['Physics C: Mechanics'],
     ['Physics C: Electricity and Magnetism'],
     ['U.S. Government and Politics']],
    [['Latin'], ['Calculus AB', 'Calculus BC'], ['Human Geography']],
    [['Physics 2'], ['English Literature and Composition'], ['European History']],
    [['Spanish Literature and Culture'], ['Chemistry'], ['Physics 1']],
    [['Art History'], ['U.S. History'], ['Computer Science A (Java)']],
    # Week 2
    [['Chinese Language and Culture'], ['Biology'], ['Environmental Science']],
    [['Music Theory'], ['Psychology'],
     ['Japanese Language and Culture', 'Italian Language and Culture']],
    [['German Language and Culture'], ['English Language and Composition'], ['Microeconomics']],
    [['French Language and Culture'], ['World History: Modern'], ['Macroeconomics']],
    [['Comparative Government and Politics'], ['Statistics'], ['Spanish Language and Culture']]
]

AP_MAKEUP_TEST_TABLE = [
    [
        ['U.S. Government and Politics', 'Physics C: Mechanics'],
        ['Human Geography', 'Physics C: Electricity and Magnetism'],
        ['Calculus AB', 'Calculus BC', 'Latin']
    ],
    [
        ['English Literature and Composition', 'Spanish Literature and Culture'],
        ['Physics 1', 'European History'],
        ['Chemistry', 'Physics 2']
    ],
    [
        ['U.S. History', 'Chinese Language and Culture'],
        ['Environmental Science', 'Computer Science A (Java)'],
        ['Biology', 'Art History']
    ],
    [
        ['World History: Modern', 'Macroeconomics'],
        ['Spanish Language and Culture', 'Comparative Government and Politics'],
        ['Statistics', 'French Language and Culture']
    ],
    [
        ['English Language and Composition', 'German Language and Culture'],
        ['Japanese Language and Culture', 'Italian Language and Culture', 'Microeconomics'],
        ['Psychology', 'Music Theory']
    ]
]


def generate_test_lookup_dict(table, begin_date) -> Dict[str, APTest]:
    return dict([(test.subject, test) for test in process_schedule_table(table, begin_date)])


AP_TESTS = generate_test_lookup_dict(AP_TEST_TABLE, AP_BEGIN_DATE)
AP_MAKEUP_TESTS = generate_test_lookup_dict(AP_MAKEUP_TEST_TABLE, AP_MAKEUP_BEGIN_DATE)


# raises KeyError for unknown subject
def exam_events(subjects: Iterable[str], makeup: bool = False) -> Iterable[APTest]:
    if makeup:
        return (AP_MAKEUP_TESTS[subject] for subject in subjects)
    else:
        return (AP_TESTS[subject] for subject in subjects)


def calendar_of_exams(tests: Iterable[APTest]) -> Calendar:
    return Calendar(events=[test.calendar_entry() for test in tests])