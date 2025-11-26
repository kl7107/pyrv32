#!/usr/bin/env python3
"""
Test BGE (Branch if Greater than or Equal - Signed) instruction
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


def test_bge_greater_than_taken(runner):
    """BGE: rs1 > rs2 (signed) - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 200)
    cpu.write_reg(6, 100)
    
    # BGE x5, x6, 100 (200 > 100)
    insn = encode_b_type(0b101, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch taken: PC = 0x1000 + 100 = 0x1064
    if cpu.pc != 0x1064:
        runner.test_fail("BGE", "0x1064", f"0x{cpu.pc:08x}")


def test_bge_equal_taken(runner):
    """BGE: rs1 == rs2 - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 100)
    
    # BGE x5, x6, 100
    insn = encode_b_type(0b101, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Equal means >=, branch taken
    if cpu.pc != 0x1064:
        runner.test_fail("BGE", "0x1064", f"0x{cpu.pc:08x}")


def test_bge_less_than_not_taken(runner):
    """BGE: rs1 < rs2 - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 200)
    
    # BGE x5, x6, 100 (100 < 200)
    insn = encode_b_type(0b101, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch not taken: PC = 0x1000 + 4 = 0x1004
    if cpu.pc != 0x1004:
        runner.test_fail("BGE", "0x1004", f"0x{cpu.pc:08x}")


def test_bge_positive_greater_than_negative(runner):
    """BGE: positive >= negative - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(7, 1)
    cpu.write_reg(8, 0xFFFFFFFF)  # -1 in signed
    
    # BGE x7, x8, 200 (1 >= -1)
    insn = encode_b_type(0b101, 7, 8, 200)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x10C8:  # 0x1000 + 200
        runner.test_fail("BGE", "0x10C8", f"0x{cpu.pc:08x}")


def test_bge_negative_not_greater_than_positive(runner):
    """BGE: negative not >= positive - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(9, 0xFFFFFFFF)  # -1
    cpu.write_reg(10, 1)
    
    # BGE x9, x10, 100 (-1 not >= 1)
    insn = encode_b_type(0b101, 9, 10, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("BGE", "0x1004", f"0x{cpu.pc:08x}")


def test_bge_zero_greater_than_max_negative(runner):
    """BGE: 0 >= max negative - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(11, 0)
    cpu.write_reg(12, 0x80000000)  # -2147483648
    
    # BGE x11, x12, 80 (0 >= -2147483648)
    insn = encode_b_type(0b101, 11, 12, 80)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1050:  # 0x1000 + 80
        runner.test_fail("BGE", "0x1050", f"0x{cpu.pc:08x}")


def test_bge_max_positive_greater_than_zero(runner):
    """BGE: max positive >= 0 - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(13, 0x7FFFFFFF)  # 2147483647
    cpu.write_reg(14, 0)
    
    # BGE x13, x14, 60 (2147483647 >= 0)
    insn = encode_b_type(0b101, 13, 14, 60)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x103C:  # 0x1000 + 60
        runner.test_fail("BGE", "0x103C", f"0x{cpu.pc:08x}")


def test_bge_negative_comparison(runner):
    """BGE: compare two negative numbers (-1 >= -2)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(15, 0xFFFFFFFF)  # -1
    cpu.write_reg(16, 0xFFFFFFFE)  # -2
    
    # BGE x15, x16, 50 (-1 >= -2)
    insn = encode_b_type(0b101, 15, 16, 50)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1032:  # 0x1000 + 50
        runner.test_fail("BGE", "0x1032", f"0x{cpu.pc:08x}")


def test_bge_backward_branch(runner):
    """BGE: backward branch (negative offset)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    cpu.write_reg(17, 100)
    cpu.write_reg(18, 42)
    
    # BGE x17, x18, -100 (100 >= 42)
    imm = (-100) & 0x1FFF
    insn = encode_b_type(0b101, 17, 18, imm)
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0x2000 - 100) & 0xFFFFFFFF
    if cpu.pc != expected:
        runner.test_fail("BGE", f"0x{expected:08x}", f"0x{cpu.pc:08x}")


def test_bge_same_register_taken(runner):
    """BGE: rs1 = rs2 (same register, always >=)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(19, 0xDEADBEEF)
    
    # BGE x19, x19, 64
    insn = encode_b_type(0b101, 19, 19, 64)
    
    execute_instruction(cpu, mem, insn)
    
    # Same value, always >=, branch taken
    if cpu.pc != 0x1040:  # 0x1000 + 64
        runner.test_fail("BGE", "0x1040", f"0x{cpu.pc:08x}")


def test_bge_compare_to_x0_positive(runner):
    """BGE: compare positive to x0 (>= 0) - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(20, 100)
    
    # BGE x20, x0, 32 (100 >= 0)
    insn = encode_b_type(0b101, 20, 0, 32)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1020:  # 0x1000 + 32
        runner.test_fail("BGE", "0x1020", f"0x{cpu.pc:08x}")


def test_bge_compare_to_x0_negative(runner):
    """BGE: compare negative to x0 (< 0) - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(21, 0xFFFFFFF0)  # -16
    
    # BGE x21, x0, 32 (-16 not >= 0)
    insn = encode_b_type(0b101, 21, 0, 32)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("BGE", "0x1004", f"0x{cpu.pc:08x}")


def test_bge_max_positive_greater_than_max_negative(runner):
    """BGE: max positive >= max negative - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(22, 0x7FFFFFFF)  # 2147483647
    cpu.write_reg(23, 0x80000000)  # -2147483648
    
    # BGE x22, x23, 100
    insn = encode_b_type(0b101, 22, 23, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1064:
        runner.test_fail("BGE", "0x1064", f"0x{cpu.pc:08x}")


def test_bge_max_forward_offset(runner):
    """BGE: maximum forward offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(24, 20)
    cpu.write_reg(25, 10)
    
    # BGE x24, x25, 4094
    insn = encode_b_type(0b101, 24, 25, 4094)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1FFE:  # 0x1000 + 4094
        runner.test_fail("BGE", "0x1FFE", f"0x{cpu.pc:08x}")


def test_bge_zero_offset_loop(runner):
    """BGE: zero offset infinite loop"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x3000
    cpu.write_reg(26, 50)
    cpu.write_reg(27, 50)
    
    # BGE x26, x27, 0 (infinite loop on equal)
    insn = encode_b_type(0b101, 26, 27, 0)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x3000:
        runner.test_fail("BGE", "0x3000", f"0x{cpu.pc:08x}")
