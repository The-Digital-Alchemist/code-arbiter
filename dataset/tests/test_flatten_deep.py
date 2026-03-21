from solution import flatten_deep


def test_one_level():
    assert flatten_deep([1, 2, 3]) == [1, 2, 3]

def test_two_levels():
    assert flatten_deep([[1, 2], [3, 4]]) == [1, 2, 3, 4]

def test_three_levels():
    assert flatten_deep([[[1, 2], 3], [4, [5]]]) == [1, 2, 3, 4, 5]

def test_arbitrary_depth():
    assert flatten_deep([1, [2, [3, [4, [5]]]]]) == [1, 2, 3, 4, 5]

def test_empty():
    assert flatten_deep([]) == []

def test_already_flat():
    assert flatten_deep([1, 2, 3, 4]) == [1, 2, 3, 4]

def test_nested_empty_lists():
    assert flatten_deep([[], [[], []], []]) == []

def test_single_deeply_nested():
    assert flatten_deep([[[[[42]]]]]) == [42]

def test_uneven_depth():
    assert flatten_deep([1, [2, 3], [[4, 5], 6], [[[7]]]]) == [1, 2, 3, 4, 5, 6, 7]

def test_deeply_nested_100_levels():
    nested = 42
    for _ in range(100):
        nested = [nested]
    assert flatten_deep(nested) == [42]

def test_wide_and_deep():
    nested = [[list(range(10))] * 10] * 100
    result = flatten_deep(nested)
    assert len(result) == 10000
