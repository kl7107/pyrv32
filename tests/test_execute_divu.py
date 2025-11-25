#!/usr/bin/env python3

"""
Unit tests for DIVU (Divide Unsigned) instruction.
Tests unsigned division with RISC-V semantics.
"""

import sys
sys.path.insert(0, '..')

def test_divu_normal():
    """Test DIVU with normal positive division"""
    # 10 / 2 = 5
    from execute import exec_divu
    result = exec_divu(10, 2)
    assert result == 5, f"Expected 5, got {result}"
    print("✓ test_divu_normal")

def test_divu_large_unsigned():
    """Test DIVU with large unsigned value"""
    # 0x80000000 / 2 = 0x40000000 (treated as unsigned)
    from execute import exec_divu
    result = exec_divu(0x80000000, 2)
    assert result == 0x40000000, f"Expected 0x40000000, got {result:#010x}"
    print("✓ test_divu_large_unsigned")

def test_divu_by_zero():
    """Test DIVU by zero returns all 1s"""
    # 100 / 0 = 0xFFFFFFFF (per RISC-V spec)
    from execute import exec_divu
    result = exec_divu(100, 0)
    assert result == 0xFFFFFFFF, f"Expected 0xFFFFFFFF, got {result:#010x}"
    print("✓ test_divu_by_zero")

def test_divu_zero_dividend():
    """Test DIVU with zero dividend"""
    # 0 / 5 = 0
    from execute import exec_divu
    result = exec_divu(0, 5)
    assert result == 0, f"Expected 0, got {result:#010x}"
    print("✓ test_divu_zero_dividend")

def test_divu_max_by_max():
    """Test DIVU with max unsigned values"""
    # 0xFFFFFFFF / 0xFFFFFFFF = 1
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFF, 0xFFFFFFFF)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_divu_max_by_max")

def test_divu_max_by_2():
    """Test DIVU with max unsigned / 2"""
    # 0xFFFFFFFF / 2 = 0x7FFFFFFF
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFF, 2)
    assert result == 0x7FFFFFFF, f"Expected 0x7FFFFFFF, got {result:#010x}"
    print("✓ test_divu_max_by_2")

def test_divu_max_by_3():
    """Test DIVU with max unsigned / 3"""
    # 0xFFFFFFFF / 3 = 0x55555555
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFF, 3)
    assert result == 0x55555555, f"Expected 0x55555555, got {result:#010x}"
    print("✓ test_divu_max_by_3")

def test_divu_by_one():
    """Test DIVU by 1"""
    # 12345 / 1 = 12345
    from execute import exec_divu
    result = exec_divu(12345, 1)
    assert result == 12345, f"Expected 12345, got {result}"
    print("✓ test_divu_by_one")

def test_divu_truncate():
    """Test DIVU truncates"""
    # 7 / 2 = 3 (not 4)
    from execute import exec_divu
    result = exec_divu(7, 2)
    assert result == 3, f"Expected 3, got {result}"
    print("✓ test_divu_truncate")

def test_divu_large_numbers():
    """Test DIVU with large numbers"""
    # 1000000 / 3 = 333333
    from execute import exec_divu
    result = exec_divu(1000000, 3)
    assert result == 333333, f"Expected 333333, got {result}"
    print("✓ test_divu_large_numbers")

def test_divu_max_minus_1():
    """Test DIVU with 0xFFFFFFFE / 0xFFFFFFFF"""
    # 0xFFFFFFFE / 0xFFFFFFFF = 0
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFE, 0xFFFFFFFF)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_divu_max_minus_1")

def test_divu_power_of_two():
    """Test DIVU with power of two"""
    # 0x10000000 / 0x100 = 0x100000
    from execute import exec_divu
    result = exec_divu(0x10000000, 0x100)
    assert result == 0x100000, f"Expected 0x100000, got {result:#010x}"
    print("✓ test_divu_power_of_two")

def test_divu_no_overflow():
    """Test DIVU has no overflow case (unlike DIV)"""
    # 0x80000000 / 0xFFFFFFFF = 0
    from execute import exec_divu
    result = exec_divu(0x80000000, 0xFFFFFFFF)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_divu_no_overflow")

def main():
    """Run all DIVU tests"""
    print("Running DIVU instruction tests...")
    test_divu_normal()
    test_divu_large_unsigned()
    test_divu_by_zero()
    test_divu_zero_dividend()
    test_divu_max_by_max()
    test_divu_max_by_2()
    test_divu_max_by_3()
    test_divu_by_one()
    test_divu_truncate()
    test_divu_large_numbers()
    test_divu_max_minus_1()
    test_divu_power_of_two()
    test_divu_no_overflow()
    print("✓ All DIVU tests passed (13/13)")

if __name__ == "__main__":
    main()
