import time
from solution import binary_search

def test_found_middle():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2

def test_found_first():
    assert binary_search([1, 3, 5, 7, 9], 1) == 0

def test_found_last():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4

def test_not_found():
    assert binary_search([1, 3, 5, 7, 9], 4) == -1

def test_not_found_out_of_range():
    assert binary_search([1, 3, 5], 100) == -1
    assert binary_search([1, 3, 5], -100) == -1

def test_empty_array():
    assert binary_search([], 5) == -1

def test_single_element_found():
    assert binary_search([7], 7) == 0

def test_single_element_not_found():
    assert binary_search([7], 3) == -1

def test_two_elements_both():
    assert binary_search([2, 8], 2) == 0
    assert binary_search([2, 8], 8) == 1
    assert binary_search([2, 8], 5) == -1

def test_repeated_values_returns_valid_index():
    nums = [1, 2, 2, 2, 3]
    result = binary_search(nums, 2)
    assert result in [1, 2, 3]
    assert nums[result] == 2

def test_all_same_values():
    nums = [5] * 100
    result = binary_search(nums, 5)
    assert 0 <= result < len(nums)
    assert nums[result] == 5

def test_negative_numbers():
    nums = [-10, -5, -3, -1, 0, 2]
    assert binary_search(nums, -5) == 1
    assert binary_search(nums, -4) == -1
    assert binary_search(nums, 0) == 4

def test_10m_elements_found():
    nums = list(range(10_000_000))
    start = time.time()
    result = binary_search(nums, 9_999_999)
    elapsed = time.time() - start
    assert result == 9_999_999
    assert elapsed < 0.05, f"Too slow ({elapsed:.4f}s) — must be O(log n)"

def test_10m_elements_not_found():
    nums = list(range(0, 20_000_000, 2))
    start = time.time()
    result = binary_search(nums, 9_999_999)
    elapsed = time.time() - start
    assert result == -1
    assert elapsed < 0.05, f"Too slow ({elapsed:.4f}s) — must be O(log n)"

def test_10m_first_element():
    nums = list(range(10_000_000))
    start = time.time()
    result = binary_search(nums, 0)
    elapsed = time.time() - start
    assert result == 0
    assert elapsed < 0.05

def test_10m_last_element():
    nums = list(range(10_000_000))
    start = time.time()
    result = binary_search(nums, 9_999_998)
    elapsed = time.time() - start
    assert result == 9_999_998
    assert elapsed < 0.05
