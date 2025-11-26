#!/usr/bin/env python3
"""
Use tsrneq to find when s4 had a VALID value (not 0x80000000)
This will show us what s4 should have been before corruption
"""

import subprocess

def main():
    cmd = [
        'python3', 'pyrv32.py',
        '--trace-size', '200000',
        '-b', '0x80162c98',  # vfprintf+0x96c where it crashes
        'nethack-3.4.3/src/nethack.bin'
    ]
    
    print("=" * 70)
    print("Finding when s4 had a VALID function pointer")
    print("=" * 70)
    print()
    print("Starting NetHack with 200K trace buffer")
    print("Breakpoint at 0x80162c98 (vfprintf+0x96c - the crash point)")
    print()
    print("When breakpoint hits, will use:")
    print("  tsrneq s4 0x80000000   - Find when s4 was NOT _start")
    print()
    print("This will show us the correct function pointer value!")
    print("=" * 70)
    print()
    
    # Run interactively
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
