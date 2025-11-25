#!/usr/bin/env python3

"""
Unit tests for REMU (Remainder Unsigned) instruction.
Tests unsigned remainder with RISC-V semantics.
"""

import sys
sys.path.insert(0, '..')

def test_remu_normal():
    """Test REMU with normal division (no remainder)"""
    # 10 % 2 = 0
    from execute import exec_remu
    result = exec_remu(10, 2)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_remu_normal")

def test_remu_with_remainder():
    """Test REMU with remainder"""
    # 10 % 3 = 1
    from execute import exec_remu
    result = exec_remu(10, 3)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_remu_with_remainder")

def test_remu_by_zero():
    """Test REMU by zero returns dividend"""
    # 100 % 0 = 100 (per RISC-V spec)
    from execute import exec_remu
    result = exec_remu(100, 0)
    assert result == 100, f"Expected 100, got {result}"
    print("✓ test_remu_by_zero")

def test_remu_zero_dividend():
    """Test REMU with zero dividend"""
    # 0 % 5 = 0
    from execute import exec_remu
    result = exec_remu(0, 5)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_remu_zero_dividend")

def test_remu_max_mod_2():
    """Test REMU with max unsigned % 2"""
    # 0xFFFFFFFF % 2 = 1
    from execute import exec_remu
    result = exec_remu(0xFFFFFFFF, 2)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_remu_max_mod_2")

def test_remu_max_mod_3():
    """Test REMU with max unsigned % 3"""
    # 0xFFFFFFFF % 3 = 0
    from execute import exec_remu
    result = exec_remu(0xFFFFFFFF, 3)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_remu_max_mod_3")

def test_remu_large_mod_small():
    """Test REMU with large unsigned % small"""
    # 0x80000000 % 3 = 2
    from execute import exec_remu
    result = exec_remu(0x80000000, 3)
    assert result == 2, f"Expected 2, got {result}"
    print("✓ test_remu_large_mod_small")

def test_remu_7_mod_2():
    """Test REMU with 7 % 2"""
    # 7 % 2 = 1
    from execute import exec_remu
    result = exec_remu(7, 2)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_remu_7_mod_2")

def test_remu_large_numbers():
    """Test REMU with large numbers"""
    # 1000000 % 7 = 1
    from execute import exec_remu
    result = exec_remu(1000000, 7)
    assert result == 1, f"Expected 1, got {result}"
    print("✓ test_remu_large_numbers")

def test_remu_max_mod_max():
    """Test REMU with max % max"""
    # 0xFFFFFFFF % 0xFFFFFFFF = 0
    from execute import exec_remu
    result = exec_remu(0xFFFFFFFF, 0xFFFFFFFF)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ test_remu_max_mod_max")

def test_remu_max_minus_1_mod_max():
    """Test REMU with (max-1) % max"""
    # 0xFFFFFFFE % 0xFFFFFFFF = 0xFFFFFFFE
    from execute import exec_remu
    result = exec_remu(0xFFFFFFFE, 0xFFFFFFFF)
    assert result == 0xFFFFFFFE, f"Expected 0xFFFFFFFE, got {result:#010x}"
    print("✓ test_remu_max_minus_1_mod_max")

def test_remu_power_of_two():
    """Test REMU with power of two"""
    # 0x12345678 % 0x100 = 0x78
    from execute import exec_remu
    result = exec_remu(0x12345678, 0x100)
    assert result == 0x78, f"Expected 0x78, got {result:#010x}"
    print("✓ test_remu_power_of_two")

def test_remu_no_negative():
    """Test REMU has no negative remainders"""
    # 0xFFFFFFFF % 10 should be positive
    from execute import exec_remu
    result = exec_remu(0xFFFFFFFF, 10)
    assert result == 5, f"Expected 5, got {result}"
    print("✓ test_remu_no_negative")

def main():
    """Run all REMU tests"""
    print("Running REMU instruction tests...")
    test_remu_normal()
    test_remu_with_remainder()
    test_remu_by_zero()
    test_remu_zero_dividend()
    test_remu_max_mod_2()
    test_remu_max_mod_3()
    test_remu_large_mod_small()
    test_remu_7_mod_2()
    test_remu_large_numbers()
    test_remu_max_mod_max()
    test_remu_max_minus_1_mod_max()
    test_remu_power_of_two()
    test_remu_no_negative()
    print("✓ All REMU tests passed (13/13)")

if __name__ == "__main__":
    main()
