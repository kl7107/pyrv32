#!/usr/bin/env python3
"""
Unit tests for MUL instruction (M extension).

MUL performs signed multiplication and returns the lower 32 bits of the result.
Format: MUL rd, rs1, rs2
Encoding: opcode=0110011, funct3=000, funct7=0000001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction

def test_mul_positive_positive():
    """Test MUL with two positive numbers: 2 × 3 = 6"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Set up registers
    cpu.regs[5] = 2
    cpu.regs[6] = 3
    
    # MUL x10, x5, x6 (2 × 3 = 6)
    # opcode=0110011, rd=01010, funct3=000, rs1=00101, rs2=00110, funct7=0000001
    # 0000001_00110_00101_000_01010_0110011
    insn = 0b0000001_00110_00101_000_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[10] == 6, f"Expected x10=6, got {cpu.regs[10]}"
    assert cpu.pc == 4, f"Expected PC=4, got {cpu.pc}"
    print("✓ test_mul_positive_positive passed")

def test_mul_positive_negative():
    """Test MUL with positive × negative: 2 × -3 = -6"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 2
    cpu.regs[6] = (-3 & 0xFFFFFFFF)  # -3 in 32-bit two's complement
    
    # MUL x11, x5, x6
    insn = 0b0000001_00110_00101_000_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = (-6 & 0xFFFFFFFF)  # 0xFFFFFFFA
    assert cpu.regs[11] == expected, f"Expected x11=0x{expected:08X}, got 0x{cpu.regs[11]:08X}"
    print("✓ test_mul_positive_negative passed")

def test_mul_zero():
    """Test MUL with zero: 0 × 5 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # MUL x12, x5, x6
    insn = 0b0000001_00110_00101_000_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[12] == 0, f"Expected x12=0, got {cpu.regs[12]}"
    print("✓ test_mul_zero passed")

def test_mul_one():
    """Test MUL with one: 1 × 1 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1
    cpu.regs[6] = 1
    
    # MUL x13, x5, x6
    insn = 0b0000001_00110_00101_000_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[13] == 1, f"Expected x13=1, got {cpu.regs[13]}"
    print("✓ test_mul_one passed")

def test_mul_negative_positive():
    """Test MUL with negative × positive: -2 × 1 = -2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-2 & 0xFFFFFFFF)
    cpu.regs[6] = 1
    
    # MUL x14, x5, x6
    insn = 0b0000001_00110_00101_000_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = (-2 & 0xFFFFFFFF)  # 0xFFFFFFFE
    assert cpu.regs[14] == expected, f"Expected x14=0x{expected:08X}, got 0x{cpu.regs[14]:08X}"
    print("✓ test_mul_negative_positive passed")

def test_mul_negative_negative():
    """Test MUL with negative × negative: -1 × -1 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-1 & 0xFFFFFFFF)
    cpu.regs[6] = (-1 & 0xFFFFFFFF)
    
    # MUL x15, x5, x6
    insn = 0b0000001_00110_00101_000_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[15] == 1, f"Expected x15=1, got {cpu.regs[15]}"
    print("✓ test_mul_negative_negative passed")

def test_mul_max_positive():
    """Test MUL with max positive: 0x7FFFFFFF × 1 = 0x7FFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF  # Max positive 32-bit signed
    cpu.regs[6] = 1
    
    # MUL x16, x5, x6
    insn = 0b0000001_00110_00101_000_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[16] == 0x7FFFFFFF, f"Expected x16=0x7FFFFFFF, got 0x{cpu.regs[16]:08X}"
    print("✓ test_mul_max_positive passed")

def test_mul_max_negative():
    """Test MUL with max negative: 0x80000000 × 1 = 0x80000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000  # Min negative 32-bit signed
    cpu.regs[6] = 1
    
    # MUL x17, x5, x6
    insn = 0b0000001_00110_00101_000_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[17] == 0x80000000, f"Expected x17=0x80000000, got 0x{cpu.regs[17]:08X}"
    print("✓ test_mul_max_negative passed")

def test_mul_overflow():
    """Test MUL overflow: 0x10000 × 0x10000 = 0x100000000, lower 32 bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x10000
    cpu.regs[6] = 0x10000
    
    # MUL x18, x5, x6
    insn = 0b0000001_00110_00101_000_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # Result is 0x100000000, lower 32 bits = 0
    assert cpu.regs[18] == 0, f"Expected x18=0 (overflow), got 0x{cpu.regs[18]:08X}"
    print("✓ test_mul_overflow passed")

def test_mul_large_numbers():
    """Test MUL with large numbers: 0xFFFF × 0x10001"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFF
    cpu.regs[6] = 0x10001
    
    # MUL x19, x5, x6
    insn = 0b0000001_00110_00101_000_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 65535 × 65537 = (65536-1) × (65536+1) = 65536² - 1 = 4294967295 = 0xFFFFFFFF
    expected = 0xFFFFFFFF
    assert cpu.regs[19] == expected, f"Expected x19=0x{expected:08X}, got 0x{cpu.regs[19]:08X}"
    print("✓ test_mul_large_numbers passed")

def test_mul_powers_of_two():
    """Test MUL with powers of two: 8 × 16 = 128"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 8
    cpu.regs[6] = 16
    
    # MUL x20, x5, x6
    insn = 0b0000001_00110_00101_000_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[20] == 128, f"Expected x20=128, got {cpu.regs[20]}"
    print("✓ test_mul_powers_of_two passed")

def test_mul_rd_x0():
    """Test MUL writing to x0 (should remain 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 200
    
    # MUL x0, x5, x6 (result discarded)
    insn = 0b0000001_00110_00101_000_00000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[0] == 0, f"Expected x0=0, got {cpu.regs[0]}"
    print("✓ test_mul_rd_x0 passed")

def test_mul_same_register():
    """Test MUL with same source registers: x5 × x5"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 7
    
    # MUL x21, x5, x5 (7 × 7 = 49)
    insn = 0b0000001_00101_00101_000_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[21] == 49, f"Expected x21=49, got {cpu.regs[21]}"
    print("✓ test_mul_same_register passed")

def main():
    """Run all MUL instruction tests."""
    # Run all tests
    test_mul_positive_positive()
    test_mul_positive_negative()
    test_mul_zero()
    test_mul_one()
    test_mul_negative_positive()
    test_mul_negative_negative()
    test_mul_max_positive()
    test_mul_max_negative()
    test_mul_overflow()
    test_mul_large_numbers()
    test_mul_powers_of_two()
    test_mul_rd_x0()
    test_mul_same_register()
    
    print("\n✓ All MUL tests passed (13/13)")

if __name__ == '__main__':
    main()

