#!/usr/bin/env python3
"""
Test tsr command with a simple program first
"""

import subprocess
import sys

def main():
    # Start pyrv32 with hello.bin and small trace buffer
    cmd = [
        'python3', 'pyrv32.py',
        '--trace-size', '1000',
        '--step',  # Step mode
        'firmware/hello.bin'
    ]
    
    print("=" * 70)
    print("Starting hello.bin in step mode with 1000 entry trace buffer")
    print("=" * 70)
    print("\nCommands to try:")
    print("  s 50                    - Step 50 instructions")
    print("  tsr pc 0x80000000       - Find when PC was at _start")
    print("  tsr a0 0                - Find when a0 was 0")
    print("  r                       - Show current registers")
    print("  t 5                     - Show last 5 trace entries")
    print("  t info                  - Show trace buffer info")
    print("  q                       - Quit")
    print("=" * 70)
    print()
    
    # Run interactively
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
