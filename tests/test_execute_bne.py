#!/usr/bin/env python3
"""
Test BNE (Branch if Not Equal) instruction
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
    # Split into imm[12] imm[10:5] (bits 31:25) and imm[4:1] imm[11] (bits 11:7)
    imm_12 = (imm >> 12) & 0x1
    imm_10_5 = (imm >> 5) & 0x3F
    imm_4_1 = (imm >> 1) & 0xF
    imm_11 = (imm >> 11) & 0x1
    
    opcode = 0b1100011
    return ((imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | 
            (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode)


def test_bne_not_equal_taken(runner):
    """BNE: unequal values - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 0x12345678)
    cpu.write_reg(6, 0x12345679)
    
    # BNE x5, x6, 100 (forward branch)
    insn = encode_b_type(0b001, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch taken: PC = 0x1000 + 100 = 0x1064
    if cpu.pc != 0x1064:
        runner.test_fail("BNE", "0x1064", f"0x{cpu.pc:08x}")


def test_bne_equal_not_taken(runner):
    """BNE: equal values - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 0x12345678)
    cpu.write_reg(6, 0x12345678)
    
    # BNE x5, x6, 100
    insn = encode_b_type(0b001, 5, 6, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch not taken: PC = 0x1000 + 4 = 0x1004
    if cpu.pc != 0x1004:
        runner.test_fail("BNE", "0x1004", f"0x{cpu.pc:08x}")


def test_bne_zero_vs_nonzero(runner):
    """BNE: zero vs non-zero - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    cpu.write_reg(7, 0)
    cpu.write_reg(8, 1)
    
    # BNE x7, x8, 200
    insn = encode_b_type(0b001, 7, 8, 200)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x20C8:  # 0x2000 + 200
        runner.test_fail("BNE", "0x20C8", f"0x{cpu.pc:08x}")


def test_bne_small_difference(runner):
    """BNE: small difference (1) - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(9, 100)
    cpu.write_reg(10, 101)
    
    # BNE x9, x10, 50
    insn = encode_b_type(0b001, 9, 10, 50)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1032:  # 0x1000 + 50
        runner.test_fail("BNE", "0x1032", f"0x{cpu.pc:08x}")


def test_bne_max_difference(runner):
    """BNE: maximum difference (0 vs 0xFFFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(11, 0)
    cpu.write_reg(12, 0xFFFFFFFF)
    
    # BNE x11, x12, 80
    insn = encode_b_type(0b001, 11, 12, 80)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1050:  # 0x1000 + 80
        runner.test_fail("BNE", "0x1050", f"0x{cpu.pc:08x}")


def test_bne_backward_branch(runner):
    """BNE: backward branch (negative offset)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    cpu.write_reg(13, 42)
    cpu.write_reg(14, 43)
    
    # BNE x13, x14, -100 (backward)
    imm = (-100) & 0x1FFF  # 13-bit immediate (must be even)
    insn = encode_b_type(0b001, 13, 14, imm)
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0x2000 - 100) & 0xFFFFFFFF
    if cpu.pc != expected:
        runner.test_fail("BNE", f"0x{expected:08x}", f"0x{cpu.pc:08x}")


def test_bne_zero_offset(runner):
    """BNE: zero offset (infinite loop if taken)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x3000
    cpu.write_reg(15, 100)
    cpu.write_reg(16, 200)
    
    # BNE x15, x16, 0 (branch to self)
    insn = encode_b_type(0b001, 15, 16, 0)
    
    execute_instruction(cpu, mem, insn)
    
    # Branch taken with offset 0: PC stays at 0x3000
    if cpu.pc != 0x3000:
        runner.test_fail("BNE", "0x3000", f"0x{cpu.pc:08x}")


def test_bne_same_register_not_taken(runner):
    """BNE: rs1 = rs2 = same register (always equal, never branch)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(17, 0xDEADBEEF)
    
    # BNE x17, x17, 64
    insn = encode_b_type(0b001, 17, 17, 64)
    
    execute_instruction(cpu, mem, insn)
    
    # Same register always equal, branch not taken
    if cpu.pc != 0x1004:
        runner.test_fail("BNE", "0x1004", f"0x{cpu.pc:08x}")


def test_bne_compare_to_x0(runner):
    """BNE: compare non-zero to x0 - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(18, 42)
    
    # BNE x18, x0, 32 (check if x18 != 0)
    insn = encode_b_type(0b001, 18, 0, 32)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1020:  # 0x1000 + 32
        runner.test_fail("BNE", "0x1020", f"0x{cpu.pc:08x}")


def test_bne_max_forward_offset(runner):
    """BNE: maximum forward offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(19, 0xABCD)
    cpu.write_reg(20, 0xABCE)
    
    # BNE x19, x20, 4094 (max positive offset)
    insn = encode_b_type(0b001, 19, 20, 4094)
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1FFE:  # 0x1000 + 4094
        runner.test_fail("BNE", "0x1FFE", f"0x{cpu.pc:08x}")


def test_bne_max_backward_offset(runner):
    """BNE: maximum backward offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x5000
    cpu.write_reg(21, 999)
    cpu.write_reg(22, 1000)
    
    # BNE x21, x22, -4096 (max negative offset)
    imm = (-4096) & 0x1FFF
    insn = encode_b_type(0b001, 21, 22, imm)
    
    execute_instruction(cpu, mem, insn)
    
    expected = (0x5000 - 4096) & 0xFFFFFFFF
    if cpu.pc != expected:
        runner.test_fail("BNE", f"0x{expected:08x}", f"0x{cpu.pc:08x}")


def test_bne_different_signs(runner):
    """BNE: positive vs negative - branch taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(23, 0x7FFFFFFF)  # Max positive
    cpu.write_reg(24, 0x80000000)  # Max negative
    
    # BNE x23, x24, 100
    insn = encode_b_type(0b001, 23, 24, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Not equal, branch taken
    if cpu.pc != 0x1064:
        runner.test_fail("BNE", "0x1064", f"0x{cpu.pc:08x}")


def test_bne_both_zero_not_taken(runner):
    """BNE: both zero - branch not taken"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(25, 0)
    cpu.write_reg(26, 0)
    
    # BNE x25, x26, 100
    insn = encode_b_type(0b001, 25, 26, 100)
    
    execute_instruction(cpu, mem, insn)
    
    # Both zero means equal, branch not taken
    if cpu.pc != 0x1004:
        runner.test_fail("BNE", "0x1004", f"0x{cpu.pc:08x}")
