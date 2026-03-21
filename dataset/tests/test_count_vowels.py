import random
import string
from solution import count_vowels

VOWELS = set("aeiouAEIOU")


def test_basic():
    assert count_vowels("hello") == 2


def test_uppercase():
    assert count_vowels("HELLO") == 2


def test_mixed_case():
    assert count_vowels("HeLLo") == 2


def test_no_vowels():
    assert count_vowels("gym") == 0
    assert count_vowels("bcdfg") == 0


def test_all_vowels():
    assert count_vowels("aeiou") == 5
    assert count_vowels("AEIOU") == 5


def test_empty():
    assert count_vowels("") == 0


def test_random_correctness():
    for _ in range(50):
        s = ''.join(random.choices(string.ascii_letters, k=random.randint(0, 100)))
        expected = sum(1 for c in s if c in VOWELS)
        assert count_vowels(s) == expected


def test_numbers_and_symbols():
    assert count_vowels("h3ll0 w0rld!") == 0
    assert count_vowels("aeiou123!@#") == 5
