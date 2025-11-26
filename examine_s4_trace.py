#!/usr/bin/env python3
"""
Check trace buffer and look at s4 values throughout execution
"""

import subprocess
import time

def main():
    print("=" * 70)
    print("Examining s4 register throughout trace buffer")
    print("=" * 70)
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '200000', '-b', '0x80162c98', 'nethack-3.4.3/src/nethack.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for breakpoint
    print("Waiting for breakpoint...")
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if 'Breakpoint 1 hit' in line:
            print(f"✓ {line.strip()}")
            for _ in range(5):
                proc.stdout.readline()
            break
    
    # Check trace buffer info
    print("\n1. Checking trace buffer info...")
    proc.stdin.write('t info\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    for _ in range(10):
        line = proc.stdout.readline()
        if not line:
            break
        print(f"  {line.rstrip()}")
        if 'debug>' in line.lower() or '(pyrv32-dbg)' in line:
            break
    
    # Look at first few entries
    print("\n2. Looking at FIRST 3 trace entries...")
    proc.stdin.write('t 0 3\n')
    proc.stdin.flush()
    time.sleep(1.0)
    
    for _ in range(50):
        line = proc.stdout.readline()
        if not line:
            break
        print(line.rstrip())
        if 'debug>' in line.lower() or '(pyrv32-dbg)' in line:
            break
    
    # Look at entries around index 100
    print("\n3. Looking at entries around index 100...")
    proc.stdin.write('t 100 3\n')
    proc.stdin.flush()
    time.sleep(1.0)
    
    for _ in range(50):
        line = proc.stdout.readline()
        if not line:
            break
        print(line.rstrip())
        if 'debug>' in line.lower() or '(pyrv32-dbg)' in line:
            break
    
    # Try searching for s4=0 (initialization value)
    print("\n4. Searching for s4=0 (initialization)...")
    proc.stdin.write('tsr s4 0\n')
    proc.stdin.flush()
    time.sleep(2.0)
    
    for _ in range(50):
        line = proc.stdout.readline()
        if not line:
            break
        print(line.rstrip())
        if 'debug>' in line.lower() or '(pyrv32-dbg)' in line:
            break
    
    # Quit
    try:
        proc.stdin.write('q\n')
        proc.stdin.flush()
        proc.wait(timeout=5)
    except:
        proc.terminate()

if __name__ == '__main__':
    main()
