#!/usr/bin/env python3
"""Compile and run the comprehensive UART test suite."""

import subprocess
import sys
import os

# Change to the pyrv32 directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("="*60)
print("Step 1: Compiling interpreter_test.c")
print("="*60)

os.chdir('../firmware')

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
print(f"✓ Created interpreter_test.bin ({size} bytes)")

print("\n" + "="*60)
print("Step 2: Running comprehensive UART tests")
print("="*60)

os.chdir('../pyrv32_mcp')
result = subprocess.run([sys.executable, 'test_uart_comprehensive.py'])
sys.exit(result.returncode)
