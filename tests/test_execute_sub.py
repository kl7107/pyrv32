#!/usr/bin/env python3
"""
Test SUB instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_sub_zero_minus_zero(runner):
    """SUB: 0 - 0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    # SUB x3, x0, x0 (funct7=0100000 for SUB)
    insn = 0b0100000_00000_00000_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SUB zero-zero", "0", f"{cpu.regs[3]}")


def test_sub_any_minus_zero(runner):
    """SUB: 100 - 0 = 100"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    insn = 0b0100000_00000_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 100:
        runner.test_fail("SUB any-zero", "100", f"{cpu.regs[3]}")


def test_sub_zero_minus_any(runner):
    """SUB: 0 - 50 = -50 (negation)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[2] = 50
    insn = 0b0100000_00010_00000_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFCE  # -50
    if cpu.regs[3] != expected:
        runner.test_fail("SUB zero-any", f"0x{expected:08X}", f"0x{cpu.regs[3]:08X}")


def test_sub_positive_minus_positive(runner):
    """SUB: 300 - 100 = 200"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 300
    cpu.regs[2] = 100
    insn = 0b0100000_00010_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 200:
        runner.test_fail("SUB positive-positive", "200", f"{cpu.regs[3]}")


def test_sub_underflow_wraps(runner):
    """SUB: 0x80000000 - 1 = 0x7FFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x80000000
    cpu.regs[2] = 1
    insn = 0b0100000_00010_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x7FFFFFFF:
        runner.test_fail("SUB underflow", "0x7FFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_sub_max_minus_min(runner):
    """SUB: 0x7FFFFFFF - 0x80000000 = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x7FFFFFFF
    cpu.regs[2] = 0x80000000
    insn = 0b0100000_00010_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("SUB max-min", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_sub_negative_minus_negative(runner):
    """SUB: -20 - (-10) = -10"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFEC  # -20
    cpu.regs[2] = 0xFFFFFFF6  # -10
    insn = 0b0100000_00010_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFF6  # -10
    if cpu.regs[3] != expected:
        runner.test_fail("SUB negative-negative", f"0x{expected:08X}", f"0x{cpu.regs[3]:08X}")


def test_sub_positive_minus_negative(runner):
    """SUB: 100 - (-50) = 150"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 0xFFFFFFCE  # -50
    insn = 0b0100000_00010_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 150:
        runner.test_fail("SUB positive-negative", "150", f"{cpu.regs[3]}")


def test_sub_negative_minus_positive(runner):
    """SUB: -100 - 50 = -150"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFF9C  # -100
    cpu.regs[2] = 50
    insn = 0b0100000_00010_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFF6A  # -150
    if cpu.regs[3] != expected:
        runner.test_fail("SUB negative-positive", f"0x{expected:08X}", f"0x{cpu.regs[3]:08X}")


def test_sub_same_register(runner):
    """SUB: x1 - x1 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 12345
    insn = 0b0100000_00001_00001_000_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SUB same register", "0", f"{cpu.regs[3]}")


def test_sub_rd_equals_x0(runner):
    """SUB: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 200
    cpu.regs[2] = 100
    insn = 0b0100000_00010_00001_000_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("SUB to x0", "0", f"{cpu.regs[0]}")


def test_sub_rd_equals_rs1(runner):
    """SUB: x1 = x1 - x2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 100
    cpu.regs[2] = 25
    insn = 0b0100000_00010_00001_000_00001_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[1] != 75:
        runner.test_fail("SUB rd=rs1", "75", f"{cpu.regs[1]}")


def test_sub_rd_equals_rs2(runner):
    """SUB: x2 = x1 - x2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 150
    cpu.regs[2] = 50
    insn = 0b0100000_00010_00001_000_00010_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[2] != 100:
        runner.test_fail("SUB rd=rs2", "100", f"{cpu.regs[2]}")
