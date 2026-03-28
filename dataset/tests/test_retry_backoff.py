import math
import pytest
from solution import compute_backoff_delays


def test_length():
    delays = compute_backoff_delays(max_retries=5, base_delay=1.0, max_delay=30.0, jitter=0.0)
    assert len(delays) == 5


def test_no_jitter_exponential():
    delays = compute_backoff_delays(max_retries=4, base_delay=1.0, max_delay=100.0, jitter=0.0)
    # Expected: 1, 2, 4, 8
    assert delays[0] == pytest.approx(1.0, abs=1e-9)
    assert delays[1] == pytest.approx(2.0, abs=1e-9)
    assert delays[2] == pytest.approx(4.0, abs=1e-9)
    assert delays[3] == pytest.approx(8.0, abs=1e-9)


def test_max_delay_cap():
    delays = compute_backoff_delays(max_retries=5, base_delay=1.0, max_delay=5.0, jitter=0.0)
    assert all(d <= 5.0 for d in delays)


def test_no_negative_delays():
    delays = compute_backoff_delays(max_retries=6, base_delay=1.0, max_delay=10.0, jitter=2.0)
    assert all(d >= 0.0 for d in delays)


def test_jitter_within_bounds():
    delays = compute_backoff_delays(max_retries=6, base_delay=1.0, max_delay=30.0, jitter=0.5)
    for i, d in enumerate(delays):
        expected_base = min(1.0 * (2 ** i), 30.0)
        assert d <= expected_base + 0.5 + 1e-9
        assert d >= 0.0


def test_zero_retries():
    assert compute_backoff_delays(max_retries=0, base_delay=1.0, max_delay=10.0, jitter=0.0) == []


def test_single_retry():
    delays = compute_backoff_delays(max_retries=1, base_delay=2.0, max_delay=10.0, jitter=0.0)
    assert len(delays) == 1
    assert delays[0] == pytest.approx(2.0)


def test_base_delay_respected():
    delays = compute_backoff_delays(max_retries=3, base_delay=0.5, max_delay=100.0, jitter=0.0)
    assert delays[0] == pytest.approx(0.5)
    assert delays[1] == pytest.approx(1.0)
    assert delays[2] == pytest.approx(2.0)
