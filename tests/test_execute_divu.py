#!/usr/bin/env python3

"""
Unit tests for DIVU (Divide Unsigned) instruction.
Tests unsigned division with RISC-V semantics.
"""

import sys
sys.path.insert(0, '..')


def test_divu_normal(runner):
    """Test DIVU with normal positive division"""
    # 10 / 2 = 5
    from execute import exec_divu
    result = exec_divu(10, 2)
    if result != 5:
        runner.test_fail("DIVU normal", "5", f"{result}")


def test_divu_large_unsigned(runner):
    """Test DIVU with large unsigned value"""
    # 0x80000000 / 2 = 0x40000000 (treated as unsigned)
    from execute import exec_divu
    result = exec_divu(0x80000000, 2)
    if result != 0x40000000:
        runner.test_fail("DIVU large unsigned", "0x40000000", f"{result:#010x}")


def test_divu_by_zero(runner):
    """Test DIVU by zero returns all 1s"""
    # 100 / 0 = 0xFFFFFFFF (per RISC-V spec)
    from execute import exec_divu
    result = exec_divu(100, 0)
    if result != 0xFFFFFFFF:
        runner.test_fail("DIVU by zero", "0xFFFFFFFF", f"{result:#010x}")


def test_divu_zero_dividend(runner):
    """Test DIVU with zero dividend"""
    # 0 / 5 = 0
    from execute import exec_divu
    result = exec_divu(0, 5)
    if result != 0:
        runner.test_fail("DIVU zero dividend", "0", f"{result:#010x}")


def test_divu_max_by_max(runner):
    """Test DIVU with max unsigned values"""
    # 0xFFFFFFFF / 0xFFFFFFFF = 1
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFF, 0xFFFFFFFF)
    if result != 1:
        runner.test_fail("DIVU max/max", "1", f"{result}")


def test_divu_max_by_2(runner):
    """Test DIVU with max unsigned / 2"""
    # 0xFFFFFFFF / 2 = 0x7FFFFFFF
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFF, 2)
    if result != 0x7FFFFFFF:
        runner.test_fail("DIVU max/2", "0x7FFFFFFF", f"{result:#010x}")


def test_divu_max_by_3(runner):
    """Test DIVU with max unsigned / 3"""
    # 0xFFFFFFFF / 3 = 0x55555555
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFF, 3)
    if result != 0x55555555:
        runner.test_fail("DIVU max/3", "0x55555555", f"{result:#010x}")


def test_divu_by_one(runner):
    """Test DIVU by 1"""
    # 12345 / 1 = 12345
    from execute import exec_divu
    result = exec_divu(12345, 1)
    if result != 12345:
        runner.test_fail("DIVU by 1", "12345", f"{result}")


def test_divu_truncate(runner):
    """Test DIVU truncates"""
    # 7 / 2 = 3 (not 4)
    from execute import exec_divu
    result = exec_divu(7, 2)
    if result != 3:
        runner.test_fail("DIVU truncate", "3", f"{result}")


def test_divu_large_numbers(runner):
    """Test DIVU with large numbers"""
    # 1000000 / 3 = 333333
    from execute import exec_divu
    result = exec_divu(1000000, 3)
    if result != 333333:
        runner.test_fail("DIVU large numbers", "333333", f"{result}")


def test_divu_max_minus_1(runner):
    """Test DIVU with 0xFFFFFFFE / 0xFFFFFFFF"""
    # 0xFFFFFFFE / 0xFFFFFFFF = 0
    from execute import exec_divu
    result = exec_divu(0xFFFFFFFE, 0xFFFFFFFF)
    if result != 0:
        runner.test_fail("DIVU max-1/max", "0", f"{result}")


def test_divu_power_of_two(runner):
    """Test DIVU with power of two"""
    # 0x10000000 / 0x100 = 0x100000
    from execute import exec_divu
    result = exec_divu(0x10000000, 0x100)
    if result != 0x100000:
        runner.test_fail("DIVU power of two", "0x100000", f"{result:#010x}")


def test_divu_no_overflow(runner):
    """Test DIVU has no overflow case (unlike DIV)"""
    # 0x80000000 / 0xFFFFFFFF = 0
    from execute import exec_divu
    result = exec_divu(0x80000000, 0xFFFFFFFF)
    if result != 0:
        runner.test_fail("DIVU no overflow", "0", f"{result}")
