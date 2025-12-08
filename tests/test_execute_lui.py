#!/usr/bin/env python3
"""
Test LUI (Load Upper Immediate) instruction
Tests cover all edge cases documented in execute.py exec_lui docstring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_lui_basic(runner):
    """LUI: basic load upper immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    # LUI x5, 0x12345 - rd = 0x12345000
    imm = 0x12345
    insn = (imm << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(5)
    expected = 0x12345000
    if result != expected:
        runner.test_fail("LUI", f"0x{expected:08x}", f"0x{result:08x}")


def test_lui_zero_imm(runner):
    """LUI: zero immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    # LUI x5, 0 - rd = 0
    insn = (0 << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(5)
    if result != 0:
        runner.test_fail("LUI zero", "0", f"0x{result:08x}")


def test_lui_max_positive(runner):
    """LUI: maximum positive immediate (0x7FFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    # LUI x5, 0x7FFFF - rd = 0x7FFFF000
    imm = 0x7FFFF
    insn = (imm << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(5)
    expected = 0x7FFFF000
    if result != expected:
        runner.test_fail("LUI max positive", f"0x{expected:08x}", f"0x{result:08x}")


def test_lui_high_bit_set(runner):
    """LUI: immediate with bit 19 set (becomes negative when sign-extended)"""
    cpu = RV32CPU()
    mem = Memory()
    
    # LUI x5, 0x80000 - rd = 0x80000000 (negative in signed interpretation)
    imm = 0x80000
    insn = (imm << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(5)
    expected = 0x80000000
    if result != expected:
        runner.test_fail("LUI high bit", f"0x{expected:08x}", f"0x{result:08x}")


def test_lui_all_ones(runner):
    """LUI: all ones immediate (0xFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    # LUI x5, 0xFFFFF - rd = 0xFFFFF000
    imm = 0xFFFFF
    insn = (imm << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(5)
    expected = 0xFFFFF000
    if result != expected:
        runner.test_fail("LUI all ones", f"0x{expected:08x}", f"0x{result:08x}")


def test_lui_x0_ignored(runner):
    """LUI: writing to x0 has no effect"""
    cpu = RV32CPU()
    mem = Memory()
    
    # LUI x0, 0x12345 - should have no effect (x0 always 0)
    imm = 0x12345
    insn = (imm << 12) | (0 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(0)
    if result != 0:
        runner.test_fail("LUI x0", "0", f"0x{result:08x}")


def test_lui_overwrite(runner):
    """LUI: overwrites previous register value"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Set x5 to some value
    cpu.write_reg(5, 0xDEADBEEF)
    
    # LUI x5, 0xABCDE - should completely replace value
    imm = 0xABCDE
    insn = (imm << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(5)
    expected = 0xABCDE000
    if result != expected:
        runner.test_fail("LUI overwrite", f"0x{expected:08x}", f"0x{result:08x}")


def test_lui_pc_advance(runner):
    """LUI: PC advances by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.pc = 0x80000100
    
    # LUI x5, 0x12345
    imm = 0x12345
    insn = (imm << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != 0x80000104:
        runner.test_fail("LUI PC", "0x80000104", f"0x{cpu.pc:08x}")


def test_lui_all_registers(runner):
    """LUI: works with all destination registers"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Test all registers x1-x31 (skip x0)
    for rd in range(1, 32):
        imm = rd  # Use register number as immediate
        insn = (imm << 12) | (rd << 7) | 0b0110111
        
        execute_instruction(cpu, mem, insn)
        
        result = cpu.read_reg(rd)
        expected = rd << 12
        if result != expected:
            runner.test_fail(f"LUI x{rd}", f"0x{expected:08x}", f"0x{result:08x}")
            return


def test_lui_addi_combo(runner):
    """LUI: commonly used with ADDI to load 32-bit constant"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Load 0x12345678 into x5 using LUI + ADDI
    # LUI x5, 0x12345 -> x5 = 0x12345000
    # Then ADDI x5, x5, 0x678 -> x5 = 0x12345678
    # But if lower 12 bits >= 0x800, need to adjust
    
    # For 0x12345678: upper = 0x12345, lower = 0x678
    lui_imm = 0x12345
    insn = (lui_imm << 12) | (5 << 7) | 0b0110111
    
    execute_instruction(cpu, mem, insn)
    
    result = cpu.read_reg(5)
    expected = 0x12345000
    if result != expected:
        runner.test_fail("LUI for combo", f"0x{expected:08x}", f"0x{result:08x}")


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
        test_lui_basic,
        test_lui_zero_imm,
        test_lui_max_positive,
        test_lui_high_bit_set,
        test_lui_all_ones,
        test_lui_x0_ignored,
        test_lui_overwrite,
        test_lui_pc_advance,
        test_lui_all_registers,
        test_lui_addi_combo,
    ]
    
    for test in tests:
        try:
            test(runner)
            runner.passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            runner.failed += 1
    
    print(f"\nLUI Tests: {runner.passed} passed, {runner.failed} failed")
    return runner.failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
