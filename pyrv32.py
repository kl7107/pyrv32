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
import time
from cpu import RV32CPU
from memory import Memory
from decoder import decode_instruction, get_instruction_name
from execute import execute_instruction
from exceptions import EBreakException, ECallException, MemoryAccessFault
from tests import run_all_tests
import os
from pathlib import Path
from debugger import Debugger
from syscalls import SyscallHandler


def interactive_debugger_cli(cpu, mem, debugger, insn, step):
    """
    Interactive debugger command-line interface.
    Returns True to continue execution, False to quit.
    """
    while True:
        try:
            cmd = input("(pyrv32-dbg) ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nQuit")
            return False
        
        if not cmd:
            continue
        
        parts = cmd.split()
        cmd_name = parts[0].lower()
        
        # Breakpoint commands
        if cmd_name == 'b' or cmd_name == 'break':
            if len(parts) < 2:
                print("Usage: b <address>                    Set breakpoint at address")
                print("       b <address> <reg> <value>     Set conditional breakpoint")
                print("       bcond <reg> <value>           Set register-only breakpoint")
                print("Example: b 0x80001000")
                print("Example: b 0x80001000 a0 0x1234")
                print("Example: bcond s4 0x80000000")
                continue
            try:
                addr = int(parts[1], 0)
                # Check if conditional
                if len(parts) >= 4:
                    reg_name = parts[2]
                    reg_value = int(parts[3], 0)
                    bp = debugger.bp_manager.add(address=addr, reg_name=reg_name, reg_value=reg_value)
                    print(f"Breakpoint {bp.id} set at 0x{addr:08x} when {reg_name}=0x{reg_value:08x}")
                else:
                    bp = debugger.bp_manager.add(addr)
                    print(f"Breakpoint {bp.id} set at 0x{addr:08x}")
            except ValueError:
                print(f"Invalid address or value: {parts[1:]}")
        
        elif cmd_name == 'bcond':
            # Register-only conditional breakpoint
            if len(parts) < 3:
                print("Usage: bcond <reg> <value>")
                print("  Set breakpoint when register equals value (any address)")
                print("Example: bcond s4 0x80000000")
                continue
            try:
                reg_name = parts[1]
                reg_value = int(parts[2], 0)
                bp = debugger.bp_manager.add(reg_name=reg_name, reg_value=reg_value)
                print(f"Breakpoint {bp.id} set when {reg_name}=0x{reg_value:08x}")
            except ValueError:
                print(f"Invalid value: {parts[2]}")
        
        elif cmd_name == 'd' or cmd_name == 'delete':
            if len(parts) < 2:
                print("Usage: d <num>  or  d *  (delete all)")
                continue
            if parts[1] == '*':
                count = debugger.bp_manager.delete_all()
                print(f"Deleted all breakpoints ({count} total)")
            else:
                try:
                    bp_id = int(parts[1])
                    if debugger.bp_manager.delete(bp_id):
                        print(f"Deleted breakpoint {bp_id}")
                    else:
                        print(f"No breakpoint {bp_id}")
                except ValueError:
                    print(f"Invalid breakpoint ID: {parts[1]}")
        
        elif cmd_name == 'l' or cmd_name == 'list':
            bps = debugger.bp_manager.list()
            if not bps:
                print("No breakpoints set")
            else:
                print("Breakpoints:")
                for bp in bps:
                    print(f"  {bp}")
        
        elif cmd_name == 'i' or cmd_name == 'info':
            if len(parts) < 2:
                print("Usage: i r  (info registers)")
                continue
            if parts[1] == 'r' or parts[1] == 'registers':
                print(debugger.format_registers(cpu.regs, cpu.pc, compact=True))
            elif parts[1] == 'b' or parts[1] == 'breakpoints':
                bps = debugger.bp_manager.list()
                if not bps:
                    print("No breakpoints set")
                else:
                    for bp in bps:
                        print(f"  {bp}")
            else:
                print(f"Unknown info command: {parts[1]}")
        
        # Step commands
        elif cmd_name == 's' or cmd_name == 'step':
            count = 1
            if len(parts) >= 2:
                try:
                    count = int(parts[1])
                except ValueError:
                    print(f"Invalid step count: {parts[1]}")
                    continue
            debugger.set_step_mode(True, count=count)
            return True
        
        elif cmd_name == 'c' or cmd_name == 'continue':
            debugger.set_step_mode(False)
            return True
        
        # Register dump
        elif cmd_name == 'r' or cmd_name == 'regs':
            nonzero_only = '--nz' in parts or '--nonzero' in parts
            print(debugger.format_registers(cpu.regs, cpu.pc, compact=True, 
                                           show_nonzero_only=nonzero_only))
        
        # Disassemble current instruction
        elif cmd_name == 'x' or cmd_name == 'disasm':
            decoded = decode_instruction(insn)
            name = get_instruction_name(decoded)
            print(f"0x{cpu.pc:08x}: {name:10s} (0x{insn:08x})")
        
        # Trace buffer commands
        elif cmd_name == 't' or cmd_name == 'trace':
            if len(parts) < 2:
                print("Usage: t <N>        Show last N trace entries")
                print("       t <M> <N>    Show N entries starting at index M")
                print("       t all        Show all trace entries")
                print("       t clear      Clear trace buffer")
                print("       t info       Show trace buffer info")
                continue
            
            if parts[1] == 'all':
                output = debugger.dump_trace()
                print(output)
            elif parts[1] == 'clear':
                debugger.trace_buffer.clear()
                print("Trace buffer cleared")
            elif parts[1] == 'info':
                print(f"Trace buffer: {debugger.trace_buffer.size()} / {debugger.trace_buffer.max_size} entries")
                print(f"Status: {'enabled' if debugger.trace_buffer.enabled else 'disabled'}")
                print(f"Full: {'yes' if debugger.trace_buffer.is_full() else 'no'}")
            else:
                try:
                    if len(parts) == 2:
                        # Show last N entries
                        count = int(parts[1])
                        output = debugger.dump_trace(count=count)
                        print(output)
                    elif len(parts) == 3:
                        # Show N entries starting at M
                        start = int(parts[1])
                        count = int(parts[2])
                        output = debugger.dump_trace(count=count, start=start)
                        print(output)
                    else:
                        print("Invalid trace command")
                except ValueError:
                    print(f"Invalid trace arguments: {' '.join(parts[1:])}")
        
        # Trace search reverse (equal)
        elif cmd_name == 'tsr':
            if len(parts) < 3:
                print("Usage: tsr <regname> <value> [<start_index>]")
                print("  Search backwards through trace buffer for register matching value")
                print("  regname: Register name (e.g., a0, s4, pc)")
                print("  value: Value to search for (hex or decimal)")
                print("  start_index: Optional starting index (default: search from end)")
                print("Example: tsr s4 0x80000000")
                print("Example: tsr pc 2147483648 1000")
                continue
            
            reg_name = parts[1]
            try:
                # Parse value (support hex)
                value_str = parts[2]
                if value_str.startswith('0x') or value_str.startswith('0X'):
                    value = int(value_str, 16)
                else:
                    value = int(value_str)
                
                # Parse optional start index
                start_idx = None
                if len(parts) >= 4:
                    start_idx = int(parts[3])
                
                # Perform search
                found, msg, entry = debugger.search_trace_reverse(reg_name, value, start_idx, not_equal=False)
                print(msg)
                
                if found:
                    # Show the found entry
                    print(debugger.format_trace_entry(entry, show_insn_name=True, show_nonzero_only=False))
                
            except ValueError as e:
                print(f"Invalid arguments: {e}")
        
        # Trace search reverse (not equal)
        elif cmd_name == 'tsrneq':
            if len(parts) < 3:
                print("Usage: tsrneq <regname> <value> [<start_index>]")
                print("  Search backwards for register NOT equal to value")
                print("  regname: Register name (e.g., a0, s4, pc)")
                print("  value: Value to avoid (hex or decimal)")
                print("  start_index: Optional starting index (default: search from end)")
                print("Example: tsrneq s4 0x80000000  (find when s4 was NOT _start)")
                continue
            
            reg_name = parts[1]
            try:
                # Parse value (support hex)
                value_str = parts[2]
                if value_str.startswith('0x') or value_str.startswith('0X'):
                    value = int(value_str, 16)
                else:
                    value = int(value_str)
                
                # Parse optional start index
                start_idx = None
                if len(parts) >= 4:
                    start_idx = int(parts[3])
                
                # Perform search (not_equal=True)
                found, msg, entry = debugger.search_trace_reverse(reg_name, value, start_idx, not_equal=True)
                print(msg)
                
                if found:
                    # Show the found entry
                    print(debugger.format_trace_entry(entry, show_insn_name=True, show_nonzero_only=False))
                
            except ValueError as e:
                print(f"Invalid arguments: {e}")
        
        # Help
        elif cmd_name == 'h' or cmd_name == 'help':
            print("""
Debugger Commands:
  b <addr>              Set breakpoint at address (hex or decimal)
  b <addr> <reg> <val>  Set conditional breakpoint at address
  bcond <reg> <val>     Set breakpoint when register equals value
  d <num>               Delete breakpoint by number
  d *                   Delete all breakpoints
  l                     List all breakpoints
  i r                   Show registers
  i b                   Show breakpoints
  
  s                     Step one instruction
  s <N>                 Step N instructions
  c                     Continue execution
  
  r                     Show registers (compact format)
  r --nz                Show non-zero registers only
  x                     Disassemble current instruction
  
  t <N>                 Show last N trace entries
  t <M> <N>             Show N entries starting at index M
  t all                 Show all trace entries
  t clear               Clear trace buffer
  t info                Show trace buffer info
  tsr <reg> <val> [<idx>]     Search backwards for reg = value
  tsrneq <reg> <val> [<idx>]  Search backwards for reg != value
  
  h                     Show this help
  q                     Quit
""")
        
        elif cmd_name == 'q' or cmd_name == 'quit':
            return False
        
        else:
            print(f"Unknown command: {cmd_name}  (type 'h' for help)")


def run_binary(binary_path, verbose=False, start_addr=0x80000000, pc_trace_interval=0, 
               step_mode=False, breakpoints=None, reg_trace_interval=0, reg_trace_file=None,
               reg_trace_nonzero=False, trace_buffer_size=10000):
    """
    Load and run a binary file.
    
    Args:
        binary_path: Path to binary file
        verbose: Print instruction trace
        start_addr: Starting PC address (default 0x80000000 per RISC-V convention)
        pc_trace_interval: If > 0, print PC every N instructions
        step_mode: Start in step mode (interactive debugger)
        breakpoints: List of breakpoint addresses to set
        reg_trace_interval: If > 0, trace registers every N instructions
        reg_trace_file: File to save register trace (None = stdout)
        reg_trace_nonzero: Only show non-zero registers in trace
        trace_buffer_size: Size of execution trace ring buffer
    """
    print("=" * 60)
    print(f"Loading binary: {binary_path}")
    print("=" * 60)
    print("=" * 60)
    
    cpu = RV32CPU()
    mem = Memory()
    cpu.pc = start_addr
    
    # Initialize syscall handler with filesystem root
    syscall_handler = SyscallHandler(fs_root="./pyrv32-fs")
    
    # Initialize debugger
    debugger = Debugger(trace_buffer_size=trace_buffer_size)
    if step_mode:
        debugger.set_step_mode(True, count=1)
        print("\nStarting in step mode (interactive debugger)")
        print(f"Trace buffer enabled ({trace_buffer_size} entries)\n")
    
    # Set initial breakpoints
    if breakpoints:
        for addr in breakpoints:
            bp = debugger.bp_manager.add(addr)
            print(f"Breakpoint {bp.id} set at 0x{addr:08x}")
    
    # Enable register tracing if requested
    if reg_trace_interval and reg_trace_interval > 0:
        debugger.enable_reg_trace(filename=reg_trace_file, interval=reg_trace_interval,
                                  nonzero_only=reg_trace_nonzero)
    
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
    elif pc_trace_interval > 0:
        print(f"Executing program (PC trace every {pc_trace_interval:,} instructions)...")
    else:
        print("Executing program...")
    
    step = 0
    max_steps = 10000000  # Safety limit (10M instructions for benchmarks)
    
    start_time = time.time()
    
    try:
        while step < max_steps:
            try:
                # Fetch instruction
                insn = mem.read_word(cpu.pc)
                
                # Record in trace buffer BEFORE executing
                debugger.trace_buffer.add(step, cpu.pc, cpu.regs, insn)
                
                # Check for breakpoint or step mode BEFORE executing
                should_break, break_msg = debugger.should_break(cpu.pc, step, cpu.regs)
                if should_break:
                    if break_msg:
                        print(f"\n{break_msg}")
                    decoded = decode_instruction(insn)
                    name = get_instruction_name(decoded)
                    print(f"0x{cpu.pc:08x}: {name:10s} (0x{insn:08x})")
                    print(debugger.format_registers(cpu.regs, cpu.pc, compact=True, show_nonzero_only=True))
                    
                    # Enter interactive debugger
                    if not interactive_debugger_cli(cpu, mem, debugger, insn, step):
                        print("\nExecution stopped by user")
                        break
                
                # PC trace at intervals
                if pc_trace_interval > 0 and (step % pc_trace_interval) == 0:
                    print(f"[{step:8d}] PC=0x{cpu.pc:08x}", flush=True)
                
                # Register trace at intervals
                if reg_trace_interval > 0:
                    debugger.trace_registers(step, cpu.pc, cpu.regs)
                
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
            
            except ECallException as e:
                # Handle syscall and continue execution
                syscall_handler.handle_syscall(cpu, mem)
                cpu.pc += 4
            
            step += 1
    
    except EBreakException as e:
        if verbose:
            print(f"  [{step:6d}] PC=0x{e.pc:08x}: EBREAK - Program terminated")
        else:
            print(f"\nProgram terminated (ebreak at PC=0x{e.pc:08x}, {step} instructions)")
    
    except MemoryAccessFault as e:
        print(f"\n{'=' * 60}")
        print(f"MEMORY ACCESS FAULT")
        print(f"{'=' * 60}")
        print(f"Type:    {e.access_type.upper()}")
        print(f"Address: 0x{e.address:08x}")
        print(f"PC:      0x{e.pc:08x}")
        print(f"\nRegisters at fault:")
        for i in range(0, 32, 4):
            print(f"  x{i:2d}-x{i+3:2d}: " + " ".join(f"0x{cpu.regs[j]:08x}" for j in range(i, min(i+4, 32))))
        print(f"\nValid memory regions:")
        print(f"  RAM:  0x80000000 - 0x807FFFFF (8MB)")
        print(f"  UART: 0x10000000 (TX register)")
        print(f"  TIMER: 0x10000004 (millisecond timer, read-only)")
        print(f"{'=' * 60}")
        sys.exit(1)
    
    if step >= max_steps:
        print(f"\nWarning: Stopped after {max_steps} instructions (safety limit)")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Show execution statistics
    print(f"\n{'=' * 60}")
    print(f"Execution Statistics:")
    print(f"{'=' * 60}")
    print(f"Instructions executed: {step:,}")
    print(f"Elapsed time: {elapsed_time:.3f} seconds")
    if elapsed_time > 0:
        print(f"Performance: {step/elapsed_time:,.0f} instructions/second")
        print(f"             {step/elapsed_time/1000:.1f} KIPS")
    print(f"{'=' * 60}")
    
    # Show UART output
    uart_output = mem.get_uart_output()
    if uart_output:
        print(f"\n{'=' * 60}")
        print(f"Debug UART Output:")
        print(f"{'=' * 60}")
        print(uart_output, end='')
        if not uart_output.endswith('\n'):
            print()  # Add newline if output doesn't have one
        print(f"{'=' * 60}")
    
    # Show Console UART output
    console_output = mem.console_uart.get_output_text()
    if console_output:
        print(f"\n{'=' * 60}")
        print(f"Console UART Output:")
        print(f"{'=' * 60}")
        print(console_output, end='')
        if not console_output.endswith('\n'):
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
  
  Debugging:
  python3 pyrv32.py --step prog.bin      # Start in step mode (interactive debugger)
  python3 pyrv32.py -b 0x80001000 prog.bin  # Set breakpoint and run
        """
    )
    
    parser.add_argument('binary', nargs='?', help='Binary file to execute')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print instruction trace during execution')
    parser.add_argument('--start', type=lambda x: int(x, 0), default=0x80000000,
                        help='Starting PC address (default: 0x80000000)')
    parser.add_argument('--pc-trace', type=int, metavar='N', default=0,
                        help='Print PC every N instructions (e.g., --pc-trace 100000)')
    parser.add_argument('--test', action='store_true',
                        help='Run all tests (default when no binary provided)')
    parser.add_argument('--no-test', action='store_true',
                        help='Skip all tests')
    parser.add_argument('--asm-test', action='store_true',
                        help='Run assembly tests only (skip unit tests)')
    
    # Debugger options
    parser.add_argument('--step', action='store_true',
                        help='Start in step mode (interactive debugger)')
    parser.add_argument('-b', '--breakpoint', type=lambda x: int(x, 0), action='append',
                        metavar='ADDR', dest='breakpoints',
                        help='Set breakpoint at address (can be used multiple times)')
    parser.add_argument('--reg-trace', type=int, metavar='N',
                        help='Enable register tracing every N instructions')
    parser.add_argument('--reg-file', type=str, metavar='FILE',
                        help='Save register trace to file (default: stdout)')
    parser.add_argument('--reg-nonzero', action='store_true',
                        help='Only show non-zero registers in trace')
    parser.add_argument('--trace-size', type=int, default=10000, metavar='N',
                        help='Execution trace buffer size (default: 10000)')
    
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
        run_binary(args.binary, verbose=args.verbose, start_addr=args.start, 
                   pc_trace_interval=args.pc_trace, step_mode=args.step,
                   breakpoints=args.breakpoints,
                   reg_trace_interval=args.reg_trace or 0,
                   reg_trace_file=args.reg_file,
                   reg_trace_nonzero=args.reg_nonzero,
                   trace_buffer_size=args.trace_size)


if __name__ == "__main__":
    main()
