#!/usr/bin/env python3
"""
Test SLL (Shift Left Logical) instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_sll_shift_by_zero(runner):
    """SLL: value << 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0
    
    # SLL x3, x1, x2 (funct3=001, funct7=0000000)
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("SLL shift by zero", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_sll_shift_by_one(runner):
    """SLL: 1 << 1 = 2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 1
    cpu.regs[2] = 1
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 2:
        runner.test_fail("SLL shift by one", "2", f"{cpu.regs[3]}")


def test_sll_shift_by_31(runner):
    """SLL: 1 << 31 = 0x80000000 (max shift)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 1
    cpu.regs[2] = 31
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x80000000:
        runner.test_fail("SLL shift by 31", "0x80000000", f"0x{cpu.regs[3]:08X}")


def test_sll_shift_amount_masked(runner):
    """SLL: shift amount uses only lower 5 bits (32 becomes 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 32  # 32 & 0x1F = 0
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("SLL shift amount masked", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_sll_shift_amount_masked_33(runner):
    """SLL: shift amount 33 & 0x1F = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 5
    cpu.regs[2] = 33  # 33 & 0x1F = 1
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 10:
        runner.test_fail("SLL shift amount 33", "10", f"{cpu.regs[3]}")


def test_sll_shift_out_bits(runner):
    """SLL: 0xFFFFFFFF << 4 = 0xFFFFFFF0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 4
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFF0:
        runner.test_fail("SLL shift out bits", "0xFFFFFFF0", f"0x{cpu.regs[3]:08X}")


def test_sll_shift_out_all_bits(runner):
    """SLL: 0xFFFFFFFF << 31 = 0x80000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 31
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x80000000:
        runner.test_fail("SLL shift out all bits", "0x80000000", f"0x{cpu.regs[3]:08X}")


def test_sll_zero_shifted(runner):
    """SLL: 0 << any = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 15
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SLL zero shifted", "0", f"{cpu.regs[3]}")


def test_sll_power_of_two(runner):
    """SLL: 1 << 10 = 1024"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 1
    cpu.regs[2] = 10
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1024:
        runner.test_fail("SLL power of two", "1024", f"{cpu.regs[3]}")


def test_sll_bit_pattern(runner):
    """SLL: 0xAAAAAAAA << 1 = 0x55555554"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xAAAAAAAA
    cpu.regs[2] = 1
    insn = 0b0000000_00010_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x55555554:
        runner.test_fail("SLL bit pattern", "0x55555554", f"0x{cpu.regs[3]:08X}")


def test_sll_rd_equals_x0(runner):
    """SLL: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 42
    cpu.regs[2] = 5
    insn = 0b0000000_00010_00001_001_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("SLL to x0", "0", f"{cpu.regs[0]}")


def test_sll_same_register(runner):
    """SLL: x1 << x1 (shift value by itself)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 5  # Shift 5 by 5 positions
    insn = 0b0000000_00001_00001_001_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 160:
        runner.test_fail("SLL same register", "160", f"{cpu.regs[3]}")


def test_sll_rd_equals_rs1(runner):
    """SLL: x1 = x1 << x2 (shift in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 8
    cpu.regs[2] = 3
    insn = 0b0000000_00010_00001_001_00001_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[1] != 64:
        runner.test_fail("SLL rd=rs1", "64", f"{cpu.regs[1]}")
