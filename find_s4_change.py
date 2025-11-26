#!/usr/bin/env python3
"""
Find when s4 changes from 0 to 0x80000000
This will show us WHERE s4 gets corrupted
"""

import subprocess
import time

def main():
    print("=" * 70)
    print("Finding when s4 changed from 0 to 0x80000000")
    print("=" * 70)
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '200000', '-b', '0x80162c98', 'nethack-3.4.3/src/nethack.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for breakpoint
    print("Waiting for breakpoint...")
    for line in iter(proc.stdout.readline, ''):
        if 'Breakpoint 1 hit' in line:
            print(f"✓ {line.strip()}")
            for _ in range(3):
                proc.stdout.readline()
            break
    
    # Search backwards for s4 != 0x80000000 (to find when it was still 0 or different)
    print("\nSearching backwards for when s4 was NOT 0x80000000...")
    print("This will show the last point before corruption...")
    proc.stdin.write('tsrneq s4 0x80000000\n')
    proc.stdin.flush()
    
    time.sleep(5.0)  # Wait for search
    
    print("\nReading output...")
    output_buffer = []
    try:
        # Try to read some output
        for _ in range(100):
            try:
                line = proc.stdout.readline()
                if line:
                    output_buffer.append(line)
                    if len(output_buffer) > 10:
                        break
            except:
                break
    except:
        pass
    
    # Force quit
    try:
        proc.stdin.write('q\n')
        proc.stdin.flush()
    except:
        pass
    
    time.sleep(1.0)
    
    # Get remaining output
    try:
        remaining = proc.stdout.read(10000)
        if remaining:
            output_buffer.append(remaining)
    except:
        pass
    
    print("\n" + "=" * 70)
    print("OUTPUT:")
    print("=" * 70)
    for line in output_buffer:
        print(line.rstrip())
    
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()
    
    print("\n" + "=" * 70)
    print("Analysis:")
    print("If 'not found' - s4 was ALWAYS 0x80000000 in the trace!")
    print("This means it was set BEFORE the first traced instruction.")
    print("Check the CPU initialization or very early startup code.")
    print("=" * 70)

if __name__ == '__main__':
    main()
