import time
from solution import binary_search_count


def test_single_occurrence():
    assert binary_search_count([1, 2, 3, 4, 5], 3) == 1

def test_multiple_occurrences():
    assert binary_search_count([1, 2, 2, 2, 3], 2) == 3

def test_all_same():
    assert binary_search_count([5, 5, 5, 5, 5], 5) == 5

def test_not_found():
    assert binary_search_count([1, 2, 3, 4, 5], 9) == 0

def test_empty():
    assert binary_search_count([], 1) == 0

def test_one_element_found():
    assert binary_search_count([7], 7) == 1

def test_one_element_not_found():
    assert binary_search_count([7], 3) == 0

def test_target_at_boundaries():
    assert binary_search_count([1, 1, 2, 3, 3], 1) == 2
    assert binary_search_count([1, 1, 2, 3, 3], 3) == 2

def test_10m_elements_performance():
    nums = [1] * 5_000_000 + [2] * 5_000_000
    start = time.time()
    count = binary_search_count(nums, 1)
    elapsed = time.time() - start
    assert count == 5_000_000
    assert elapsed < 0.1, f"Too slow ({elapsed:.3f}s) — must be O(log n)"

def test_10m_not_found_performance():
    nums = list(range(10_000_000))
    start = time.time()
    count = binary_search_count(nums, -1)
    elapsed = time.time() - start
    assert count == 0
    assert elapsed < 0.1, f"Too slow ({elapsed:.3f}s)"
