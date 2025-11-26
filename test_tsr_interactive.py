#!/usr/bin/env python3
"""
Simple test of tsr command - interactive test with NetHack
"""

import subprocess
import sys

def main():
    # Start pyrv32 with NetHack and large trace buffer
    cmd = [
        'python3', 'pyrv32.py',
        '--trace-size', '100000',
        '-b', '0x80162c98',  # vfprintf+0x96c
        'nethack-3.4.3/build/nethack'
    ]
    
    print("=" * 70)
    print("Starting NetHack with 100K trace buffer")
    print("Breakpoint at 0x80162c98 (vfprintf+0x96c)")
    print("=" * 70)
    print("\nWhen breakpoint hits, try these commands:")
    print("  tsr s4 0x80000000       - Find when s4 was set to _start")
    print("  r                       - Show current registers")
    print("  t 10                    - Show last 10 trace entries")
    print("  q                       - Quit")
    print("=" * 70)
    print()
    
    # Run interactively
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
