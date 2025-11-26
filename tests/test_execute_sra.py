#!/usr/bin/env python3
"""
Test SRA (Shift Right Arithmetic) instruction  
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_sra_shift_by_zero(runner):
    """SRA: value >>s 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0
    
    # SRA x3, x1, x2 (funct3=101, funct7=0100000)
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("SRA shift by zero", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_sra_positive_shift_one(runner):
    """SRA: 8 >>s 1 = 4 (positive, fill with 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 8
    cpu.regs[2] = 1
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 4:
        runner.test_fail("SRA positive shift one", "4", f"{cpu.regs[3]}")


def test_sra_negative_shift_one(runner):
    """SRA: 0xFFFFFFFF >>s 1 = 0xFFFFFFFF (negative, fill with 1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF  # -1
    cpu.regs[2] = 1
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("SRA negative shift one", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_sra_negative_shift_31(runner):
    """SRA: 0xFFFFFFFF >>s 31 = 0xFFFFFFFF (all 1s remain)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 31
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("SRA negative shift 31", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_sra_negative_value_sign_extend(runner):
    """SRA: 0x80000000 >>s 1 = 0xC0000000 (sign extension)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x80000000  # MSB set
    cpu.regs[2] = 1
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xC0000000:
        runner.test_fail("SRA sign extend", "0xC0000000", f"0x{cpu.regs[3]:08X}")


def test_sra_negative_shift_31_msb_set(runner):
    """SRA: 0x80000000 >>s 31 = 0xFFFFFFFF (all 1s)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x80000000
    cpu.regs[2] = 31
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("SRA MSB shift 31", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_sra_positive_shift_31(runner):
    """SRA: 0x7FFFFFFF >>s 31 = 0 (positive, all 0s)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x7FFFFFFF
    cpu.regs[2] = 31
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SRA positive shift 31", "0", f"{cpu.regs[3]}")


def test_sra_shift_amount_masked(runner):
    """SRA: shift amount uses only lower 5 bits (32 becomes 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 32  # 32 & 0x1F = 0
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("SRA shift amount masked", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_sra_zero_shifted(runner):
    """SRA: 0 >>s any = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 15
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SRA zero shifted", "0", f"{cpu.regs[3]}")


def test_sra_rd_equals_x0(runner):
    """SRA: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 5
    insn = 0b0100000_00010_00001_101_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("SRA to x0", "0", f"{cpu.regs[0]}")


def test_sra_same_register(runner):
    """SRA: x1 >>s x1 (shift value by itself)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 5
    insn = 0b0100000_00001_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SRA same register", "0", f"{cpu.regs[3]}")


def test_sra_rd_equals_rs1(runner):
    """SRA: x1 = x1 >>s x2 (shift in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 64
    cpu.regs[2] = 3
    insn = 0b0100000_00010_00001_101_00001_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[1] != 8:
        runner.test_fail("SRA rd=rs1", "8", f"{cpu.regs[1]}")


def test_sra_negative_division_by_power_of_two(runner):
    """SRA: -8 >>s 1 = -4 (arithmetic shift for signed division)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFF8  # -8
    cpu.regs[2] = 1
    insn = 0b0100000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFC  # -4
    if cpu.regs[3] != expected:
        runner.test_fail("SRA negative division", f"0x{expected:08X}", f"0x{cpu.regs[3]:08X}")
