from solution import LRUCache

# --- correctness ---

def test_basic_put_and_get():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1

def test_missing_key_returns_minus_one():
    cache = LRUCache(2)
    assert cache.get(99) == -1

# --- trap: eviction order ---

def test_eviction_evicts_lru_not_oldest():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)       # 1 is now MRU, 2 is LRU
    cache.put(3, 3)    # must evict 2, not 1
    assert cache.get(2) == -1
    assert cache.get(1) == 1
    assert cache.get(3) == 3

# --- trap: put refreshes recency ---

def test_put_existing_refreshes_recency():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 10)   # update makes 1 MRU
    cache.put(3, 3)    # must evict 2, not 1
    assert cache.get(1) == 10
    assert cache.get(2) == -1
    assert cache.get(3) == 3

# --- trap: get refreshes recency ---

def test_get_promotes_to_mru():
    cache = LRUCache(3)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    cache.get(1)       # 1 is now MRU, LRU is 2
    cache.put(4, 4)    # must evict 2
    assert cache.get(2) == -1
    assert cache.get(1) == 1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

# --- trap: capacity one ---

def test_capacity_one():
    cache = LRUCache(1)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == -1
    assert cache.get(2) == 2

# --- trap: overwrite value ---

def test_overwrite_returns_new_value():
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(1, 200)
    assert cache.get(1) == 200

# --- stress: 100k operations must be O(1) per op ---

def test_100k_sequential_puts():
    import time
    cache = LRUCache(1000)
    start = time.time()
    for i in range(100_000):
        cache.put(i, i)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"100k puts took {elapsed:.2f}s — must be O(1) per op"
    # Only last 1000 keys should be present
    for i in range(99_000):
        assert cache.get(i) == -1
    for i in range(99_000, 100_000):
        assert cache.get(i) == i

def test_100k_mixed_ops():
    import time
    import random
    cache = LRUCache(500)
    start = time.time()
    for i in range(100_000):
        if random.random() < 0.6:
            cache.put(random.randint(0, 999), random.randint(0, 9999))
        else:
            cache.get(random.randint(0, 999))
    elapsed = time.time() - start
    assert elapsed < 1.0, f"100k mixed ops took {elapsed:.2f}s — must be O(1) per op"
