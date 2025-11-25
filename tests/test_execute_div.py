#!/usr/bin/env python3

"""
Unit tests for DIV (Divide Signed) instruction.
Tests signed division with special RISC-V semantics.
"""

import sys
sys.path.insert(0, '..')


def test_div_normal(runner):
    """Test DIV with normal positive division"""
    # 10 / 2 = 5
    from execute import exec_div
    result = exec_div(10, 2)
    if result != 5:
        runner.test_fail("DIV normal", "5", f"{result}")


def test_div_negative_result(runner):
    """Test DIV with positive / negative"""
    # 10 / -2 = -5
    from execute import exec_div
    result = exec_div(10, -2)
    if result != 0xFFFFFFFB:
        runner.test_fail("DIV positive/negative", "0xFFFFFFFB (-5)", f"{result:#010x}")


def test_div_by_zero(runner):
    """Test DIV by zero returns -1"""
    # 100 / 0 = -1 (per RISC-V spec)
    from execute import exec_div
    result = exec_div(100, 0)
    if result != 0xFFFFFFFF:
        runner.test_fail("DIV by zero", "0xFFFFFFFF (-1)", f"{result:#010x}")


def test_div_overflow(runner):
    """Test DIV overflow case: 0x80000000 / -1"""
    # 0x80000000 / -1 = 0x80000000 (per RISC-V spec)
    from execute import exec_div
    result = exec_div(-2147483648, -1)
    if result != 0x80000000:
        runner.test_fail("DIV overflow", "0x80000000", f"{result:#010x}")


def test_div_zero_dividend(runner):
    """Test DIV with zero dividend"""
    # 0 / 5 = 0
    from execute import exec_div
    result = exec_div(0, 5)
    if result != 0:
        runner.test_fail("DIV zero dividend", "0", f"{result:#010x}")


def test_div_negative_negative(runner):
    """Test DIV with both operands negative"""
    # -10 / -2 = 5
    from execute import exec_div
    result = exec_div(-10, -2)
    if result != 5:
        runner.test_fail("DIV negative/negative", "5", f"{result}")


def test_div_truncate_positive(runner):
    """Test DIV truncates towards zero (positive)"""
    # 7 / 2 = 3 (not 4)
    from execute import exec_div
    result = exec_div(7, 2)
    if result != 3:
        runner.test_fail("DIV truncate positive", "3", f"{result}")


def test_div_truncate_negative(runner):
    """Test DIV truncates towards zero (negative)"""
    # -7 / 2 = -3 (not -4)
    from execute import exec_div
    result = exec_div(-7, 2)
    if result != 0xFFFFFFFD:
        runner.test_fail("DIV truncate negative", "0xFFFFFFFD (-3)", f"{result:#010x}")


def test_div_by_one(runner):
    """Test DIV by 1"""
    # 12345 / 1 = 12345
    from execute import exec_div
    result = exec_div(12345, 1)
    if result != 12345:
        runner.test_fail("DIV by 1", "12345", f"{result}")


def test_div_by_minus_one(runner):
    """Test DIV by -1 (normal case, not overflow)"""
    # 100 / -1 = -100
    from execute import exec_div
    result = exec_div(100, -1)
    if result != 0xFFFFFF9C:
        runner.test_fail("DIV by -1", "0xFFFFFF9C (-100)", f"{result:#010x}")


def test_div_large_numbers(runner):
    """Test DIV with large numbers"""
    # 1000000 / 3 = 333333
    from execute import exec_div
    result = exec_div(1000000, 3)
    if result != 333333:
        runner.test_fail("DIV large numbers", "333333", f"{result}")


def test_div_max_positive(runner):
    """Test DIV with max positive"""
    # 0x7FFFFFFF / 2 = 0x3FFFFFFF
    from execute import exec_div
    result = exec_div(0x7FFFFFFF, 2)
    if result != 0x3FFFFFFF:
        runner.test_fail("DIV max positive", "0x3FFFFFFF", f"{result:#010x}")


def test_div_max_negative(runner):
    """Test DIV with max negative (not overflow)"""
    # 0x80000000 / 2 = 0xC0000000
    from execute import exec_div
    result = exec_div(-2147483648, 2)
    if result != 0xC0000000:
        runner.test_fail("DIV max negative", "0xC0000000", f"{result:#010x}")
