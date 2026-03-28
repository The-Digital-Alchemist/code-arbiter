from solution import LRUCacheTTL


def test_basic_put_get():
    c = LRUCacheTTL(capacity=3, ttl=10.0)
    c.put(1, "a", current_time=0.0)
    assert c.get(1, current_time=1.0) == "a"


def test_miss_returns_minus_one():
    c = LRUCacheTTL(capacity=3, ttl=10.0)
    assert c.get(99, current_time=0.0) == -1


def test_expired_returns_minus_one():
    c = LRUCacheTTL(capacity=3, ttl=5.0)
    c.put(1, "a", current_time=0.0)
    assert c.get(1, current_time=5.1) == -1


def test_not_expired_at_boundary():
    c = LRUCacheTTL(capacity=3, ttl=5.0)
    c.put(1, "a", current_time=0.0)
    assert c.get(1, current_time=5.0) == "a"


def test_evicts_lru_when_full():
    c = LRUCacheTTL(capacity=2, ttl=100.0)
    c.put(1, "a", current_time=0.0)
    c.put(2, "b", current_time=1.0)
    c.put(3, "c", current_time=2.0)   # should evict key 1 (LRU)
    assert c.get(1, current_time=3.0) == -1
    assert c.get(2, current_time=3.0) == "b"
    assert c.get(3, current_time=3.0) == "c"


def test_get_updates_recency():
    c = LRUCacheTTL(capacity=2, ttl=100.0)
    c.put(1, "a", current_time=0.0)
    c.put(2, "b", current_time=1.0)
    c.get(1, current_time=2.0)         # access key 1 — now most recent
    c.put(3, "c", current_time=3.0)   # should evict key 2
    assert c.get(2, current_time=4.0) == -1
    assert c.get(1, current_time=4.0) == "a"


def test_put_updates_existing_key_ttl():
    c = LRUCacheTTL(capacity=3, ttl=5.0)
    c.put(1, "a", current_time=0.0)
    c.put(1, "b", current_time=4.0)   # refresh TTL
    assert c.get(1, current_time=8.0) == "b"   # would be expired if not refreshed
    assert c.get(1, current_time=9.1) == -1    # now expired


def test_expired_not_counted_toward_capacity():
    c = LRUCacheTTL(capacity=2, ttl=3.0)
    c.put(1, "a", current_time=0.0)
    c.put(2, "b", current_time=0.0)
    # both expire by t=4; put two new entries — shouldn't fail
    c.put(3, "c", current_time=4.0)
    c.put(4, "d", current_time=4.0)
    assert c.get(3, current_time=4.0) == "c"
    assert c.get(4, current_time=4.0) == "d"
