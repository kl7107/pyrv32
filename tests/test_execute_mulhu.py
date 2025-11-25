#!/usr/bin/env python3

"""
Unit tests for MULHU (Multiply High Unsigned) instruction.
Tests the upper 32 bits of unsigned × unsigned multiplication.
"""

import sys
sys.path.insert(0, '..')

def test_mulhu_small_values():
    """Test MULHU with small unsigned values"""
    # 2 × 3 = 6, upper 32 bits = 0
    from execute import exec_mulhu
    result = exec_mulhu(2, 3)
    assert result == 0, f"Expected 0, got {result:#010x}"
    print("✓ test_mulhu_small_values")

def test_mulhu_medium_values():
    """Test MULHU with medium unsigned values"""
    # 100 × 200 = 20000, upper 32 bits = 0
    from execute import exec_mulhu
    result = exec_mulhu(100, 200)
    assert result == 0, f"Expected 0, got {result:#010x}"
    print("✓ test_mulhu_medium_values")

def test_mulhu_max_unsigned_squared():
    """Test MULHU with max unsigned × max unsigned"""
    # 0xFFFFFFFF × 0xFFFFFFFF = 0xFFFFFFFE00000001
    # Upper 32 bits = 0xFFFFFFFE
    from execute import exec_mulhu
    result = exec_mulhu(0xFFFFFFFF, 0xFFFFFFFF)
    assert result == 0xFFFFFFFE, f"Expected 0xFFFFFFFE, got {result:#010x}"
    print("✓ test_mulhu_max_unsigned_squared")

def test_mulhu_large_times_2():
    """Test MULHU with 0x80000000 × 2"""
    # 0x80000000 × 2 = 0x100000000
    # Upper 32 bits = 1
    from execute import exec_mulhu
    result = exec_mulhu(0x80000000, 2)
    assert result == 1, f"Expected 1, got {result:#010x}"
    print("✓ test_mulhu_large_times_2")

def test_mulhu_0x80000000_squared():
    """Test MULHU with 0x80000000 × 0x80000000"""
    # 0x80000000 × 0x80000000 = 0x4000000000000000
    # Upper 32 bits = 0x40000000
    from execute import exec_mulhu
    result = exec_mulhu(0x80000000, 0x80000000)
    assert result == 0x40000000, f"Expected 0x40000000, got {result:#010x}"
    print("✓ test_mulhu_0x80000000_squared")

def test_mulhu_0x40000000_squared():
    """Test MULHU with 0x40000000 × 0x40000000"""
    # 0x40000000 × 0x40000000 = 0x1000000000000000
    # Upper 32 bits = 0x10000000
    from execute import exec_mulhu
    result = exec_mulhu(0x40000000, 0x40000000)
    assert result == 0x10000000, f"Expected 0x10000000, got {result:#010x}"
    print("✓ test_mulhu_0x40000000_squared")

def test_mulhu_max_unsigned_times_1():
    """Test MULHU with 0xFFFFFFFF × 1"""
    # 0xFFFFFFFF × 1 = 0xFFFFFFFF
    # Upper 32 bits = 0
    from execute import exec_mulhu
    result = exec_mulhu(0xFFFFFFFF, 1)
    assert result == 0, f"Expected 0, got {result:#010x}"
    print("✓ test_mulhu_max_unsigned_times_1")

def test_mulhu_0x10000_squared():
    """Test MULHU with 0x10000 × 0x10000"""
    # 0x10000 × 0x10000 = 0x100000000
    # Upper 32 bits = 1
    from execute import exec_mulhu
    result = exec_mulhu(0x10000, 0x10000)
    assert result == 1, f"Expected 1, got {result:#010x}"
    print("✓ test_mulhu_0x10000_squared")

def test_mulhu_max_unsigned_times_0x80000000():
    """Test MULHU with 0xFFFFFFFF × 0x80000000"""
    # 0xFFFFFFFF × 0x80000000 = 0x7FFFFFFF80000000
    # Upper 32 bits = 0x7FFFFFFF
    from execute import exec_mulhu
    result = exec_mulhu(0xFFFFFFFF, 0x80000000)
    assert result == 0x7FFFFFFF, f"Expected 0x7FFFFFFF, got {result:#010x}"
    print("✓ test_mulhu_max_unsigned_times_0x80000000")

def test_mulhu_0xFFFF_squared():
    """Test MULHU with 0xFFFF × 0xFFFF"""
    # 0xFFFF × 0xFFFF = 0xFFFE0001
    # Upper 32 bits = 0
    from execute import exec_mulhu
    result = exec_mulhu(0xFFFF, 0xFFFF)
    assert result == 0, f"Expected 0, got {result:#010x}"
    print("✓ test_mulhu_0xFFFF_squared")

def test_mulhu_zero():
    """Test MULHU with zero operands"""
    from execute import exec_mulhu
    result = exec_mulhu(0, 0xFFFFFFFF)
    assert result == 0, f"Expected 0, got {result:#010x}"
    result = exec_mulhu(0xFFFFFFFF, 0)
    assert result == 0, f"Expected 0, got {result:#010x}"
    print("✓ test_mulhu_zero")

def test_mulhu_commutative():
    """Test MULHU commutative property"""
    from execute import exec_mulhu
    result1 = exec_mulhu(0x12345678, 0x87654321)
    result2 = exec_mulhu(0x87654321, 0x12345678)
    assert result1 == result2, f"Expected {result1:#010x} == {result2:#010x}"
    print("✓ test_mulhu_commutative")

def test_mulhu_power_of_two():
    """Test MULHU with powers of two"""
    # 0x1000000 × 0x100 = 0x100000000
    # Upper 32 bits = 1
    from execute import exec_mulhu
    result = exec_mulhu(0x1000000, 0x100)
    assert result == 1, f"Expected 1, got {result:#010x}"
    print("✓ test_mulhu_power_of_two")

def main():
    """Run all MULHU tests"""
    print("Running MULHU instruction tests...")
    test_mulhu_small_values()
    test_mulhu_medium_values()
    test_mulhu_max_unsigned_squared()
    test_mulhu_large_times_2()
    test_mulhu_0x80000000_squared()
    test_mulhu_0x40000000_squared()
    test_mulhu_max_unsigned_times_1()
    test_mulhu_0x10000_squared()
    test_mulhu_max_unsigned_times_0x80000000()
    test_mulhu_0xFFFF_squared()
    test_mulhu_zero()
    test_mulhu_commutative()
    test_mulhu_power_of_two()
    print("✓ All MULHU tests passed (13/13)")

if __name__ == "__main__":
    main()
