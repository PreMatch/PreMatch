from hashlib import blake2b

from adapters.flask.validate import BLOCKS
from entities.student import Student


def name_hash(name: str):
    hash_obj = blake2b(name.encode(), key=b'april fools')
    return int(hash_obj.hexdigest(), 16)


def match_score(a: Student, b: Student):
    name_score = ((name_hash(a.name) + name_hash(b.name)) % 117) / 117
    shared_classes = 0

    for semester in [1, 2]:
        schedule_a = a.semester_schedule(semester)
        schedule_b = b.semester_schedule(semester)
        if schedule_a is None or schedule_b is None:
            break
        for block in BLOCKS:
            if schedule_a[block] == schedule_b[block]:
                shared_classes += 1

    # max theoretical shared classes: BLOCKS*2
    # use a sqrt curve
    classes_score = -4 / (0.8 * shared_classes * shared_classes + 4) + 1

    # same grade?
    grade_score = (3 - abs(a.graduating_year() - b.graduating_year())) / 3

    # print(f"match score query between {a.handle} and {b.handle}: name_score={name_score:.3f} classes_score={classes_score:.3f} grade_score={grade_score:.3f}")
    return name_score * 0.3 + classes_score * 0.5 + grade_score * 0.2
