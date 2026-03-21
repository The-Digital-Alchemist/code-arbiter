import random
from solution import word_frequency


def test_basic():
    assert word_frequency("hello world hello") == {"hello": 2, "world": 1}


def test_single_word():
    assert word_frequency("hello") == {"hello": 1}


def test_repeated():
    assert word_frequency("a a a") == {"a": 3}


def test_empty():
    assert word_frequency("") == {}


def test_case_sensitive():
    assert word_frequency("Hello hello") == {"Hello": 1, "hello": 1}


def test_random_correctness():
    words = ["apple", "banana", "cherry", "apple", "banana", "apple"]
    random.shuffle(words)
    text = " ".join(words)
    result = word_frequency(text)
    for word in set(words):
        assert result[word] == words.count(word)


def test_all_unique():
    words = ["one", "two", "three", "four", "five"]
    result = word_frequency(" ".join(words))
    assert all(v == 1 for v in result.values())


def test_large_input():
    words = ["word"] * 10000
    result = word_frequency(" ".join(words))
    assert result == {"word": 10000}
