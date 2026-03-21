import random
import time
from solution import two_sum

# --- correctness ---

def test_basic():
    i, j = two_sum([2, 7, 11, 15], 9)
    assert {i, j} == {0, 1}

def test_no_solution():
    assert two_sum([1, 2, 3], 100) is None

def test_negative_numbers():
    nums = [-3, 4, 3, 90]
    i, j = two_sum(nums, 0)
    assert nums[i] + nums[j] == 0

# --- traps ---

def test_duplicate_values_same_number():
    result = two_sum([3, 3], 6)
    assert result is not None
    i, j = result
    assert i != j

def test_duplicate_values_larger_array():
    nums = [1, 3, 3, 7]
    result = two_sum(nums, 6)
    assert result is not None
    i, j = result
    assert nums[i] + nums[j] == 6
    assert i != j

def test_returns_indices_not_values():
    nums = [10, 20, 30]
    result = two_sum(nums, 50)
    assert result is not None
    i, j = result
    assert 0 <= i < len(nums) and 0 <= j < len(nums)
    assert nums[i] + nums[j] == 50

def test_answer_at_boundaries():
    nums = list(range(2, 1000)) + [1, 999_001]
    target = 1 + 999_001
    result = two_sum(nums, target)
    assert result is not None
    i, j = result
    assert nums[i] + nums[j] == target

def test_negative_target():
    nums = [-5, -3, -1, 2, 4]
    result = two_sum(nums, -8)
    assert result is not None
    i, j = result
    assert nums[i] + nums[j] == -8

def test_zero_target():
    nums = [-4, 0, 4, 7]
    result = two_sum(nums, 0)
    assert result is not None
    i, j = result
    assert nums[i] + nums[j] == 0

# --- robustness ---

def test_random_100_rounds():
    for _ in range(100):
        a = random.randint(-10_000, 10_000)
        b = random.randint(-10_000, 10_000)
        noise = [random.randint(-10_000, 10_000) for _ in range(48)]
        nums = noise + [a, b]
        random.shuffle(nums)
        target = a + b
        result = two_sum(nums, target)
        assert result is not None
        i, j = result
        assert nums[i] + nums[j] == target
        assert i != j

# --- performance: O(n²) fails, O(n) passes ---

def test_1m_elements():
    n = 1_000_000
    nums = list(range(n))
    target = (n - 2) + (n - 1)
    start = time.time()
    result = two_sum(nums, target)
    elapsed = time.time() - start
    assert result is not None
    i, j = result
    assert nums[i] + nums[j] == target
    assert elapsed < 2.0, f"Too slow ({elapsed:.2f}s) — O(n²) brute force cannot pass this"

def test_1m_no_solution():
    nums = list(range(0, 2_000_000, 2))  # all even
    target = 1  # impossible
    start = time.time()
    result = two_sum(nums, target)
    elapsed = time.time() - start
    assert result is None
    assert elapsed < 2.0, f"Too slow ({elapsed:.2f}s)"
