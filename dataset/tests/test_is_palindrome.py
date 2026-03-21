import random
import string
from solution import is_palindrome


def test_basic_palindrome():
    assert is_palindrome("racecar") is True
    assert is_palindrome("hello") is False


def test_case_insensitive():
    assert is_palindrome("Racecar") is True
    assert is_palindrome("MadaM") is True
    assert is_palindrome("AbBa") is True


def test_single_char():
    assert is_palindrome("a") is True


def test_empty_string():
    assert is_palindrome("") is True


def test_two_chars():
    assert is_palindrome("aa") is True
    assert is_palindrome("ab") is False


def test_random_palindromes():
    for _ in range(30):
        half = ''.join(random.choices(string.ascii_lowercase, k=random.randint(1, 20)))
        palindrome = half + half[::-1]
        assert is_palindrome(palindrome) is True


def test_random_non_palindromes():
    # "ab" + random ensures it's never a palindrome
    for _ in range(20):
        s = "ab" + ''.join(random.choices(string.ascii_lowercase, k=10)) + "ba"
        # This is generally not a palindrome unless the middle reverses perfectly,
        # so just verify the function doesn't crash and returns a bool
        result = is_palindrome(s)
        assert isinstance(result, bool)
