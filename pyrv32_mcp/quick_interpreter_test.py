#!/usr/bin/env python3
"""Quick test of interpreter_test.bin"""

import sys
import os

os.chdir('/home/dev/git/zesarux/pyrv32')
sys.path.insert(0, '.')

from pyrv32_system import RV32System

print("="*60)
print("Testing interpreter_test.bin")
print("="*60)

sys_obj = RV32System()
sys_obj.load_binary('firmware/interpreter_test.bin')

# Run until we get the prompt
print("\n1. Starting interpreter...")
result = sys_obj.run_until_output(max_steps=50000)

output = sys_obj.console_uart_read()
print(f"Initial output ({len(output)} bytes):")
print(output)
print()

# Send ADD command
print("2. Sending: ADD 42 13")
sys_obj.console_uart_write("ADD 42 13\n")

result = sys_obj.run_until_output(max_steps=10000)
output = sys_obj.console_uart_read()

print(f"Response:")
print(output)
print()

if "55" in output:
    print("✓ TEST PASSED - Got expected result '55'")
else:
    print(f"✗ TEST FAILED - Expected '55' in output")
    sys.exit(1)

# Try another command
print("\n3. Sending: MUL 7 8")
sys_obj.console_uart_write("MUL 7 8\n")

result = sys_obj.run_until_output(max_steps=10000)
output = sys_obj.console_uart_read()

print(f"Response:")
print(output)
print()

if "56" in output:
    print("✓ TEST PASSED - Got expected result '56'")
else:
    print(f"✗ TEST FAILED - Expected '56' in output")
    sys.exit(1)

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
