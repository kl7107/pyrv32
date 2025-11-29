#!/usr/bin/env python3
"""Simple script to compile and test the interpreter."""

import subprocess
import sys
import os

# Step 1: Compile
print("Compiling interpreter_test.c...")
os.chdir('/home/dev/git/zesarux/pyrv32/firmware')

result = subprocess.run([
    'riscv32-unknown-elf-gcc',
    '-march=rv32im',
    '-mabi=ilp32',
    '-nostdlib',
    '-T', 'link.ld',
    '-o', 'interpreter_test.elf',
    'crt0.S',
    'interpreter_test.c',
    'runtime.c'
], capture_output=True, text=True)

if result.returncode != 0:
    print("COMPILATION FAILED:")
    print(result.stderr)
    sys.exit(1)

result = subprocess.run([
    'riscv32-unknown-elf-objcopy',
    '-O', 'binary',
    'interpreter_test.elf',
    'interpreter_test.bin'
], capture_output=True, text=True)

if result.returncode != 0:
    print("OBJCOPY FAILED:")
    print(result.stderr)
    sys.exit(1)

size = os.path.getsize('interpreter_test.bin')
print(f"✓ Created interpreter_test.bin ({size} bytes)\n")

# Step 2: Test
print("="*60)
print("Running basic interpreter test...")
print("="*60)

os.chdir('..')
sys.path.insert(0, '.')

from pyrv32_system import RV32System

sys_obj = RV32System()
sys_obj.load_binary('firmware/interpreter_test.bin')

# Run until we get the prompt
print("Starting interpreter...")
result = sys_obj.run_until_output(max_steps=50000)

output = sys_obj.console_uart_read()
print(f"Initial output:\n{output}\n")

# Send ADD command
print("Sending: ADD 42 13")
sys_obj.console_uart_write("ADD 42 13\n")

result = sys_obj.run_until_output(max_steps=10000)
output = sys_obj.console_uart_read()

print(f"Response:\n{output}\n")

if "55" in output:
    print("✓ TEST PASSED - Got expected result '55'")
else:
    print(f"✗ TEST FAILED - Expected '55' in output")
    sys.exit(1)
