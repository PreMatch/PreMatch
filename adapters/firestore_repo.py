import random
from typing import Iterable, Optional, Dict, Any, Callable, List

from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentSnapshot

from entities.klass import Class
from entities.student import Student
from entities.types import Semester, Block, Name, Handle, LunchNumber
from use_cases.types import StudentRepository, ClassRepository

USER_COUNTER_DOC = 'counters/user'
STUDENT_COL = 'students'
TEACHER_COL = 'teachers'


class FirestoreStudentRepo(StudentRepository):
    client: firestore.Client
    cache: Optional[List[DocumentSnapshot]] = None

    def __init__(self, client: firestore.Client = firestore.Client(project="prematch-db")):
        self.client = client
        self._sync_user_count()

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

        if not self.exists(student.handle):
            self._increment_user_count()

        self.client.collection(STUDENT_COL).document(student.handle).set(data)
        cache = None

    def exists(self, handle: Handle) -> bool:
        return self.client.collection(STUDENT_COL).document(handle).get(field_paths=[]).exists

    def load(self, handle: Handle) -> Optional[Student]:
        entry = self.client.collection(STUDENT_COL).document(handle)
        return self._read_doc(entry.get())

    def students_in_class(self, semester: Semester, block: Block, teacher_name: Name) -> Iterable[Student]:
        yield from map(self._read_doc, self.client.collection(STUDENT_COL)
                       .where(self.client.field_path('semesters', str(semester), block), '==', teacher_name).stream())

    def search(self, query: str) -> Iterable[Student]:
        query = query.strip().lower()
        if len(query) == 0:
            return

        if self.cache is None:
            self._populate_cache()

        for doc in self.cache:
            if query in doc.id.lower() \
                    or query in doc.get('name').lower():
                yield self._read_doc(doc)

    def user_count(self) -> int:
        if random.random() < 0.1:
            self._sync_user_count()
        return self.client.document(USER_COUNTER_DOC).get().get('value')

    def _sync_user_count(self):
        self.client.document(USER_COUNTER_DOC).set({
            'value': len(list(self.client.collection('students').list_documents()))
        })

    def _increment_user_count(self):
        self.client.document(USER_COUNTER_DOC).update({'value': self.user_count() + 1})

    def _populate_cache(self):
        self.cache = list(self.client.collection(STUDENT_COL).stream())

    @staticmethod
    def _read_doc(entry: firestore.DocumentSnapshot) -> Optional[Student]:
        data = entry.to_dict()

        if data is None:
            return None

        return Student(
            handle=entry.id,
            name=data['name'],
            schedules=None if data['semesters'] is None else key_transform(data['semesters'], int),
            accepts_terms=data['accepts_terms'],
            accepts_privacy=data['accepts_privacy'],
            is_public=data['is_public'],
            discord_id=data.get('discord_id')
        )


class FirestoreClassRepo(ClassRepository):
    client: firestore.Client

    def __init__(self, client: firestore.Client = firestore.Client(project="prematch-db")):
        self.client = client

    def save(self, klass: Class):
        self.classes_col(klass.block, klass.semester).document(klass.teacher).set({
            'lunch': klass.lunch,
            'location': klass.location
        })

    def exists(self, teacher: Name, block: Block, semester: Semester) -> bool:
        return self.classes_col(block, semester).document(teacher).get(field_paths=[]).exists

    def load(self, teacher: Name, block: Block, semester: Semester) -> Optional[Class]:
        diction = self.classes_col(block, semester).document(teacher).get().to_dict()
        return None if diction is None else \
            Class(teacher, block, semester, lunch=diction.get('lunch'), location=diction.get('location'))

    def update_batch(self, classes: Iterable[Class]):
        batch = self.client.batch()

        for klass in classes:
            doc_ref = self.classes_col(klass.block, klass.semester).document(klass.teacher)
            batch.update(doc_ref, {
                'lunch': klass.lunch,
                'location': klass.location
            })

        batch.commit()

    def names_of_teachers_in_lunch(self, semester: Semester, block: Block, number: LunchNumber) -> Iterable[Name]:
        stream = self.classes_col(block, semester).where('lunch', '==', number).stream()
        yield from map(lambda doc: doc.id, stream)

    def list_teacher_names(self) -> Iterable[Name]:
        yield from map(lambda doc: doc.id, self.client.collection(TEACHER_COL).list_documents())

    def classes_col(self, block: Block, semester: Semester) -> firestore.CollectionReference:
        return self.client.collection('classes', str(semester), block)


def key_transform(diction: Dict[Semester, Any], operation: Callable) -> Dict[Any, Any]:
    return dict(map(lambda pair: (operation(pair[0]), pair[1]), diction.items()))
