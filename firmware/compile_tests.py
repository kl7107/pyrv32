#!/usr/bin/env python3
"""Compile test programs for UART testing."""

import subprocess
import os
import sys

# Change to firmware directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

programs = [
    'interpreter_test.c',
]

for prog in programs:
    name = prog.replace('.c', '')
    print(f"Compiling {prog}...")
    
    # Compile
    result = subprocess.run([
        'riscv32-unknown-elf-gcc',
        '-march=rv32im',
        '-mabi=ilp32',
        '-nostdlib',
        '-T', 'link.ld',
        '-o', f'{name}.elf',
        'crt0.S',
        prog,
        'runtime.c'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR compiling {prog}:")
        print(result.stderr)
        sys.exit(1)
    
    # Create binary
    result = subprocess.run([
        'riscv32-unknown-elf-objcopy',
        '-O', 'binary',
        f'{name}.elf',
        f'{name}.bin'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR creating binary for {prog}:")
        print(result.stderr)
        sys.exit(1)
    
    print(f"  Created {name}.bin")

print("\nAll programs compiled successfully!")
