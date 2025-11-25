#!/usr/bin/env python3

"""
Unit tests for REM (Remainder Signed) instruction.
Tests signed remainder with RISC-V semantics.
"""

import sys
sys.path.insert(0, '..')

def test_rem_normal():
    """Test REM with normal division (no remainder)"""
    # 10 % 2 = 0
    from execute import exec_rem
    result = exec_rem(10, 2)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_rem_normal")

def test_rem_with_remainder():
    """Test REM with remainder"""
    # 10 % 3 = 1
    from execute import exec_rem
    result = exec_rem(10, 3)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_rem_with_remainder")

def test_rem_by_zero():
    """Test REM by zero returns dividend"""
    # 100 % 0 = 100 (per RISC-V spec)
    from execute import exec_rem
    result = exec_rem(100, 0)
    assert result == 100, f"Expected 100, got {result}"
    print("✓ test_rem_by_zero")

def test_rem_overflow():
    """Test REM overflow case: 0x80000000 % -1"""
    # 0x80000000 % -1 = 0 (per RISC-V spec)
    from execute import exec_rem
    result = exec_rem(-2147483648, -1)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_rem_overflow")

def test_rem_zero_dividend():
    """Test REM with zero dividend"""
    # 0 % 5 = 0
    from execute import exec_rem
    result = exec_rem(0, 5)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_rem_zero_dividend")

def test_rem_negative_dividend_positive_divisor():
    """Test REM with negative dividend, positive divisor"""
    # -10 % 3 = -1 (sign follows dividend)
    from execute import exec_rem
    result = exec_rem(-10, 3)
    assert result == 0xFFFFFFFF, f"Expected 0xFFFFFFFF (-1), got {result:#010x}"
    print("✓ test_rem_negative_dividend_positive_divisor")

def test_rem_positive_dividend_negative_divisor():
    """Test REM with positive dividend, negative divisor"""
    # 10 % -3 = 1 (sign follows dividend)
    from execute import exec_rem
    result = exec_rem(10, -3)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_rem_positive_dividend_negative_divisor")

def test_rem_negative_negative():
    """Test REM with both operands negative"""
    # -10 % -3 = -1 (sign follows dividend)
    from execute import exec_rem
    result = exec_rem(-10, -3)
    assert result == 0xFFFFFFFF, f"Expected 0xFFFFFFFF (-1), got {result:#010x}"
    print("✓ test_rem_negative_negative")

def test_rem_7_mod_2():
    """Test REM with 7 % 2"""
    # 7 % 2 = 1
    from execute import exec_rem
    result = exec_rem(7, 2)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_rem_7_mod_2")

def test_rem_negative_7_mod_2():
    """Test REM with -7 % 2"""
    # -7 % 2 = -1 (sign follows dividend)
    from execute import exec_rem
    result = exec_rem(-7, 2)
    assert result == 0xFFFFFFFF, f"Expected 0xFFFFFFFF (-1), got {result:#010x}"
    print("✓ test_rem_negative_7_mod_2")

def test_rem_large_numbers():
    """Test REM with large numbers"""
    # 1000000 % 7 = 1
    from execute import exec_rem
    result = exec_rem(1000000, 7)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_rem_large_numbers")

def test_rem_max_positive():
    """Test REM with max positive"""
    # 0x7FFFFFFF % 2 = 1
    from execute import exec_rem
    result = exec_rem(0x7FFFFFFF, 2)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_rem_max_positive")

def test_rem_max_negative():
    """Test REM with max negative (not overflow)"""
    # 0x80000000 % 2 = 0
    from execute import exec_rem
    result = exec_rem(-2147483648, 2)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_rem_max_negative")

def main():
    """Run all REM tests"""
    print("Running REM instruction tests...")
    test_rem_normal()
    test_rem_with_remainder()
    test_rem_by_zero()
    test_rem_overflow()
    test_rem_zero_dividend()
    test_rem_negative_dividend_positive_divisor()
    test_rem_positive_dividend_negative_divisor()
    test_rem_negative_negative()
    test_rem_7_mod_2()
    test_rem_negative_7_mod_2()
    test_rem_large_numbers()
    test_rem_max_positive()
    test_rem_max_negative()
    print("✓ All REM tests passed (13/13)")

if __name__ == "__main__":
    main()
