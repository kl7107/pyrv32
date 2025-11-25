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
from tests.test_cpu import run_cpu_tests
from tests.test_memory import run_memory_tests
from tests.test_execute import run_decoder_tests
from tests.test_decoder_utils import run_all_tests as run_decoder_utils_tests


def run_all_tests():
    """
    Run all unit tests.
    Returns list of log file paths.
    """
    log_paths = []
    
    # Run all test modules
    print("Running CPU tests...")
    log_paths.append(run_cpu_tests())
    print("Running Memory tests...")
    log_paths.append(run_memory_tests())
    print("Running Execution tests...")
    log_paths.append(run_decoder_tests())
    print("Running Decoder Utility tests...")
    run_decoder_utils_tests()  # This one doesn't return a log path yet
    
    return log_paths


def run_binary(binary_path, verbose=False, start_addr=0x80000000):
    """
    Load and run a binary file.
    
    Args:
        binary_path: Path to binary file
        verbose: Print instruction trace
        start_addr: Starting PC address (default 0x80000000)
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
    
    while step < max_steps:
        # Fetch instruction
        insn = mem.read_word(cpu.pc)
        
        # Check for ebreak (0x00100073)
        if insn == 0x00100073:
            if verbose:
                print(f"  [{step:6d}] PC=0x{cpu.pc:08x}: EBREAK - Program terminated")
            else:
                print(f"\nProgram terminated (ebreak at PC=0x{cpu.pc:08x}, {step} instructions)")
            break
        
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


def run_demo():
    """
    Run the built-in demo program.
    """
    print("=" * 60)
    print("Demo: Output 'Hello' to UART")
    print("=" * 60)
    
    cpu = RV32CPU()
    mem = Memory()
    
    # Start at standard RISC-V boot address
    cpu.pc = 0x80000000
    
    # Simple program to output "Hello" - no loops, just linear code
    # This is intentionally inefficient for clarity
    program = [
        # Load UART address into x10
        0x10000537,  # lui  x10, 0x10000    -> x10 = 0x10000000
        
        # Output 'H' (72)
        0x04800593,  # addi x11, x0, 72     -> x11 = 'H'
        0x00B50023,  # sb   x11, 0(x10)     -> UART = 'H'
        
        # Output 'e' (101)
        0x06500593,  # addi x11, x0, 101    -> x11 = 'e'
        0x00B50023,  # sb   x11, 0(x10)     -> UART = 'e'
        
        # Output 'l' (108)
        0x06C00593,  # addi x11, x0, 108    -> x11 = 'l'
        0x00B50023,  # sb   x11, 0(x10)     -> UART = 'l'
        
        # Output 'l' (108)
        0x06C00593,  # addi x11, x0, 108    -> x11 = 'l'
        0x00B50023,  # sb   x11, 0(x10)     -> UART = 'l'
        
        # Output 'o' (111)
        0x06F00593,  # addi x11, x0, 111    -> x11 = 'o'
        0x00B50023,  # sb   x11, 0(x10)     -> UART = 'o'
        
        # Output newline (10)
        0x00A00593,  # addi x11, x0, 10     -> x11 = '\n'
        0x00B50023,  # sb   x11, 0(x10)     -> UART = '\n'
    ]
    
    # Load program into memory (convert to bytes, little-endian)
    program_bytes = []
    for insn in program:
        program_bytes.extend([
            insn & 0xFF,
            (insn >> 8) & 0xFF,
            (insn >> 16) & 0xFF,
            (insn >> 24) & 0xFF
        ])
    
    mem.load_program(cpu.pc, program_bytes)
    
    print(f"\nProgram loaded at 0x{cpu.pc:08x}")
    print(f"Program size: {len(program)} instructions ({len(program_bytes)} bytes)\n")
    
    # Execute the program
    print("Executing program...")
    step = 0
    max_steps = 100  # Safety limit
    
    while step < max_steps:
        # Fetch instruction
        insn = mem.read_word(cpu.pc)
        
        # Decode for display
        decoded = decode_instruction(insn)
        name = get_instruction_name(decoded)
        
        print(f"  [{step:2d}] PC=0x{cpu.pc:08x}: {name:6s} (0x{insn:08x})")
        
        # Execute
        continue_exec = execute_instruction(cpu, mem, insn)
        
        if not continue_exec:
            break
        
        step += 1
        
        # Stop when we've executed all instructions
        if step >= len(program):
            break
    
    # Show UART output
    uart_output = mem.get_uart_output()
    print(f"\n{'=' * 60}")
    print(f"UART Output:")
    print(f"{'=' * 60}")
    print(uart_output)
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
  python3 pyrv32.py                      # Run tests + demo
  python3 pyrv32.py program.bin          # Run binary file
  python3 pyrv32.py -v program.bin       # Run with instruction trace
  python3 pyrv32.py --start 0x0 prog.bin # Run at different start address
  python3 pyrv32.py --test               # Run tests only
        """
    )
    
    parser.add_argument('binary', nargs='?', help='Binary file to execute')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print instruction trace during execution')
    parser.add_argument('--start', type=lambda x: int(x, 0), default=0x80000000,
                        help='Starting PC address (default: 0x80000000)')
    parser.add_argument('--test', action='store_true',
                        help='Run tests only (no demo)')
    parser.add_argument('--no-test', action='store_true',
                        help='Skip tests (run binary/demo only)')
    
    args = parser.parse_args()
    
    # Run tests unless --no-test
    if not args.no_test:
        log_paths = run_all_tests()
        print(f"All tests PASSED ✓")
        print(f"Test logs: {', '.join(log_paths)}\n")
    
    # If --test flag, exit after tests
    if args.test:
        return
    
    # Run binary if provided, otherwise run demo
    if args.binary:
        run_binary(args.binary, verbose=args.verbose, start_addr=args.start)
    else:
        run_demo()


if __name__ == "__main__":
    main()
