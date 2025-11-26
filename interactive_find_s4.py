#!/usr/bin/env python3
"""
Simple: run to breakpoint, then search for when s4=0x80000000
"""

import subprocess

def main():
    print("Starting NetHack with breakpoint, will search for s4=0x80000000\n")
    
    # Just run interactively
    subprocess.run([
        'python3', 'pyrv32.py',
        '--trace-size', '200000',
        '-b', '0x80162c98',
        'nethack-3.4.3/src/nethack.bin'
    ])

if __name__ == '__main__':
    print("=" * 70)
    print("When breakpoint hits, type:")
    print("  tsr s4 0x80000000")
    print()
    print("This will show you WHEN and WHERE s4 was set to 0x80000000")
    print("=" * 70)
    print()
    main()
