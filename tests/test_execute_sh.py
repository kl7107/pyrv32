#!/usr/bin/env python3
"""
Test SH (Store Halfword) instruction
Tests cover all edge cases documented in execute.py exec_store docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_sh_basic(runner):
    """SH: basic halfword store"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)  # Base address
    cpu.write_reg(3, 0xABCD)  # Value to store
    
    # SH x3, 0(x2) - Store halfword from x3 to address in x2
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1000)
    if stored != 0xABCD:
        runner.test_fail("SH", "0xABCD", f"0x{stored:04x}")


def test_sh_zero_value(runner):
    """SH: store zero halfword"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)
    cpu.write_reg(3, 0)
    
    # SH x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1000)
    if stored != 0:
        runner.test_fail("SH", "0", f"{stored}")


def test_sh_all_ones(runner):
    """SH: store 0xFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)
    cpu.write_reg(3, 0xFFFF)
    
    # SH x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1000)
    if stored != 0xFFFF:
        runner.test_fail("SH", "0xFFFF", f"0x{stored:04x}")


def test_sh_upper_bits_ignored(runner):
    """SH: only lower 16 bits stored, upper bits ignored"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)
    cpu.write_reg(3, 0x12345678)  # Upper bits should be ignored
    
    # SH x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1000)
    if stored != 0x5678:
        runner.test_fail("SH", "0x5678", f"0x{stored:04x}")


def test_sh_positive_offset(runner):
    """SH: store with positive offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)
    cpu.write_reg(3, 0x1234)
    
    # SH x3, 100(x2) - Store at 0x1000 + 100 = 0x1064
    imm = 100
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1064)
    if stored != 0x1234:
        runner.test_fail("SH", "0x1234", f"0x{stored:04x}")


def test_sh_negative_offset(runner):
    """SH: store with negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x2000)
    cpu.write_reg(3, 0xABCD)
    
    # SH x3, -100(x2) - Store at 0x2000 - 100 = 0x1F9C
    imm = (-100) & 0xFFF  # 12-bit immediate
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1F9C)
    if stored != 0xABCD:
        runner.test_fail("SH", "0xABCD", f"0x{stored:04x}")


def test_sh_max_positive_offset(runner):
    """SH: maximum positive offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)
    cpu.write_reg(3, 0x9999)
    
    # SH x3, 2047(x2)
    imm = 2047
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x17FF)
    if stored != 0x9999:
        runner.test_fail("SH", "0x9999", f"0x{stored:04x}")


def test_sh_max_negative_offset(runner):
    """SH: maximum negative offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x2000)
    cpu.write_reg(3, 0x7777)
    
    # SH x3, -2048(x2)
    imm = (-2048) & 0xFFF
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1800)
    if stored != 0x7777:
        runner.test_fail("SH", "0x7777", f"0x{stored:04x}")


def test_sh_rs1_x0(runner):
    """SH: base address from x0 (uses 0 as base)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(3, 0xBEEF)
    
    # SH x3, 100(x0) - Store at 0 + 100 = 100
    imm = 100
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (0 << 15) | (0b001 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(100)
    if stored != 0xBEEF:
        runner.test_fail("SH", "0xBEEF", f"0x{stored:04x}")


def test_sh_rs2_x0(runner):
    """SH: store value from x0 (stores 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)
    mem.write_halfword(0x1000, 0xFFFF)  # Pre-fill with non-zero
    
    # SH x0, 0(x2) - Store 0
    insn = (0 << 25) | (0 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_halfword(0x1000)
    if stored != 0:
        runner.test_fail("SH", "0", f"{stored}")


def test_sh_misaligned(runner):
    """SH: store to misaligned (odd) address"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1001)  # Odd address
    cpu.write_reg(3, 0xCAFE)
    
    # SH x3, 0(x2) - Store at odd address (implementation dependent)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    # Should still store (RISC-V allows misaligned access)
    stored = mem.read_halfword(0x1001)
    if stored != 0xCAFE:
        runner.test_fail("SH", "0xCAFE", f"0x{stored:04x}")


def test_sh_store_then_load(runner):
    """SH: verify store persists through load"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x1000)
    cpu.write_reg(3, 0x5A5A)
    
    # SH x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    execute_instruction(cpu, mem, insn)
    
    # LH x4, 0(x2) - Load it back
    insn_load = (0 << 20) | (2 << 15) | (0b001 << 12) | (4 << 7) | 0b0000011
    execute_instruction(cpu, mem, insn_load)
    
    if cpu.read_reg(4) != 0x5A5A:
        runner.test_fail("SH", "0x5A5A", f"0x{cpu.read_reg(4):04x}")


def test_sh_pc_increment(runner):
    """SH: PC should increment by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2000)
    cpu.write_reg(3, 0x1111)
    
    # SH x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("SH", "0x1004", f"0x{cpu.pc:08x}")
