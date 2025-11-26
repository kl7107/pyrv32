#!/usr/bin/env python3
"""
Test BLTU (Branch if Less Than - Unsigned) instruction
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


def test_bltu_less_than_taken(runner):
    """BLTU: rs1 < rs2 (unsigned) - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 200)
    
    # BLTU x5, x6, 100 (100 < 200 unsigned)
    insn = encode_b_type(0b110, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch taken: PC = 0x1000 + 100 = 0x1064
    if cpu.pc != 0x1064:
        runner.test_fail("BLTU", "0x1064", f"0x{cpu.pc:08x}")


def test_bltu_greater_than_not_taken(runner):
    """BLTU: rs1 > rs2 - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 200)
    cpu.write_reg(6, 100)
    
    # BLTU x5, x6, 100 (200 > 100)
    insn = encode_b_type(0b110, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch not taken: PC = 0x1000 + 4 = 0x1004
    if cpu.pc != 0x1004:
        runner.test_fail("BLTU", "0x1004", f"0x{cpu.pc:08x}")


def test_bltu_equal_not_taken(runner):
    """BLTU: rs1 == rs2 - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 100)
    cpu.write_reg(6, 100)
    
    # BLTU x5, x6, 100
    insn = encode_b_type(0b110, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Not less than (equal), branch not taken
    if cpu.pc != 0x1004:
        runner.test_fail("BLTU", "0x1004", f"0x{cpu.pc:08x}")


def test_bltu_zero_less_than_anything(runner):
    """BLTU: 0 < any positive value - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(7, 0)
    cpu.write_reg(8, 1)
    
    # BLTU x7, x8, 200 (0 < 1)
    insn = encode_b_type(0b110, 7, 8, 200)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x10C8:  # 0x1000 + 200
        runner.test_fail("BLTU", "0x10C8", f"0x{cpu.pc:08x}")


def test_bltu_max_not_less_than_anything(runner):
    """BLTU: 0xFFFFFFFF not < anything - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(9, 0xFFFFFFFF)
    cpu.write_reg(10, 0)
    
    # BLTU x9, x10, 100 (0xFFFFFFFF not < 0)
    insn = encode_b_type(0b110, 9, 10, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("BLTU", "0x1004", f"0x{cpu.pc:08x}")


def test_bltu_small_less_than_max(runner):
    """BLTU: small value < 0xFFFFFFFF - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(11, 100)
    cpu.write_reg(12, 0xFFFFFFFF)
    
    # BLTU x11, x12, 80 (100 < 0xFFFFFFFF)
    insn = encode_b_type(0b110, 11, 12, 80)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1050:  # 0x1000 + 80
        runner.test_fail("BLTU", "0x1050", f"0x{cpu.pc:08x}")


def test_bltu_unsigned_vs_signed_difference(runner):
    """BLTU: 0xFFFFFFFF > 0x7FFFFFFF (unsigned, opposite of signed)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(13, 0x7FFFFFFF)  # Max positive (signed), but less in unsigned
    cpu.write_reg(14, 0xFFFFFFFF)  # Max unsigned
    
    # BLTU x13, x14, 60 (0x7FFFFFFF < 0xFFFFFFFF unsigned)
    insn = encode_b_type(0b110, 13, 14, 60)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x103C:  # 0x1000 + 60
        runner.test_fail("BLTU", "0x103C", f"0x{cpu.pc:08x}")


def test_bltu_boundary_values(runner):
    """BLTU: boundary value comparison"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(15, 0x7FFFFFFF)
    cpu.write_reg(16, 0x80000000)
    
    # BLTU x15, x16, 50 (0x7FFFFFFF < 0x80000000 unsigned)
    insn = encode_b_type(0b110, 15, 16, 50)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1032:  # 0x1000 + 50
        runner.test_fail("BLTU", "0x1032", f"0x{cpu.pc:08x}")


def test_bltu_backward_branch(runner):
    """BLTU: backward branch (negative offset)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    cpu.write_reg(17, 42)
    cpu.write_reg(18, 100)
    
    # BLTU x17, x18, -100 (42 < 100)
    imm = (-100) & 0x1FFF
    insn = encode_b_type(0b110, 17, 18, imm)
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0x2000 - 100) & 0xFFFFFFFF
    if cpu.pc != expected:
        runner.test_fail("BLTU", f"0x{expected:08x}", f"0x{cpu.pc:08x}")


def test_bltu_same_register_not_taken(runner):
    """BLTU: rs1 = rs2 (same register, not less than itself)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(19, 0xDEADBEEF)
    
    # BLTU x19, x19, 64
    insn = encode_b_type(0b110, 19, 19, 64)
    
    execute_instruction(cpu, mem, insn)
    
    # Same value, not less than, branch not taken
    if cpu.pc != 0x1004:
        runner.test_fail("BLTU", "0x1004", f"0x{cpu.pc:08x}")


def test_bltu_compare_to_x0(runner):
    """BLTU: compare 0 to x0 (equal) - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(20, 0)
    
    # BLTU x20, x0, 32 (0 < 0 is false)
    insn = encode_b_type(0b110, 20, 0, 32)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("BLTU", "0x1004", f"0x{cpu.pc:08x}")


def test_bltu_nonzero_vs_x0(runner):
    """BLTU: x0 < non-zero value - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(21, 100)
    
    # BLTU x0, x21, 48 (0 < 100)
    insn = encode_b_type(0b110, 0, 21, 48)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1030:  # 0x1000 + 48
        runner.test_fail("BLTU", "0x1030", f"0x{cpu.pc:08x}")


def test_bltu_max_forward_offset(runner):
    """BLTU: maximum forward offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(22, 10)
    cpu.write_reg(23, 20)
    
    # BLTU x22, x23, 4094
    insn = encode_b_type(0b110, 22, 23, 4094)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1FFE:  # 0x1000 + 4094
        runner.test_fail("BLTU", "0x1FFE", f"0x{cpu.pc:08x}")


def test_bltu_high_bit_unsigned(runner):
    """BLTU: high bit set is large unsigned (not negative)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(24, 0x80000000)  # Large unsigned, not negative
    cpu.write_reg(25, 0x80000001)
    
    # BLTU x24, x25, 100 (0x80000000 < 0x80000001)
    insn = encode_b_type(0b110, 24, 25, 100)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1064:
        runner.test_fail("BLTU", "0x1064", f"0x{cpu.pc:08x}")
