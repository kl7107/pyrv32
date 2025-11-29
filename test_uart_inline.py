#!/usr/bin/env python3
"""Inline UART test execution."""

import sys
import os

# Setup
os.chdir('/home/dev/git/zesarux/pyrv32')
if '.' not in sys.path:
    sys.path.insert(0, '.')

print("Importing pyrv32_system...")
from pyrv32_system import RV32System

print("\n" + "="*60)
print("UART TEST SUITE")
print("="*60)

try:
    # Test 1: Debug UART
    print("\n[Test 1] Debug UART with hello.bin")
    sys1 = RV32System()
    sys1.load_binary('firmware/hello.bin')
    result1 = sys1.run(max_steps=10000)
    output1 = sys1.uart_read()
    
    print(f"  Status: {result1.status}")
    print(f"  Instructions: {result1.instruction_count}")
    print(f"  Output length: {len(output1)} bytes")
    
    if "Hello, World from RV32IM!" in output1:
        print("  ✓ PASS")
    else:
        print("  ✗ FAIL - Expected hello message")
        print(f"  Got: {output1[:100]}")
        sys.exit(1)

    # Test 2: Console UART
    print("\n[Test 2] Console UART with interpreter_test.bin")
    
    if not os.path.exists('firmware/interpreter_test.bin'):
        print("  ⚠ SKIP - interpreter_test.bin not found")
    else:
        sys2 = RV32System()
        sys2.load_binary('firmware/interpreter_test.bin')
        
        # Get initial output
        result2 = sys2.run_until_output(max_steps=50000)
        output2 = sys2.console_uart_read()
        
        print(f"  Got {len(output2)} bytes of output")
        
        if "Simple Command Interpreter" not in output2:
            print("  ✗ FAIL - No banner")
            print(f"  Output: {output2[:200]}")
            sys.exit(1)
        
        if ">" not in output2:
            print("  ✗ FAIL - No prompt")
            sys.exit(1)
        
        print("  ✓ Got banner and prompt")
        
        # Test ADD
        print("\n[Test 3] ADD command")
        sys2.console_uart_write("ADD 42 13\n")
        result3 = sys2.run_until_output(max_steps=10000)
        output3 = sys2.console_uart_read()
        
        print(f"  Response: {repr(output3.strip())}")
        
        if "55" in output3:
            print("  ✓ PASS - ADD works")
        else:
            print("  ✗ FAIL - Expected 55")
            sys.exit(1)
        
        # Test MUL
        print("\n[Test 4] MUL command")
        sys2.console_uart_write("MUL 7 8\n")
        result4 = sys2.run_until_output(max_steps=10000)
        output4 = sys2.console_uart_read()
        
        print(f"  Response: {repr(output4.strip())}")
        
        if "56" in output4:
            print("  ✓ PASS - MUL works")
        else:
            print("  ✗ FAIL - Expected 56")
            sys.exit(1)

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)

except Exception as e:
    print(f"\n✗ TEST FAILED WITH EXCEPTION:")
    print(f"  {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
