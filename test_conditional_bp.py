#!/usr/bin/env python3
"""
Test conditional breakpoint to find when s4 becomes 0x80000000
"""

import subprocess

def main():
    print("=" * 70)
    print("Using conditional breakpoint to find when s4=0x80000000")
    print("=" * 70)
    print()
    print("Starting NetHack with:")
    print("  --trace-size 200000")
    print("  bcond s4 0x80000000   (conditional breakpoint)")
    print()
    print("This will stop IMMEDIATELY when s4 becomes 0x80000000!")
    print("=" * 70)
    print()
    
    # Run with conditional breakpoint
    subprocess.run([
        'python3', 'pyrv32.py',
        '--trace-size', '200000',
        '--step',  # Start in step mode to set breakpoint
        'nethack-3.4.3/src/nethack.bin'
    ])

if __name__ == '__main__':
    print("When step mode starts, type:")
    print("  bcond s4 0x80000000")
    print("  c")
    print()
    print("Then it will run until s4 becomes 0x80000000 and stop!")
    print("=" * 70)
    print()
    main()
