#!/usr/bin/env python3
"""
Unit tests for MULHSU instruction (M extension).

MULHSU performs signed × unsigned multiplication and returns the upper 32 bits.
Format: MULHSU rd, rs1, rs2
Encoding: opcode=0110011, funct3=010, funct7=0000001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction

def test_mulhsu_small_positive():
    """Test MULHSU: 2 × 3, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 2
    cpu.regs[6] = 3
    
    # MULHSU x10, x5, x6
    # opcode=0110011, rd=01010, funct3=010, rs1=00101, rs2=00110, funct7=0000001
    insn = 0b0000001_00110_00101_010_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[10] == 0, f"Expected x10=0, got {cpu.regs[10]}"
    assert cpu.pc == 4, f"Expected PC=4, got {cpu.pc}"
    print("✓ test_mulhsu_small_positive passed")

def test_mulhsu_medium_values():
    """Test MULHSU: 100 × 200, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 200
    
    # MULHSU x11, x5, x6
    insn = 0b0000001_00110_00101_010_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[11] == 0, f"Expected x11=0, got {cpu.regs[11]}"
    print("✓ test_mulhsu_medium_values passed")

def test_mulhsu_negative_max_unsigned():
    """Test MULHSU: -1 × 0xFFFFFFFF, upper bits = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF  # -1 as signed
    cpu.regs[6] = 0xFFFFFFFF  # Max unsigned
    
    # MULHSU x12, x5, x6
    insn = 0b0000001_00110_00101_010_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -1 × 0xFFFFFFFF = -0xFFFFFFFF = 0xFFFFFFFF00000001
    # Upper 32 bits = 0xFFFFFFFF
    expected = 0xFFFFFFFF
    assert cpu.regs[12] == expected, f"Expected x12=0x{expected:08X}, got 0x{cpu.regs[12]:08X}"
    print("✓ test_mulhsu_negative_max_unsigned passed")

def test_mulhsu_max_positive_max_unsigned():
    """Test MULHSU: 0x7FFFFFFF × 0xFFFFFFFF, upper = 0x7FFFFFFE"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF  # Max positive signed
    cpu.regs[6] = 0xFFFFFFFF  # Max unsigned
    
    # MULHSU x13, x5, x6
    insn = 0b0000001_00110_00101_010_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x7FFFFFFF × 0xFFFFFFFF = 0x7FFFFFFE80000001
    # Upper 32 bits = 0x7FFFFFFE
    expected = 0x7FFFFFFE
    assert cpu.regs[13] == expected, f"Expected x13=0x{expected:08X}, got 0x{cpu.regs[13]:08X}"
    print("✓ test_mulhsu_max_positive_max_unsigned passed")

def test_mulhsu_min_negative_max_unsigned():
    """Test MULHSU: 0x80000000 × 0xFFFFFFFF, upper = 0x80000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000  # Min negative signed
    cpu.regs[6] = 0xFFFFFFFF  # Max unsigned
    
    # MULHSU x14, x5, x6
    insn = 0b0000001_00110_00101_010_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -0x80000000 × 0xFFFFFFFF = 0x8000000080000000
    # Upper 32 bits = 0x80000000
    expected = 0x80000000
    assert cpu.regs[14] == expected, f"Expected x14=0x{expected:08X}, got 0x{cpu.regs[14]:08X}"
    print("✓ test_mulhsu_min_negative_max_unsigned passed")

def test_mulhsu_positive_large_unsigned():
    """Test MULHSU: 0x40000000 × 0x80000000, upper = 0x20000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x40000000
    cpu.regs[6] = 0x80000000
    
    # MULHSU x15, x5, x6
    insn = 0b0000001_00110_00101_010_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x40000000 × 0x80000000 = 0x2000000000000000
    # Upper 32 bits = 0x20000000
    expected = 0x20000000
    assert cpu.regs[15] == expected, f"Expected x15=0x{expected:08X}, got 0x{cpu.regs[15]:08X}"
    print("✓ test_mulhsu_positive_large_unsigned passed")

def test_mulhsu_negative_two():
    """Test MULHSU: -2 × 0x7FFFFFFF, upper = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-2 & 0xFFFFFFFF)  # -2 as signed
    cpu.regs[6] = 0x7FFFFFFF  # Large unsigned
    
    # MULHSU x16, x5, x6
    insn = 0b0000001_00110_00101_010_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -2 × 0x7FFFFFFF = -0xFFFFFFFE = 0xFFFFFFFF00000002
    # Upper 32 bits = 0xFFFFFFFF
    expected = 0xFFFFFFFF
    assert cpu.regs[16] == expected, f"Expected x16=0x{expected:08X}, got 0x{cpu.regs[16]:08X}"
    print("✓ test_mulhsu_negative_two passed")

def test_mulhsu_one_max_unsigned():
    """Test MULHSU: 1 × 0xFFFFFFFF, upper = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHSU x17, x5, x6
    insn = 0b0000001_00110_00101_010_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 1 × 0xFFFFFFFF = 0xFFFFFFFF
    # Upper 32 bits = 0
    assert cpu.regs[17] == 0, f"Expected x17=0, got {cpu.regs[17]}"
    print("✓ test_mulhsu_one_max_unsigned passed")

def test_mulhsu_negative_0x10000():
    """Test MULHSU: -0x10000 × 0x10000, upper = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFF0000  # -0x10000 as signed
    cpu.regs[6] = 0x10000
    
    # MULHSU x18, x5, x6
    insn = 0b0000001_00110_00101_010_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -0x10000 × 0x10000 = -0x100000000
    # Upper 32 bits = 0xFFFFFFFF
    expected = 0xFFFFFFFF
    assert cpu.regs[18] == expected, f"Expected x18=0x{expected:08X}, got 0x{cpu.regs[18]:08X}"
    print("✓ test_mulhsu_negative_0x10000 passed")

def test_mulhsu_zero():
    """Test MULHSU: 0 × 5, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # MULHSU x19, x5, x6
    insn = 0b0000001_00110_00101_010_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[19] == 0, f"Expected x19=0, got {cpu.regs[19]}"
    print("✓ test_mulhsu_zero passed")

def test_mulhsu_rd_x0():
    """Test MULHSU writing to x0 (should remain 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHSU x0, x5, x6 (result discarded)
    insn = 0b0000001_00110_00101_010_00000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    assert cpu.regs[0] == 0, f"Expected x0=0, got {cpu.regs[0]}"
    print("✓ test_mulhsu_rd_x0 passed")

def test_mulhsu_same_register():
    """Test MULHSU with same source registers: -100 × -100 (as unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-100 & 0xFFFFFFFF)
    
    # MULHSU x20, x5, x5
    # -100 (signed) × 0xFFFFFF9C (unsigned)
    insn = 0b0000001_00101_00101_010_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -100 × 4294967196 = -429496719600 = 0xFFFFFF9C00002710
    # Upper 32 bits = 0xFFFFFF9C
    expected = 0xFFFFFF9C
    assert cpu.regs[20] == expected, f"Expected x20=0x{expected:08X}, got 0x{cpu.regs[20]:08X}"
    print("✓ test_mulhsu_same_register passed")

def test_mulhsu_negative_one_one():
    """Test MULHSU: -1 × 1, upper = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF  # -1
    cpu.regs[6] = 1
    
    # MULHSU x21, x5, x6
    insn = 0b0000001_00110_00101_010_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # -1 × 1 = -1 = 0xFFFFFFFFFFFFFFFF
    # Upper 32 bits = 0xFFFFFFFF
    expected = 0xFFFFFFFF
    assert cpu.regs[21] == expected, f"Expected x21=0x{expected:08X}, got 0x{cpu.regs[21]:08X}"
    print("✓ test_mulhsu_negative_one_one passed")

def main():
    """Run all MULHSU instruction tests."""
    test_mulhsu_small_positive()
    test_mulhsu_medium_values()
    test_mulhsu_negative_max_unsigned()
    test_mulhsu_max_positive_max_unsigned()
    test_mulhsu_min_negative_max_unsigned()
    test_mulhsu_positive_large_unsigned()
    test_mulhsu_negative_two()
    test_mulhsu_one_max_unsigned()
    test_mulhsu_negative_0x10000()
    test_mulhsu_zero()
    test_mulhsu_rd_x0()
    test_mulhsu_same_register()
    test_mulhsu_negative_one_one()
    
    print("\n✓ All MULHSU tests passed (13/13)")

if __name__ == '__main__':
    main()
