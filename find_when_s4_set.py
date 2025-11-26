#!/usr/bin/env python3
"""
Find WHEN s4 becomes 0x80000000 by stepping and checking trace
"""

import subprocess
import time

def main():
    print("=" * 70)
    print("Finding when s4 changes from 0 to 0x80000000")
    print("=" * 70)
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '100000', '--step', 'nethack-3.4.3/src/nethack.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for initial step
    for line in iter(proc.stdout.readline, ''):
        if '(pyrv32-dbg)' in line:
            break
    
    # Step 1000 instructions
    print("Stepping 1000 instructions...")
    proc.stdin.write('s 1000\n')
    proc.stdin.flush()
    time.sleep(2.0)
    
    # Consume output
    for _ in range(20):
        proc.stdout.readline()
    
    # Now use tsr to find when s4 became 0x80000000
    print("\nSearching backwards for s4=0x80000000...")
    proc.stdin.write('tsr s4 0x80000000\n')
    proc.stdin.flush()
    time.sleep(2.0)
    
    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    
    output = []
    for _ in range(60):
        line = proc.stdout.readline()
        if not line:
            break
        output.append(line)
        print(line.rstrip())
        if '(pyrv32-dbg)' in line:
            break
    
    # Quit
    try:
        proc.stdin.write('q\n')
        proc.stdin.flush()
        proc.wait(timeout=3)
    except:
        proc.terminate()
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS:")
    print("=" * 70)
    
    for line in output:
        if 'Found s4=0x80000000' in line:
            print(f"\n✓ {line.strip()}")
            # Look for index
            if 'index' in line:
                parts = line.split('index')
                if len(parts) > 1:
                    idx_part = parts[1].split()[0]
                    print(f"\n  s4 was set to 0x80000000 at instruction index: {idx_part}")
                    print(f"  Now we know WHICH instruction did this!")
            break
        elif 'not found' in line.lower() and 's4' in line:
            print(f"\n✗ {line.strip()}")
            print("\n  s4 never became 0x80000000 in first 1000 instructions")
            print("  Need to step more instructions...")

if __name__ == '__main__':
    main()
