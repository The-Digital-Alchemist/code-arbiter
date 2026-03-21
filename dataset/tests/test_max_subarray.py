import random
import time
from solution import max_subarray

def test_mixed():
    assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6

def test_all_positive():
    assert max_subarray([1, 2, 3, 4]) == 10

def test_single_positive():
    assert max_subarray([5]) == 5

def test_single_negative():
    assert max_subarray([-5]) == -5

def test_all_negative():
    assert max_subarray([-3, -1, -4, -2]) == -1

def test_all_negative_large():
    assert max_subarray([-100, -50, -200, -1, -99]) == -1

def test_two_negatives():
    assert max_subarray([-2, -1]) == -1

def test_zeros_mixed():
    assert max_subarray([0, -1, 0, -2, 0]) == 0

def test_contiguous_not_subset():
    assert max_subarray([-2, 4, -1, 2, 1, -5]) == 6

def test_random_correctness_50_rounds():
    for _ in range(50):
        nums = [random.randint(-100, 100) for _ in range(random.randint(1, 30))]
        result = max_subarray(nums)
        expected = max(
            sum(nums[i:j + 1])
            for i in range(len(nums))
            for j in range(i, len(nums))
        )
        assert result == expected, f"Wrong on {nums}: got {result}, expected {expected}"

def test_1m_all_positive():
    nums = [1] * 1_000_000
    start = time.time()
    result = max_subarray(nums)
    elapsed = time.time() - start
    assert result == 1_000_000
    assert elapsed < 1.0, f"Too slow ({elapsed:.2f}s) — must be O(n)"

def test_1m_random():
    random.seed(42)
    nums = [random.randint(-100, 100) for _ in range(1_000_000)]
    start = time.time()
    result = max_subarray(nums)
    elapsed = time.time() - start
    assert isinstance(result, int)
    assert elapsed < 1.0, f"Too slow ({elapsed:.2f}s) — must be O(n) Kadane's"

def test_1m_all_negative():
    nums = [-1] * 1_000_000
    start = time.time()
    result = max_subarray(nums)
    elapsed = time.time() - start
    assert result == -1
    assert elapsed < 1.0, f"Too slow ({elapsed:.2f}s)"
