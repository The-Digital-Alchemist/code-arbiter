import random
from solution import merge_sorted_arrays


def test_basic():
    assert merge_sorted_arrays([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]


def test_first_empty():
    assert merge_sorted_arrays([], [1, 2, 3]) == [1, 2, 3]


def test_second_empty():
    assert merge_sorted_arrays([1, 2, 3], []) == [1, 2, 3]


def test_both_empty():
    assert merge_sorted_arrays([], []) == []


def test_duplicates():
    assert merge_sorted_arrays([1, 2, 2], [2, 3]) == [1, 2, 2, 2, 3]


def test_different_lengths():
    assert merge_sorted_arrays([1], [2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def test_random_correctness():
    for _ in range(50):
        a = sorted(random.randint(-1000, 1000) for _ in range(random.randint(0, 50)))
        b = sorted(random.randint(-1000, 1000) for _ in range(random.randint(0, 50)))
        result = merge_sorted_arrays(a, b)
        assert result == sorted(a + b)


def test_output_is_sorted():
    a = [1, 5, 9, 13]
    b = [2, 4, 6, 8, 10]
    result = merge_sorted_arrays(a, b)
    assert result == sorted(result)


def test_large_input():
    a = list(range(0, 10000, 2))
    b = list(range(1, 10001, 2))
    result = merge_sorted_arrays(a, b)
    assert result == list(range(10000))
