#!/usr/bin/env python3
"""
pyrv32 - Simple RV32IMC Instruction Simulator

A simple, easy-to-understand RISC-V RV32IMC instruction simulator.
Not cycle-accurate. Designed for simulating user-space programs and testing.

Design principle: Clarity over performance.

Usage:
    python3 pyrv32.py                    # Run tests + demo
    python3 pyrv32.py program.bin        # Run binary file
    python3 pyrv32.py --help             # Show help
"""

import sys
import argparse
from cpu import RV32CPU
from memory import Memory
from decoder import decode_instruction, get_instruction_name
from execute import execute_instruction
from exceptions import EBreakException, ECallException, MemoryAccessFault
from tests import run_all_tests
import os
from pathlib import Path


def run_binary(binary_path, verbose=False, start_addr=0x80000000):
    """
    Load and run a binary file.
    
    Args:
        binary_path: Path to binary file
        verbose: Print instruction trace
        start_addr: Starting PC address (default 0x80000000 per RISC-V convention)
    """
    print("=" * 60)
    print(f"Loading binary: {binary_path}")
    print("=" * 60)
    
    cpu = RV32CPU()
    mem = Memory()
    cpu.pc = start_addr
    
    # Load binary file
    try:
        with open(binary_path, 'rb') as f:
            program_bytes = list(f.read())
    except FileNotFoundError:
        print(f"Error: File not found: {binary_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
    
    mem.load_program(cpu.pc, program_bytes)
    
    print(f"\nProgram loaded at 0x{cpu.pc:08x}")
    print(f"Program size: {len(program_bytes)} bytes\n")
    
    # Execute
    if verbose:
        print("Executing program (verbose mode)...")
    else:
        print("Executing program...")
    
    step = 0
    max_steps = 100000  # Safety limit
    
    try:
        while step < max_steps:
            # Fetch instruction
            insn = mem.read_word(cpu.pc)
            
            # Decode and display if verbose
            if verbose:
                decoded = decode_instruction(insn)
                name = get_instruction_name(decoded)
                print(f"  [{step:6d}] PC=0x{cpu.pc:08x}: {name:6s} (0x{insn:08x})")
            
            # Execute
            continue_exec = execute_instruction(cpu, mem, insn)
            
            if not continue_exec:
                if verbose:
                    print(f"  Execution stopped at step {step}")
                break
            
            step += 1
    
    except EBreakException as e:
        if verbose:
            print(f"  [{step:6d}] PC=0x{e.pc:08x}: EBREAK - Program terminated")
        else:
            print(f"\nProgram terminated (ebreak at PC=0x{e.pc:08x}, {step} instructions)")
    
    except ECallException as e:
        print(f"\nECALL encountered at PC=0x{e.pc:08x} - not implemented")
        sys.exit(1)
    
    except MemoryAccessFault as e:
        print(f"\n{'=' * 60}")
        print(f"MEMORY ACCESS FAULT")
        print(f"{'=' * 60}")
        print(f"Type:    {e.access_type.upper()}")
        print(f"Address: 0x{e.address:08x}")
        print(f"PC:      0x{e.pc:08x}")
        print(f"\nValid memory regions:")
        print(f"  RAM:  0x80000000 - 0x807FFFFF (8MB)")
        print(f"  UART: 0x10000000 (TX register only)")
        print(f"{'=' * 60}")
        sys.exit(1)
    
    if step >= max_steps:
        print(f"\nWarning: Stopped after {max_steps} instructions (safety limit)")
    
    # Show UART output
    uart_output = mem.get_uart_output()
    if uart_output:
        print(f"\n{'=' * 60}")
        print(f"UART Output:")
        print(f"{'=' * 60}")
        print(uart_output, end='')
        if not uart_output.endswith('\n'):
            print()  # Add newline if output doesn't have one
        print(f"{'=' * 60}")
    
    # Show final register state
    print()
    cpu.dump_registers()


def main():
    """
    Main entry point for pyrv32 simulator.
    """
    parser = argparse.ArgumentParser(
        description='pyrv32 - Simple RV32IMC Instruction Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 pyrv32.py                      # Run all tests (unit + assembly)
  python3 pyrv32.py --asm-test           # Run assembly tests only
  python3 pyrv32.py program.bin          # Run binary file (with all tests first)
  python3 pyrv32.py --no-test prog.bin   # Run binary without any tests
  python3 pyrv32.py -v program.bin       # Run with instruction trace
  python3 pyrv32.py --start 0x0 prog.bin # Run at different start address
        """
    )
    
    parser.add_argument('binary', nargs='?', help='Binary file to execute')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print instruction trace during execution')
    parser.add_argument('--start', type=lambda x: int(x, 0), default=0x80000000,
                        help='Starting PC address (default: 0x80000000)')
    parser.add_argument('--test', action='store_true',
                        help='Run all tests (default when no binary provided)')
    parser.add_argument('--no-test', action='store_true',
                        help='Skip all tests')
    parser.add_argument('--asm-test', action='store_true',
                        help='Run assembly tests only (skip unit tests)')
    
    args = parser.parse_args()
    
    # Determine what to run
    run_unit_tests = not args.no_test and not args.asm_test and not args.binary
    run_asm_tests = args.asm_test or (not args.no_test and not args.binary)
    
    # Run unit tests
    if run_unit_tests:
        log_paths = run_all_tests()
        print(f"All unit tests PASSED ✓")
        print(f"Test logs: {', '.join(log_paths)}\n")
    
    # Run assembly tests
    if run_asm_tests:
        asm_test_dir = Path(__file__).parent / 'asm_tests'
        if asm_test_dir.exists():
            sys.path.insert(0, str(asm_test_dir))
            from run_tests import AsmTestRunner
            
            print("=" * 60)
            print("Running Assembly Tests")
            print("=" * 60)
            
            runner = AsmTestRunner(verbose=args.verbose)
            success = runner.run_tests(asm_test_dir)
            
            if not success:
                sys.exit(1)
            print()  # Add blank line after asm tests
        else:
            print(f"Warning: Assembly test directory not found: {asm_test_dir}\n")
    
    # Run binary if provided
    if args.binary:
        run_binary(args.binary, verbose=args.verbose, start_addr=args.start)


if __name__ == "__main__":
    main()
