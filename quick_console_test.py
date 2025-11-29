#!/usr/bin/env python3
"""Test console UART via direct Python, not MCP."""

import sys
sys.path.insert(0, '/home/dev/git/zesarux/pyrv32')

from pyrv32_system import RV32System

print("="*60)
print("CONSOLE UART TEST - Interpreter")
print("="*60)

# Create session and load interpreter
sys_obj = RV32System()
sys_obj.load_binary('/home/dev/git/zesarux/pyrv32/firmware/interpreter_test.bin')

print("\n1. Running until console UART output...")
result = sys_obj.run_until_output(max_steps=50000)

# Note: run_until_output checks debug UART, not console UART
# So we need to just run and then check
print(f"   Ran {result.instruction_count} instructions")

# Check console UART
output = sys_obj.console_uart_read()
print(f"\n2. Console UART output ({len(output)} bytes):")
print(output[:300] if len(output) > 300 else output)

if ">" in output:
    print("\n✓ Got prompt!")
else:
    print("\n⚠ No prompt yet, running more...")
    result = sys_obj.run(max_steps=10000)
    output = sys_obj.console_uart_read()
    print(output)

# Send ADD command
print("\n3. Sending: ADD 42 13")
sys_obj.console_uart_write("ADD 42 13\n")

# Run more
result = sys_obj.run(max_steps=10000)
response = sys_obj.console_uart_read()

print(f"\n4. Response:")
print(response)

if "55" in response:
    print("\n✓ PASS - Got 55!")
else:
    print(f"\n✗ FAIL - Expected 55")

print("\n" + "="*60)
