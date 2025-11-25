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
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decoder import sign_extend_32

# Logging setup
log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_test_decoder_utils.log')
def log(msg):
    print(msg)
    log_file.write(msg + '\n')
    log_file.flush()

def test_sign_extend_32_positive_32bit():
    """Test that positive 32-bit values pass through unchanged"""
    log("TEST: sign_extend_32 with positive 32-bit values")
    test_cases = [
        0x00000000,
        0x00000001,
        0x0000007F,
        0x00007FFF,
        0x7FFFFFFF,  # Max positive 32-bit signed
    ]
    for value in test_cases:
        result = sign_extend_32(value)
        assert result == value, f"Expected {value:#x}, got {result:#x}"
        log(f"  ✓ {value:#x} -> {result:#x}")

def test_sign_extend_32_negative_32bit():
    """Test that negative 32-bit values (bit 31 set) are preserved"""
    log("TEST: sign_extend_32 with negative 32-bit values")
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
        assert result == expected, f"Expected {expected:#x}, got {result:#x}"
        log(f"  ✓ {value:#x} -> {result:#x}")

def test_sign_extend_32_64bit_positive():
    """Test that 64-bit positive values are masked to 32 bits"""
    log("TEST: sign_extend_32 masking 64-bit positive to 32 bits")
    test_cases = [
        (0x0000000100000000, 0x00000000),
        (0x0000000100000001, 0x00000001),
        (0x00000001FFFFFFFF, 0xFFFFFFFF),
        (0x123456787FFFFFFF, 0x7FFFFFFF),
    ]
    for value, expected in test_cases:
        result = sign_extend_32(value)
        assert result == expected, f"Expected {expected:#x}, got {result:#x} for input {value:#x}"
        log(f"  ✓ {value:#x} -> {result:#x}")

def test_sign_extend_32_64bit_negative():
    """Test that sign-extended 64-bit negative values are masked correctly"""
    log("TEST: sign_extend_32 with 64-bit sign-extended negative values")
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
        assert result == expected, f"Expected {expected:#x}, got {result:#x} for input {value:#x}"
        log(f"  ✓ {value:#x} -> {result:#x}")

def test_sign_extend_32_zero():
    """Test sign extension of zero"""
    log("TEST: sign_extend_32 with zero")
    result = sign_extend_32(0)
    assert result == 0, f"Expected 0, got {result:#x}"
    log(f"  ✓ 0x00000000 -> {result:#x}")

def test_sign_extend_32_all_ones_32bit():
    """Test sign extension of 32-bit all ones (-1)"""
    log("TEST: sign_extend_32 with 32-bit all ones")
    result = sign_extend_32(0xFFFFFFFF)
    expected = 0xFFFFFFFF
    assert result == expected, f"Expected {expected:#x}, got {result:#x}"
    log(f"  ✓ 0xFFFFFFFF -> {result:#x}")

def test_sign_extend_32_boundary_cases():
    """Test boundary cases around 32-bit sign bit"""
    log("TEST: sign_extend_32 boundary cases")
    test_cases = [
        (0x7FFFFFFE, 0x7FFFFFFE),  # Just below sign bit
        (0x7FFFFFFF, 0x7FFFFFFF),  # Max positive
        (0x80000000, 0x80000000),  # Min negative (sign bit set)
        (0x80000001, 0x80000001),  # Just above sign bit
    ]
    for value, expected in test_cases:
        result = sign_extend_32(value)
        assert result == expected, f"Expected {expected:#x}, got {result:#x} for {value:#x}"
        log(f"  ✓ {value:#x} -> {result:#x}")

def test_sign_extend_32_idempotent():
    """Test that sign_extend_32 is idempotent (applying twice gives same result)"""
    log("TEST: sign_extend_32 idempotency")
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
        assert result1 == result2, f"Not idempotent: {value:#x} -> {result1:#x} -> {result2:#x}"
        log(f"  ✓ {value:#x} -> {result1:#x} -> {result2:#x} (idempotent)")

def test_sign_extend_32_immediate_simulation():
    """Test simulated immediate values as they would come from decoder"""
    log("TEST: sign_extend_32 with simulated decoder immediate values")
    
    # I-type 12-bit immediate: 0x800 (-2048) extended to 64 bits then to 32
    imm_i_neg = 0x800
    if imm_i_neg & 0x800:
        imm_i_neg |= 0xFFFFFFFFFFFFF000
    result = sign_extend_32(imm_i_neg)
    expected = 0xFFFFF800
    assert result == expected, f"I-type negative: expected {expected:#x}, got {result:#x}"
    log(f"  ✓ I-type negative immediate (0x800) -> {result:#x}")
    
    # I-type positive: 0x7FF (2047)
    imm_i_pos = 0x7FF
    result = sign_extend_32(imm_i_pos)
    expected = 0x7FF
    assert result == expected, f"I-type positive: expected {expected:#x}, got {result:#x}"
    log(f"  ✓ I-type positive immediate (0x7FF) -> {result:#x}")
    
    # B-type 13-bit immediate: 0x1000 (bit 12 set, sign bit for 13-bit value)
    # Minimum negative 13-bit value is when only bit 12 is set
    imm_b_neg = 0x1000
    if imm_b_neg & 0x1000:
        imm_b_neg |= 0xFFFFFFFFFFFFE000  # Extend from bit 12
    result = sign_extend_32(imm_b_neg)
    expected = 0xFFFFF000  # Not 0xFFFFE000 - bit 12 itself stays set!
    assert result == expected, f"B-type negative: expected {expected:#x}, got {result:#x}"
    log(f"  ✓ B-type negative immediate (0x1000) -> {result:#x}")
    
    # J-type 21-bit immediate: 0x100000 (bit 20 set, sign bit for 21-bit value)
    # Minimum negative 21-bit value is when only bit 20 is set
    imm_j_neg = 0x100000
    if imm_j_neg & 0x100000:
        imm_j_neg |= 0xFFFFFFFFFFE00000  # Extend from bit 20
    result = sign_extend_32(imm_j_neg)
    expected = 0xFFF00000  # Not 0xFFE00000 - bit 20 itself stays set!
    assert result == expected, f"J-type negative: expected {expected:#x}, got {result:#x}"
    log(f"  ✓ J-type negative immediate (0x100000) -> {result:#x}")

def run_all_tests():
    """Run all decoder utility tests"""
    log("=" * 60)
    log("DECODER UTILITIES TEST SUITE")
    log("=" * 60)
    
    tests = [
        test_sign_extend_32_positive_32bit,
        test_sign_extend_32_negative_32bit,
        test_sign_extend_32_64bit_positive,
        test_sign_extend_32_64bit_negative,
        test_sign_extend_32_zero,
        test_sign_extend_32_all_ones_32bit,
        test_sign_extend_32_boundary_cases,
        test_sign_extend_32_idempotent,
        test_sign_extend_32_immediate_simulation,
    ]
    
    for test in tests:
        try:
            test()
        except AssertionError as e:
            log(f"✗ FAIL: {test.__name__}")
            log(f"  Error: {e}")
            log_file.close()
            sys.exit(1)
    
    log("=" * 60)
    log(f"All {len(tests)} decoder utility tests passed ✓")
    log("=" * 60)
    log_file.close()

if __name__ == '__main__':
    run_all_tests()
