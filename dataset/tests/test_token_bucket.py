from solution import TokenBucket


def test_basic_consume():
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    assert tb.consume(5, current_time=0.0) is True


def test_consume_full_capacity():
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    assert tb.consume(10, current_time=0.0) is True


def test_consume_exceeds_available():
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    assert tb.consume(11, current_time=0.0) is False


def test_refill_over_time():
    tb = TokenBucket(capacity=10, refill_rate=2.0)
    tb.consume(10, current_time=0.0)       # drain to 0
    assert tb.consume(4, current_time=2.0) is True   # 4 tokens refilled in 2s


def test_refill_does_not_exceed_capacity():
    tb = TokenBucket(capacity=5, refill_rate=10.0)
    tb.consume(5, current_time=0.0)        # drain
    # 100s * 10/s = 1000 tokens, but capped at 5
    assert tb.consume(5, current_time=100.0) is True
    assert tb.consume(1, current_time=100.0) is False


def test_partial_consume_then_refill():
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    tb.consume(8, current_time=0.0)        # 2 remaining
    assert tb.consume(3, current_time=0.0) is False   # not enough yet
    assert tb.consume(3, current_time=1.0) is True    # 1 more refilled = 3 total


def test_no_refill_before_time_passes():
    tb = TokenBucket(capacity=10, refill_rate=5.0)
    tb.consume(10, current_time=0.0)
    assert tb.consume(1, current_time=0.0) is False


def test_fractional_refill():
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    tb.consume(10, current_time=0.0)
    # 0.5s * 1/s = 0.5 tokens — not enough for 1
    assert tb.consume(1, current_time=0.5) is False
    # 1.0s * 1/s = 1.0 token — enough
    assert tb.consume(1, current_time=1.0) is True


def test_multiple_sequential_consumes():
    tb = TokenBucket(capacity=10, refill_rate=2.0)
    assert tb.consume(4, current_time=0.0) is True    # 6 left
    assert tb.consume(4, current_time=0.0) is True    # 2 left
    assert tb.consume(4, current_time=0.0) is False   # only 2, need 4
    assert tb.consume(4, current_time=1.0) is True    # 2 + 2 refilled = 4
