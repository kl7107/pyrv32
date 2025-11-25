#!/usr/bin/env python3
"""
Assembly Test Runner for pyrv32

Runs assembly tests and verifies their output against expected values
embedded in the source files.
"""

import sys
import os
import re
import argparse
from pathlib import Path

# Add parent directory to path for pyrv32 imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cpu import RV32CPU
from memory import Memory
from decoder import decode_instruction
from execute import execute_instruction


class TestMetadata:
    """Metadata extracted from test source file"""
    def __init__(self, source_path):
        self.source_path = source_path
        self.test_name = None
        self.description = None
        self.expected_output = None
        self.expected_regs = {}
        self.expected_exit = 0
        self.expected_pc = None
        
        self._parse_metadata()
    
    def _parse_metadata(self):
        """Parse metadata from assembly source file"""
        with open(self.source_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('#'):
                    continue
                
                # Remove leading '#' and whitespace
                line = line[1:].strip()
                
                if line.startswith('TEST:'):
                    self.test_name = line[5:].strip()
                elif line.startswith('DESCRIPTION:'):
                    self.description = line[12:].strip()
                elif line.startswith('EXPECTED_OUTPUT:'):
                    self.expected_output = line[16:].strip()
                elif line.startswith('EXPECTED_REGS:'):
                    self._parse_expected_regs(line[14:].strip())
                elif line.startswith('EXPECTED_EXIT:'):
                    self.expected_exit = int(line[14:].strip(), 0)
                elif line.startswith('EXPECTED_PC:'):
                    self.expected_pc = int(line[12:].strip(), 0)
    
    def _parse_expected_regs(self, reg_string):
        """Parse expected register values like 'x10=0x42 x11=0xDEAD'"""
        for match in re.finditer(r'x(\d+)=(0x[0-9a-fA-F]+|\d+)', reg_string):
            reg_num = int(match.group(1))
            value = int(match.group(2), 0)
            self.expected_regs[reg_num] = value


class AsmTestRunner:
    """Runner for assembly tests"""
    
    # Maximum instructions to execute before timeout
    MAX_INSTRUCTIONS = 10000
    
    def __init__(self, verbose=False, debug=False):
        self.verbose = verbose
        self.debug = debug
        self.tests_passed = 0
        self.tests_failed = 0
    
    def run_test(self, binary_path, metadata):
        """Run a single test and verify results"""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"TEST: {metadata.test_name}")
            print(f"DESC: {metadata.description}")
            print(f"BIN:  {binary_path}")
            print(f"{'='*60}")
        else:
            print(f"Testing {metadata.test_name}...", end=' ')
        
        # Initialize CPU and memory
        cpu = RV32CPU()
        mem = Memory()
        
        # Load binary
        with open(binary_path, 'rb') as f:
            program = list(f.read())
        
        # Load at standard RISC-V address
        load_address = 0x80000000
        mem.load_program(load_address, program)
        cpu.pc = load_address
        
        # Execute until ebreak or timeout
        instruction_count = 0
        ebreak_encountered = False
        
        try:
            while instruction_count < self.MAX_INSTRUCTIONS:
                # Fetch instruction
                insn = mem.read_word(cpu.pc)
                
                # Check for ebreak (0x00100073)
                if insn == 0x00100073:
                    if self.debug:
                        print(f"  [{instruction_count:4d}] PC={cpu.pc:#010x}: EBREAK (0x00100073)")
                        print(f"  Test completed via ebreak")
                    ebreak_encountered = True
                    break
                
                if self.debug:
                    # Decode for display purposes only
                    decoded = decode_instruction(insn)
                    from decoder import get_instruction_name
                    print(f"  [{instruction_count:4d}] PC={cpu.pc:#010x}: {get_instruction_name(decoded):6s} ({insn:#010x})")
                
                # Execute (this will decode internally)
                old_pc = cpu.pc
                execute_instruction(cpu, mem, insn)
                
                # Increment PC if not modified by instruction
                if cpu.pc == old_pc:
                    cpu.pc += 4
                
                instruction_count += 1
            
            # If we got here without ebreak, it's a timeout
            if not ebreak_encountered:
                raise TimeoutError(f"Test exceeded {self.MAX_INSTRUCTIONS} instructions without ebreak")
            
        except Exception as e:
            if not ebreak_encountered:
                if self.debug:
                    print(f"\nException during execution: {e}")
                    import traceback
                    traceback.print_exc()
                # Re-raise if not already handled
                raise
        
        # Get results
        uart_output = mem.get_uart_output()
        
        # Verify results
        success = True
        errors = []
        
        # Check UART output
        if metadata.expected_output is not None:
            # Convert escape sequences in expected output
            expected = metadata.expected_output.replace('\\n', '\n').replace('\\t', '\t')
            # Handle the UART's conversion of non-printable chars to \xNN format
            actual = uart_output
            if actual != expected:
                success = False
                errors.append(f"UART output mismatch:\n  Expected: {repr(expected)}\n  Got:      {repr(actual)}")
        
        # Check registers
        for reg_num, expected_value in metadata.expected_regs.items():
            actual_value = cpu.read_reg(reg_num)
            if actual_value != expected_value:
                success = False
                errors.append(f"x{reg_num} mismatch: expected {expected_value:#010x}, got {actual_value:#010x}")
        
        # Check PC if specified
        if metadata.expected_pc is not None:
            if cpu.pc != metadata.expected_pc:
                success = False
                errors.append(f"PC mismatch: expected {metadata.expected_pc:#010x}, got {cpu.pc:#010x}")
        
        # Report results
        if success:
            self.tests_passed += 1
            if self.verbose:
                print(f"✓ PASS")
                if uart_output:
                    print(f"  UART output: {repr(uart_output)}")
            else:
                print(f"✓")
        else:
            self.tests_failed += 1
            print(f"✗ FAIL")
            for error in errors:
                print(f"  {error}")
            
            if self.debug:
                print(f"\n  Register dump:")
                for i in range(32):
                    if i % 4 == 0:
                        print(f"  ", end='')
                    print(f"x{i:2d}={cpu.read_reg(i):#010x}  ", end='')
                    if i % 4 == 3:
                        print()
                print(f"  PC={cpu.pc:#010x}")
                print(f"  Instructions executed: {instruction_count}")
        
        return success
    
    def run_tests(self, test_dir, pattern=None):
        """Run all tests in directory matching optional pattern"""
        test_dir = Path(test_dir)
        
        # Find all .s files
        if pattern:
            source_files = sorted(test_dir.rglob(f"*{pattern}*.s"))
        else:
            source_files = sorted(test_dir.rglob("*.s"))
        
        if not source_files:
            print(f"No test files found in {test_dir}")
            return
        
        print(f"Found {len(source_files)} test(s)")
        print()
        
        for source_path in source_files:
            # Get corresponding binary
            binary_path = source_path.with_suffix('.bin')
            
            if not binary_path.exists():
                print(f"⚠ SKIP {source_path.name}: binary not found (run 'make')")
                continue
            
            # Parse metadata
            metadata = TestMetadata(source_path)
            
            if metadata.test_name is None:
                print(f"⚠ SKIP {source_path.name}: no TEST: metadata found")
                continue
            
            # Run test
            self.run_test(binary_path, metadata)
        
        # Summary
        print()
        print(f"{'='*60}")
        print(f"Results: {self.tests_passed} passed, {self.tests_failed} failed")
        print(f"{'='*60}")
        
        return self.tests_failed == 0


def main():
    parser = argparse.ArgumentParser(description='Run pyrv32 assembly tests')
    parser.add_argument('pattern', nargs='?', help='Test pattern to match (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode (show instructions and registers)')
    parser.add_argument('--dir', default='.', help='Test directory (default: current directory)')
    
    args = parser.parse_args()
    
    # Find test directory (relative to script location)
    script_dir = Path(__file__).parent
    test_dir = script_dir / args.dir
    if not test_dir.exists():
        print(f"Error: Test directory {test_dir} not found")
        sys.exit(1)
    
    # Run tests
    runner = AsmTestRunner(verbose=args.verbose, debug=args.debug)
    success = runner.run_tests(test_dir, args.pattern)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
