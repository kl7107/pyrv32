#!/usr/bin/env python3
"""Compile test programs for UART I/O testing."""

import subprocess
import os

os.chdir('/home/dev/git/zesarux/pyrv32/firmware')

programs = [
    ('echo_test.c', 'echo_test.bin'),
    ('interpreter_test.c', 'interpreter_test.bin')
]

for src, bin_out in programs:
    print(f"Compiling {src}...")
    
    # Compile to object file
    cmd = [
        'riscv64-unknown-elf-gcc',
        '-march=rv32im', '-mabi=ilp32', '-O2',
        '-nostdlib', '-nostartfiles', '-ffreestanding',
        '-T', 'link.ld',
        '-o', bin_out.replace('.bin', '.elf'),
        'crt0.S', 'runtime.c', src
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        continue
    
    # Convert to binary
    cmd = [
        'riscv64-unknown-elf-objcopy',
        '-O', 'binary',
        bin_out.replace('.bin', '.elf'),
        bin_out
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        continue
    
    # Get size
    size = os.path.getsize(bin_out)
    print(f"  ✓ Created {bin_out} ({size} bytes)")

print("\nDone!")
