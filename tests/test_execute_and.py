#!/usr/bin/env python3
"""
Test AND instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_and_same_values(runner):
    """AND: x & x = x (idempotent)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0x12345678
    
    # AND x3, x1, x2 (funct3=111, funct7=0000000)
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("AND same values", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_and_with_zero(runner):
    """AND: value & 0 = 0 (annihilator)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xABCDEF01
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("AND with zero", "0", f"0x{cpu.regs[3]:08X}")


def test_and_with_all_ones(runner):
    """AND: value & 0xFFFFFFFF = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0xFFFFFFFF
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("AND with all ones", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_and_bit_patterns(runner):
    """AND: 0xAAAAAAAA & 0x55555555 = 0 (complementary bits)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xAAAAAAAA
    cpu.regs[2] = 0x55555555
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("AND bit patterns", "0", f"0x{cpu.regs[3]:08X}")


def test_and_partial_overlap(runner):
    """AND: 0xFFFF0000 & 0x0000FFFF = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFF0000
    cpu.regs[2] = 0x0000FFFF
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("AND partial overlap", "0", f"0x{cpu.regs[3]:08X}")


def test_and_bit_masking(runner):
    """AND: 0x12345678 & 0x0000FFFF = 0x00005678 (mask lower 16 bits)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0x0000FFFF
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x00005678:
        runner.test_fail("AND bit masking", "0x00005678", f"0x{cpu.regs[3]:08X}")


def test_and_commutative(runner):
    """AND: a & b = b & a (commutative property)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0xABCDEF01
    
    # First: x3 = x1 & x2
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    result1 = cpu.regs[3]
    
    # Second: x4 = x2 & x1
    insn2 = 0b0000000_00001_00010_111_00100_0110011
    execute_instruction(cpu, mem, insn2)
    result2 = cpu.regs[4]
    
    if result1 != result2:
        runner.test_fail("AND commutative", f"0x{result1:08X}", f"0x{result2:08X}")


def test_and_zero_values(runner):
    """AND: 0 & 0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("AND zero & zero", "0", f"{cpu.regs[3]}")


def test_and_rd_equals_x0(runner):
    """AND: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 0x12345678
    insn = 0b0000000_00010_00001_111_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("AND to x0", "0", f"{cpu.regs[0]}")


def test_and_same_register(runner):
    """AND: x1 & x1 = x1 (idempotent)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    insn = 0b0000000_00001_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("AND same register", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_and_with_x0(runner):
    """AND: value & x0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x87654321
    insn = 0b0000000_00000_00001_111_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("AND with x0", "0", f"0x{cpu.regs[3]:08X}")


def test_and_rd_equals_rs1(runner):
    """AND: x1 = x1 & x2 (AND in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 0x00FF00FF
    insn = 0b0000000_00010_00001_111_00001_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[1] != 0x00FF00FF:
        runner.test_fail("AND rd=rs1", "0x00FF00FF", f"0x{cpu.regs[1]:08X}")
