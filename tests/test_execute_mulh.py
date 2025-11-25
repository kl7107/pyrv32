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


def test_mulh_small_positive(runner):
    """Test MULH with small positive numbers: 2 × 3, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 2
    cpu.regs[6] = 3
    
    # MULH x10, x5, x6
    insn = 0b0000001_00110_00101_001_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[10] != 0:
        runner.test_fail("MULH small positive result", "0", f"{cpu.regs[10]}")
    if cpu.pc != 4:
        runner.test_fail("MULH PC increment", "4", f"{cpu.pc}")


def test_mulh_large_positive_negative(runner):
    """Test MULH: 0x7FFFFFFF × -2, upper bits = -1 (0xFFFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = (-2 & 0xFFFFFFFF)
    
    # MULH x11, x5, x6
    insn = 0b0000001_00110_00101_001_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[11] != expected:
        runner.test_fail("MULH positive×negative", f"0x{expected:08X}", f"0x{cpu.regs[11]:08X}")


def test_mulh_medium_values(runner):
    """Test MULH: 100 × 200 = 20000, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 200
    
    # MULH x12, x5, x6
    insn = 0b0000001_00110_00101_001_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[12] != 0:
        runner.test_fail("MULH medium values", "0", f"{cpu.regs[12]}")


def test_mulh_max_positive_squared(runner):
    """Test MULH: 0x7FFFFFFF × 0x7FFFFFFF, upper bits = 0x3FFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 0x7FFFFFFF
    
    # MULH x13, x5, x6
    insn = 0b0000001_00110_00101_001_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x3FFFFFFF
    if cpu.regs[13] != expected:
        runner.test_fail("MULH max positive squared", f"0x{expected:08X}", f"0x{cpu.regs[13]:08X}")


def test_mulh_max_negative_squared(runner):
    """Test MULH: 0x80000000 × 0x80000000, upper bits = 0x40000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000
    cpu.regs[6] = 0x80000000
    
    # MULH x14, x5, x6
    insn = 0b0000001_00110_00101_001_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x40000000
    if cpu.regs[14] != expected:
        runner.test_fail("MULH max negative squared", f"0x{expected:08X}", f"0x{cpu.regs[14]:08X}")


def test_mulh_negative_negative(runner):
    """Test MULH: -1 × -1, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 0xFFFFFFFF
    
    # MULH x15, x5, x6
    insn = 0b0000001_00110_00101_001_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[15] != 0:
        runner.test_fail("MULH negative×negative", "0", f"{cpu.regs[15]}")


def test_mulh_positive_negative_medium(runner):
    """Test MULH: 0x10000 × -0x10000, upper bits = -1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x10000
    cpu.regs[6] = 0xFFFF0000
    
    # MULH x16, x5, x6
    insn = 0b0000001_00110_00101_001_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[16] != expected:
        runner.test_fail("MULH positive×negative medium", f"0x{expected:08X}", f"0x{cpu.regs[16]:08X}")


def test_mulh_large_positive_squared(runner):
    """Test MULH: 0x40000000 × 0x40000000, upper bits = 0x10000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x40000000
    cpu.regs[6] = 0x40000000
    
    # MULH x17, x5, x6
    insn = 0b0000001_00110_00101_001_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x10000000
    if cpu.regs[17] != expected:
        runner.test_fail("MULH large positive squared", f"0x{expected:08X}", f"0x{cpu.regs[17]:08X}")


def test_mulh_negative_one_times_max_positive(runner):
    """Test MULH: -1 × 0x7FFFFFFF, upper bits = -1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 0x7FFFFFFF
    
    # MULH x18, x5, x6
    insn = 0b0000001_00110_00101_001_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[18] != expected:
        runner.test_fail("MULH -1×max positive", f"0x{expected:08X}", f"0x{cpu.regs[18]:08X}")


def test_mulh_zero(runner):
    """Test MULH: 0 × 5, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # MULH x19, x5, x6
    insn = 0b0000001_00110_00101_001_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[19] != 0:
        runner.test_fail("MULH zero", "0", f"{cpu.regs[19]}")


def test_mulh_rd_x0(runner):
    """Test MULH writing to x0 (should remain 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 0x7FFFFFFF
    
    # MULH x0, x5, x6
    insn = 0b0000001_00110_00101_001_00000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("MULH to x0", "0", f"{cpu.regs[0]}")


def test_mulh_same_register(runner):
    """Test MULH with same source registers: 0x8000 × 0x8000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x8000
    
    # MULH x20, x5, x5
    insn = 0b0000001_00101_00101_001_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[20] != 0:
        runner.test_fail("MULH same register", "0", f"{cpu.regs[20]}")


def test_mulh_one(runner):
    """Test MULH: 1 × 1, upper bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1
    cpu.regs[6] = 1
    
    # MULH x21, x5, x6
    insn = 0b0000001_00110_00101_001_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[21] != 0:
        runner.test_fail("MULH one", "0", f"{cpu.regs[21]}")
