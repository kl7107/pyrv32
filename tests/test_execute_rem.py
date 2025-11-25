#!/usr/bin/env python3
"""
Unit tests for REM instruction (M extension).

REM performs signed remainder operation with RISC-V semantics.
Format: REM rd, rs1, rs2
Encoding: opcode=0110011, funct3=110, funct7=0000001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_rem_normal(runner):
    """Test REM with normal division: 10 % 2 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 10
    cpu.regs[6] = 2
    
    # REM x10, x5, x6
    insn = 0b0000001_00110_00101_110_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[10] != 0:
        runner.test_fail("REM normal", "0", f"{cpu.regs[10]}")


def test_rem_with_remainder(runner):
    """Test REM with remainder: 10 % 3 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 10
    cpu.regs[6] = 3
    
    # REM x11, x5, x6
    insn = 0b0000001_00110_00101_110_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[11] != 1:
        runner.test_fail("REM with remainder", "1", f"{cpu.regs[11]}")


def test_rem_by_zero(runner):
    """Test REM by zero returns dividend (RISC-V spec)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 0
    
    # REM x12, x5, x6
    insn = 0b0000001_00110_00101_110_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[12] != 100:
        runner.test_fail("REM by zero", "100", f"{cpu.regs[12]}")


def test_rem_overflow(runner):
    """Test REM overflow: 0x80000000 % -1 = 0 (RISC-V spec)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000
    cpu.regs[6] = 0xFFFFFFFF
    
    # REM x13, x5, x6
    insn = 0b0000001_00110_00101_110_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[13] != 0:
        runner.test_fail("REM overflow", "0", f"{cpu.regs[13]}")


def test_rem_zero_dividend(runner):
    """Test REM with zero dividend: 0 % 5 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # REM x14, x5, x6
    insn = 0b0000001_00110_00101_110_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[14] != 0:
        runner.test_fail("REM zero dividend", "0", f"{cpu.regs[14]}")


def test_rem_negative_dividend_positive_divisor(runner):
    """Test REM: -10 % 3 = -1 (sign follows dividend)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-10 & 0xFFFFFFFF)
    cpu.regs[6] = 3
    
    # REM x15, x5, x6
    insn = 0b0000001_00110_00101_110_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[15] != expected:
        runner.test_fail("REM -10 % 3", f"0x{expected:08X}", f"0x{cpu.regs[15]:08X}")


def test_rem_positive_dividend_negative_divisor(runner):
    """Test REM: 10 % -3 = 1 (sign follows dividend)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 10
    cpu.regs[6] = (-3 & 0xFFFFFFFF)
    
    # REM x16, x5, x6
    insn = 0b0000001_00110_00101_110_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[16] != 1:
        runner.test_fail("REM 10 % -3", "1", f"{cpu.regs[16]}")


def test_rem_negative_negative(runner):
    """Test REM: -10 % -3 = -1 (sign follows dividend)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-10 & 0xFFFFFFFF)
    cpu.regs[6] = (-3 & 0xFFFFFFFF)
    
    # REM x17, x5, x6
    insn = 0b0000001_00110_00101_110_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[17] != expected:
        runner.test_fail("REM -10 % -3", f"0x{expected:08X}", f"0x{cpu.regs[17]:08X}")


def test_rem_7_mod_2(runner):
    """Test REM: 7 % 2 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 7
    cpu.regs[6] = 2
    
    # REM x18, x5, x6
    insn = 0b0000001_00110_00101_110_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[18] != 1:
        runner.test_fail("REM 7 % 2", "1", f"{cpu.regs[18]}")


def test_rem_negative_7_mod_2(runner):
    """Test REM: -7 % 2 = -1 (sign follows dividend)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-7 & 0xFFFFFFFF)
    cpu.regs[6] = 2
    
    # REM x19, x5, x6
    insn = 0b0000001_00110_00101_110_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFF
    if cpu.regs[19] != expected:
        runner.test_fail("REM -7 % 2", f"0x{expected:08X}", f"0x{cpu.regs[19]:08X}")


def test_rem_large_numbers(runner):
    """Test REM with large numbers: 1000000 % 7 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1000000
    cpu.regs[6] = 7
    
    # REM x20, x5, x6
    insn = 0b0000001_00110_00101_110_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[20] != 1:
        runner.test_fail("REM large numbers", "1", f"{cpu.regs[20]}")


def test_rem_max_positive(runner):
    """Test REM with max positive: 0x7FFFFFFF % 2 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF
    cpu.regs[6] = 2
    
    # REM x21, x5, x6
    insn = 0b0000001_00110_00101_110_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[21] != 1:
        runner.test_fail("REM max positive", "1", f"{cpu.regs[21]}")


def test_rem_max_negative(runner):
    """Test REM with max negative: 0x80000000 % 2 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000
    cpu.regs[6] = 2
    
    # REM x22, x5, x6
    insn = 0b0000001_00110_00101_110_10110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[22] != 0:
        runner.test_fail("REM max negative", "0", f"{cpu.regs[22]}")
