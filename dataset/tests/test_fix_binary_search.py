import time
from solution import binary_search


def test_basic_found():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2

def test_not_found():
    assert binary_search([1, 3, 5, 7, 9], 4) == -1

def test_empty():
    assert binary_search([], 5) == -1

def test_single_found():
    assert binary_search([7], 7) == 0

def test_single_not_found():
    assert binary_search([7], 3) == -1

def test_first_element():
    assert binary_search([1, 3, 5, 7, 9], 1) == 0

def test_last_element():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4

def test_trigger_original_bug():
    # [1,3] target=3: lo=0,hi=1,mid=0, nums[0]=1 < 3, original sets lo=0 -> infinite
    result = binary_search([1, 3], 3)
    assert result == 1

def test_no_infinite_loop_ascending():
    result = binary_search([1, 2, 3, 4, 5], 5)
    assert result == 4

def test_performance_no_infinite_loop():
    nums = list(range(1_000_000))
    start = time.time()
    result = binary_search(nums, 999_999)
    elapsed = time.time() - start
    assert result == 999_999
    assert elapsed < 0.05, f"Too slow or looping ({elapsed:.3f}s)"
