#!/usr/bin/env python3
"""Minimal test to verify UART works."""

import sys
import os

os.chdir('/home/dev/git/zesarux/pyrv32')
sys.path.insert(0, '.')

from pyrv32_system import RV32System

print("Loading hello.bin...")
sys_obj = RV32System()
sys_obj.load_binary('firmware/hello.bin')

print("Running...")
result = sys_obj.run(max_steps=10000)

print(f"Status: {result.status}")
print(f"Instructions: {result.instruction_count}")

output = sys_obj.uart_read()
print(f"\nDebug UART output ({len(output)} bytes):")
print(output)

if "Hello, World" in output:
    print("\n✓ TEST PASSED")
else:
    print("\n✗ TEST FAILED")
    sys.exit(1)
