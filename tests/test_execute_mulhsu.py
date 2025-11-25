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


def test_mulhsu_small_positive(runner):
    """Test MULHSU: 2 × 3, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 2
    cpu.regs[6] = 3
    
    # MULHSU x10, x5, x6
    insn = 0b0000001_00110_00101_010_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[10] != 0:
        runner.test_fail("MULHSU small positive result", "0", f"{cpu.regs[10]}")
    if cpu.pc != 4:
        runner.test_fail("MULHSU PC increment", "4", f"{cpu.pc}")


def test_mulhsu_medium_values(runner):
    """Test MULHSU: 100 × 200, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 200
    
    # MULHSU x11, x5, x6
    insn = 0b0000001_00110_00101_010_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[11] != 0:
        runner.test_fail("MULHSU medium values", "0", f"{cpu.regs[11]}")


def test_mulhsu_negative_max_unsigned(runner):
    """Test MULHSU: -1 × 0xFFFFFFFF, upper bits = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHSU x12, x5, x6
    insn = 0b0000001_00110_00101_010_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[12] != expected:
        runner.test_fail("MULHSU -1×max unsigned", f"0x{expected:08X}", f"0x{cpu.regs[12]:08X}")


def test_mulhsu_max_positive_max_unsigned(runner):
    """Test MULHSU: 0x7FFFFFFF × 0xFFFFFFFF, upper = 0x7FFFFFFE"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHSU x13, x5, x6
    insn = 0b0000001_00110_00101_010_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x7FFFFFFE
    if cpu.regs[13] != expected:
        runner.test_fail("MULHSU max positive×max unsigned", f"0x{expected:08X}", f"0x{cpu.regs[13]:08X}")


def test_mulhsu_min_negative_max_unsigned(runner):
    """Test MULHSU: 0x80000000 × 0xFFFFFFFF, upper = 0x80000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHSU x14, x5, x6
    insn = 0b0000001_00110_00101_010_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x80000000
    if cpu.regs[14] != expected:
        runner.test_fail("MULHSU min negative×max unsigned", f"0x{expected:08X}", f"0x{cpu.regs[14]:08X}")


def test_mulhsu_positive_large_unsigned(runner):
    """Test MULHSU: 0x40000000 × 0x80000000, upper = 0x20000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x40000000
    cpu.regs[6] = 0x80000000
    
    # MULHSU x15, x5, x6
    insn = 0b0000001_00110_00101_010_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x20000000
    if cpu.regs[15] != expected:
        runner.test_fail("MULHSU positive×large unsigned", f"0x{expected:08X}", f"0x{cpu.regs[15]:08X}")


def test_mulhsu_negative_two(runner):
    """Test MULHSU: -2 × 0x7FFFFFFF, upper = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-2 & 0xFFFFFFFF)
    cpu.regs[6] = 0x7FFFFFFF
    
    # MULHSU x16, x5, x6
    insn = 0b0000001_00110_00101_010_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[16] != expected:
        runner.test_fail("MULHSU -2×large unsigned", f"0x{expected:08X}", f"0x{cpu.regs[16]:08X}")


def test_mulhsu_one_max_unsigned(runner):
    """Test MULHSU: 1 × 0xFFFFFFFF, upper = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHSU x17, x5, x6
    insn = 0b0000001_00110_00101_010_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[17] != 0:
        runner.test_fail("MULHSU 1×max unsigned", "0", f"{cpu.regs[17]}")


def test_mulhsu_negative_0x10000(runner):
    """Test MULHSU: -0x10000 × 0x10000, upper = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFF0000
    cpu.regs[6] = 0x10000
    
    # MULHSU x18, x5, x6
    insn = 0b0000001_00110_00101_010_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[18] != expected:
        runner.test_fail("MULHSU -0x10000×0x10000", f"0x{expected:08X}", f"0x{cpu.regs[18]:08X}")


def test_mulhsu_zero(runner):
    """Test MULHSU: 0 × 5, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # MULHSU x19, x5, x6
    insn = 0b0000001_00110_00101_010_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[19] != 0:
        runner.test_fail("MULHSU zero", "0", f"{cpu.regs[19]}")


def test_mulhsu_rd_x0(runner):
    """Test MULHSU writing to x0 (should remain 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULHSU x0, x5, x6
    insn = 0b0000001_00110_00101_010_00000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("MULHSU to x0", "0", f"{cpu.regs[0]}")


def test_mulhsu_same_register(runner):
    """Test MULHSU with same source registers: -100 × -100 (as unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-100 & 0xFFFFFFFF)
    
    # MULHSU x20, x5, x5
    insn = 0b0000001_00101_00101_010_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFF9C
    if cpu.regs[20] != expected:
        runner.test_fail("MULHSU same register", f"0x{expected:08X}", f"0x{cpu.regs[20]:08X}")


def test_mulhsu_negative_one_one(runner):
    """Test MULHSU: -1 × 1, upper = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 1
    
    # MULHSU x21, x5, x6
    insn = 0b0000001_00110_00101_010_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[21] != expected:
        runner.test_fail("MULHSU -1×1", f"0x{expected:08X}", f"0x{cpu.regs[21]:08X}")
