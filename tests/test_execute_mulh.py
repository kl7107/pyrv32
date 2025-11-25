#!/usr/bin/env python3
"""
Unit tests for MULH instruction (M extension).

MULH performs signed multiplication and returns the upper 32 bits of the 64-bit result.
Format: MULH rd, rs1, rs2
Encoding: opcode=0110011, funct3=001, funct7=0000001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction

def test_mulh_small_positive():
    """Test MULH with small positive numbers: 2 × 3, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 2
    cpu.regs[6] = 3
    
    # MULH x10, x5, x6
    # opcode=0110011, rd=01010, funct3=001, rs1=00101, rs2=00110, funct7=0000001
    insn = 0b0000001_00110_00101_001_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[10] == 0, f"Expected x10=0, got {cpu.regs[10]}"
    assert cpu.pc == 4, f"Expected PC=4, got {cpu.pc}"
    print("✓ test_mulh_small_positive passed")

def test_mulh_large_positive_negative():
    """Test MULH: 0x7FFFFFFF × -2, upper bits = -1 (0xFFFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF  # Max positive
    cpu.regs[6] = (-2 & 0xFFFFFFFF)  # -2
    
    # MULH x11, x5, x6
    insn = 0b0000001_00110_00101_001_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x7FFFFFFF × -2 = -0xFFFFFFFE = 0xFFFFFFFF00000002 (in 64-bit)
    # Upper 32 bits = 0xFFFFFFFF (-1)
    expected = 0xFFFFFFFF
    assert cpu.regs[11] == expected, f"Expected x11=0x{expected:08X}, got 0x{cpu.regs[11]:08X}"
    print("✓ test_mulh_large_positive_negative passed")

def test_mulh_medium_values():
    """Test MULH: 100 × 200 = 20000, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 200
    
    # MULH x12, x5, x6
    insn = 0b0000001_00110_00101_001_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[12] == 0, f"Expected x12=0, got {cpu.regs[12]}"
    print("✓ test_mulh_medium_values passed")

def test_mulh_max_positive_squared():
    """Test MULH: 0x7FFFFFFF × 0x7FFFFFFF, upper bits = 0x3FFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 0x7FFFFFFF
    
    # MULH x13, x5, x6
    insn = 0b0000001_00110_00101_001_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x7FFFFFFF × 0x7FFFFFFF = 0x3FFFFFFF00000001
    # Upper 32 bits = 0x3FFFFFFF
    expected = 0x3FFFFFFF
    assert cpu.regs[13] == expected, f"Expected x13=0x{expected:08X}, got 0x{cpu.regs[13]:08X}"
    print("✓ test_mulh_max_positive_squared passed")

def test_mulh_max_negative_squared():
    """Test MULH: 0x80000000 × 0x80000000, upper bits = 0x40000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000  # Min negative
    cpu.regs[6] = 0x80000000
    
    # MULH x14, x5, x6
    insn = 0b0000001_00110_00101_001_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -0x80000000 × -0x80000000 = 0x4000000000000000
    # Upper 32 bits = 0x40000000
    expected = 0x40000000
    assert cpu.regs[14] == expected, f"Expected x14=0x{expected:08X}, got 0x{cpu.regs[14]:08X}"
    print("✓ test_mulh_max_negative_squared passed")

def test_mulh_negative_negative():
    """Test MULH: -1 × -1, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF  # -1
    cpu.regs[6] = 0xFFFFFFFF  # -1
    
    # MULH x15, x5, x6
    insn = 0b0000001_00110_00101_001_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -1 × -1 = 1, upper bits = 0
    assert cpu.regs[15] == 0, f"Expected x15=0, got {cpu.regs[15]}"
    print("✓ test_mulh_negative_negative passed")

def test_mulh_positive_negative_medium():
    """Test MULH: 0x10000 × -0x10000, upper bits = -1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x10000
    cpu.regs[6] = 0xFFFF0000  # -0x10000 in two's complement
    
    # MULH x16, x5, x6
    insn = 0b0000001_00110_00101_001_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x10000 × -0x10000 = -0x100000000
    # Upper 32 bits = 0xFFFFFFFF (-1)
    expected = 0xFFFFFFFF
    assert cpu.regs[16] == expected, f"Expected x16=0x{expected:08X}, got 0x{cpu.regs[16]:08X}"
    print("✓ test_mulh_positive_negative_medium passed")

def test_mulh_large_positive_squared():
    """Test MULH: 0x40000000 × 0x40000000, upper bits = 0x10000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x40000000
    cpu.regs[6] = 0x40000000
    
    # MULH x17, x5, x6
    insn = 0b0000001_00110_00101_001_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x40000000 × 0x40000000 = 0x1000000000000000
    # Upper 32 bits = 0x10000000
    expected = 0x10000000
    assert cpu.regs[17] == expected, f"Expected x17=0x{expected:08X}, got 0x{cpu.regs[17]:08X}"
    print("✓ test_mulh_large_positive_squared passed")

def test_mulh_negative_one_times_max_positive():
    """Test MULH: -1 × 0x7FFFFFFF, upper bits = -1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF  # -1
    cpu.regs[6] = 0x7FFFFFFF  # Max positive
    
    # MULH x18, x5, x6
    insn = 0b0000001_00110_00101_001_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -1 × 0x7FFFFFFF = -0x7FFFFFFF = 0xFFFFFFFF80000001
    # Upper 32 bits = 0xFFFFFFFF (-1)
    expected = 0xFFFFFFFF
    assert cpu.regs[18] == expected, f"Expected x18=0x{expected:08X}, got 0x{cpu.regs[18]:08X}"
    print("✓ test_mulh_negative_one_times_max_positive passed")

def test_mulh_zero():
    """Test MULH: 0 × 5, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # MULH x19, x5, x6
    insn = 0b0000001_00110_00101_001_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[19] == 0, f"Expected x19=0, got {cpu.regs[19]}"
    print("✓ test_mulh_zero passed")

def test_mulh_rd_x0():
    """Test MULH writing to x0 (should remain 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 0x7FFFFFFF
    
    # MULH x0, x5, x6 (result discarded)
    insn = 0b0000001_00110_00101_001_00000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[0] == 0, f"Expected x0=0, got {cpu.regs[0]}"
    print("✓ test_mulh_rd_x0 passed")

def test_mulh_same_register():
    """Test MULH with same source registers: 0x8000 × 0x8000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x8000
    
    # MULH x20, x5, x5
    # 0x8000 × 0x8000 = 0x40000000
    # Upper 32 bits = 0
    insn = 0b0000001_00101_00101_001_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[20] == 0, f"Expected x20=0, got {cpu.regs[20]}"
    print("✓ test_mulh_same_register passed")

def test_mulh_one():
    """Test MULH: 1 × 1, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1
    cpu.regs[6] = 1
    
    # MULH x21, x5, x6
    insn = 0b0000001_00110_00101_001_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[21] == 0, f"Expected x21=0, got {cpu.regs[21]}"
    print("✓ test_mulh_one passed")

def main():
    """Run all MULH instruction tests."""
    test_mulh_small_positive()
    test_mulh_large_positive_negative()
    test_mulh_medium_values()
    test_mulh_max_positive_squared()
    test_mulh_max_negative_squared()
    test_mulh_negative_negative()
    test_mulh_positive_negative_medium()
    test_mulh_large_positive_squared()
    test_mulh_negative_one_times_max_positive()
    test_mulh_zero()
    test_mulh_rd_x0()
    test_mulh_same_register()
    test_mulh_one()
    
    print("\n✓ All MULH tests passed (13/13)")

if __name__ == '__main__':
    main()
