import random
from solution import two_sum


def test_basic_correct():
    nums = [2, 7, 11, 15]
    result = two_sum(nums, 9)
    assert result is not None
    i, j = result
    assert i != j
    assert nums[i] + nums[j] == 9

def test_no_solution():
    assert two_sum([1, 2, 3], 100) is None

def test_same_index_bug_fixed():
    # Original bug: two_sum([3,5], 6) returns (0,0) because 3+3=6 using index 0 twice
    result = two_sum([3, 5], 6)
    assert result is None, "Bug not fixed: returned same-index pair (0,0)"

def test_duplicate_values_different_indices():
    # [3,3] target=6 is valid — uses indices 0 and 1, which are different
    result = two_sum([3, 3], 6)
    assert result is not None
    i, j = result
    assert i != j

def test_self_pair_impossible():
    # 5+5=10 but only one 5 exists — must return None
    result = two_sum([5, 1, 2, 3], 10)
    assert result is None

def test_negative_numbers():
    nums = [-3, 4, 3, 90]
    result = two_sum(nums, 0)
    assert result is not None
    i, j = result
    assert i != j
    assert nums[i] + nums[j] == 0

def test_random_never_same_index():
    for _ in range(100):
        nums = [random.randint(-100, 100) for _ in range(20)]
        target = random.randint(-200, 200)
        result = two_sum(nums, target)
        if result is not None:
            i, j = result
            assert i != j, f"Same index used: i=j={i}"
            assert nums[i] + nums[j] == target
