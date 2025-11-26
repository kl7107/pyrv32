#!/usr/bin/env python3
"""
Test SLTU (Set Less Than Unsigned) instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_sltu_equal_values(runner):
    """SLTU: 100 < 100 = 0 (equal, not less than)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 100
    
    # SLTU x3, x1, x2 (funct3=011, funct7=0000000)
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU equal values", "0", f"{cpu.regs[3]}")


def test_sltu_less_than(runner):
    """SLTU: 50 < 100 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 50
    cpu.regs[2] = 100
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLTU less than", "1", f"{cpu.regs[3]}")


def test_sltu_greater_than(runner):
    """SLTU: 100 < 50 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 50
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU greater than", "0", f"{cpu.regs[3]}")


def test_sltu_zero_less_than_any(runner):
    """SLTU: 0 < 1 = 1 (unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 1
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLTU 0 < 1", "1", f"{cpu.regs[3]}")


def test_sltu_max_unsigned_not_less_than(runner):
    """SLTU: 0xFFFFFFFF < anything = 0 (max unsigned not < anything)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 100
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU max unsigned", "0", f"{cpu.regs[3]}")


def test_sltu_anything_less_than_max(runner):
    """SLTU: 100 < 0xFFFFFFFF = 1 (anything < max unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 0xFFFFFFFF
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLTU anything < max", "1", f"{cpu.regs[3]}")


def test_sltu_high_bit_comparison(runner):
    """SLTU: 0x80000000 < 0x7FFFFFFF = 0 (unsigned: 2^31 > 2^31-1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x80000000
    cpu.regs[2] = 0x7FFFFFFF
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU high bit comparison", "0", f"{cpu.regs[3]}")


def test_sltu_boundary_values(runner):
    """SLTU: 0x7FFFFFFF < 0x80000000 = 1 (unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x7FFFFFFF
    cpu.regs[2] = 0x80000000
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SLTU boundary values", "1", f"{cpu.regs[3]}")


def test_sltu_zero_values(runner):
    """SLTU: 0 < 0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU zero < zero", "0", f"{cpu.regs[3]}")


def test_sltu_rd_equals_x0(runner):
    """SLTU: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 50
    cpu.regs[2] = 100
    insn = 0b0000000_00010_00001_011_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("SLTU to x0", "0", f"{cpu.regs[0]}")


def test_sltu_same_register(runner):
    """SLTU: x1 < x1 = 0 (always equal)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 12345
    insn = 0b0000000_00001_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU same register", "0", f"{cpu.regs[3]}")


def test_sltu_compare_to_x0_positive(runner):
    """SLTU: positive < x0 = 0 (positive not < 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    insn = 0b0000000_00000_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU positive < x0", "0", f"{cpu.regs[3]}")


def test_sltu_compare_to_x0_negative(runner):
    """SLTU: 0xFFFFFFFF < x0 = 0 (max unsigned not < 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    insn = 0b0000000_00000_00001_011_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLTU 0xFFFFFFFF < x0", "0", f"{cpu.regs[3]}")
