#!/usr/bin/env python3
"""
Check s4 value at reset BEFORE executing any instructions
"""

import subprocess
import time

def main():
    print("=" * 70)
    print("Checking s4 at RESET (before any instruction execution)")
    print("=" * 70)
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '1000', '--step', 'nethack-3.4.3/src/nethack.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for step mode prompt
    print("Waiting for step mode to start...")
    for line in iter(proc.stdout.readline, ''):
        print(line.rstrip())
        if '(pyrv32-dbg)' in line or 'debug>' in line.lower():
            print("\n" + "=" * 70)
            print("Step mode ready - NOW checking registers BEFORE first instruction")
            print("=" * 70)
            break
    
    # Show registers immediately (before executing anything)
    time.sleep(0.2)
    print("\nSending command: r")
    proc.stdin.write('r\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Read register dump
    print("\nRegister values at RESET (no instructions executed yet):")
    print("=" * 70)
    reg_output = []
    for _ in range(30):
        line = proc.stdout.readline()
        if not line:
            break
        reg_output.append(line)
        print(line.rstrip())
        if '(pyrv32-dbg)' in line or 'debug>' in line.lower():
            break
    
    # Check PC value
    print("\nSending command: i r  (show PC)")
    proc.stdin.write('i r\n')
    proc.stdin.flush()
    time.sleep(0.3)
    
    for _ in range(10):
        line = proc.stdout.readline()
        if not line:
            break
        print(line.rstrip())
        if '(pyrv32-dbg)' in line:
            break
    
    # Quit
    proc.stdin.write('q\n')
    proc.stdin.flush()
    time.sleep(0.3)
    
    proc.terminate()
    proc.wait(timeout=2)
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS:")
    print("=" * 70)
    
    found_s4 = False
    for line in reg_output:
        if 's4=' in line or 'x20' in line:
            print(f"\nFound s4 line: {line.rstrip()}")
            found_s4 = True
            if 's4=0x80000000' in line:
                print("\n⚠️  s4 = 0x80000000 at RESET!")
                print("    This is WRONG - registers should all be 0 at reset!")
                print("    The CPU or memory is being initialized incorrectly!")
            elif 's4=0x00000000' in line or 's4=0' in line:
                print("\n✓  s4 = 0x00000000 at RESET (correct)")
                print("    Now need to find when it changes to 0x80000000")
    
    if not found_s4:
        print("\nCouldn't find s4 in output - check register dump format")

if __name__ == '__main__':
    main()
