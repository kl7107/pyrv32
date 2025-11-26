#!/usr/bin/env python3
"""
Test OR instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_or_same_values(runner):
    """OR: x | x = x (idempotent)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0x12345678
    
    # OR x3, x1, x2 (funct3=110, funct7=0000000)
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("OR same values", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_or_with_zero(runner):
    """OR: value | 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xABCDEF01
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xABCDEF01:
        runner.test_fail("OR with zero", "0xABCDEF01", f"0x{cpu.regs[3]:08X}")


def test_or_with_all_ones(runner):
    """OR: value | 0xFFFFFFFF = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0xFFFFFFFF
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("OR with all ones", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_or_bit_patterns(runner):
    """OR: 0xAAAAAAAA | 0x55555555 = 0xFFFFFFFF (complementary bits)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xAAAAAAAA
    cpu.regs[2] = 0x55555555
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("OR bit patterns", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_or_partial_overlap(runner):
    """OR: 0xFFFF0000 | 0x0000FFFF = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFF0000
    cpu.regs[2] = 0x0000FFFF
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("OR partial overlap", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_or_specific_bits(runner):
    """OR: 0x12340000 | 0x00005678 = 0x12345678"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12340000
    cpu.regs[2] = 0x00005678
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("OR specific bits", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_or_commutative(runner):
    """OR: a | b = b | a (commutative property)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0xABCDEF01
    
    # First: x3 = x1 | x2
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    result1 = cpu.regs[3]
    
    # Second: x4 = x2 | x1
    insn2 = 0b0000000_00001_00010_110_00100_0110011
    execute_instruction(cpu, mem, insn2)
    result2 = cpu.regs[4]
    
    if result1 != result2:
        runner.test_fail("OR commutative", f"0x{result1:08X}", f"0x{result2:08X}")


def test_or_zero_values(runner):
    """OR: 0 | 0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("OR zero | zero", "0", f"{cpu.regs[3]}")


def test_or_rd_equals_x0(runner):
    """OR: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 0x12345678
    insn = 0b0000000_00010_00001_110_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("OR to x0", "0", f"{cpu.regs[0]}")


def test_or_same_register(runner):
    """OR: x1 | x1 = x1 (idempotent)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    insn = 0b0000000_00001_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("OR same register", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_or_with_x0(runner):
    """OR: value | x0 = value"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x87654321
    insn = 0b0000000_00000_00001_110_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x87654321:
        runner.test_fail("OR with x0", "0x87654321", f"0x{cpu.regs[3]:08X}")


def test_or_rd_equals_rs1(runner):
    """OR: x1 = x1 | x2 (OR in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFF00FF00
    cpu.regs[2] = 0x00FF00FF
    insn = 0b0000000_00010_00001_110_00001_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[1] != 0xFFFFFFFF:
        runner.test_fail("OR rd=rs1", "0xFFFFFFFF", f"0x{cpu.regs[1]:08X}")
