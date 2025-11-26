#!/usr/bin/env python3
"""
Test SRAI (Shift Right Arithmetic Immediate) instruction
Tests cover all edge cases documented in execute.py exec_i_type_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_srai_shift_by_zero(runner):
    """SRAI: value >>s 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # SRAI x1, x2, 0 (shamt=0, funct3=101, imm[11:5]=0100000)
    insn = (0b0100000_00000 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("SRAI", "0x12345678", f"0x{cpu.read_reg(1):08x}")


def test_srai_positive_shift_one(runner):
    """SRAI: 8 >>s 1 = 4 (positive, fill with 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 8)
    
    # SRAI x1, x2, 1 (shamt=1 in imm[4:0], imm[11:5]=0100000)
    insn = (0b0100000_00001 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 4:
        runner.test_fail("SRAI", "4", f"{cpu.read_reg(1)}")


def test_srai_negative_shift_one(runner):
    """SRAI: -1 >>s 1 = -1 (negative, fill with 1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # SRAI x1, x2, 1
    insn = (0b0100000_00001 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF >>s 1 = 0xFFFFFFFF (sign extends with 1s)
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail("SRAI", "0xFFFFFFFF", f"0x{cpu.read_reg(1):08x}")


def test_srai_sign_extension(runner):
    """SRAI: sign extension preserves sign bit"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80000000)  # Most negative 32-bit value
    
    # SRAI x1, x2, 1
    insn = (0b0100000_00001 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x80000000 >>s 1 = 0xC0000000 (fills with 1s from MSB)
    if cpu.read_reg(1) != 0xC0000000:
        runner.test_fail("SRAI", "0xC0000000", f"0x{cpu.read_reg(1):08x}")


def test_srai_positive_shift_31(runner):
    """SRAI: positive >> 31 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x7FFFFFFF)  # Max positive
    
    # SRAI x1, x2, 31
    insn = (0b0100000_11111 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x7FFFFFFF >>s 31 = 0 (sign bit is 0, fills with 0s)
    if cpu.read_reg(1) != 0:
        runner.test_fail("SRAI", "0", f"{cpu.read_reg(1)}")


def test_srai_negative_shift_31(runner):
    """SRAI: negative >> 31 = -1 (0xFFFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80000000)  # Most negative
    
    # SRAI x1, x2, 31
    insn = (0b0100000_11111 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x80000000 >>s 31 = 0xFFFFFFFF (sign bit is 1, fills with 1s)
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail("SRAI", "0xFFFFFFFF", f"0x{cpu.read_reg(1):08x}")


def test_srai_zero_shifted(runner):
    """SRAI: 0 >>s any = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0)
    
    # SRAI x1, x2, 16
    insn = (0b0100000_10000 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail("SRAI", "0", f"{cpu.read_reg(1)}")


def test_srai_rd_x0(runner):
    """SRAI: writing to x0 discards result"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # SRAI x0, x2, 4 (result discarded)
    insn = (0b0100000_00100 << 20) | (2 << 15) | (0b101 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail("SRAI", "0", f"{cpu.read_reg(0)}")


def test_srai_rs1_x0(runner):
    """SRAI: shifting x0 gives 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    # SRAI x1, x0, 8
    insn = (0b0100000_01000 << 20) | (0 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail("SRAI", "0", f"{cpu.read_reg(1)}")


def test_srai_negative_division(runner):
    """SRAI: arithmetic shift for signed division by power of 2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFF8)  # -8 in two's complement
    
    # SRAI x1, x2, 1 (divide by 2, should be -4)
    insn = (0b0100000_00001 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # -8 / 2 = -4 = 0xFFFFFFFC
    if cpu.read_reg(1) != 0xFFFFFFFC:
        runner.test_fail("SRAI", "0xFFFFFFFC", f"0x{cpu.read_reg(1):08x}")


def test_srai_shift_by_16(runner):
    """SRAI: shifting by 16 with sign extension"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xABCD0000)  # Negative value (MSB set)
    
    # SRAI x1, x2, 16 (extract upper halfword with sign extension)
    insn = (0b0100000_10000 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xABCD0000 >>s 16 = 0xFFFFABCD (sign extends from bit 31)
    if cpu.read_reg(1) != 0xFFFFABCD:
        runner.test_fail("SRAI", "0xFFFFABCD", f"0x{cpu.read_reg(1):08x}")


def test_srai_small_negative(runner):
    """SRAI: small negative value with arithmetic shift"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFE)  # -2
    
    # SRAI x1, x2, 1 (divide by 2, should be -1)
    insn = (0b0100000_00001 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # -2 / 2 = -1 = 0xFFFFFFFF
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail("SRAI", "0xFFFFFFFF", f"0x{cpu.read_reg(1):08x}")


def test_srai_pc_increment(runner):
    """SRAI: PC should increment by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 42)
    
    # SRAI x1, x2, 2
    insn = (0b0100000_00010 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("SRAI", "0x1004", f"0x{cpu.pc:08x}")
