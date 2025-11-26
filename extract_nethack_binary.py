#!/usr/bin/env python3
"""
Extract binary from ELF file using objcopy
"""

import subprocess
import os

elf_file = 'nethack-3.4.3/src/nethack.elf'
bin_file = 'nethack-3.4.3/src/nethack.bin'

print(f"Extracting binary from {elf_file}...")

# Use objcopy to extract binary
result = subprocess.run([
    'riscv64-unknown-elf-objcopy',
    '-O', 'binary',
    elf_file,
    bin_file
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"✓ Created {bin_file}")
    # Check file size
    size = os.path.getsize(bin_file)
    print(f"  Size: {size:,} bytes")
else:
    print(f"✗ Error: {result.stderr}")

print("\nNow you can run:")
print(f"  python3 pyrv32.py --trace-size 200000 -b 0x80162c98 {bin_file}")
