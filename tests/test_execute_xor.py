#!/usr/bin/env python3
"""
Test XOR instruction
Tests cover all edge cases documented in execute.py exec_register_alu docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_xor_same_values_zero(runner):
    """XOR: x ^ x = 0 (same values)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0x12345678
    
    # XOR x3, x1, x2 (funct3=100, funct7=0000000)
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("XOR same values", "0", f"0x{cpu.regs[3]:08X}")


def test_xor_all_ones_all_zeros(runner):
    """XOR: 0xFFFFFFFF ^ 0x00000000 = 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 0x00000000
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("XOR all ones ^ zero", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_xor_identity_zero(runner):
    """XOR: value ^ 0 = value (identity)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xABCDEF01
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xABCDEF01:
        runner.test_fail("XOR identity", "0xABCDEF01", f"0x{cpu.regs[3]:08X}")


def test_xor_bit_patterns(runner):
    """XOR: 0xAAAAAAAA ^ 0x55555555 = 0xFFFFFFFF (complementary bits)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xAAAAAAAA
    cpu.regs[2] = 0x55555555
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0xFFFFFFFF:
        runner.test_fail("XOR bit patterns", "0xFFFFFFFF", f"0x{cpu.regs[3]:08X}")


def test_xor_alternating_bits(runner):
    """XOR: 0xAAAAAAAA ^ 0xAAAAAAAA = 0 (same alternating pattern)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xAAAAAAAA
    cpu.regs[2] = 0xAAAAAAAA
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("XOR alternating bits", "0", f"0x{cpu.regs[3]:08X}")


def test_xor_specific_bits(runner):
    """XOR: 0x12345678 ^ 0x0000FFFF = 0x1234A987"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0x0000FFFF
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    expected = 0x1234A987
    if cpu.regs[3] != expected:
        runner.test_fail("XOR specific bits", f"0x{expected:08X}", f"0x{cpu.regs[3]:08X}")


def test_xor_commutative(runner):
    """XOR: a ^ b = b ^ a (commutative property)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    cpu.regs[2] = 0xABCDEF01
    
    # First: x3 = x1 ^ x2
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    result1 = cpu.regs[3]
    
    # Second: x4 = x2 ^ x1
    insn2 = 0b0000000_00001_00010_100_00100_0110011
    execute_instruction(cpu, mem, insn2)
    result2 = cpu.regs[4]
    
    if result1 != result2:
        runner.test_fail("XOR commutative", f"0x{result1:08X}", f"0x{result2:08X}")


def test_xor_zero_values(runner):
    """XOR: 0 ^ 0 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0
    cpu.regs[2] = 0
    insn = 0b0000000_00010_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("XOR zero ^ zero", "0", f"{cpu.regs[3]}")


def test_xor_rd_equals_x0(runner):
    """XOR: result to x0 (write ignored)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFFFFFF
    cpu.regs[2] = 0x12345678
    insn = 0b0000000_00010_00001_100_00000_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[0] != 0:
        runner.test_fail("XOR to x0", "0", f"{cpu.regs[0]}")


def test_xor_same_register(runner):
    """XOR: x1 ^ x1 = 0 (clear register)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x12345678
    insn = 0b0000000_00001_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0:
        runner.test_fail("XOR same register", "0", f"0x{cpu.regs[3]:08X}")


def test_xor_with_x0(runner):
    """XOR: value ^ x0 = value"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0x87654321
    insn = 0b0000000_00000_00001_100_00011_0110011
    execute_instruction(cpu, mem, insn)
    
    if cpu.regs[3] != 0x87654321:
        runner.test_fail("XOR with x0", "0x87654321", f"0x{cpu.regs[3]:08X}")


def test_xor_rd_equals_rs1(runner):
    """XOR: x1 = x1 ^ x2 (XOR in place)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.regs[1] = 0xFFFF0000
    cpu.regs[2] = 0x00FFFF00
    insn = 0b0000000_00010_00001_100_00001_0110011
    execute_instruction(cpu, mem, insn)
    
    expected = 0xFF00FF00
    if cpu.regs[1] != expected:
        runner.test_fail("XOR rd=rs1", f"0x{expected:08X}", f"0x{cpu.regs[1]:08X}")
