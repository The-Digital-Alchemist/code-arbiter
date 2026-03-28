import pytest
from solution import evaluate


def test_single_number():
    assert evaluate("3") == 3


def test_addition():
    assert evaluate("1+2") == 3


def test_subtraction():
    assert evaluate("5-3") == 2


def test_multiplication():
    assert evaluate("3*4") == 12


def test_division():
    assert evaluate("8/4") == 2


def test_precedence_mul_before_add():
    assert evaluate("2+3*4") == 14


def test_precedence_div_before_sub():
    assert evaluate("10-6/2") == 7


def test_left_to_right_same_precedence():
    assert evaluate("10-3-2") == 5


def test_parentheses_override_precedence():
    assert evaluate("(2+3)*4") == 20


def test_nested_parentheses():
    assert evaluate("((2+3)*4)-5") == 15


def test_complex_expression():
    assert evaluate("3+5/2*4-1") == 12


def test_division_truncates_toward_zero():
    assert evaluate("7/2") == 3


def test_multi_digit_numbers():
    assert evaluate("100+200") == 300


def test_only_parenthesized():
    assert evaluate("(42)") == 42


def test_all_ops():
    # 2 * (3 + 4) / 7 - 1 = 2*7/7 - 1 = 2 - 1 = 1
    assert evaluate("2*(3+4)/7-1") == 1
