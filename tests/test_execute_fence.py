#!/usr/bin/env python3
"""
Test FENCE instruction
FENCE is a memory ordering instruction that is a no-op in single-core systems
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_fence_basic(runner):
    """FENCE: basic fence instruction (no-op)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 0x12345678)
    
    # FENCE instruction: opcode=0b0001111, funct3=0b000
    # fm(4) pred(4) succ(4) rs1(5) funct3(3) rd(5) opcode(7)
    # All zeros for simplest fence
    insn = 0b0001111
    
    execute_instruction(cpu, mem, insn)
    
    # Should be a no-op, only PC increments
    if cpu.pc != 0x1004:
        runner.test_fail("FENCE", "0x1004", f"0x{cpu.pc:08x}")
    
    # Register unchanged
    if cpu.read_reg(5) != 0x12345678:
        runner.test_fail("FENCE", "0x12345678", f"0x{cpu.read_reg(5):08x}")


def test_fence_all_fields(runner):
    """FENCE: with all ordering bits set"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x2000
    
    # FENCE with pred=0xF, succ=0xF (iorw, iorw)
    # fm=0, pred=1111, succ=1111, rs1=0, funct3=000, rd=0, opcode=0001111
    fm = 0
    pred = 0xF  # iorw
    succ = 0xF  # iorw
    rs1 = 0
    funct3 = 0b000
    rd = 0
    opcode = 0b0001111
    
    insn = (fm << 28) | (pred << 24) | (succ << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x2004:
        runner.test_fail("FENCE", "0x2004", f"0x{cpu.pc:08x}")


def test_fence_memory_unchanged(runner):
    """FENCE: memory remains unchanged"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80000000  # Valid RAM address
    mem.write_word(0x80003000, 0xDEADBEEF)  # Valid RAM address
    
    # FENCE
    insn = 0b0001111
    
    execute_instruction(cpu, mem, insn)
    
    # Memory should be unchanged
    if mem.read_word(0x80003000) != 0xDEADBEEF:
        runner.test_fail("FENCE", "0xDEADBEEF", f"0x{mem.read_word(0x80003000):08x}")


def test_fence_registers_unchanged(runner):
    """FENCE: all registers remain unchanged"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    # Set multiple registers
    for i in range(1, 32):
        cpu.write_reg(i, i * 0x1000)
    
    # FENCE
    insn = 0b0001111
    
    execute_instruction(cpu, mem, insn)
    
    # All registers should be unchanged
    for i in range(1, 32):
        expected = i * 0x1000
        if cpu.read_reg(i) != expected:
            runner.test_fail("FENCE", f"x{i}={expected}", f"x{i}={cpu.read_reg(i)}")
            break


def test_fence_fence_i(runner):
    """FENCE: FENCE.I (instruction fence, fm=0b0001)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # FENCE.I: fm=0b0001, rest zeros
    fm = 0b0001
    insn = (fm << 28) | 0b0001111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("FENCE", "0x1004", f"0x{cpu.pc:08x}")


def test_fence_different_pred_succ(runner):
    """FENCE: different predecessor/successor combinations"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Test pred=r, succ=w
    cpu.pc = 0x1000
    pred = 0b0010  # r (read)
    succ = 0b0001  # w (write)
    insn = (pred << 24) | (succ << 20) | 0b0001111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x1004:
        runner.test_fail("FENCE", "0x1004", f"0x{cpu.pc:08x}")


def test_fence_pc_only_increment(runner):
    """FENCE: verify only PC changes"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80000000  # Valid RAM address
    cpu.write_reg(10, 0xAAAAAAAA)
    cpu.write_reg(20, 0xBBBBBBBB)
    mem.write_word(0x80006000, 0xCCCCCCCC)  # Valid RAM address
    
    # FENCE
    insn = 0b0001111
    
    old_pc = cpu.pc
    execute_instruction(cpu, mem, insn)
    
    # Only PC should change
    if cpu.pc != old_pc + 4:
        runner.test_fail("FENCE", f"0x{old_pc + 4:08x}", f"0x{cpu.pc:08x}")
    if cpu.read_reg(10) != 0xAAAAAAAA:
        runner.test_fail("FENCE", "0xAAAAAAAA", f"0x{cpu.read_reg(10):08x}")
    if cpu.read_reg(20) != 0xBBBBBBBB:
        runner.test_fail("FENCE", "0xBBBBBBBB", f"0x{cpu.read_reg(20):08x}")
    if mem.read_word(0x80006000) != 0xCCCCCCCC:
        runner.test_fail("FENCE", "0xCCCCCCCC", f"0x{mem.read_word(0x80006000):08x}")
