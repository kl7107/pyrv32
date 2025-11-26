#!/usr/bin/env python3
"""
Test JAL (Jump And Link) instruction
Tests cover all edge cases documented in execute.py exec_jal docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_jal_forward_jump(runner):
    """JAL: forward jump with positive offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x1, 100 - Jump forward by 100 bytes
    # J-Type: imm[20|10:1|11|19:12] encoded in bits [31:12]
    # Offset 100 = 0x64, need to encode in J-Type format
    imm = 100
    # J-Type immediate encoding: [20][10:1][11][19:12]
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1064:
        runner.test_fail("JAL", "0x1064", f"0x{cpu.pc:08x}")
    if cpu.read_reg(1) != 0x1004:
        runner.test_fail("JAL", "0x1004", f"0x{cpu.read_reg(1):08x}")


def test_jal_backward_jump(runner):
    """JAL: backward jump with negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    
    # JAL x1, -100 - Jump backward by 100 bytes
    imm = -100 & 0xFFFFFFFF  # Two's complement
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x2000 - 100 = 0x2000 - 0x64 = 0x1F9C
    if cpu.pc != 0x1F9C:
        runner.test_fail("JAL", "0x1F9C", f"0x{cpu.pc:08x}")


def test_jal_zero_offset(runner):
    """JAL: zero offset (save PC+4 without jumping)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x5, 0 - Save PC+4 to x5, continue to next instruction
    insn = (0 << 12) | (5 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1000:
        runner.test_fail("JAL", "0x1000", f"0x{cpu.pc:08x}")
    if cpu.read_reg(5) != 0x1004:
        runner.test_fail("JAL", "0x1004", f"0x{cpu.read_reg(5):08x}")


def test_jal_min_offset(runner):
    """JAL: minimum offset (jump to next instruction: offset=4)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x1, 4 - Jump to next instruction
    imm = 4
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("JAL", "0x1004", f"0x{cpu.pc:08x}")


def test_jal_rd_x0(runner):
    """JAL: unconditional jump with rd=x0 (discard return address)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x0, 200 - Unconditional jump, no return address saved
    imm = 200
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (0 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x10C8:
        runner.test_fail("JAL", "0x10C8", f"0x{cpu.pc:08x}")
    if cpu.read_reg(0) != 0:
        runner.test_fail("JAL", "0", f"{cpu.read_reg(0)}")


def test_jal_function_call(runner):
    """JAL: typical function call (save return in x1/ra)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x1, 1024 - Call function at offset 1024
    imm = 1024
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1400:
        runner.test_fail("JAL", "0x1400", f"0x{cpu.pc:08x}")
    if cpu.read_reg(1) != 0x1004:
        runner.test_fail("JAL", "0x1004", f"0x{cpu.read_reg(1):08x}")


def test_jal_alternate_link(runner):
    """JAL: save return in alternate register (x5/t0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x5, 512
    imm = 512
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (5 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1200:
        runner.test_fail("JAL", "0x1200", f"0x{cpu.pc:08x}")
    if cpu.read_reg(5) != 0x1004:
        runner.test_fail("JAL", "0x1004", f"0x{cpu.read_reg(5):08x}")


def test_jal_large_forward(runner):
    """JAL: large forward jump"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x1, 0x10000 (65536 bytes)
    imm = 0x10000
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x11000:
        runner.test_fail("JAL", "0x11000", f"0x{cpu.pc:08x}")


def test_jal_large_backward(runner):
    """JAL: large backward jump"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x20000
    
    # JAL x1, -0x10000 (-65536 bytes)
    imm = (-0x10000) & 0xFFFFFFFF
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x20000 - 0x10000 = 0x10000
    if cpu.pc != 0x10000:
        runner.test_fail("JAL", "0x10000", f"0x{cpu.pc:08x}")


def test_jal_misaligned_offset(runner):
    """JAL: offset not multiple of 4 (but multiple of 2 is valid)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x1, 6 - Jump by 6 bytes (valid for RISC-V, though unusual)
    imm = 6
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1006:
        runner.test_fail("JAL", "0x1006", f"0x{cpu.pc:08x}")


def test_jal_wraparound(runner):
    """JAL: PC wraparound at 32-bit boundary"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0xFFFFFFF0
    
    # JAL x1, 32 - Should wrap: 0xFFFFFFF0 + 32 = 0x00000010
    imm = 32
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x00000010:
        runner.test_fail("JAL", "0x00000010", f"0x{cpu.pc:08x}")
    if cpu.read_reg(1) != 0xFFFFFFF4:
        runner.test_fail("JAL", "0xFFFFFFF4", f"0x{cpu.read_reg(1):08x}")


def test_jal_negative_small(runner):
    """JAL: small negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # JAL x1, -4 - Jump backward by 4 bytes
    imm = (-4) & 0xFFFFFFFF
    imm_bits = ((imm >> 20) & 0x1) << 31 | \
                ((imm >> 1) & 0x3FF) << 21 | \
                ((imm >> 11) & 0x1) << 20 | \
                ((imm >> 12) & 0xFF) << 12
    insn = imm_bits | (1 << 7) | 0b1101111
    
    execute_instruction(cpu, mem, insn)
    
    # 0x1000 - 4 = 0x0FFC
    if cpu.pc != 0x0FFC:
        runner.test_fail("JAL", "0x0FFC", f"0x{cpu.pc:08x}")
