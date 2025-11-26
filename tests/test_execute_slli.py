#!/usr/bin/env python3
"""
Test SLLI (Shift Left Logical Immediate) instruction
Tests cover all edge cases documented in execute.py exec_i_type_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_slli_shift_by_zero(runner):
    """SLLI: value << 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # SLLI x1, x2, 0 (shamt=0 in imm[4:0], imm[11:5]=0)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("SLLI", "0x12345678", f"0x{cpu.read_reg(1):08x}")


def test_slli_shift_by_one(runner):
    """SLLI: 1 << 1 = 2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 1)
    
    # SLLI x1, x2, 1
    insn = (1 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 2:
        runner.test_fail("SLLI", "2", f"{cpu.read_reg(1)}")


def test_slli_shift_by_31(runner):
    """SLLI: 1 << 31 = 0x80000000 (max shift)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 1)
    
    # SLLI x1, x2, 31 (shamt=31 in imm[4:0])
    insn = (31 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x80000000:
        runner.test_fail("SLLI", "0x80000000", f"0x{cpu.read_reg(1):08x}")


def test_slli_shift_out_bits(runner):
    """SLLI: shifting out bits from MSB"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # SLLI x1, x2, 4 (shift out top 4 bits)
    insn = (4 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF << 4 = 0xFFFFFFF0
    if cpu.read_reg(1) != 0xFFFFFFF0:
        runner.test_fail("SLLI", "0xFFFFFFF0", f"0x{cpu.read_reg(1):08x}")


def test_slli_zero_shifted(runner):
    """SLLI: 0 << any = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0)
    
    # SLLI x1, x2, 16
    insn = (16 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail("SLLI", "0", f"{cpu.read_reg(1)}")


def test_slli_power_of_two(runner):
    """SLLI: multiplying by power of 2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 5)
    
    # SLLI x1, x2, 3 (5 << 3 = 5 * 8 = 40)
    insn = (3 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 40:
        runner.test_fail("SLLI", "40", f"{cpu.read_reg(1)}")


def test_slli_bit_pattern(runner):
    """SLLI: shifting bit pattern"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xAAAAAAAA)
    
    # SLLI x1, x2, 1 (alternating pattern shifted)
    insn = (1 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xAAAAAAAA << 1 = 0x55555554
    if cpu.read_reg(1) != 0x55555554:
        runner.test_fail("SLLI", "0x55555554", f"0x{cpu.read_reg(1):08x}")


def test_slli_rd_x0(runner):
    """SLLI: writing to x0 discards result"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # SLLI x0, x2, 4 (result discarded)
    insn = (4 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail("SLLI", "0", f"{cpu.read_reg(0)}")


def test_slli_rs1_x0(runner):
    """SLLI: shifting x0 gives 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    # SLLI x1, x0, 8
    insn = (8 << 20) | (0 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail("SLLI", "0", f"{cpu.read_reg(1)}")


def test_slli_shift_by_16(runner):
    """SLLI: shifting by 16 (common case)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x0000ABCD)
    
    # SLLI x1, x2, 16 (move to upper halfword)
    insn = (16 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x0000ABCD << 16 = 0xABCD0000
    if cpu.read_reg(1) != 0xABCD0000:
        runner.test_fail("SLLI", "0xABCD0000", f"0x{cpu.read_reg(1):08x}")


def test_slli_single_bit(runner):
    """SLLI: shifting single bit position"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x00000001)
    
    # SLLI x1, x2, 7 (bit 0 -> bit 7)
    insn = (7 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x00000001 << 7 = 0x00000080
    if cpu.read_reg(1) != 0x00000080:
        runner.test_fail("SLLI", "0x00000080", f"0x{cpu.read_reg(1):08x}")


def test_slli_pc_increment(runner):
    """SLLI: PC should increment by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(2, 42)
    
    # SLLI x1, x2, 2
    insn = (2 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("SLLI", "0x1004", f"0x{cpu.pc:08x}")
