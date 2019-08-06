from unittest.mock import MagicMock

from entities.student import Student
from use_cases.search import SearchCase

student_repo = MagicMock()
case = SearchCase(student_repo)


def test_pass_query_to_repo():
    student_repo.search.return_value = [Student('qry', 'Que Ry'), Student('mquery', 'Myq Uery')]

    results = case.perform_search('my query')

    student_repo.search.assert_called_once_with('my query')
    assert list(results) == student_repo.search.return_value
