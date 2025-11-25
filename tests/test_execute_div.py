#!/usr/bin/env python3

"""
Unit tests for DIV (Divide Signed) instruction.
Tests signed division with special RISC-V semantics.
"""

import sys
sys.path.insert(0, '..')

def test_div_normal():
    """Test DIV with normal positive division"""
    # 10 / 2 = 5
    from execute import exec_div
    result = exec_div(10, 2)
    assert result == 5, f"Expected 5, got {result}"
    print("✓ test_div_normal")

def test_div_negative_result():
    """Test DIV with positive / negative"""
    # 10 / -2 = -5
    from execute import exec_div
    result = exec_div(10, -2)
    assert result == 0xFFFFFFFB, f"Expected 0xFFFFFFFB (-5), got {result:#010x}"
    print("✓ test_div_negative_result")

def test_div_by_zero():
    """Test DIV by zero returns -1"""
    # 100 / 0 = -1 (per RISC-V spec)
    from execute import exec_div
    result = exec_div(100, 0)
    assert result == 0xFFFFFFFF, f"Expected 0xFFFFFFFF (-1), got {result:#010x}"
    print("✓ test_div_by_zero")

def test_div_overflow():
    """Test DIV overflow case: 0x80000000 / -1"""
    # 0x80000000 / -1 = 0x80000000 (per RISC-V spec)
    from execute import exec_div
    result = exec_div(-2147483648, -1)
    assert result == 0x80000000, f"Expected 0x80000000, got {result:#010x}"
    print("✓ test_div_overflow")

def test_div_zero_dividend():
    """Test DIV with zero dividend"""
    # 0 / 5 = 0
    from execute import exec_div
    result = exec_div(0, 5)
    assert result == 0, f"Expected 0, got {result:#010x}"
    print("✓ test_div_zero_dividend")

def test_div_negative_negative():
    """Test DIV with both operands negative"""
    # -10 / -2 = 5
    from execute import exec_div
    result = exec_div(-10, -2)
    assert result == 5, f"Expected 5, got {result}"
    print("✓ test_div_negative_negative")

def test_div_truncate_positive():
    """Test DIV truncates towards zero (positive)"""
    # 7 / 2 = 3 (not 4)
    from execute import exec_div
    result = exec_div(7, 2)
    assert result == 3, f"Expected 3, got {result}"
    print("✓ test_div_truncate_positive")

def test_div_truncate_negative():
    """Test DIV truncates towards zero (negative)"""
    # -7 / 2 = -3 (not -4)
    from execute import exec_div
    result = exec_div(-7, 2)
    assert result == 0xFFFFFFFD, f"Expected 0xFFFFFFFD (-3), got {result:#010x}"
    print("✓ test_div_truncate_negative")

def test_div_by_one():
    """Test DIV by 1"""
    # 12345 / 1 = 12345
    from execute import exec_div
    result = exec_div(12345, 1)
    assert result == 12345, f"Expected 12345, got {result}"
    print("✓ test_div_by_one")

def test_div_by_minus_one():
    """Test DIV by -1 (normal case, not overflow)"""
    # 100 / -1 = -100
    from execute import exec_div
    result = exec_div(100, -1)
    assert result == 0xFFFFFF9C, f"Expected 0xFFFFFF9C (-100), got {result:#010x}"
    print("✓ test_div_by_minus_one")

def test_div_large_numbers():
    """Test DIV with large numbers"""
    # 1000000 / 3 = 333333
    from execute import exec_div
    result = exec_div(1000000, 3)
    assert result == 333333, f"Expected 333333, got {result}"
    print("✓ test_div_large_numbers")

def test_div_max_positive():
    """Test DIV with max positive"""
    # 0x7FFFFFFF / 2 = 0x3FFFFFFF
    from execute import exec_div
    result = exec_div(0x7FFFFFFF, 2)
    assert result == 0x3FFFFFFF, f"Expected 0x3FFFFFFF, got {result:#010x}"
    print("✓ test_div_max_positive")

def test_div_max_negative():
    """Test DIV with max negative (not overflow)"""
    # 0x80000000 / 2 = 0xC0000000
    from execute import exec_div
    result = exec_div(-2147483648, 2)
    assert result == 0xC0000000, f"Expected 0xC0000000, got {result:#010x}"
    print("✓ test_div_max_negative")

def main():
    """Run all DIV tests"""
    print("Running DIV instruction tests...")
    test_div_normal()
    test_div_negative_result()
    test_div_by_zero()
    test_div_overflow()
    test_div_zero_dividend()
    test_div_negative_negative()
    test_div_truncate_positive()
    test_div_truncate_negative()
    test_div_by_one()
    test_div_by_minus_one()
    test_div_large_numbers()
    test_div_max_positive()
    test_div_max_negative()
    print("✓ All DIV tests passed (13/13)")

if __name__ == "__main__":
    main()
