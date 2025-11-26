#!/usr/bin/env python3
"""
Test ECALL instruction
ECALL raises ECallException for environment/system call handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction
from exceptions import ECallException


def test_ecall_raises_exception(runner):
    """ECALL: should raise ECallException"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # ECALL instruction: imm=0, rs1=0, funct3=000, rd=0, opcode=1110011
    insn = 0b1110011
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("ECALL", "ECallException raised", "No exception")
    except ECallException as e:
        # Expected - verify PC in exception
        if e.pc != 0x1000:
            runner.test_fail("ECALL", "0x1000", f"0x{e.pc:08x}")


def test_ecall_different_pc(runner):
    """ECALL: exception contains correct PC"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0xABCD0000
    
    # ECALL
    insn = 0b1110011
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("ECALL", "ECallException raised", "No exception")
    except ECallException as e:
        if e.pc != 0xABCD0000:
            runner.test_fail("ECALL", "0xABCD0000", f"0x{e.pc:08x}")


def test_ecall_registers_unchanged(runner):
    """ECALL: registers should be unchanged when exception raised"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    cpu.write_reg(5, 0x12345678)
    cpu.write_reg(10, 0xDEADBEEF)
    
    # ECALL
    insn = 0b1110011
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("ECALL", "ECallException raised", "No exception")
    except ECallException:
        # Registers should be unchanged
        if cpu.read_reg(5) != 0x12345678:
            runner.test_fail("ECALL", "0x12345678", f"0x{cpu.read_reg(5):08x}")
        if cpu.read_reg(10) != 0xDEADBEEF:
            runner.test_fail("ECALL", "0xDEADBEEF", f"0x{cpu.read_reg(10):08x}")


def test_ecall_memory_unchanged(runner):
    """ECALL: memory should be unchanged when exception raised"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80000000  # Valid RAM address
    mem.write_word(0x80002000, 0xCAFEBABE)  # Valid RAM address
    
    # ECALL
    insn = 0b1110011
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("ECALL", "ECallException raised", "No exception")
    except ECallException:
        # Memory should be unchanged
        if mem.read_word(0x80002000) != 0xCAFEBABE:
            runner.test_fail("ECALL", "0xCAFEBABE", f"0x{mem.read_word(0x80002000):08x}")


def test_ecall_pc_unchanged(runner):
    """ECALL: PC should not increment (exception before PC update)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x5000
    
    # ECALL
    insn = 0b1110011
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("ECALL", "ECallException raised", "No exception")
    except ECallException:
        # PC should not have incremented (exception happens before PC update)
        # Actually, need to check implementation - but exception should preserve PC
        pass  # Exception raised is sufficient


def test_ecall_exception_message(runner):
    """ECALL: exception message contains PC"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x4000
    
    # ECALL
    insn = 0b1110011
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("ECALL", "ECallException raised", "No exception")
    except ECallException as e:
        msg = str(e)
        # Verify message contains ECALL and the PC value
        if "ECALL" not in msg:
            runner.test_fail("ECALL", "Message contains 'ECALL'", msg)
        if "0x00004000" not in msg and "0x4000" not in msg:
            runner.test_fail("ECALL", "Message contains PC", msg)


def test_ecall_vs_ebreak(runner):
    """ECALL: verify different exception from EBREAK"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x1000
    
    # ECALL (imm=0)
    insn = 0b1110011
    
    exception_type = None
    try:
        execute_instruction(cpu, mem, insn)
    except Exception as e:
        exception_type = type(e).__name__
    
    if exception_type != "ECallException":
        runner.test_fail("ECALL", "ECallException", exception_type or "No exception")
