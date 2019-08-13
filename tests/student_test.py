from entities.student import Student


def test_semester_schedule_with_schedule():
    student = Student('hpeng2021', 'Michael')
    student.schedules = {1: {'A': 'glee', 'B': '', 'C': 'see', 'D': 'dee'}}

    output = student.semester_schedule(1)

    assert output == student.schedules[1]
    assert student.semester_schedule(2) is None


def test_semester_schedule_without_schedule():
    student = Student('hpeng2021', 'Michael')
    student.schedules = None

    assert student.semester_schedule(1) is None


def test_hash_by_handle():
    student = Student('divanovich2021', 'Daniel')

    assert hash(student) == hash(student.handle)