#!/usr/bin/env python3
"""
Runner for C filesystem tests

Compiles and runs each test in tests/c/
"""

import sys
import os
import subprocess
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test(test_bin, sim_root):
    """Run a single test binary"""
    from cpu import RV32CPU
    from memory import Memory
    from execute import execute_instruction
    from syscalls import SyscallHandler
    from exceptions import EBreakException, ECallException
    
    # Create components
    mem = Memory()
    cpu = RV32CPU()
    syscall_handler = SyscallHandler(fs_root=sim_root)
    
    # Load binary
    with open(test_bin, 'rb') as f:
        program = f.read()
    
    for i, byte in enumerate(program):
        mem.write_byte(0x80000000 + i, byte)
    
    cpu.pc = 0x80000000
    
    # Run with timeout
    max_instructions = 1000000
    instruction_count = 0
    for i in range(max_instructions):
        try:
            insn = mem.read_word(cpu.pc)
            execute_instruction(cpu, mem, insn)
            instruction_count += 1
        except ECallException:
            # Handle syscall and continue
            syscall_handler.handle_syscall(cpu, mem)
            cpu.pc += 4
            instruction_count += 1
        except EBreakException:
            # Program exited cleanly
            break
        except Exception as e:
            output = mem.get_uart_output()
            print(f"Exception at instruction {instruction_count}, PC=0x{cpu.pc:08x}: {e}")
            print(f"Output so far: {output[:200]}")
            break
    
    # Get output
    output = mem.console_uart.get_output_text()
    
    # Check if test passed
    # Look for PASS on its own line and no "FAIL:" error messages
    lines = [line.strip() for line in output.strip().split('\n')]
    has_pass = 'PASS' in lines
    has_fail = any(line.startswith('FAIL:') for line in lines)
    passed = has_pass and not has_fail
    
    return passed, output

def main():
    test_dir = os.path.join(os.path.dirname(__file__), 'tests', 'c')
    
    if not os.path.exists(test_dir):
        print(f"Test directory not found: {test_dir}")
        return 1
    
    # Build tests
    print("Building C tests...")
    build_script = os.path.join(test_dir, 'build.sh')
    if os.path.exists(build_script):
        result = subprocess.run(['bash', build_script], cwd=test_dir, 
                                capture_output=True, text=True)
        if result.returncode != 0:
            print("Build failed:")
            print(result.stdout)
            print(result.stderr)
            return 1
        print(result.stdout)
    
    # Find test binaries
    test_bins = []
    for f in os.listdir(test_dir):
        if f.startswith('test_') and f.endswith('.bin'):
            test_bins.append(os.path.join(test_dir, f))
    
    if not test_bins:
        print("No test binaries found")
        return 1
    
    test_bins.sort()
    
    # Run each test
    passed = 0
    failed = 0
    
    print(f"\nRunning {len(test_bins)} tests...")
    print("=" * 70)
    
    for test_bin in test_bins:
        test_name = os.path.basename(test_bin).replace('.bin', '')
        
        # Create temp directory for this test
        with tempfile.TemporaryDirectory(prefix='pyrv32-test-') as sim_root:
            # Create /tmp subdirectory
            os.makedirs(os.path.join(sim_root, 'tmp'), exist_ok=True)
            
            try:
                test_passed, output = run_test(test_bin, sim_root)
                
                if test_passed:
                    print(f"✓ {test_name}")
                    passed += 1
                else:
                    print(f"✗ {test_name}")
                    # Debug: show why it failed
                    lines = [line.strip() for line in output.strip().split('\n')]
                    has_pass = 'PASS' in lines
                    has_fail = any(line.startswith('FAIL:') for line in lines)
                    if has_pass and not has_fail:
                        print(f"  DEBUG: Marked as fail but has PASS and no FAIL:")
                        print(f"  DEBUG: PASS in lines? {has_pass}")
                        print(f"  DEBUG: lines = {lines[:10]}")
                    if not output.strip():
                        print(f"  No output")
                    else:
                        print(f"  Output:")
                        for line in output.split('\n')[-10:]:  # Last 10 lines
                            if line.strip():
                                print(f"    {line}")
                    failed += 1
                    
            except Exception as e:
                print(f"✗ {test_name} - Exception: {e}")
                failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
