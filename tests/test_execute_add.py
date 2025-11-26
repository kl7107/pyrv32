#!/usr/bin/env python3
"""
Test ADD instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_add_zero_plus_zero(runner):
    """ADD: 0 + 0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    # ADD x3, x0, x0
    # opcode=0110011, rd=00011, funct3=000, rs1=00000, rs2=00000, funct7=0000000
    insn = 0b0000000_00000_00000_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("ADD zero+zero", "0", f"{cpu.regs[3]}")


def test_add_zero_plus_any(runner):
    """ADD: 0 + 42 = 42 (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 42
    
    # ADD x3, x0, x1
    insn = 0b0000000_00001_00000_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 42:
        runner.test_fail("ADD zero+any", "42", f"{cpu.regs[3]}")


def test_add_any_plus_zero(runner):
    """ADD: 123 + 0 = 123 (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 123
    
    # ADD x3, x1, x0
    insn = 0b0000000_00000_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 123:
        runner.test_fail("ADD any+zero", "123", f"{cpu.regs[3]}")


def test_add_positive_plus_positive(runner):
    """ADD: 100 + 200 = 300 (no overflow)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 200
    
    # ADD x3, x1, x2
    insn = 0b0000000_00010_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 300:
        runner.test_fail("ADD positive+positive", "300", f"{cpu.regs[3]}")


def test_add_overflow_wraps(runner):
    """ADD: 0x7FFFFFFF + 1 = 0x80000000 (overflow wraps to negative)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x7FFFFFFF
    cpu.regs[2] = 1
    
    # ADD x3, x1, x2
    insn = 0b0000000_00010_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x80000000:
        runner.test_fail("ADD overflow", "0x80000000", f"0x{cpu.regs[3]:08X}")


def test_add_max_values(runner):
    """ADD: 0x7FFFFFFF + 0x7FFFFFFF = 0xFFFFFFFE (overflow)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x7FFFFFFF
    cpu.regs[2] = 0x7FFFFFFF
    
    # ADD x3, x1, x2
    insn = 0b0000000_00010_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFE:
        runner.test_fail("ADD max values", "0xFFFFFFFE", f"0x{cpu.regs[3]:08X}")


def test_add_negative_plus_negative(runner):
    """ADD: -10 + -20 = -30 (underflow wraps)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFF6  # -10
    cpu.regs[2] = 0xFFFFFFEC  # -20
    
    # ADD x3, x1, x2
    insn = 0b0000000_00010_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFE2  # -30
    if cpu.regs[3] != expected:
        runner.test_fail("ADD negative+negative", f"0x{expected:08X}", f"0x{cpu.regs[3]:08X}")


def test_add_positive_plus_negative(runner):
    """ADD: 100 + (-50) = 50"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 0xFFFFFFCE  # -50
    
    # ADD x3, x1, x2
    insn = 0b0000000_00010_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 50:
        runner.test_fail("ADD positive+negative", "50", f"{cpu.regs[3]}")


def test_add_negative_plus_positive(runner):
    """ADD: -100 + 150 = 50"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFF9C  # -100
    cpu.regs[2] = 150
    
    # ADD x3, x1, x2
    insn = 0b0000000_00010_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 50:
        runner.test_fail("ADD negative+positive", "50", f"{cpu.regs[3]}")


def test_add_all_ones_plus_one(runner):
    """ADD: 0xFFFFFFFF + 1 = 0 (wraparound)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 1
    
    # ADD x3, x1, x2
    insn = 0b0000000_00010_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("ADD wraparound", "0", f"{cpu.regs[3]}")


def test_add_rd_equals_x0(runner):
    """ADD: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 200
    
    # ADD x0, x1, x2
    insn = 0b0000000_00010_00001_000_00000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("ADD to x0", "0", f"{cpu.regs[0]}")


def test_add_same_register(runner):
    """ADD: x1 + x1 (double value)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 50
    
    # ADD x3, x1, x1
    insn = 0b0000000_00001_00001_000_00011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 100:
        runner.test_fail("ADD same register", "100", f"{cpu.regs[3]}")


def test_add_rd_equals_rs1(runner):
    """ADD: x1 = x1 + x2 (accumulate in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 50
    cpu.regs[2] = 25
    
    # ADD x1, x1, x2
    insn = 0b0000000_00010_00001_000_00001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[1] != 75:
        runner.test_fail("ADD rd=rs1", "75", f"{cpu.regs[1]}")


def test_add_rd_equals_rs2(runner):
    """ADD: x2 = x1 + x2 (accumulate in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 30
    cpu.regs[2] = 70
    
    # ADD x2, x1, x2
    insn = 0b0000000_00010_00001_000_00010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[2] != 100:
        runner.test_fail("ADD rd=rs2", "100", f"{cpu.regs[2]}")

