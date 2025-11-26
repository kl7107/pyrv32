#!/usr/bin/env python3
"""
Test BLT (Branch if Less Than - Signed) instruction
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


def test_blt_less_than_taken(runner):
    """BLT: rs1 < rs2 (signed) - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 200)
    
    # BLT x5, x6, 100 (100 < 200)
    insn = encode_b_type(0b100, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch taken: PC = 0x1000 + 100 = 0x1064
    if cpu.pc != 0x1064:
        runner.test_fail("BLT", "0x1064", f"0x{cpu.pc:08x}")


def test_blt_greater_than_not_taken(runner):
    """BLT: rs1 > rs2 - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 200)
    cpu.write_reg(6, 100)
    
    # BLT x5, x6, 100 (200 > 100)
    insn = encode_b_type(0b100, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch not taken: PC = 0x1000 + 4 = 0x1004
    if cpu.pc != 0x1004:
        runner.test_fail("BLT", "0x1004", f"0x{cpu.pc:08x}")


def test_blt_equal_not_taken(runner):
    """BLT: rs1 == rs2 - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 100)
    
    # BLT x5, x6, 100
    insn = encode_b_type(0b100, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Not less than (equal), branch not taken
    if cpu.pc != 0x1004:
        runner.test_fail("BLT", "0x1004", f"0x{cpu.pc:08x}")


def test_blt_negative_less_than_positive(runner):
    """BLT: negative < positive - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(7, 0xFFFFFFFF)  # -1 in signed
    cpu.write_reg(8, 1)
    
    # BLT x7, x8, 200 (-1 < 1)
    insn = encode_b_type(0b100, 7, 8, 200)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x10C8:  # 0x1000 + 200
        runner.test_fail("BLT", "0x10C8", f"0x{cpu.pc:08x}")


def test_blt_positive_not_less_than_negative(runner):
    """BLT: positive not < negative - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(9, 1)
    cpu.write_reg(10, 0xFFFFFFFF)  # -1
    
    # BLT x9, x10, 100 (1 not < -1)
    insn = encode_b_type(0b100, 9, 10, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("BLT", "0x1004", f"0x{cpu.pc:08x}")


def test_blt_max_negative_less_than_zero(runner):
    """BLT: max negative < 0 - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(11, 0x80000000)  # -2147483648
    cpu.write_reg(12, 0)
    
    # BLT x11, x12, 80 (-2147483648 < 0)
    insn = encode_b_type(0b100, 11, 12, 80)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1050:  # 0x1000 + 80
        runner.test_fail("BLT", "0x1050", f"0x{cpu.pc:08x}")


def test_blt_zero_less_than_max_positive(runner):
    """BLT: 0 < max positive - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(13, 0)
    cpu.write_reg(14, 0x7FFFFFFF)  # 2147483647
    
    # BLT x13, x14, 60 (0 < 2147483647)
    insn = encode_b_type(0b100, 13, 14, 60)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x103C:  # 0x1000 + 60
        runner.test_fail("BLT", "0x103C", f"0x{cpu.pc:08x}")


def test_blt_negative_comparison(runner):
    """BLT: compare two negative numbers"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(15, 0xFFFFFFFE)  # -2
    cpu.write_reg(16, 0xFFFFFFFF)  # -1
    
    # BLT x15, x16, 50 (-2 < -1)
    insn = encode_b_type(0b100, 15, 16, 50)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1032:  # 0x1000 + 50
        runner.test_fail("BLT", "0x1032", f"0x{cpu.pc:08x}")


def test_blt_backward_branch(runner):
    """BLT: backward branch (negative offset)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    cpu.write_reg(17, 42)
    cpu.write_reg(18, 100)
    
    # BLT x17, x18, -100 (42 < 100)
    imm = (-100) & 0x1FFF
    insn = encode_b_type(0b100, 17, 18, imm)
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0x2000 - 100) & 0xFFFFFFFF
    if cpu.pc != expected:
        runner.test_fail("BLT", f"0x{expected:08x}", f"0x{cpu.pc:08x}")


def test_blt_same_register_not_taken(runner):
    """BLT: rs1 = rs2 (same register, not less than itself)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(19, 0xDEADBEEF)
    
    # BLT x19, x19, 64
    insn = encode_b_type(0b100, 19, 19, 64)
    
    execute_instruction(cpu, mem, insn)
    
    # Same value, not less than, branch not taken
    if cpu.pc != 0x1004:
        runner.test_fail("BLT", "0x1004", f"0x{cpu.pc:08x}")


def test_blt_compare_to_x0(runner):
    """BLT: compare negative to x0 (< 0) - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(20, 0xFFFFFFF0)  # -16
    
    # BLT x20, x0, 32 (-16 < 0)
    insn = encode_b_type(0b100, 20, 0, 32)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1020:  # 0x1000 + 32
        runner.test_fail("BLT", "0x1020", f"0x{cpu.pc:08x}")


def test_blt_max_negative_less_than_max_positive(runner):
    """BLT: max negative < max positive - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(21, 0x80000000)  # -2147483648
    cpu.write_reg(22, 0x7FFFFFFF)  # 2147483647
    
    # BLT x21, x22, 100
    insn = encode_b_type(0b100, 21, 22, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1064:
        runner.test_fail("BLT", "0x1064", f"0x{cpu.pc:08x}")


def test_blt_max_forward_offset(runner):
    """BLT: maximum forward offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(23, 10)
    cpu.write_reg(24, 20)
    
    # BLT x23, x24, 4094
    insn = encode_b_type(0b100, 23, 24, 4094)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1FFE:  # 0x1000 + 4094
        runner.test_fail("BLT", "0x1FFE", f"0x{cpu.pc:08x}")
