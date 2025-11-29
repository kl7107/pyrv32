#!/usr/bin/env python3
"""Compile the interpreter test program."""

import subprocess
import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), '../firmware'))

print("Compiling interpreter_test.c...")

# Compile
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

print("Creating binary...")

# Create binary
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

# Check file size
size = os.path.getsize('interpreter_test.bin')
print(f"✓ Created interpreter_test.bin ({size} bytes)")
