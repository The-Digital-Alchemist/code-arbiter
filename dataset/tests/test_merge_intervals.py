from solution import merge_intervals


def test_no_overlap():
    assert merge_intervals([(1, 2), (4, 6)]) == [(1, 2), (4, 6)]


def test_full_overlap():
    assert merge_intervals([(1, 10), (2, 5)]) == [(1, 10)]


def test_partial_overlap():
    assert merge_intervals([(1, 3), (2, 5)]) == [(1, 5)]


def test_adjacent_intervals_merge():
    # (1,3) and (3,5) share endpoint — should merge
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]


def test_single_interval():
    assert merge_intervals([(2, 4)]) == [(2, 4)]


def test_empty_input():
    assert merge_intervals([]) == []


def test_already_merged():
    assert merge_intervals([(1, 5)]) == [(1, 5)]


def test_unsorted_input():
    result = merge_intervals([(5, 7), (1, 3), (2, 4)])
    assert result == [(1, 4), (5, 7)]


def test_all_merge_into_one():
    assert merge_intervals([(1, 2), (2, 3), (3, 4), (4, 5)]) == [(1, 5)]


def test_multiple_separate_groups():
    result = merge_intervals([(1, 3), (2, 4), (6, 8), (7, 9)])
    assert result == [(1, 4), (6, 9)]


def test_identical_intervals():
    assert merge_intervals([(2, 5), (2, 5)]) == [(2, 5)]


def test_one_contains_another():
    assert merge_intervals([(1, 10), (3, 6), (8, 12)]) == [(1, 12)]
