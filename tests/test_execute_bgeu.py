#!/usr/bin/env python3
"""
Test BGEU (Branch if Greater than or Equal - Unsigned) instruction
Tests cover all edge cases documented in execute.py exec_branch docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def encode_b_type(funct3, rs1, rs2, imm):
    """Helper to encode B-type instruction"""
    # B-type immediate encoding: imm[12|10:5|4:1|11]
    imm_12 = (imm >> 12) & 0x1
    imm_10_5 = (imm >> 5) & 0x3F
    imm_4_1 = (imm >> 1) & 0xF
    imm_11 = (imm >> 11) & 0x1
    
    opcode = 0b1100011
    return ((imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | 
            (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode)


def test_bgeu_greater_than_taken(runner):
    """BGEU: rs1 > rs2 (unsigned) - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 200)
    cpu.write_reg(6, 100)
    
    # BGEU x5, x6, 100 (200 > 100 unsigned)
    insn = encode_b_type(0b111, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch taken: PC = 0x1000 + 100 = 0x1064
    if cpu.pc != 0x1064:
        runner.test_fail("BGEU", "0x1064", f"0x{cpu.pc:08x}")


def test_bgeu_equal_taken(runner):
    """BGEU: rs1 == rs2 - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 100)
    
    # BGEU x5, x6, 100
    insn = encode_b_type(0b111, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Equal means >=, branch taken
    if cpu.pc != 0x1064:
        runner.test_fail("BGEU", "0x1064", f"0x{cpu.pc:08x}")


def test_bgeu_less_than_not_taken(runner):
    """BGEU: rs1 < rs2 - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 200)
    
    # BGEU x5, x6, 100 (100 < 200)
    insn = encode_b_type(0b111, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch not taken: PC = 0x1000 + 4 = 0x1004
    if cpu.pc != 0x1004:
        runner.test_fail("BGEU", "0x1004", f"0x{cpu.pc:08x}")


def test_bgeu_max_greater_than_anything(runner):
    """BGEU: 0xFFFFFFFF >= anything - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(7, 0xFFFFFFFF)
    cpu.write_reg(8, 0)
    
    # BGEU x7, x8, 200 (0xFFFFFFFF >= 0)
    insn = encode_b_type(0b111, 7, 8, 200)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x10C8:  # 0x1000 + 200
        runner.test_fail("BGEU", "0x10C8", f"0x{cpu.pc:08x}")


def test_bgeu_anything_greater_than_zero(runner):
    """BGEU: any value >= 0 - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(9, 1)
    cpu.write_reg(10, 0)
    
    # BGEU x9, x10, 100 (1 >= 0)
    insn = encode_b_type(0b111, 9, 10, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1064:
        runner.test_fail("BGEU", "0x1064", f"0x{cpu.pc:08x}")


def test_bgeu_zero_not_greater_than_nonzero(runner):
    """BGEU: 0 not >= non-zero - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(11, 0)
    cpu.write_reg(12, 1)
    
    # BGEU x11, x12, 80 (0 < 1)
    insn = encode_b_type(0b111, 11, 12, 80)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("BGEU", "0x1004", f"0x{cpu.pc:08x}")


def test_bgeu_unsigned_vs_signed_difference(runner):
    """BGEU: 0xFFFFFFFF >= 0x7FFFFFFF (unsigned, opposite of signed)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(13, 0xFFFFFFFF)  # Max unsigned
    cpu.write_reg(14, 0x7FFFFFFF)  # Max positive signed
    
    # BGEU x13, x14, 60 (0xFFFFFFFF >= 0x7FFFFFFF unsigned)
    insn = encode_b_type(0b111, 13, 14, 60)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x103C:  # 0x1000 + 60
        runner.test_fail("BGEU", "0x103C", f"0x{cpu.pc:08x}")


def test_bgeu_boundary_values(runner):
    """BGEU: boundary value comparison (0x80000000 >= 0x7FFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(15, 0x80000000)
    cpu.write_reg(16, 0x7FFFFFFF)
    
    # BGEU x15, x16, 50 (0x80000000 >= 0x7FFFFFFF unsigned)
    insn = encode_b_type(0b111, 15, 16, 50)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1032:  # 0x1000 + 50
        runner.test_fail("BGEU", "0x1032", f"0x{cpu.pc:08x}")


def test_bgeu_backward_branch(runner):
    """BGEU: backward branch (negative offset)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    cpu.write_reg(17, 100)
    cpu.write_reg(18, 42)
    
    # BGEU x17, x18, -100 (100 >= 42)
    imm = (-100) & 0x1FFF
    insn = encode_b_type(0b111, 17, 18, imm)
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0x2000 - 100) & 0xFFFFFFFF
    if cpu.pc != expected:
        runner.test_fail("BGEU", f"0x{expected:08x}", f"0x{cpu.pc:08x}")


def test_bgeu_same_register_taken(runner):
    """BGEU: rs1 = rs2 (same register, always >=)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(19, 0xDEADBEEF)
    
    # BGEU x19, x19, 64
    insn = encode_b_type(0b111, 19, 19, 64)
    
    execute_instruction(cpu, mem, insn)
    
    # Same value, always >=, branch taken
    if cpu.pc != 0x1040:  # 0x1000 + 64
        runner.test_fail("BGEU", "0x1040", f"0x{cpu.pc:08x}")


def test_bgeu_compare_to_x0_always_taken(runner):
    """BGEU: any value >= x0 (0) - always branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(20, 100)
    
    # BGEU x20, x0, 32 (100 >= 0)
    insn = encode_b_type(0b111, 20, 0, 32)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1020:  # 0x1000 + 32
        runner.test_fail("BGEU", "0x1020", f"0x{cpu.pc:08x}")


def test_bgeu_x0_vs_x0(runner):
    """BGEU: x0 >= x0 - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # BGEU x0, x0, 48 (0 >= 0)
    insn = encode_b_type(0b111, 0, 0, 48)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1030:  # 0x1000 + 48
        runner.test_fail("BGEU", "0x1030", f"0x{cpu.pc:08x}")


def test_bgeu_max_forward_offset(runner):
    """BGEU: maximum forward offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(21, 20)
    cpu.write_reg(22, 10)
    
    # BGEU x21, x22, 4094
    insn = encode_b_type(0b111, 21, 22, 4094)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1FFE:  # 0x1000 + 4094
        runner.test_fail("BGEU", "0x1FFE", f"0x{cpu.pc:08x}")


def test_bgeu_high_bit_unsigned(runner):
    """BGEU: high bit values as unsigned (0x80000001 >= 0x80000000)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(23, 0x80000001)
    cpu.write_reg(24, 0x80000000)
    
    # BGEU x23, x24, 100
    insn = encode_b_type(0b111, 23, 24, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1064:
        runner.test_fail("BGEU", "0x1064", f"0x{cpu.pc:08x}")


def test_bgeu_zero_offset_loop(runner):
    """BGEU: zero offset infinite loop"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x3000
    cpu.write_reg(25, 50)
    cpu.write_reg(26, 50)
    
    # BGEU x25, x26, 0 (infinite loop on equal)
    insn = encode_b_type(0b111, 25, 26, 0)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x3000:
        runner.test_fail("BGEU", "0x3000", f"0x{cpu.pc:08x}")
