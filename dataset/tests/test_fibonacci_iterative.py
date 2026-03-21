import random
import time
from solution import fib

# --- correctness ---

def test_base_cases():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(10) == 55

def test_known_values():
    assert fib(20) == 6765
    assert fib(30) == 832040
    assert fib(50) == 12586269025

# --- trap: negative input must raise ---

def test_raises_on_negative():
    import pytest
    with pytest.raises(ValueError):
        fib(-1)
    with pytest.raises(ValueError):
        fib(-100)

# --- correctness: Fibonacci identity ---

def test_fibonacci_recurrence_property():
    for n in random.sample(range(2, 50), 15):
        assert fib(n) == fib(n - 1) + fib(n - 2), f"Recurrence failed at n={n}"

# --- known exact value at large n ---

def test_fib_100_exact():
    assert fib(100) == 354224848179261915075

# --- performance: recursive without memoization cannot pass these ---

def test_fib_500_fast():
    start = time.time()
    result = fib(500)
    elapsed = time.time() - start
    assert result > 0
    assert elapsed < 0.1, f"fib(500) took {elapsed:.3f}s — must be iterative"

def test_fib_10000_fast():
    start = time.time()
    result = fib(10_000)
    elapsed = time.time() - start
    assert result > 0
    assert elapsed < 0.5, f"fib(10000) took {elapsed:.3f}s — must be iterative"

def test_fib_100000_fast():
    # Recursive blows the stack. Naive memoized recursion also hits recursion limit.
    start = time.time()
    result = fib(100_000)
    elapsed = time.time() - start
    assert result > 0
    assert elapsed < 2.0, f"fib(100000) took {elapsed:.3f}s — must be iterative"
