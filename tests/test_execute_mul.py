#!/usr/bin/env python3
"""
Unit tests for MUL instruction (M extension).

MUL performs signed multiplication and returns the lower 32 bits of the result.
Format: MUL rd, rs1, rs2
Encoding: opcode=0110011, funct3=000, funct7=0000001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction

def test_mul_positive_positive(runner):
    """Test MUL with two positive numbers: 2 × 3 = 6"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Set up registers
    cpu.regs[5] = 2
    cpu.regs[6] = 3
    
    # MUL x10, x5, x6 (2 × 3 = 6)
    # opcode=0110011, rd=01010, funct3=000, rs1=00101, rs2=00110, funct7=0000001
    # 0000001_00110_00101_000_01010_0110011
    insn = 0b0000001_00110_00101_000_01010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[10] != 6:
        runner.test_fail("MUL positive×positive result", "6", f"{cpu.regs[10]}")
    if cpu.pc != 4:
        runner.test_fail("MUL PC increment", "4", f"{cpu.pc}")

def test_mul_positive_negative(runner):
    """Test MUL with positive × negative: 2 × -3 = -6"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 2
    cpu.regs[6] = (-3 & 0xFFFFFFFF)  # -3 in 32-bit two's complement
    
    # MUL x11, x5, x6
    insn = 0b0000001_00110_00101_000_01011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = (-6 & 0xFFFFFFFF)  # 0xFFFFFFFA
    if cpu.regs[11] != expected:
        runner.test_fail("MUL positive×negative", f"0x{expected:08X}", f"0x{cpu.regs[11]:08X}")

def test_mul_zero(runner):
    """Test MUL with zero: 0 × 5 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0
    cpu.regs[6] = 5
    
    # MUL x12, x5, x6
    insn = 0b0000001_00110_00101_000_01100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[12] != 0:
        runner.test_fail("MUL with zero", "0", f"{cpu.regs[12]}")

def test_mul_one(runner):
    """Test MUL with one: 1 × 1 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 1
    cpu.regs[6] = 1
    
    # MUL x13, x5, x6
    insn = 0b0000001_00110_00101_000_01101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[13] != 1:
        runner.test_fail("MUL with one", "1", f"{cpu.regs[13]}")

def test_mul_negative_positive(runner):
    """Test MUL with negative × positive: -2 × 1 = -2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-2 & 0xFFFFFFFF)
    cpu.regs[6] = 1
    
    # MUL x14, x5, x6
    insn = 0b0000001_00110_00101_000_01110_0110011
    
    execute_instruction(cpu, mem, insn)
    
    expected = (-2 & 0xFFFFFFFF)  # 0xFFFFFFFE
    if cpu.regs[14] != expected:
        runner.test_fail("MUL negative×positive", f"0x{expected:08X}", f"0x{cpu.regs[14]:08X}")

def test_mul_negative_negative(runner):
    """Test MUL with negative × negative: -1 × -1 = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = (-1 & 0xFFFFFFFF)
    cpu.regs[6] = (-1 & 0xFFFFFFFF)
    
    # MUL x15, x5, x6
    insn = 0b0000001_00110_00101_000_01111_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[15] != 1:
        runner.test_fail("MUL negative×negative", "1", f"{cpu.regs[15]}")

def test_mul_max_positive(runner):
    """Test MUL with max positive: 0x7FFFFFFF × 1 = 0x7FFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x7FFFFFFF  # Max positive 32-bit signed
    cpu.regs[6] = 1
    
    # MUL x16, x5, x6
    insn = 0b0000001_00110_00101_000_10000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[16] != 0x7FFFFFFF:
        runner.test_fail("MUL max positive", "0x7FFFFFFF", f"0x{cpu.regs[16]:08X}")

def test_mul_max_negative(runner):
    """Test MUL with max negative: 0x80000000 × 1 = 0x80000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x80000000  # Min negative 32-bit signed
    cpu.regs[6] = 1
    
    # MUL x17, x5, x6
    insn = 0b0000001_00110_00101_000_10001_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[17] != 0x80000000:
        runner.test_fail("MUL max negative", "0x80000000", f"0x{cpu.regs[17]:08X}")

def test_mul_overflow(runner):
    """Test MUL overflow: 0x10000 × 0x10000 = 0x100000000, lower 32 bits = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0x10000
    cpu.regs[6] = 0x10000
    
    # MUL x18, x5, x6
    insn = 0b0000001_00110_00101_000_10010_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # Result is 0x100000000, lower 32 bits = 0
    if cpu.regs[18] != 0:
        runner.test_fail("MUL overflow", "0", f"0x{cpu.regs[18]:08X}")

def test_mul_large_numbers(runner):
    """Test MUL with large numbers: 0xFFFF × 0x10001"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 0xFFFF
    cpu.regs[6] = 0x10001
    
    # MUL x19, x5, x6
    insn = 0b0000001_00110_00101_000_10011_0110011
    
    execute_instruction(cpu, mem, insn)
    
    # 65535 × 65537 = (65536-1) × (65536+1) = 65536² - 1 = 4294967295 = 0xFFFFFFFF
    expected = 0xFFFFFFFF
    if cpu.regs[19] != expected:
        runner.test_fail("MUL large numbers", f"0x{expected:08X}", f"0x{cpu.regs[19]:08X}")

def test_mul_powers_of_two(runner):
    """Test MUL with powers of two: 8 × 16 = 128"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 8
    cpu.regs[6] = 16
    
    # MUL x20, x5, x6
    insn = 0b0000001_00110_00101_000_10100_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[20] != 128:
        runner.test_fail("MUL powers of two", "128", f"{cpu.regs[20]}")

def test_mul_rd_x0(runner):
    """Test MUL writing to x0 (should remain 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 100
    cpu.regs[6] = 200
    
    # MUL x0, x5, x6 (result discarded)
    insn = 0b0000001_00110_00101_000_00000_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("MUL to x0", "0", f"{cpu.regs[0]}")

def test_mul_same_register(runner):
    """Test MUL with same source registers: x5 × x5"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[5] = 7
    
    # MUL x21, x5, x5 (7 × 7 = 49)
    insn = 0b0000001_00101_00101_000_10101_0110011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[21] != 49:
        runner.test_fail("MUL same register", "49", f"{cpu.regs[21]}")

