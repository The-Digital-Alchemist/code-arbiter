import time
from solution import is_prime

def test_known_primes():
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 97, 101, 997]:
        assert is_prime(p), f"{p} should be prime"

def test_known_composites():
    for n in [4, 6, 8, 9, 10, 15, 25, 49, 100, 121]:
        assert not is_prime(n), f"{n} should not be prime"

def test_zero_not_prime():
    assert not is_prime(0)

def test_one_not_prime():
    assert not is_prime(1)

def test_two_is_prime():
    assert is_prime(2)

def test_negative_not_prime():
    assert not is_prime(-1)
    assert not is_prime(-7)

def test_perfect_squares_not_prime():
    for n in [4, 9, 25, 49, 121, 169, 289]:
        assert not is_prime(n), f"{n} is a perfect square, not prime"

def test_carmichael_numbers_not_prime():
    for n in [561, 1105, 1729, 2465, 2821]:
        assert not is_prime(n), f"{n} is a Carmichael number, not prime"

def test_large_prime_billion_range():
    for p in [999_999_937, 998_244_353, 1_000_000_007]:
        start = time.time()
        result = is_prime(p)
        elapsed = time.time() - start
        assert result is True, f"{p} should be prime"
        assert elapsed < 0.5, f"Too slow on {p} ({elapsed:.2f}s) — need O(sqrt(n))"

def test_large_composite_billion_range():
    for n in [999_999_936, 999_999_938, 1_000_000_000]:
        start = time.time()
        result = is_prime(n)
        elapsed = time.time() - start
        assert result is False, f"{n} should not be prime"
        assert elapsed < 0.1

def test_stress_first_1000_primes():
    primes = [n for n in range(2, 7920) if is_prime(n)]
    assert len(primes) == 1000, f"Expected 1000 primes, got {len(primes)}"
    assert primes[-1] == 7919
