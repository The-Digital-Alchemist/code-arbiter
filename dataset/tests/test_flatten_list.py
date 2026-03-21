import random
from solution import flatten_list


def test_basic():
    assert flatten_list([[1, 2], [3, 4]]) == [1, 2, 3, 4]


def test_single_elements():
    assert flatten_list([[1], [2], [3]]) == [1, 2, 3]


def test_empty_inner():
    assert flatten_list([[], [1, 2], []]) == [1, 2]


def test_empty_outer():
    assert flatten_list([]) == []


def test_mixed_lengths():
    assert flatten_list([[1, 2, 3], [4]]) == [1, 2, 3, 4]


def test_preserves_order():
    assert flatten_list([[3, 1], [4, 1], [5, 9]]) == [3, 1, 4, 1, 5, 9]


def test_random_correctness():
    for _ in range(30):
        nested = [[random.randint(-100, 100) for _ in range(random.randint(0, 10))]
                  for _ in range(random.randint(1, 10))]
        expected = [x for sublist in nested for x in sublist]
        assert flatten_list(nested) == expected


def test_large_input():
    nested = [list(range(100)) for _ in range(100)]
    result = flatten_list(nested)
    assert len(result) == 10000
    assert result[:100] == list(range(100))
