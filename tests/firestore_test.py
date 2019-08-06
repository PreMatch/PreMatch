from unittest.mock import MagicMock, Mock

import pytest

from adapters.firestore_repo import FirestoreStudentRepo, FirestoreTeacherRepo
from entities.student import Student
from entities.teacher import Teacher
from mock_helper import require

mock_db = MagicMock()
student_repo = FirestoreStudentRepo(mock_db)
teacher_repo = FirestoreTeacherRepo(mock_db)


@pytest.fixture
def reset_mock():
    mock_db.reset_mock()


def test_set_student_without_discord(reset_mock):
    student = Student('hpeng2021', 'Michael Peng',
                      schedules={1: {'C': 'Messina'}, 2: {'F': 'Parsons'}})

    student_repo.save(student)

    mock_db.collection('students').document('hpeng2021').set.assert_called_once_with({
        'name': 'Michael Peng',
        'semesters': {
            '1': {
                'C': 'Messina'
            },
            '2': {
                'F': 'Parsons'
            }
        },
        'accepts_terms': student.accepts_terms,
        'accepts_privacy': student.accepts_privacy,
        'is_public': student.is_public
    })


def test_set_student_with_discord(reset_mock):
    student = Student('hpeng2021', 'Michael Peng',
                      schedules=None,
                      discord_id='1040293723984713431')

    student_repo.save(student)

    mock_db.collection('students').document('hpeng2021').set.assert_called_once_with({
        'name': 'Michael Peng',
        'semesters': None,
        'accepts_terms': student.accepts_terms,
        'accepts_privacy': student.accepts_privacy,
        'is_public': student.is_public,
        'discord_id': student.discord_id
    })


def test_load_student_without_discord(reset_mock):
    db_entry = {
        'name': 'Michael Peng',
        'semesters': {
            '1': {
                'A': 'Holm-Andersen',
                'B': 'Gonzalez',
                'C': 'Ream',
                'D': 'Givens'
            },
            '2': {
                'E': 'Messina',
                'F': 'Parsons',
                'G': 'Reidy'
            }
        },
        'accepts_terms': True,
        'accepts_privacy': True,
        'is_public': True
    }
    mock_db.collection('students').document('hpeng2021').get().to_dict.return_value = db_entry
    mock_db.collection('students').document('hpeng2021').id = 'hpeng2021'

    student = student_repo.load('hpeng2021')

    assert student == Student(
        handle='hpeng2021',
        name='Michael Peng',
        schedules={
            1: db_entry['semesters']['1'],
            2: db_entry['semesters']['2']
        },
        accepts_terms=True,
        accepts_privacy=True,
        is_public=True,
        discord_id=None
    )


def test_load_student_with_discord_without_schedule(reset_mock):
    db_entry = {
        'name': 'Michael Peng',
        'semesters': None,
        'accepts_terms': True,
        'accepts_privacy': True,
        'is_public': True,
        'discord_id': '100923842098207349'
    }
    mock_db.collection('students').document('hpeng2021').get().to_dict.return_value = db_entry

    student = student_repo.load('hpeng2021')

    assert student == Student(
        handle='hpeng2021',
        name='Michael Peng',
        schedules=None,
        accepts_terms=True,
        accepts_privacy=True,
        is_public=True,
        discord_id=db_entry['discord_id']
    )


def test_load_nonexistent_student(reset_mock):
    mock_db.collection('students').document('divanovich2021').get().to_dict.return_value = None
    assert student_repo.load('divanovich2021') is None


def test_students_in_class(reset_mock):
    classmates = [
        Student('a', 'A'),
        Student('b', 'B'),
        Student('c', 'C')
    ]
    mock_db.collection('students').where('semesters.1.D', '==', 'Caveney').stream.return_value = classmates

    results = student_repo.students_in_class(1, 'D', 'Caveney')

    assert set(results) == set(classmates)


search_students = [
    Student('tbowlin', 'Tamekia Bowlin'),
    Student('blanterman', 'Brock Lanterman'),
    Student('hmateo', 'Hedwig Mateo'),
    Student('skrzeminski', 'Sadye Krzeminski'),
    Student('choltz', 'Clayton Holtz'),
    Student('mmchaney', 'Maryam Mchaney'),
    Student('lcuen', 'Liane Cuen'),
    Student('calbrecht', 'Cristobal Albrecht'),
    Student('dhohman', 'Dianna Hohman'),
    Student('ksecrist', 'Katelynn Secrist')
]


def populate_search_students():
    ret_val = []
    for student in search_students:
        mock = MagicMock()
        mock.get(field_paths=['name']).get.side_effect = require(('name',), student.name)
        mock.get().id = student.handle
        mock.id = student.handle
        ret_val.append(mock)
    mock_db.collection('students').stream.return_value = iter(ret_val)


def test_search_by_exact_handle(reset_mock):
    populate_search_students()

    results = list(student_repo.search('lcuen'))
    assert len(results) == 1 and results[0].handle == 'lcuen'


def test_search_by_handle_substring(reset_mock):
    populate_search_students()

    results = list(student_repo.search('chan'))
    assert len(results) == 1 and results[0].handle == 'mmchaney'


def test_search_with_whitespace(reset_mock):
    populate_search_students()

    results = list(student_repo.search('   \tzemin   '))
    assert len(results) == 1 and results[0].handle == 'skrzeminski'


def test_search_with_full_name(reset_mock):
    populate_search_students()

    results = list(student_repo.search('Hedwig Mateo'))
    assert len(results) == 1 and results[0].handle == 'hmateo'


def test_search_with_name_substring(reset_mock):
    populate_search_students()

    results = list(student_repo.search('hohm   '))
    assert len(results) == 1 and results[0].handle == 'dhohman'


def test_search_with_nothing(reset_mock):
    populate_search_students()

    results = list(student_repo.search('   \t\n\t  '))
    assert len(results) == 0


def test_save_teacher_without_lunch(reset_mock):
    teacher = Teacher('khibino', 'Hibino, Krista')

    teacher_repo.save(teacher)

    mock_db.collection('teachers').document('Hibino, Krista').set.assert_called_once_with({
        'handle': 'khibino',
        'semesters': {}
    })


def test_save_teacher_with_lunch(reset_mock):
    teacher = Teacher('ahibino', 'Hibino, Alan', {
        1: {
            'C': 2,
            'D': 4,
            'F': 2,
            'G': 1
        },
        2: {
            'D': 3,
            'E': 1
        }
    })

    teacher_repo.save(teacher)

    mock_db.collection('teachers').document('Hibino, Alan').set.assert_called_once_with({
        'handle': 'ahibino',
        'semesters': {
            '1': teacher.lunches[1],
            '2': teacher.lunches[2]
        }
    })


def test_teacher_exists(reset_mock):
    teachers = ['Hibino, Krista', 'Waters', 'Reidy', 'Smith', 'Emery']
    for t in teachers:
        mock_db.collection('teachers').document(t).get(field_paths=[]).exists = True
        assert teacher_repo.exists(t) is True  # cannot be just truthy, must be exactly True

    mock_db.collection('teachers').document('No teacher').get(field_paths=[]).exists = False
    assert not teacher_repo.exists('No teacher')


def test_load_nonexistent_teacher(reset_mock):
    mock_db.collection('teachers').document('Reidy').get().to_dict.return_value = None

    assert teacher_repo.load('Reidy') is None


def test_load_teacher_without_lunches(reset_mock):
    teacher = {
        'handle': 'memery',
        'semesters': {}
    }
    mock_db.collection('teachers').document('Emery').get().to_dict.return_value = teacher

    loaded = teacher_repo.load('Emery')

    assert loaded == Teacher('memery', 'Emery')


def test_load_teacher_with_lunches(reset_mock):
    teacher = {
        'handle': 'ddonovan',
        'semesters': {
            '1': {
                'D': 2,
                'E': 1,
                'F': 4
            },
            '2': {
                'F': 1,
                'G': 4
            }
        }
    }
    mock_db.collection('teachers').document('Donovan').get().to_dict.return_value = teacher

    loaded = teacher_repo.load('Donovan')

    assert loaded == Teacher('ddonovan', 'Donovan', {
        1: teacher['semesters']['1'],
        2: teacher['semesters']['2']
    })


def test_update_batch_lunch_one_per_teacher(reset_mock):
    mock_batch = Mock()
    mock_db.batch.return_value = mock_batch

    updates = {
        'Donovan': {
            2: {'D': 1}
        },
        'Reidy': {
            1: {'G': 4}
        },
        'Emery': {
            2: {'C': 3}
        }
    }
    teacher_repo.update_batch_lunch(updates)

    patches = {
        'Donovan': {'semesters.2.D': 1},
        'Reidy': {'semesters.1.G': 4},
        'Emery': {'semesters.2.C': 3}
    }
    for (teacher, patch) in patches.items():
        mock_batch.update.assert_any_call(mock_db.collection('teachers').document(teacher), patch)

    mock_batch.commit.assert_called_once()


def test_update_batch_lunch_multiple_per_teacher(reset_mock):
    mock_batch = Mock()
    mock_db.batch.return_value = mock_batch

    updates = {
        'Donovan': {2: {
                'D': 1,
                'E': 3,
                'F': 1
            }, 1: {
                'C': 2,
                'D': 4,
                'G': 2
            }
        },
        'Reidy': {1: {
                'G': 4,
                'C': 2,
                'D': 1
            }, 2: {
                'C': 2,
                'G': 4,
                'F': 3
            }
        },
        'Emery': {2: {
                'C': 3,
                'D': 1,
                'E': 4
            }, 1: {
                'C': 2,
                'G': 4,
                'F': 3
            }
        }
    }
    teacher_repo.update_batch_lunch(updates)

    patches = {
        'Donovan': {
            'semesters.2.D': 1,
            'semesters.2.E': 3,
            'semesters.2.F': 1,
            'semesters.1.C': 2,
            'semesters.1.D': 4,
            'semesters.1.G': 2,
        },
        'Reidy': {
            'semesters.1.G': 4,
            'semesters.1.C': 2,
            'semesters.1.D': 1,
            'semesters.2.C': 2,
            'semesters.2.G': 4,
            'semesters.2.F': 3,
        },
        'Emery': {
            'semesters.2.C': 3,
            'semesters.2.D': 1,
            'semesters.2.E': 4,
            'semesters.1.C': 2,
            'semesters.1.G': 4,
            'semesters.1.F': 3,
        }
    }
    for (teacher, patch) in patches.items():
        mock_batch.update.assert_any_call(mock_db.collection('teachers').document(teacher), patch)

    mock_batch.commit.assert_called_once()


def test_names_of_teachers_in_lunch(reset_mock):
    teacher_names = ['Donovan', 'Reidy', 'Waters', 'Rainha']
    teachers = map(lambda name: MagicMock(id=name), teacher_names)
    mock_db.collection('teachers').where('semesters.2.D', '==', 3).stream.return_value = teachers

    result = teacher_repo.names_of_teachers_in_lunch(2, 'D', 3)

    assert set(result) == set(teacher_names)


def test_student_exists(reset_mock):
    mock_db.collection('students').document('hpeng2021').get(field_paths=[]).exists = True
    assert student_repo.exists('hpeng2021')
    mock_db.collection.assert_any_call('students')
    mock_db.collection('students').document.assert_any_call('hpeng2021')

    mock_db.collection('students').document('divanovich2021').get(field_paths=[]).exists = False
    assert not student_repo.exists('divanovich2021')
    mock_db.collection.assert_any_call('students')
    mock_db.collection('students').document.assert_any_call('divanovich2021')
