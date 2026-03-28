from solution import count_events_in_window


def test_basic():
    assert count_events_in_window([1, 2, 3, 10], window=2) == 3


def test_all_in_window():
    assert count_events_in_window([1, 2, 3, 4], window=10) == 4


def test_none_in_window():
    assert count_events_in_window([1, 10, 20, 30], window=2) == 1


def test_empty():
    assert count_events_in_window([], window=5) == 0


def test_single_event():
    assert count_events_in_window([5], window=3) == 1


def test_window_boundary_inclusive():
    # window=2: [1,3] all fit (3-1=2 <= 2)
    assert count_events_in_window([1, 2, 3], window=2) == 3


def test_sliding_finds_best_window():
    # Best window: [4,5,6,7] = 4 events
    assert count_events_in_window([1, 4, 5, 6, 7, 20], window=3) == 4


def test_large_input_performance():
    import time
    events = list(range(0, 100000, 1))  # 100k events, all within range
    start = time.time()
    result = count_events_in_window(events, window=10)
    elapsed = time.time() - start
    assert result == 11  # window covers 11 consecutive timestamps
    assert elapsed < 1.0, f"Too slow: {elapsed:.2f}s — expected O(n)"


def test_does_not_count_events_before_window_start():
    # If window starts at t=5 with size 3, events at t=1,2,3 should NOT count
    assert count_events_in_window([1, 2, 3, 5, 6, 7], window=3) == 3


def test_duplicate_timestamps():
    assert count_events_in_window([1, 1, 1, 5, 5], window=0) == 3
