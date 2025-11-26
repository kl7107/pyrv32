#!/usr/bin/env python3
"""
Test SRLI (Shift Right Logical Immediate) instruction
Tests cover all edge cases documented in execute.py exec_i_type_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_srli_shift_by_zero(runner):
    """SRLI: value >> 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # SRLI x1, x2, 0 (shamt=0, funct3=101, imm[11:5]=0)
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("SRLI", "0x12345678", f"0x{cpu.read_reg(1):08x}")


def test_srli_shift_by_one(runner):
    """SRLI: 8 >> 1 = 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 8)
    
    # SRLI x1, x2, 1
    insn = (1 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 4:
        runner.test_fail("SRLI", "4", f"{cpu.read_reg(1)}")


def test_srli_shift_by_31(runner):
    """SRLI: 0x80000000 >> 31 = 1 (MSB to LSB)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80000000)
    
    # SRLI x1, x2, 31
    insn = (31 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail("SRLI", "1", f"{cpu.read_reg(1)}")


def test_srli_negative_value_zero_extension(runner):
    """SRLI: negative value shifted (zero extension, not sign extension)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # SRLI x1, x2, 1 (should fill with 0, not 1)
    insn = (1 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF >> 1 = 0x7FFFFFFF (logical, fills with 0)
    if cpu.read_reg(1) != 0x7FFFFFFF:
        runner.test_fail("SRLI", "0x7FFFFFFF", f"0x{cpu.read_reg(1):08x}")


def test_srli_shift_out_bits(runner):
    """SRLI: shifting out bits from LSB"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # SRLI x1, x2, 4 (shift out bottom 4 bits)
    insn = (4 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF >> 4 = 0x0FFFFFFF
    if cpu.read_reg(1) != 0x0FFFFFFF:
        runner.test_fail("SRLI", "0x0FFFFFFF", f"0x{cpu.read_reg(1):08x}")


def test_srli_zero_shifted(runner):
    """SRLI: 0 >> any = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0)
    
    # SRLI x1, x2, 16
    insn = (16 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail("SRLI", "0", f"{cpu.read_reg(1)}")


def test_srli_power_of_two(runner):
    """SRLI: dividing by power of 2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 40)
    
    # SRLI x1, x2, 3 (40 >> 3 = 40 / 8 = 5)
    insn = (3 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 5:
        runner.test_fail("SRLI", "5", f"{cpu.read_reg(1)}")


def test_srli_rd_x0(runner):
    """SRLI: writing to x0 discards result"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # SRLI x0, x2, 4 (result discarded)
    insn = (4 << 20) | (2 << 15) | (0b101 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail("SRLI", "0", f"{cpu.read_reg(0)}")


def test_srli_rs1_x0(runner):
    """SRLI: shifting x0 gives 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    # SRLI x1, x0, 8
    insn = (8 << 20) | (0 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail("SRLI", "0", f"{cpu.read_reg(1)}")


def test_srli_shift_by_16(runner):
    """SRLI: shifting by 16 (common case)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xABCD0000)
    
    # SRLI x1, x2, 16 (extract upper halfword)
    insn = (16 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xABCD0000 >> 16 = 0x0000ABCD
    if cpu.read_reg(1) != 0x0000ABCD:
        runner.test_fail("SRLI", "0x0000ABCD", f"0x{cpu.read_reg(1):08x}")


def test_srli_single_bit(runner):
    """SRLI: shifting single bit position"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x00000080)
    
    # SRLI x1, x2, 7 (bit 7 -> bit 0)
    insn = (7 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x00000080 >> 7 = 0x00000001
    if cpu.read_reg(1) != 0x00000001:
        runner.test_fail("SRLI", "0x00000001", f"0x{cpu.read_reg(1):08x}")


def test_srli_pc_increment(runner):
    """SRLI: PC should increment by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 42)
    
    # SRLI x1, x2, 2
    insn = (2 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("SRLI", "0x1004", f"0x{cpu.pc:08x}")
