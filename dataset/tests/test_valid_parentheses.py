import random
from solution import valid_parentheses


def test_valid_simple():
    assert valid_parentheses("()") is True
    assert valid_parentheses("[]") is True
    assert valid_parentheses("{}") is True


def test_valid_mixed():
    assert valid_parentheses("()[]{}") is True
    assert valid_parentheses("{[()]}") is True
    assert valid_parentheses("({[]})") is True


def test_invalid_mismatched():
    assert valid_parentheses("(]") is False
    assert valid_parentheses("([)]") is False
    assert valid_parentheses("{[}]") is False


def test_invalid_unclosed():
    assert valid_parentheses("{") is False
    assert valid_parentheses("(()") is False
    assert valid_parentheses("((((") is False


def test_invalid_extra_closing():
    assert valid_parentheses(")") is False
    assert valid_parentheses("())") is False


def test_empty():
    assert valid_parentheses("") is True


def test_long_valid():
    s = "({[" * 100 + "]})" * 100
    assert valid_parentheses(s) is True


def test_long_invalid():
    s = "({[" * 100 + "[]})" * 100
    assert valid_parentheses(s) is False
