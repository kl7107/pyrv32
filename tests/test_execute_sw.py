#!/usr/bin/env python3
"""
Test SW (Store Word) instruction
Tests cover all edge cases documented in execute.py exec_store docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_sw_basic(runner):
    """SW: basic word store"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)  # Base address
    cpu.write_reg(3, 0x12345678)  # Value to store
    
    # SW x3, 0(x2) - Store word from x3 to address in x2
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001000)
    if stored != 0x12345678:
        runner.test_fail("SW", "0x12345678", f"0x{stored:08x}")


def test_sw_zero_value(runner):
    """SW: store zero word"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    cpu.write_reg(3, 0)
    
    # SW x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001000)
    if stored != 0:
        runner.test_fail("SW", "0", f"{stored}")


def test_sw_all_ones(runner):
    """SW: store 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    cpu.write_reg(3, 0xFFFFFFFF)
    
    # SW x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001000)
    if stored != 0xFFFFFFFF:
        runner.test_fail("SW", "0xFFFFFFFF", f"0x{stored:08x}")


def test_sw_max_positive(runner):
    """SW: store maximum positive signed value"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    cpu.write_reg(3, 0x7FFFFFFF)
    
    # SW x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001000)
    if stored != 0x7FFFFFFF:
        runner.test_fail("SW", "0x7FFFFFFF", f"0x{stored:08x}")


def test_sw_max_negative(runner):
    """SW: store maximum negative signed value"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    cpu.write_reg(3, 0x80000000)
    
    # SW x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001000)
    if stored != 0x80000000:
        runner.test_fail("SW", "0x80000000", f"0x{stored:08x}")


def test_sw_positive_offset(runner):
    """SW: store with positive offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    cpu.write_reg(3, 0xDEADBEEF)
    
    # SW x3, 100(x2) - Store at 0x80001000 + 100 = 0x1064
    imm = 100
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001064)
    if stored != 0xDEADBEEF:
        runner.test_fail("SW", "0xDEADBEEF", f"0x{stored:08x}")


def test_sw_negative_offset(runner):
    """SW: store with negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80002000)
    cpu.write_reg(3, 0xCAFEBABE)
    
    # SW x3, -100(x2) - Store at 0x80002000 - 100 = 0x1F9C
    imm = (-100) & 0xFFF  # 12-bit immediate
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001F9C)
    if stored != 0xCAFEBABE:
        runner.test_fail("SW", "0xCAFEBABE", f"0x{stored:08x}")


def test_sw_max_positive_offset(runner):
    """SW: maximum positive offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    cpu.write_reg(3, 0xAAAAAAAA)
    
    # SW x3, 2047(x2)
    imm = 2047
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x800017FF)
    if stored != 0xAAAAAAAA:
        runner.test_fail("SW", "0xAAAAAAAA", f"0x{stored:08x}")


def test_sw_max_negative_offset(runner):
    """SW: maximum negative offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80002000)
    cpu.write_reg(3, 0x55555555)
    
    # SW x3, -2048(x2)
    imm = (-2048) & 0xFFF
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001800)
    if stored != 0x55555555:
        runner.test_fail("SW", "0x55555555", f"0x{stored:08x}")


def test_sw_rs1_x0(runner):
    """SW: base address from x0 (modified to use valid RAM with x2 as base)"""
    cpu = RV32CPU()
    mem = Memory()
    
    base_addr = 0x80000000
    offset = 100
    cpu.write_reg(2, base_addr)
    cpu.write_reg(3, 0x11223344)
    
    # SW x3, 100(x2) - changed from x0 to x2 for valid RAM
    imm = offset
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    insn = (imm_11_5 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (imm_4_0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(base_addr + offset)
    if stored != 0x11223344:
        runner.test_fail("SW", "0x11223344", f"0x{stored:08x}")


def test_sw_rs2_x0(runner):
    """SW: store value from x0 (stores 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    mem.write_word(0x80001000, 0xFFFFFFFF)  # Pre-fill with non-zero
    
    # SW x0, 0(x2) - Store 0
    insn = (0 << 25) | (0 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    stored = mem.read_word(0x80001000)
    if stored != 0:
        runner.test_fail("SW", "0", f"{stored}")


def test_sw_misaligned(runner):
    """SW: store to misaligned address"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001002)  # Misaligned (not multiple of 4)
    cpu.write_reg(3, 0x99887766)
    
    # SW x3, 0(x2) - Store at misaligned address
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    # Should still store (RISC-V allows misaligned access)
    stored = mem.read_word(0x80001002)
    if stored != 0x99887766:
        runner.test_fail("SW", "0x99887766", f"0x{stored:08x}")


def test_sw_store_then_load(runner):
    """SW: verify store persists through load"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80001000)
    cpu.write_reg(3, 0xFEEDFACE)
    
    # SW x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    execute_instruction(cpu, mem, insn)
    
    # LW x4, 0(x2) - Load it back
    insn_load = (0 << 20) | (2 << 15) | (0b010 << 12) | (4 << 7) | 0b0000011
    execute_instruction(cpu, mem, insn_load)
    
    if cpu.read_reg(4) != 0xFEEDFACE:
        runner.test_fail("SW", "0xFEEDFACE", f"0x{cpu.read_reg(4):08x}")


def test_sw_pc_increment(runner):
    """SW: PC should increment by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80001000
    cpu.write_reg(2, 0x80002000)
    cpu.write_reg(3, 0x12121212)
    
    # SW x3, 0(x2)
    insn = (0 << 25) | (3 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0100011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x80001004:
        runner.test_fail("SW", "0x80001004", f"0x{cpu.pc:08x}")
