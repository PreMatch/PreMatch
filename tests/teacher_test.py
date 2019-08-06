# testing a teacher... such irony.
from entities.teacher import Teacher


def test_teacher_lunch():
    teacher = Teacher('cgivens', 'Givens', {1: {'E': 2, 'C': 1}, 2: {'F': 4, 'G': 1}})

    assert teacher.lunch_number(1, 'E') == 2
    assert teacher.lunch_number(2, 'G') == 1
    assert teacher.lunch_number(1, 'G') is None
    assert teacher.lunch_number(3, 'C') is None
