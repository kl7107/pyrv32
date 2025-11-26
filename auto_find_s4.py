#!/usr/bin/env python3
"""
Automatically find when s4 becomes 0x80000000 using conditional breakpoint
"""

import subprocess
import time

def main():
    print("=" * 70)
    print("Finding when s4 becomes 0x80000000 using conditional breakpoint")
    print("=" * 70)
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '200000', '--step', 'nethack-3.4.3/src/nethack.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for step prompt
    for line in iter(proc.stdout.readline, ''):
        print(line.rstrip())
        if '(pyrv32-dbg)' in line:
            break
    
    # Set conditional breakpoint
    print("\nSetting conditional breakpoint: bcond s4 0x80000000")
    proc.stdin.write('bcond s4 0x80000000\n')
    proc.stdin.flush()
    time.sleep(0.2)
    
    # Read confirmation
    for _ in range(3):
        line = proc.stdout.readline()
        print(line.rstrip())
    
    # Continue execution
    print("\nContinuing execution until s4=0x80000000...")
    proc.stdin.write('c\n')
    proc.stdin.flush()
    
    # Wait for breakpoint hit
    print("\nWaiting for breakpoint...\n")
    hit_breakpoint = False
    for line in iter(proc.stdout.readline, ''):
        print(line.rstrip())
        if 'Breakpoint' in line and 'hit' in line:
            hit_breakpoint = True
            # Read a few more lines
            for _ in range(10):
                line = proc.stdout.readline()
                print(line.rstrip())
                if '(pyrv32-dbg)' in line:
                    break
            break
    
    if hit_breakpoint:
        print("\n" + "=" * 70)
        print("SUCCESS! Found where s4 becomes 0x80000000!")
        print("=" * 70)
        print("\nNow examining the instruction that set s4...")
        
        # Show current instruction
        proc.stdin.write('x\n')
        proc.stdin.flush()
        time.sleep(0.2)
        
        for _ in range(5):
            line = proc.stdout.readline()
            print(line.rstrip())
        
        # Show trace context (last 5 entries)
        print("\nLast 5 instructions before s4 was set:")
        proc.stdin.write('t 5\n')
        proc.stdin.flush()
        time.sleep(0.5)
        
        for _ in range(80):
            line = proc.stdout.readline()
            if not line:
                break
            print(line.rstrip())
            if '(pyrv32-dbg)' in line:
                break
    
    # Quit
    try:
        proc.stdin.write('q\n')
        proc.stdin.flush()
        proc.wait(timeout=2)
    except:
        proc.terminate()
    
    print("\n" + "=" * 70)
    print("Investigation complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
