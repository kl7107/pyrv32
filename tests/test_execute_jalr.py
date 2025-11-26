#!/usr/bin/env python3
"""
Test JALR (Jump And Link Register) instruction
Tests cover all edge cases documented in execute.py exec_jalr docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_jalr_basic_jump(runner):
    """JALR: basic indirect jump with return address"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2000)
    
    # JALR x1, 0(x2) - Jump to 0x2000, save 0x1004 to x1
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x2000:
        runner.test_fail("JALR", "0x2000", f"0x{cpu.pc:08x}")
    if cpu.read_reg(1) != 0x1004:
        runner.test_fail("JALR", "0x1004", f"0x{cpu.read_reg(1):08x}")


def test_jalr_with_offset(runner):
    """JALR: jump with positive offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2000)
    
    # JALR x1, 100(x2) - Jump to 0x2000 + 100 = 0x2064
    insn = (100 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x2064:
        runner.test_fail("JALR", "0x2064", f"0x{cpu.pc:08x}")


def test_jalr_negative_offset(runner):
    """JALR: jump with negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2000)
    
    # JALR x1, -100(x2) - negative offset
    imm_neg100 = 0xF9C  # -100 in 12-bit signed
    insn = (imm_neg100 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x2000 + (-100) = 0x2000 - 64 = 0x1F9C
    if cpu.pc != 0x1F9C:
        runner.test_fail("JALR", "0x1F9C", f"0x{cpu.pc:08x}")


def test_jalr_lsb_cleared(runner):
    """JALR: LSB of target address is cleared (alignment)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2001)  # Odd address
    
    # JALR x1, 0(x2) - LSB should be cleared: 0x2001 -> 0x2000
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x2000:
        runner.test_fail("JALR", "0x2000", f"0x{cpu.pc:08x}")


def test_jalr_lsb_cleared_with_offset(runner):
    """JALR: LSB cleared even with odd offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2000)
    
    # JALR x1, 7(x2) - Result 0x2007, LSB cleared -> 0x2006
    insn = (7 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x2006:
        runner.test_fail("JALR", "0x2006", f"0x{cpu.pc:08x}")


def test_jalr_return_ret_pseudoinstruction(runner):
    """JALR: return from function (ret = jalr x0, 0(x1))"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x5000
    cpu.write_reg(1, 0x1234)  # Return address
    
    # JALR x0, 0(x1) - Jump to x1, discard return address (ret)
    insn = (0 << 20) | (1 << 15) | (0b000 << 12) | (0 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1234:
        runner.test_fail("JALR", "0x1234", f"0x{cpu.pc:08x}")
    if cpu.read_reg(0) != 0:
        runner.test_fail("JALR", "0", f"{cpu.read_reg(0)}")


def test_jalr_indirect_call(runner):
    """JALR: indirect function call"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 0x3000)  # Function pointer
    
    # JALR x1, 0(x5) - Call function at x5, save return address
    insn = (0 << 20) | (5 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x3000:
        runner.test_fail("JALR", "0x3000", f"0x{cpu.pc:08x}")
    if cpu.read_reg(1) != 0x1004:
        runner.test_fail("JALR", "0x1004", f"0x{cpu.read_reg(1):08x}")


def test_jalr_rd_rs1_same(runner):
    """JALR: rd and rs1 are the same register"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(3, 0x2000)
    
    # JALR x3, 0(x3) - Jump to x3, save return to x3
    # Return address (0x1004) is written AFTER reading rs1
    insn = (0 << 20) | (3 << 15) | (0b000 << 12) | (3 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x2000:
        runner.test_fail("JALR", "0x2000", f"0x{cpu.pc:08x}")
    if cpu.read_reg(3) != 0x1004:
        runner.test_fail("JALR", "0x1004", f"0x{cpu.read_reg(3):08x}")


def test_jalr_rs1_x0(runner):
    """JALR: jump using x0 (always 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JALR x1, 100(x0) - Jump to 0 + 100 = 100 (0x64)
    insn = (100 << 20) | (0 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x64:
        runner.test_fail("JALR", "0x64", f"0x{cpu.pc:08x}")


def test_jalr_zero_offset(runner):
    """JALR: zero offset (common case)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(7, 0x4000)
    
    # JALR x1, 0(x7)
    insn = (0 << 20) | (7 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x4000:
        runner.test_fail("JALR", "0x4000", f"0x{cpu.pc:08x}")


def test_jalr_max_positive_offset(runner):
    """JALR: maximum positive offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2000)
    
    # JALR x1, 2047(x2)
    insn = (2047 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x2000 + 2047 = 0x27FF, LSB cleared -> 0x27FE
    if cpu.pc != 0x27FE:
        runner.test_fail("JALR", "0x27FE", f"0x{cpu.pc:08x}")


def test_jalr_max_negative_offset(runner):
    """JALR: maximum negative offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0x2000)
    
    # JALR x1, -2048(x2)
    imm_neg2048 = 0x800  # -2048 in 12-bit signed
    insn = (imm_neg2048 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x2000 - 2048 = 0x2000 - 0x800 = 0x1800
    if cpu.pc != 0x1800:
        runner.test_fail("JALR", "0x1800", f"0x{cpu.pc:08x}")


def test_jalr_address_wraparound(runner):
    """JALR: address wraparound at 32-bit boundary"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # JALR x1, 10(x2) - Should wrap: 0xFFFFFFFF + 10 = 0x00000009, LSB cleared -> 0x00000008
    insn = (10 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b1100111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x00000008:
        runner.test_fail("JALR", "0x00000008", f"0x{cpu.pc:08x}")
