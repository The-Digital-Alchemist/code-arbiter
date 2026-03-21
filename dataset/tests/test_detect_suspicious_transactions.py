from solution import detect_suspicious


def test_three_under_threshold_in_window():
    txns = [
        {"id": "t1", "sender": "alice", "amount": 50.0, "timestamp": 0},
        {"id": "t2", "sender": "alice", "amount": 60.0, "timestamp": 30},
        {"id": "t3", "sender": "alice", "amount": 70.0, "timestamp": 59},
    ]
    result = detect_suspicious(txns)
    assert set(result) == {"t1", "t2", "t3"}

def test_no_suspicious_only_two():
    txns = [
        {"id": "t1", "sender": "alice", "amount": 50.0, "timestamp": 0},
        {"id": "t2", "sender": "alice", "amount": 60.0, "timestamp": 30},
    ]
    assert detect_suspicious(txns) == []

def test_amount_over_threshold_not_suspicious():
    txns = [
        {"id": "t1", "sender": "alice", "amount": 100.1, "timestamp": 0},
        {"id": "t2", "sender": "alice", "amount": 150.0, "timestamp": 10},
        {"id": "t3", "sender": "alice", "amount": 200.0, "timestamp": 20},
    ]
    assert detect_suspicious(txns) == []

def test_exactly_100_not_suspicious():
    # strictly under 100 — 100.0 itself does NOT count
    txns = [
        {"id": "t1", "sender": "bob", "amount": 100.0, "timestamp": 0},
        {"id": "t2", "sender": "bob", "amount": 100.0, "timestamp": 10},
        {"id": "t3", "sender": "bob", "amount": 100.0, "timestamp": 20},
    ]
    assert detect_suspicious(txns) == []

def test_window_just_inside_59s():
    txns = [
        {"id": "t1", "sender": "dave", "amount": 50.0, "timestamp": 0},
        {"id": "t2", "sender": "dave", "amount": 50.0, "timestamp": 30},
        {"id": "t3", "sender": "dave", "amount": 50.0, "timestamp": 59},
    ]
    result = detect_suspicious(txns)
    assert set(result) == {"t1", "t2", "t3"}

def test_only_suspicious_sender_flagged():
    txns = [
        {"id": "t1", "sender": "alice", "amount": 50.0, "timestamp": 0},
        {"id": "t2", "sender": "alice", "amount": 50.0, "timestamp": 10},
        {"id": "t3", "sender": "alice", "amount": 50.0, "timestamp": 20},
        {"id": "t4", "sender": "bob", "amount": 50.0, "timestamp": 0},
        {"id": "t5", "sender": "bob", "amount": 50.0, "timestamp": 10},
    ]
    result = detect_suspicious(txns)
    assert "t1" in result
    assert "t4" not in result
    assert "t5" not in result

def test_sliding_window_not_just_first_60s():
    txns = [
        {"id": "t1", "sender": "eve", "amount": 50.0, "timestamp": 0},
        {"id": "t2", "sender": "eve", "amount": 150.0, "timestamp": 10},
        {"id": "t3", "sender": "eve", "amount": 50.0, "timestamp": 1000},
        {"id": "t4", "sender": "eve", "amount": 50.0, "timestamp": 1030},
        {"id": "t5", "sender": "eve", "amount": 50.0, "timestamp": 1050},
    ]
    result = detect_suspicious(txns)
    assert "t3" in result
    assert "t4" in result
    assert "t5" in result
    assert "t1" not in result

def test_multiple_windows_same_sender():
    txns = [
        {"id": "t1", "sender": "frank", "amount": 10.0, "timestamp": 0},
        {"id": "t2", "sender": "frank", "amount": 10.0, "timestamp": 20},
        {"id": "t3", "sender": "frank", "amount": 10.0, "timestamp": 40},
        {"id": "t4", "sender": "frank", "amount": 10.0, "timestamp": 500},
        {"id": "t5", "sender": "frank", "amount": 10.0, "timestamp": 520},
        {"id": "t6", "sender": "frank", "amount": 10.0, "timestamp": 540},
    ]
    result = detect_suspicious(txns)
    assert "t1" in result
    assert "t4" in result
