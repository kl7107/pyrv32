#!/usr/bin/env python3
"""
Test AUIPC (Add Upper Immediate to PC) instruction
Tests cover all edge cases documented in execute.py exec_auipc docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_auipc_zero_immediate(runner):
    """AUIPC: zero immediate (rd = PC)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # AUIPC x5, 0 - rd = PC + 0
    imm = 0
    insn = (imm << 12) | (5 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(5) != 0x1000:
        runner.test_fail("AUIPC", "0x1000", f"0x{cpu.read_reg(5):08x}")


def test_auipc_positive_immediate(runner):
    """AUIPC: positive immediate (forward address)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # AUIPC x6, 0x12345 - rd = PC + (0x12345 << 12)
    imm = 0x12345
    insn = (imm << 12) | (6 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x1000 + (0x12345 << 12)
    expected &= 0xFFFFFFFF
    if cpu.read_reg(6) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(6):08x}")


def test_auipc_negative_immediate(runner):
    """AUIPC: negative immediate (backward address, bit 19 = 1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80000000
    
    # AUIPC x7, 0xFFFFF (sign-extends to 0xFFFFF000)
    imm = 0xFFFFF  # Upper 20 bits, bit 19 = 1 means negative
    insn = (imm << 12) | (7 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x80000000 + 0xFFFFF000 = 0x7FFFF000 (with wraparound)
    expected = (0x80000000 + 0xFFFFF000) & 0xFFFFFFFF
    if cpu.read_reg(7) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(7):08x}")


def test_auipc_max_positive_offset(runner):
    """AUIPC: maximum positive offset (0x7FFFF << 12)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # AUIPC x8, 0x7FFFF - Max positive (bit 19 = 0)
    imm = 0x7FFFF
    insn = (imm << 12) | (8 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0x1000 + (0x7FFFF << 12)) & 0xFFFFFFFF
    if cpu.read_reg(8) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(8):08x}")


def test_auipc_max_negative_offset(runner):
    """AUIPC: maximum negative offset (0x80000 << 12)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x90000000
    
    # AUIPC x9, 0x80000 - Max negative (bit 19 = 1, extends to 0xFFF80000)
    imm = 0x80000
    insn = (imm << 12) | (9 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    # Sign-extend: 0x80000 becomes 0xFFF80000 after left shift 12
    offset = 0x80000 << 12
    # Sign extend from bit 31
    if offset & 0x80000000:
        offset |= 0xFFFFFFFF00000000  # Extend to 64-bit signed
    expected = (cpu.pc + offset) & 0xFFFFFFFF
    
    # Actually, in 32-bit: 0x90000000 + 0x80000000 = 0x10000000 (wraparound)
    expected = (0x90000000 + 0x80000000) & 0xFFFFFFFF
    if cpu.read_reg(9) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(9):08x}")


def test_auipc_pc_wraparound(runner):
    """AUIPC: PC wraparound (PC near 0xFFFFFFFF with positive offset)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0xFFFFF000
    
    # AUIPC x10, 0x2 - Small positive offset causes wraparound
    imm = 0x2
    insn = (imm << 12) | (10 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0xFFFFF000 + 0x2000) & 0xFFFFFFFF
    if cpu.read_reg(10) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(10):08x}")


def test_auipc_rd_x0(runner):
    """AUIPC: rd = x0 (write ignored, effectively NOP)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # AUIPC x0, 0x123 - Write to x0 is ignored
    imm = 0x123
    insn = (imm << 12) | (0 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail("AUIPC", "0", f"{cpu.read_reg(0)}")


def test_auipc_different_pc_values(runner):
    """AUIPC: verify PC-relative nature with different PC"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Test 1: PC = 0x2000
    cpu.pc = 0x2000
    imm = 0x100
    insn = (imm << 12) | (11 << 7) | 0b0010111
    execute_instruction(cpu, mem, insn)
    result1 = cpu.read_reg(11)
    
    # Test 2: Same instruction at different PC = 0x4000
    cpu.pc = 0x4000
    execute_instruction(cpu, mem, insn)
    result2 = cpu.read_reg(11)
    
    # Results should differ by 0x2000 (PC difference)
    if (result2 - result1) != 0x2000:
        runner.test_fail("AUIPC", "0x2000", f"0x{result2 - result1:08x}")


def test_auipc_pc_increment(runner):
    """AUIPC: PC should increment by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # AUIPC x12, 0x456
    imm = 0x456
    insn = (imm << 12) | (12 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("AUIPC", "0x1004", f"0x{cpu.pc:08x}")


def test_auipc_small_offset(runner):
    """AUIPC: small offset (0x1 << 12 = 0x1000)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x5000
    
    # AUIPC x13, 0x1
    imm = 0x1
    insn = (imm << 12) | (13 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    expected = 0x5000 + 0x1000
    if cpu.read_reg(13) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(13):08x}")


def test_auipc_all_ones_imm(runner):
    """AUIPC: all ones immediate (0xFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x10000000
    
    # AUIPC x14, 0xFFFFF
    imm = 0xFFFFF
    insn = (imm << 12) | (14 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x10000000 + 0xFFFFF000 = 0x0FFFF000
    expected = (0x10000000 + 0xFFFFF000) & 0xFFFFFFFF
    if cpu.read_reg(14) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(14):08x}")


def test_auipc_pc_plus_offset_relationship(runner):
    """AUIPC: verify rd = PC + (imm << 12) relationship"""
    cpu = RV32CPU()
    mem = Memory()
    
    pc_val = 0xABCD0000
    imm_val = 0x54321
    cpu.pc = pc_val
    
    # AUIPC x15, imm_val
    insn = (imm_val << 12) | (15 << 7) | 0b0010111
    
    execute_instruction(cpu, mem, insn)
    
    expected = (pc_val + (imm_val << 12)) & 0xFFFFFFFF
    if cpu.read_reg(15) != expected:
        runner.test_fail("AUIPC", f"0x{expected:08x}", f"0x{cpu.read_reg(15):08x}")


def test_auipc_compare_with_lui(runner):
    """AUIPC: verify difference from LUI (PC-relative vs absolute)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x8000
    imm = 0x12345
    
    # AUIPC x16, imm - PC-relative
    insn_auipc = (imm << 12) | (16 << 7) | 0b0010111
    execute_instruction(cpu, mem, insn_auipc)
    auipc_result = cpu.read_reg(16)
    
    # LUI x17, imm - Absolute
    cpu.pc = 0x8004  # Advance PC
    insn_lui = (imm << 12) | (17 << 7) | 0b0110111
    execute_instruction(cpu, mem, insn_lui)
    lui_result = cpu.read_reg(17)
    
    # AUIPC should include PC (0x8000), LUI should not
    expected_diff = 0x8000
    actual_diff = auipc_result - lui_result
    if actual_diff != expected_diff:
        runner.test_fail("AUIPC", f"0x{expected_diff:08x}", f"0x{actual_diff:08x}")
