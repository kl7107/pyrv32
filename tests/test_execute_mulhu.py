#!/usr/bin/env python3
"""
Unit tests for MULHU instruction (M extension).

MULHU performs unsigned multiplication and returns the upper 32 bits of the 64-bit result.
Format: MULHU rd, rs1, rs2
Encoding: opcode=0110011, funct3=011, funct7=0000001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_mulhu_small_values(runner):
    """Test MULHU with small unsigned values: 2 × 3, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 2
    cpu.regs[6] = 3
    
    # MULHU x10, x5, x6
    insn = 0b0000001_00110_00101_011_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[10] != 0:
        runner.test_fail("MULHU small values", "0", f"{cpu.regs[10]}")


def test_mulhu_medium_values(runner):
    """Test MULHU with medium unsigned values: 100 × 200, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 200
    
    # MULHU x11, x5, x6
    insn = 0b0000001_00110_00101_011_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[11] != 0:
        runner.test_fail("MULHU medium values", "0", f"{cpu.regs[11]}")


def test_mulhu_max_unsigned_squared(runner):
    """Test MULHU: 0xFFFFFFFF × 0xFFFFFFFF, upper = 0xFFFFFFFE"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHU x12, x5, x6
    insn = 0b0000001_00110_00101_011_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFE
    if cpu.regs[12] != expected:
        runner.test_fail("MULHU max unsigned squared", f"0x{expected:08X}", f"0x{cpu.regs[12]:08X}")


def test_mulhu_large_times_2(runner):
    """Test MULHU: 0x80000000 × 2, upper bits = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000
    cpu.regs[6] = 2
    
    # MULHU x13, x5, x6
    insn = 0b0000001_00110_00101_011_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[13] != 1:
        runner.test_fail("MULHU 0x80000000×2", "1", f"{cpu.regs[13]}")


def test_mulhu_0x80000000_squared(runner):
    """Test MULHU: 0x80000000 × 0x80000000, upper = 0x40000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000
    cpu.regs[6] = 0x80000000
    
    # MULHU x14, x5, x6
    insn = 0b0000001_00110_00101_011_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x40000000
    if cpu.regs[14] != expected:
        runner.test_fail("MULHU 0x80000000 squared", f"0x{expected:08X}", f"0x{cpu.regs[14]:08X}")


def test_mulhu_0x40000000_squared(runner):
    """Test MULHU: 0x40000000 × 0x40000000, upper = 0x10000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x40000000
    cpu.regs[6] = 0x40000000
    
    # MULHU x15, x5, x6
    insn = 0b0000001_00110_00101_011_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x10000000
    if cpu.regs[15] != expected:
        runner.test_fail("MULHU 0x40000000 squared", f"0x{expected:08X}", f"0x{cpu.regs[15]:08X}")


def test_mulhu_max_unsigned_times_1(runner):
    """Test MULHU: 0xFFFFFFFF × 1, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 1
    
    # MULHU x16, x5, x6
    insn = 0b0000001_00110_00101_011_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[16] != 0:
        runner.test_fail("MULHU max unsigned×1", "0", f"{cpu.regs[16]}")


def test_mulhu_0x10000_squared(runner):
    """Test MULHU: 0x10000 × 0x10000, upper bits = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x10000
    cpu.regs[6] = 0x10000
    
    # MULHU x17, x5, x6
    insn = 0b0000001_00110_00101_011_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[17] != 1:
        runner.test_fail("MULHU 0x10000 squared", "1", f"{cpu.regs[17]}")


def test_mulhu_max_unsigned_times_0x80000000(runner):
    """Test MULHU: 0xFFFFFFFF × 0x80000000, upper = 0x7FFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 0x80000000
    
    # MULHU x18, x5, x6
    insn = 0b0000001_00110_00101_011_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x7FFFFFFF
    if cpu.regs[18] != expected:
        runner.test_fail("MULHU max unsigned×0x80000000", f"0x{expected:08X}", f"0x{cpu.regs[18]:08X}")


def test_mulhu_0xFFFF_squared(runner):
    """Test MULHU: 0xFFFF × 0xFFFF, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFF
    cpu.regs[6] = 0xFFFF
    
    # MULHU x19, x5, x6
    insn = 0b0000001_00110_00101_011_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[19] != 0:
        runner.test_fail("MULHU 0xFFFF squared", "0", f"{cpu.regs[19]}")


def test_mulhu_zero(runner):
    """Test MULHU with zero operands"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHU x20, x5, x6
    insn = 0b0000001_00110_00101_011_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[20] != 0:
        runner.test_fail("MULHU zero", "0", f"{cpu.regs[20]}")


def test_mulhu_commutative(runner):
    """Test MULHU commutative property"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x12345678
    cpu.regs[6] = 0x87654321
    
    # MULHU x21, x5, x6
    insn = 0b0000001_00110_00101_011_10101_0110011
    execute_instruction(cpu, mem, insn)
    result1 = cpu.regs[21]
    
    # MULHU x22, x6, x5
    insn = 0b0000001_00101_00110_011_10110_0110011
    execute_instruction(cpu, mem, insn)
    result2 = cpu.regs[22]
    
    if result1 != result2:
        runner.test_fail("MULHU commutative", f"0x{result1:08X}", f"0x{result2:08X}")


def test_mulhu_power_of_two(runner):
    """Test MULHU with powers of two: 0x1000000 × 0x100, upper = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x1000000
    cpu.regs[6] = 0x100
    
    # MULHU x23, x5, x6
    insn = 0b0000001_00110_00101_011_10111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[23] != 1:
        runner.test_fail("MULHU power of two", "1", f"{cpu.regs[23]}")
