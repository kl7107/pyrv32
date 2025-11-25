#!/usr/bin/env python3
"""
Unit tests for REMU instruction (M extension).

REMU performs unsigned remainder operation with RISC-V semantics.
Format: REMU rd, rs1, rs2
Encoding: opcode=0110011, funct3=111, funct7=0000001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_remu_normal(runner):
    """Test REMU with normal division: 10 % 2 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 10
    cpu.regs[6] = 2
    
    # REMU x10, x5, x6
    insn = 0b0000001_00110_00101_111_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[10] != 0:
        runner.test_fail("REMU normal", "0", f"{cpu.regs[10]}")


def test_remu_with_remainder(runner):
    """Test REMU with remainder: 10 % 3 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 10
    cpu.regs[6] = 3
    
    # REMU x11, x5, x6
    insn = 0b0000001_00110_00101_111_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[11] != 1:
        runner.test_fail("REMU with remainder", "1", f"{cpu.regs[11]}")


def test_remu_by_zero(runner):
    """Test REMU by zero returns dividend (RISC-V spec)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 0
    
    # REMU x12, x5, x6
    insn = 0b0000001_00110_00101_111_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[12] != 100:
        runner.test_fail("REMU by zero", "100", f"{cpu.regs[12]}")


def test_remu_zero_dividend(runner):
    """Test REMU with zero dividend: 0 % 5 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # REMU x13, x5, x6
    insn = 0b0000001_00110_00101_111_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[13] != 0:
        runner.test_fail("REMU zero dividend", "0", f"{cpu.regs[13]}")


def test_remu_max_mod_2(runner):
    """Test REMU with max unsigned % 2: 0xFFFFFFFF % 2 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 2
    
    # REMU x14, x5, x6
    insn = 0b0000001_00110_00101_111_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[14] != 1:
        runner.test_fail("REMU max % 2", "1", f"{cpu.regs[14]}")


def test_remu_max_mod_3(runner):
    """Test REMU with max unsigned % 3: 0xFFFFFFFF % 3 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 3
    
    # REMU x15, x5, x6
    insn = 0b0000001_00110_00101_111_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[15] != 0:
        runner.test_fail("REMU max % 3", "0", f"{cpu.regs[15]}")


def test_remu_large_mod_small(runner):
    """Test REMU with large unsigned % small: 0x80000000 % 3 = 2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000
    cpu.regs[6] = 3
    
    # REMU x16, x5, x6
    insn = 0b0000001_00110_00101_111_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[16] != 2:
        runner.test_fail("REMU 0x80000000 % 3", "2", f"{cpu.regs[16]}")


def test_remu_7_mod_2(runner):
    """Test REMU: 7 % 2 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 7
    cpu.regs[6] = 2
    
    # REMU x17, x5, x6
    insn = 0b0000001_00110_00101_111_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[17] != 1:
        runner.test_fail("REMU 7 % 2", "1", f"{cpu.regs[17]}")


def test_remu_large_numbers(runner):
    """Test REMU with large numbers: 1000000 % 7 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1000000
    cpu.regs[6] = 7
    
    # REMU x18, x5, x6
    insn = 0b0000001_00110_00101_111_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[18] != 1:
        runner.test_fail("REMU large numbers", "1", f"{cpu.regs[18]}")


def test_remu_max_mod_max(runner):
    """Test REMU: 0xFFFFFFFF % 0xFFFFFFFF = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 0xFFFFFFFF
    
    # REMU x19, x5, x6
    insn = 0b0000001_00110_00101_111_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[19] != 0:
        runner.test_fail("REMU max % max", "0", f"{cpu.regs[19]}")


def test_remu_max_minus_1_mod_max(runner):
    """Test REMU: 0xFFFFFFFE % 0xFFFFFFFF = 0xFFFFFFFE"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFE
    cpu.regs[6] = 0xFFFFFFFF
    
    # REMU x20, x5, x6
    insn = 0b0000001_00110_00101_111_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFFFFFFFE
    if cpu.regs[20] != expected:
        runner.test_fail("REMU (max-1) % max", f"0x{expected:08X}", f"0x{cpu.regs[20]:08X}")


def test_remu_power_of_two(runner):
    """Test REMU with power of two: 0x12345678 % 0x100 = 0x78"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x12345678
    cpu.regs[6] = 0x100
    
    # REMU x21, x5, x6
    insn = 0b0000001_00110_00101_111_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x78
    if cpu.regs[21] != expected:
        runner.test_fail("REMU power of two", f"0x{expected:02X}", f"0x{cpu.regs[21]:02X}")


def test_remu_no_negative(runner):
    """Test REMU has no negative remainders: 0xFFFFFFFF % 10 = 5"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFFFFFF
    cpu.regs[6] = 10
    
    # REMU x22, x5, x6
    insn = 0b0000001_00110_00101_111_10110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[22] != 5:
        runner.test_fail("REMU no negative", "5", f"{cpu.regs[22]}")
