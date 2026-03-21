from solution import two_sum_all_pairs


def test_single_pair():
    assert two_sum_all_pairs([2, 7, 11, 15], 9) == [(0, 1)]

def test_multiple_pairs():
    nums = [1, 2, 3, 4, 5]
    result = two_sum_all_pairs(nums, 6)
    assert sorted(result) == [(1, 4), (2, 3)]

def test_no_pairs():
    assert two_sum_all_pairs([1, 2, 3], 100) == []

def test_empty():
    assert two_sum_all_pairs([], 5) == []

def test_i_less_than_j():
    result = two_sum_all_pairs([3, 3, 3], 6)
    for i, j in result:
        assert i < j, f"Pair ({i},{j}) violates i < j"

def test_all_duplicates():
    result = two_sum_all_pairs([3, 3, 3], 6)
    assert sorted(result) == [(0, 1), (0, 2), (1, 2)]

def test_negative_numbers():
    nums = [-1, 0, 1, 2, -2]
    result = two_sum_all_pairs(nums, 0)
    for i, j in result:
        assert nums[i] + nums[j] == 0
        assert i < j

def test_output_is_sorted():
    nums = [1, 2, 3, 4, 5, 6]
    result = two_sum_all_pairs(nums, 7)
    assert result == sorted(result), "Output must be sorted"
    assert result == [(0, 5), (1, 4), (2, 3)]

def test_no_self_pairs():
    assert two_sum_all_pairs([5, 1, 3], 10) == []

def test_large_input():
    import time
    nums = list(range(1000))
    target = 999
    start = time.time()
    result = two_sum_all_pairs(nums, target)
    elapsed = time.time() - start
    assert len(result) == 500
    assert all(nums[i] + nums[j] == target for i, j in result)
    assert all(i < j for i, j in result)
    assert elapsed < 1.0
