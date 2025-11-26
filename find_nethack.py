#!/usr/bin/env python3
"""Find NetHack binary and ELF files"""
import os
import subprocess
from pathlib import Path

# Find nethack files
print("Searching for NetHack files...")
for root, dirs, files in os.walk('.'):
    for f in files:
        if f in ['nethack.bin', 'nethack.elf']:
            full_path = os.path.join(root, f)
            size = os.path.getsize(full_path)
            print(f"Found: {full_path} ({size:,} bytes)")
            
            # If it's the ELF file, try to find main address
            if f == 'nethack.elf':
                print(f"\nSearching for main() in {full_path}...")
                try:
                    result = subprocess.run(
                        ['riscv64-unknown-elf-nm', full_path],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        for line in result.stdout.splitlines():
                            if ' main' in line or line.endswith(' main'):
                                print(f"  {line}")
                except Exception as e:
                    print(f"  Error running nm: {e}")
