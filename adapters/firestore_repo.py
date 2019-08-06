from typing import Iterable, Optional, Dict, Any, Callable

from google.cloud import firestore

from entities.student import Student
from entities.teacher import Teacher
from entities.types import Semester, Block, Name, Handle, LunchNumber, SemesterLunches
from use_cases.types import StudentRepository, TeacherRepository

STUDENT_COL = 'students'
TEACHER_COL = 'teachers'


class FirestoreStudentRepo(StudentRepository):
    client: firestore.Client

    def __init__(self, client: firestore.Client = firestore.Client()):
        self.client = client

    def save(self, student: Student):
        data = {
            'name': student.name,
            'semesters': None if student.schedules is None else key_transform(student.schedules, str),
            'accepts_terms': student.accepts_terms,
            'accepts_privacy': student.accepts_privacy,
            'is_public': student.is_public
        }
        if student.discord_id is not None:
            data['discord_id'] = student.discord_id

        self.client.collection(STUDENT_COL).document(student.handle).set(data)

    def exists(self, handle: Handle) -> bool:
        return self.client.collection(STUDENT_COL).document(handle).get(field_paths=[]).exists

    def load(self, handle: Handle) -> Optional[Student]:
        entry = self.client.collection(STUDENT_COL).document(handle)
        return self._read_doc(entry)

    def students_in_class(self, semester: Semester, block: Block, teacher_name: Name) -> Iterable[Student]:
        yield from self.client.collection(STUDENT_COL) \
            .where(f'semesters.{semester}.{block}', '==', teacher_name).stream()

    def search(self, query: str) -> Iterable[Student]:
        query = query.strip().lower()
        if len(query) == 0:
            return

        for doc in self.client.collection(STUDENT_COL).stream():
            if query in doc.id.lower() \
                    or query in doc.get(field_paths=['name']).get('name').lower():
                yield self._read_doc(doc)

    @staticmethod
    def _read_doc(doc: firestore.DocumentReference):
        entry = doc.get()
        data = entry.to_dict()

        if data is None:
            return None

        return Student(
            handle=doc.id,
            name=data['name'],
            schedules=None if data['semesters'] is None else key_transform(data['semesters'], int),
            accepts_terms=data['accepts_terms'],
            accepts_privacy=data['accepts_privacy'],
            is_public=data['is_public'],
            discord_id=data.get('discord_id')
        )


class FirestoreTeacherRepo(TeacherRepository):
    client: firestore.Client

    def __init__(self, client: firestore.Client = firestore.Client()):
        self.client = client

    def save(self, teacher: Teacher):
        self.client.collection(TEACHER_COL).document(teacher.name).set({
            'handle': teacher.handle,
            'semesters': key_transform(teacher.lunches, str)
        })

    def exists(self, name: Name) -> bool:
        return self.client.collection(TEACHER_COL).document(name).get(field_paths=[]).exists

    def load(self, name: Name) -> Optional[Teacher]:
        diction = self.client.collection(TEACHER_COL).document(name).get().to_dict()
        return None if diction is None else \
            Teacher(diction['handle'], name, key_transform(diction['semesters'], int))

    def update_batch_lunch(self, updates: Dict[Name, Dict[Semester, SemesterLunches]]):
        batch = self.client.batch()
        for (teacher, update) in updates.items():
            update_dict = {}
            for (semester, lunches) in update.items():
                for (block, number) in lunches.items():
                    update_dict[f'semesters.{semester}.{block}'] = number
            batch.update(self.client.collection(TEACHER_COL).document(teacher), update_dict)
        batch.commit()

    def names_of_teachers_in_lunch(self, semester: Semester, block: Block, number: LunchNumber) -> Iterable[Name]:
        stream = self.client.collection(TEACHER_COL).where(f'semesters.{semester}.{block}', '==', number).stream()
        yield from map(lambda doc: doc.id, stream)


def key_transform(diction: Dict[Semester, Any], operation: Callable) -> Dict[Any, Any]:
    return dict(map(lambda pair: (operation(pair[0]), pair[1]), diction.items()))
