#!/usr/bin/env python3
"""
test_decoder_utils.py - Unit tests for decoder utility functions

Tests the critical sign_extend_32() function which masks values to 32 bits
and handles the sign extension from 64-bit Python integers.

The function is used throughout the simulator after manual sign extension
in the decoder for all immediate value types (I, S, B, U, J formats).

This is a cornerstone utility - if it has bugs, everything breaks.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decoder import sign_extend_32


def test_sign_extend_32_positive_32bit(runner):
    """Test that positive 32-bit values pass through unchanged"""
    test_cases = [
        0x00000000,
        0x00000001,
        0x0000007F,
        0x00007FFF,
        0x7FFFFFFF,  # Max positive 32-bit signed
    ]
    for value in test_cases:
        result = sign_extend_32(value)
        runner.log(f"  {value:#x} -> {result:#x}")
        if result != value:
            runner.test_fail("sign_extend_32 positive 32-bit", f"{value:#x}", f"{result:#x}")


def test_sign_extend_32_negative_32bit(runner):
    """Test that negative 32-bit values (bit 31 set) are preserved"""
    test_cases = [
        0x80000000,  # Min negative 32-bit signed
        0x80000001,
        0xFFFF8000,
        0xFFFFFF80,
        0xFFFFFFFF,  # -1 in 32-bit
    ]
    for value in test_cases:
        result = sign_extend_32(value)
        expected = value & 0xFFFFFFFF
        runner.log(f"  {value:#x} -> {result:#x}")
        if result != expected:
            runner.test_fail("sign_extend_32 negative 32-bit", f"{expected:#x}", f"{result:#x}")


def test_sign_extend_32_64bit_positive(runner):
    """Test that 64-bit positive values are masked to 32 bits"""
    test_cases = [
        (0x0000000100000000, 0x00000000),
        (0x0000000100000001, 0x00000001),
        (0x00000001FFFFFFFF, 0xFFFFFFFF),
        (0x123456787FFFFFFF, 0x7FFFFFFF),
    ]
    for value, expected in test_cases:
        result = sign_extend_32(value)
        runner.log(f"  {value:#x} -> {result:#x}")
        if result != expected:
            runner.test_fail("sign_extend_32 64-bit positive", f"{expected:#x}", f"{result:#x}",
                           f"input {value:#x}")


def test_sign_extend_32_64bit_negative(runner):
    """Test that sign-extended 64-bit negative values are masked correctly"""
    # These are values that have been sign-extended to 64 bits (as happens in decoder)
    test_cases = [
        (0xFFFFFFFFFFFFF000, 0xFFFFF000),  # 12-bit negative immediate extended
        (0xFFFFFFFFFFFFE000, 0xFFFFE000),  # 13-bit negative immediate extended
        (0xFFFFFFFFFFE00000, 0xFFE00000),  # 21-bit negative immediate extended
        (0xFFFFFFFF80000000, 0x80000000),  # 32-bit negative
        (0xFFFFFFFFFFFFFFFF, 0xFFFFFFFF),  # -1 extended
    ]
    for value, expected in test_cases:
        result = sign_extend_32(value)
        runner.log(f"  {value:#x} -> {result:#x}")
        if result != expected:
            runner.test_fail("sign_extend_32 64-bit negative", f"{expected:#x}", f"{result:#x}",
                           f"input {value:#x}")


def test_sign_extend_32_zero(runner):
    """Test sign extension of zero"""
    result = sign_extend_32(0)
    runner.log(f"  0x00000000 -> {result:#x}")
    if result != 0:
        runner.test_fail("sign_extend_32 zero", "0", f"{result:#x}")


def test_sign_extend_32_all_ones_32bit(runner):
    """Test sign extension of 32-bit all ones (-1)"""
    result = sign_extend_32(0xFFFFFFFF)
    expected = 0xFFFFFFFF
    runner.log(f"  0xFFFFFFFF -> {result:#x}")
    if result != expected:
        runner.test_fail("sign_extend_32 all ones", f"{expected:#x}", f"{result:#x}")


def test_sign_extend_32_boundary_cases(runner):
    """Test boundary cases around 32-bit sign bit"""
    test_cases = [
        (0x7FFFFFFE, 0x7FFFFFFE),  # Just below sign bit
        (0x7FFFFFFF, 0x7FFFFFFF),  # Max positive
        (0x80000000, 0x80000000),  # Min negative (sign bit set)
        (0x80000001, 0x80000001),  # Just above sign bit
    ]
    for value, expected in test_cases:
        result = sign_extend_32(value)
        runner.log(f"  {value:#x} -> {result:#x}")
        if result != expected:
            runner.test_fail("sign_extend_32 boundary", f"{expected:#x}", f"{result:#x}",
                           f"{value:#x}")


def test_sign_extend_32_idempotent(runner):
    """Test that sign_extend_32 is idempotent (applying twice gives same result)"""
    test_cases = [
        0x00000000,
        0x7FFFFFFF,
        0x80000000,
        0xFFFFFFFF,
        0xFFFFF000,  # Negative immediate
        0x00000FFF,  # Positive immediate
    ]
    for value in test_cases:
        result1 = sign_extend_32(value)
        result2 = sign_extend_32(result1)
        runner.log(f"  {value:#x} -> {result1:#x} -> {result2:#x}")
        if result1 != result2:
            runner.test_fail("sign_extend_32 idempotent", f"{result1:#x}", f"{result2:#x}",
                           f"Not idempotent: {value:#x}")


def test_sign_extend_32_immediate_simulation(runner):
    """Test simulated immediate values as they would come from decoder"""
    
    # I-type 12-bit immediate: 0x800 (-2048) extended to 64 bits then to 32
    imm_i_neg = 0x800
    if imm_i_neg & 0x800:
        imm_i_neg |= 0xFFFFFFFFFFFFF000
    result = sign_extend_32(imm_i_neg)
    expected = 0xFFFFF800
    runner.log(f"  I-type negative immediate (0x800) -> {result:#x}")
    if result != expected:
        runner.test_fail("I-type negative immediate", f"{expected:#x}", f"{result:#x}")
    
    # I-type positive: 0x7FF (2047)
    imm_i_pos = 0x7FF
    result = sign_extend_32(imm_i_pos)
    expected = 0x7FF
    runner.log(f"  I-type positive immediate (0x7FF) -> {result:#x}")
    if result != expected:
        runner.test_fail("I-type positive immediate", f"{expected:#x}", f"{result:#x}")
    
    # B-type 13-bit immediate: 0x1000 (bit 12 set, sign bit for 13-bit value)
    # Minimum negative 13-bit value is when only bit 12 is set
    imm_b_neg = 0x1000
    if imm_b_neg & 0x1000:
        imm_b_neg |= 0xFFFFFFFFFFFFE000  # Extend from bit 12
    result = sign_extend_32(imm_b_neg)
    expected = 0xFFFFF000  # Not 0xFFFFE000 - bit 12 itself stays set!
    runner.log(f"  B-type negative immediate (0x1000) -> {result:#x}")
    if result != expected:
        runner.test_fail("B-type negative immediate", f"{expected:#x}", f"{result:#x}")
    
    # J-type 21-bit immediate: 0x100000 (bit 20 set, sign bit for 21-bit value)
    # Minimum negative 21-bit value is when only bit 20 is set
    imm_j_neg = 0x100000
    if imm_j_neg & 0x100000:
        imm_j_neg |= 0xFFFFFFFFFFE00000  # Extend from bit 20
    result = sign_extend_32(imm_j_neg)
    expected = 0xFFF00000  # Not 0xFFE00000 - bit 20 itself stays set!
    runner.log(f"  J-type negative immediate (0x100000) -> {result:#x}")
    if result != expected:
        runner.test_fail("J-type negative immediate", f"{expected:#x}", f"{result:#x}")

