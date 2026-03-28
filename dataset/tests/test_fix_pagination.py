from solution import paginate


def test_first_page():
    assert paginate(list(range(10)), page=1, page_size=3) == [0, 1, 2]


def test_second_page():
    assert paginate(list(range(10)), page=2, page_size=3) == [3, 4, 5]


def test_third_page():
    assert paginate(list(range(10)), page=3, page_size=3) == [6, 7, 8]


def test_last_partial_page():
    assert paginate(list(range(10)), page=4, page_size=3) == [9]


def test_out_of_range_page():
    assert paginate(list(range(10)), page=5, page_size=3) == []


def test_page_size_larger_than_list():
    assert paginate([1, 2], page=1, page_size=10) == [1, 2]


def test_exact_fit():
    assert paginate(list(range(6)), page=2, page_size=3) == [3, 4, 5]


def test_single_item_pages():
    items = ["a", "b", "c"]
    assert paginate(items, page=1, page_size=1) == ["a"]
    assert paginate(items, page=2, page_size=1) == ["b"]
    assert paginate(items, page=3, page_size=1) == ["c"]


def test_empty_list():
    assert paginate([], page=1, page_size=5) == []
