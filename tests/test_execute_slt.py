#!/usr/bin/env python3
"""
Test SLT (Set Less Than) instruction - signed comparison
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_slt_equal_values(runner):
    """SLT: 100 < 100 = 0 (equal, not less than)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 100
    
    # SLT x3, x1, x2 (funct3=010, funct7=0000000)
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLT equal values", "0", f"{cpu.regs[3]}")


def test_slt_less_than(runner):
    """SLT: 50 < 100 = 1 (less than)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 50
    cpu.regs[2] = 100
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLT less than", "1", f"{cpu.regs[3]}")


def test_slt_greater_than(runner):
    """SLT: 100 < 50 = 0 (not less than)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 50
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLT greater than", "0", f"{cpu.regs[3]}")


def test_slt_negative_less_than_positive(runner):
    """SLT: -50 < 100 = 1 (signed: negative < positive)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFCE  # -50
    cpu.regs[2] = 100
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLT negative < positive", "1", f"{cpu.regs[3]}")


def test_slt_positive_not_less_than_negative(runner):
    """SLT: 100 < -50 = 0 (signed: positive not < negative)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 0xFFFFFFCE  # -50
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLT positive not < negative", "0", f"{cpu.regs[3]}")


def test_slt_max_negative_less_than_zero(runner):
    """SLT: 0x80000000 < 0 = 1 (min negative < 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x80000000  # -2147483648
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLT min negative < 0", "1", f"{cpu.regs[3]}")


def test_slt_zero_less_than_max_positive(runner):
    """SLT: 0 < 0x7FFFFFFF = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 0x7FFFFFFF
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLT 0 < max positive", "1", f"{cpu.regs[3]}")


def test_slt_negative_comparison(runner):
    """SLT: -100 < -50 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFF9C  # -100
    cpu.regs[2] = 0xFFFFFFCE  # -50
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLT negative comparison", "1", f"{cpu.regs[3]}")


def test_slt_max_values(runner):
    """SLT: 0x80000000 < 0x7FFFFFFF = 1 (min < max)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x80000000
    cpu.regs[2] = 0x7FFFFFFF
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLT min < max", "1", f"{cpu.regs[3]}")


def test_slt_zero_values(runner):
    """SLT: 0 < 0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLT zero < zero", "0", f"{cpu.regs[3]}")


def test_slt_rd_equals_x0(runner):
    """SLT: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 50
    cpu.regs[2] = 100
    insn = 0b0000000_00010_00001_010_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("SLT to x0", "0", f"{cpu.regs[0]}")


def test_slt_same_register(runner):
    """SLT: x1 < x1 = 0 (always equal)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 12345
    insn = 0b0000000_00001_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLT same register", "0", f"{cpu.regs[3]}")


def test_slt_compare_to_x0(runner):
    """SLT: x1 < x0 (compare to zero)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF  # -1
    insn = 0b0000000_00000_00001_010_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLT compare to x0", "1", f"{cpu.regs[3]}")
