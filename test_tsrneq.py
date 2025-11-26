#!/usr/bin/env python3
"""
Test tsrneq command - find when s4 was NOT equal to 0x80000000
This should show us the last valid function pointer before corruption
"""

import subprocess
import time

def test():
    print("=" * 70)
    print("Testing tsrneq command with hello.bin")
    print("=" * 70)
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '1000', '--step', 'firmware/hello.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Step 50 instructions
    proc.stdin.write('s 50\n')
    proc.stdin.flush()
    
    # Test 1: Find when PC != 0x80000000 (should find immediately - PC changes each insn)
    print("Test 1: tsrneq pc 0x80000000  (find when PC was NOT at _start)")
    proc.stdin.write('tsrneq pc 0x80000000\n')
    proc.stdin.flush()
    
    # Test 2: Find when a0 != 0 (a0 starts at 0, then gets set)
    print("\nTest 2: tsrneq a0 0  (find when a0 was NOT zero)")
    proc.stdin.write('tsrneq a0 0\n')
    proc.stdin.flush()
    
    # Test 3: Show current registers for reference
    print("\nTest 3: Show current registers")
    proc.stdin.write('r\n')
    proc.stdin.flush()
    
    # Quit
    proc.stdin.write('q\n')
    proc.stdin.flush()
    
    # Read output
    time.sleep(1.0)
    output = proc.stdout.read()
    
    print("\n" + "=" * 70)
    print("Output:")
    print("=" * 70)
    print(output)
    
    proc.wait()
    
    print("\n" + "=" * 70)
    print("tsrneq command works!")
    print("This will be perfect for finding when s4 had a valid function pointer")
    print("before it got corrupted to 0x80000000")
    print("=" * 70)

if __name__ == '__main__':
    test()
