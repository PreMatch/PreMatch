from unittest.mock import MagicMock, Mock

import pytest
from google.cloud import firestore

from adapters.firestore_repo import FirestoreStudentRepo, FirestoreClassRepo
from entities.klass import Class
from entities.student import Student
from tests.mock_helper import require

mock_db = MagicMock()
student_repo = FirestoreStudentRepo(mock_db)
class_repo = FirestoreClassRepo(mock_db)


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
    mock_db.collection('students').document('hpeng2021').get().id = 'hpeng2021'

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

    def mock_student_doc_snapshot(student):
        snapshot = Mock(id=student.handle)
        snapshot.to_dict.return_value = {
            'name': student.name,
            'semesters': None,
            'accepts_terms': False,
            'accepts_privacy': False,
            'is_public': False,
            'discord_id': None
        }
        return snapshot

    mock_db.collection('students').where('semesters.1.D', '==', 'Caveney')\
        .stream.return_value = map(mock_student_doc_snapshot, classmates)

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
        mock.get.side_effect = require(('name',), student.name)
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


def test_save_class_without_lunch(reset_mock):
    klass = Class('Hibino, Krista', 'G', 1, lunch=None)

    class_repo.save(klass)

    mock_db.collection('classes', '1', 'G').document('Hibino, Krista').set.assert_called_once_with({
        'lunch': None,
        'location': None
    })


def test_save_class_with_lunch(reset_mock):
    klass = Class('Hibino, Alan', 'E', 2, lunch=3)

    class_repo.save(klass)

    mock_db.collection('classes', '2', 'E').document('Hibino, Alan').set.assert_called_once_with({
        'lunch': 3,
        'location': None
    })


def test_class_exists(reset_mock):
    classes = [
        Class('Reidy', 'G', 1),
        Class('Michaud, Rob', 'A', 2),
        Class('Donovan', 'D', 1, 1, 'physics lab'),
        Class('McNally', 'E', 2, 3, 'fields')
    ]
    for c in classes:
        mock_db.collection('classes', str(c.semester), c.block)\
            .document(c.teacher).get(field_paths=[]).exists = True
        assert class_repo.exists(c.teacher, c.block, c.semester) is True  # cannot be just truthy, must be exactly True

    mock_db.collection('classes', '1', 'B').document('Smith').get(field_paths=[]).exists = False
    assert not class_repo.exists('Smith', 'B', 1)


def test_load_nonexistent_class(reset_mock):
    mock_db.collection('classes', '2', 'F').document('Reidy').get().to_dict.return_value = None

    assert class_repo.load('Reidy', 'F', 2) is None


def test_load_class_with_lunch_location(reset_mock):
    klass = {
        'lunch': 2,
        'location': 'gym'
    }
    mock_db.collection('classes', '2', 'E').document('Emery').get().to_dict.return_value = klass

    loaded = class_repo.load('Emery', 'E', 2)

    assert loaded == Class('Emery', 'E', 2, lunch=2, location='gym')


def test_load_class_without_lunch(reset_mock):
    klass = {}
    mock_db.collection('classes', '1', 'B').document('Donovan').get().to_dict.return_value = klass

    loaded = class_repo.load('Donovan', 'B', 1)

    assert loaded == Class('Donovan', 'B', 1, lunch=None, location=None)


def test_update_batch_lunch_one_per_teacher(reset_mock):
    mock_batch = Mock()
    mock_db.batch.return_value = mock_batch
    mock_db.field_path.side_effect = firestore.Client.field_path

    updates = [
        Class('Donovan', 'D', 2, lunch=1),
        Class('Reidy', 'G', 1, lunch=4),
        Class('Emery', 'C', 2, lunch=3)
    ]
    class_repo.update_batch(updates)

    patches = [
        ('classes.2.D', 'Donovan', {'lunch': 1, 'location': None}),
        ('classes.1.G', 'Reidy', {'lunch': 4, 'location': None}),
        ('classes.2.C', 'Emery', {'lunch': 3, 'location': None})
    ]
    for (col, teacher, patch) in patches:
        mock_batch.update.assert_any_call(mock_db.collection(col).document(teacher), patch)

    mock_batch.commit.assert_called_once()


def test_update_batch_lunch_multiple_per_teacher(reset_mock):
    mock_batch = Mock()
    mock_db.batch.return_value = mock_batch
    mock_db.field_path.side_effect = firestore.Client.field_path

    updates = [
        Class('Donovan', 'D', 2, lunch=1),
        Class('Donovan', 'E', 2, lunch=3),
        Class('Donovan', 'F', 2, lunch=1),
        Class('Donovan', 'C', 1, lunch=2),
        Class('Donovan', 'D', 1, lunch=4),
        Class('Donovan', 'G', 1, lunch=2),
        Class('Reidy', 'G', 1, lunch=4),
        Class('Reidy', 'C', 1, lunch=2),
        Class('Reidy', 'G', 2, lunch=4),
        Class('Reidy', 'F', 2, lunch=3)
    ]
    class_repo.update_batch(updates)

    patches = [
        ('classes.2.D', 'Donovan', {'lunch': 1, 'location': None}),
        ('classes.2.E', 'Donovan', {'lunch': 3, 'location': None}),
        ('classes.2.F', 'Donovan', {'lunch': 1, 'location': None}),
        ('classes.1.C', 'Donovan', {'lunch': 2, 'location': None}),
        ('classes.1.D', 'Donovan', {'lunch': 4, 'location': None}),
        ('classes.1.G', 'Donovan', {'lunch': 2, 'location': None}),
        ('classes.1.G', 'Reidy', {'lunch': 4, 'location': None}),
        ('classes.1.C', 'Reidy', {'lunch': 2, 'location': None}),
        ('classes.2.G', 'Reidy', {'lunch': 4, 'location': None}),
        ('classes.2.F', 'Reidy', {'lunch': 3, 'location': None}),
    ]
    for (col, teacher, patch) in patches:
        mock_batch.update.assert_any_call(mock_db.collection(col).document(teacher), patch)

    mock_batch.commit.assert_called_once()


def test_names_of_teachers_in_lunch(reset_mock):
    teacher_names = ['Donovan', 'Reidy', 'Waters', 'Rainha']
    teachers = map(lambda name: MagicMock(id=name), teacher_names)
    mock_db.collection('classes.2.D').where('lunch', '==', 3).stream.return_value = teachers

    result = class_repo.names_of_teachers_in_lunch(2, 'D', 3)

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


def test_list_teacher_names(reset_mock):
    teachers = ['Caveney', 'D\'Alise', 'Rainha']
    mock_db.collection('teachers').list_documents.return_value =\
        list(map(lambda name: MagicMock(id=name), teachers))

    result = class_repo.list_teacher_names()

    assert set(result) == set(teachers)


def test_add_new_user(reset_mock):
    mock_db.collection('students').document('hpeng2021').get().exists = False
    mock_db.document('counters/user').get().get.side_effect = require(('value',), 412)

    student_repo.save(Student('hpeng2021', 'Michael'))

    mock_db.document.assert_called_with('counters/user')
    mock_db.document('counters/user').update.assert_called_once_with({'value': 413})


def test_add_existing_user(reset_mock):
    mock_db.collection('students').document('hpeng2021').get().exists = True
    mock_db.document('counters/user').get().get.side_effect = require(('value',), 412)

    student_repo.save(Student('hpeng2021', 'Michael'))

    mock_db.document.assert_called_with('counters/user')