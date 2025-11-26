#!/usr/bin/env python3
"""
Demonstration of the tsr (trace search reverse) command.
Shows how to search backwards through trace buffer for specific register values.
"""

import subprocess
import time

def demo():
    print("=" * 70)
    print("TSR (Trace Search Reverse) Command Demo")
    print("=" * 70)
    print()
    print("The tsr command searches backwards through the trace buffer")
    print("to find when a register had a specific value.")
    print()
    print("Syntax: tsr <regname> <value> [<start_index>]")
    print()
    print("Examples:")
    print("  tsr pc 0x80000000        - Find when PC was at _start")
    print("  tsr a0 0                 - Find when a0 was 0")
    print("  tsr s4 0x80000000        - Find when s4 was set to _start")
    print("  tsr ra 0x800001a8 100    - Search from index 100 backwards")
    print()
    print("The trace buffer uses a monotonic index counter that starts at 0")
    print("and increments for each instruction. The index is preserved even")
    print("as old entries are dropped from the ring buffer.")
    print()
    print("=" * 70)
    print()
    
    # Test with hello.bin
    print("Running demo with hello.bin (50 instructions)...")
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '1000', '--step', 'firmware/hello.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Step through 50 instructions
    proc.stdin.write('s 50\n')
    proc.stdin.flush()
    time.sleep(1.0)
    
    # Show trace info
    print("\n1. Check trace buffer status:")
    print("   Command: t info")
    proc.stdin.write('t info\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Search for PC at _start (0x80000000)
    print("\n2. Find when PC was at _start (0x80000000):")
    print("   Command: tsr pc 0x80000000")
    proc.stdin.write('tsr pc 0x80000000\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Search for a0 = 0
    print("\n3. Find when a0 was 0:")
    print("   Command: tsr a0 0")
    proc.stdin.write('tsr a0 0\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Search for a value that doesn't exist
    print("\n4. Search for value that doesn't exist:")
    print("   Command: tsr pc 0xdeadbeef")
    proc.stdin.write('tsr pc 0xdeadbeef\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Show current registers
    print("\n5. Show current registers:")
    print("   Command: r")
    proc.stdin.write('r\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Quit
    proc.stdin.write('q\n')
    proc.stdin.flush()
    
    # Read all output
    time.sleep(0.5)
    output = proc.stdout.read()
    
    # Print output
    print("\n" + "=" * 70)
    print("Output:")
    print("=" * 70)
    print(output)
    
    proc.wait()
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print()
    print("Key features:")
    print("  ✓ Monotonic index counter (never resets except on 't clear')")
    print("  ✓ Search backwards from end or from specific index")
    print("  ✓ Supports all register names (a0-a7, s0-s11, t0-t6, ra, sp, etc.)")
    print("  ✓ Also supports PC searches")
    print("  ✓ Values can be hex (0x...) or decimal")
    print("  ✓ Shows complete trace entry when found")
    print("=" * 70)

if __name__ == '__main__':
    demo()
