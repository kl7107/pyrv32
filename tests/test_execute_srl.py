#!/usr/bin/env python3
"""
Test SRL (Shift Right Logical) instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_srl_shift_by_zero(runner):
    """SRL: value >> 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0
    
    # SRL x3, x1, x2 (funct3=101, funct7=0000000)
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("SRL shift by zero", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_srl_shift_by_one(runner):
    """SRL: 8 >> 1 = 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 8
    cpu.regs[2] = 1
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 4:
        runner.test_fail("SRL shift by one", "4", f"{cpu.regs[3]}")


def test_srl_shift_by_31(runner):
    """SRL: 0x80000000 >> 31 = 1 (MSB to LSB)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x80000000
    cpu.regs[2] = 31
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SRL shift by 31", "1", f"{cpu.regs[3]}")


def test_srl_shift_amount_masked(runner):
    """SRL: shift amount uses only lower 5 bits (32 becomes 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 32  # 32 & 0x1F = 0
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x12345678:
        runner.test_fail("SRL shift amount masked", "0x12345678", f"0x{cpu.regs[3]:08X}")


def test_srl_negative_value_no_sign_extend(runner):
    """SRL: 0xFFFFFFFF >> 1 = 0x7FFFFFFF (zero extension, not sign)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 1
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x7FFFFFFF:
        runner.test_fail("SRL negative no sign extend", "0x7FFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_srl_negative_shift_31(runner):
    """SRL: 0xFFFFFFFF >> 31 = 1 (zero extension)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 31
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SRL negative shift 31", "1", f"{cpu.regs[3]}")


def test_srl_shift_out_bits(runner):
    """SRL: 0xFFFFFFFF >> 4 = 0x0FFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 4
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x0FFFFFFF:
        runner.test_fail("SRL shift out bits", "0x0FFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_srl_zero_shifted(runner):
    """SRL: 0 >> any = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 15
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SRL zero shifted", "0", f"{cpu.regs[3]}")


def test_srl_power_of_two(runner):
    """SRL: 1024 >> 10 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 1024
    cpu.regs[2] = 10
    insn = 0b0000000_00010_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 1:
        runner.test_fail("SRL power of two", "1", f"{cpu.regs[3]}")


def test_srl_rd_equals_x0(runner):
    """SRL: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 5
    insn = 0b0000000_00010_00001_101_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("SRL to x0", "0", f"{cpu.regs[0]}")


def test_srl_same_register(runner):
    """SRL: x1 >> x1 (shift value by itself)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 5  # Shift 5 by 5 positions
    insn = 0b0000000_00001_00001_101_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("SRL same register", "0", f"{cpu.regs[3]}")


def test_srl_rd_equals_rs1(runner):
    """SRL: x1 = x1 >> x2 (shift in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 64
    cpu.regs[2] = 3
    insn = 0b0000000_00010_00001_101_00001_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[1] != 8:
        runner.test_fail("SRL rd=rs1", "8", f"{cpu.regs[1]}")
