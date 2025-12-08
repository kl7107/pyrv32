#!/usr/bin/env python3
"""
Test EBREAK instruction
EBREAK raises an exception to enter the debugger
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction
from exceptions import EBreakException


def test_ebreak_basic(runner):
    """EBREAK: raises EBreakException"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80000100
    
    # EBREAK instruction: imm=1, funct3=0, opcode=0b1110011
    # Full encoding: 0x00100073
    insn = 0x00100073
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("EBREAK", "EBreakException", "no exception")
    except EBreakException as e:
        # Expected - check that PC is correct
        if e.pc != 0x80000100:
            runner.test_fail("EBREAK PC", "0x80000100", f"0x{e.pc:08x}")


def test_ebreak_pc_preserved(runner):
    """EBREAK: PC is preserved in exception"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80001234
    
    insn = 0x00100073
    
    try:
        execute_instruction(cpu, mem, insn)
        runner.test_fail("EBREAK", "EBreakException", "no exception")
    except EBreakException as e:
        if e.pc != 0x80001234:
            runner.test_fail("EBREAK PC", "0x80001234", f"0x{e.pc:08x}")


def test_ebreak_not_ecall(runner):
    """EBREAK: different from ECALL"""
    cpu = RV32CPU()
    mem = Memory()
    
    # ECALL is 0x00000073, EBREAK is 0x00100073
    from exceptions import ECallException
    
    # Test ECALL
    cpu.pc = 0x80000100
    ecall_insn = 0x00000073
    try:
        execute_instruction(cpu, mem, ecall_insn)
    except ECallException:
        pass  # Expected
    except EBreakException:
        runner.test_fail("ECALL", "ECallException", "EBreakException")
    
    # Test EBREAK
    cpu.pc = 0x80000100
    ebreak_insn = 0x00100073
    try:
        execute_instruction(cpu, mem, ebreak_insn)
    except EBreakException:
        pass  # Expected
    except ECallException:
        runner.test_fail("EBREAK", "EBreakException", "ECallException")


def test_ebreak_registers_unchanged(runner):
    """EBREAK: registers are not modified"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Set some register values
    for i in range(1, 32):
        cpu.write_reg(i, i * 0x1000)
    
    cpu.pc = 0x80000100
    insn = 0x00100073
    
    try:
        execute_instruction(cpu, mem, insn)
    except EBreakException:
        pass
    
    # Verify registers unchanged
    for i in range(1, 32):
        expected = i * 0x1000
        got = cpu.read_reg(i)
        if got != expected:
            runner.test_fail(f"EBREAK x{i}", f"0x{expected:08x}", f"0x{got:08x}")
            return


# Test runner class
class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        
    def test_fail(self, test_name, expected, got):
        print(f"FAIL: {test_name}: expected {expected}, got {got}")
        self.failed += 1


def run_all_tests():
    runner = TestRunner()
    
    tests = [
        test_ebreak_basic,
        test_ebreak_pc_preserved,
        test_ebreak_not_ecall,
        test_ebreak_registers_unchanged,
    ]
    
    for test in tests:
        try:
            test(runner)
            runner.passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            runner.failed += 1
    
    print(f"\nEBREAK Tests: {runner.passed} passed, {runner.failed} failed")
    return runner.failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
