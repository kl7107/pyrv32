#!/usr/bin/env python3
"""Direct UART test - no subprocess."""

import sys
import os

# Setup path
os.chdir('/home/dev/git/zesarux/pyrv32')
sys.path.insert(0, '.')

from pyrv32_system import RV32System

print("="*60)
print("UART COMPREHENSIVE TEST")
print("="*60)

# Test 1: Debug UART with hello.bin
print("\nTest 1: Debug UART (hello.bin)")
print("-"*60)

sys_obj = RV32System()
sys_obj.load_binary('firmware/hello.bin')
result = sys_obj.run(max_steps=10000)

print(f"Status: {result.status}, Instructions: {result.instruction_count}")

debug_output = sys_obj.uart_read()
print(f"Debug UART output ({len(debug_output)} bytes):")
print(debug_output)

if "Hello, World from RV32IM!" in debug_output:
    print("✓ PASS - Debug UART works")
else:
    print("✗ FAIL - Expected hello message")
    sys.exit(1)

# Test 2: Console UART with interpreter
print("\n" + "="*60)
print("Test 2: Console UART Interactive (interpreter_test.bin)")
print("-"*60)

# Check if file exists
if not os.path.exists('firmware/interpreter_test.bin'):
    print("⚠ interpreter_test.bin not found, skipping test")
else:
    sys_obj2 = RV32System()
    sys_obj2.load_binary('firmware/interpreter_test.bin')
    
    # Run until prompt
    print("\nStarting interpreter...")
    result = sys_obj2.run_until_output(max_steps=50000)
    
    initial_output = sys_obj2.console_uart_read()
    print(f"Initial console output ({len(initial_output)} bytes):")
    print(initial_output[:200] + "..." if len(initial_output) > 200 else initial_output)
    
    if "Simple Command Interpreter" in initial_output and ">" in initial_output:
        print("✓ PASS - Got interpreter prompt")
    else:
        print("✗ FAIL - Expected interpreter banner and prompt")
        sys.exit(1)
    
    # Test command: ADD
    print("\nSending: ADD 42 13")
    sys_obj2.console_uart_write("ADD 42 13\n")
    
    result = sys_obj2.run_until_output(max_steps=10000)
    response = sys_obj2.console_uart_read()
    
    print(f"Response: {response.strip()}")
    
    if "55" in response:
        print("✓ PASS - ADD command works (42 + 13 = 55)")
    else:
        print(f"✗ FAIL - Expected '55' in response")
        sys.exit(1)
    
    # Test command: MUL
    print("\nSending: MUL 7 8")
    sys_obj2.console_uart_write("MUL 7 8\n")
    
    result = sys_obj2.run_until_output(max_steps=10000)
    response = sys_obj2.console_uart_read()
    
    print(f"Response: {response.strip()}")
    
    if "56" in response:
        print("✓ PASS - MUL command works (7 * 8 = 56)")
    else:
        print(f"✗ FAIL - Expected '56' in response")
        sys.exit(1)
    
    # Test command: ECHO
    print("\nSending: ECHO Hello Test")
    sys_obj2.console_uart_write("ECHO Hello Test\n")
    
    result = sys_obj2.run_until_output(max_steps=10000)
    response = sys_obj2.console_uart_read()
    
    print(f"Response: {response.strip()}")
    
    if "Hello Test" in response:
        print("✓ PASS - ECHO command works")
    else:
        print(f"✗ FAIL - Expected 'Hello Test' in response")
        sys.exit(1)

print("\n" + "="*60)
print("ALL UART TESTS PASSED!")
print("="*60)
print("\nSummary:")
print("  ✓ Debug UART (0x10000000) - read-only output")
print("  ✓ Console UART (0x10001000-0x10001008) - bidirectional I/O")
print("  ✓ Interactive commands work correctly")
