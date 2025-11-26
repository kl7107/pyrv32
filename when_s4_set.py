#!/usr/bin/env python3
"""
Find when s4 was SET to 0x80000000
Use tsr to find the FIRST time s4 became 0x80000000
"""

import subprocess
import time

def main():
    print("=" * 70)
    print("Finding when s4 was SET to 0x80000000")
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
    found_bp = False
    for line in iter(proc.stdout.readline, ''):
        if 'Breakpoint 1 hit' in line:
            print(f"✓ {line.strip()}")
            found_bp = True
            # Read a few more lines
            for _ in range(3):
                proc.stdout.readline()
            break
    
    if not found_bp:
        print("Breakpoint not hit!")
        proc.terminate()
        return
    
    # Send tsr command to find s4=0x80000000
    print("\nSearching for when s4=0x80000000...")
    print("(Searching backwards from end...)")
    proc.stdin.write('tsr s4 0x80000000\n')
    proc.stdin.flush()
    
    # Read result with longer timeout
    time.sleep(3.0)
    
    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    
    result = []
    try:
        proc.stdout.read(1)  # Trigger buffering
    except:
        pass
    
    # Force quit and get output
    try:
        proc.stdin.write('q\n')
        proc.stdin.flush()
    except:
        pass
    
    time.sleep(1.0)
    
    # Read remaining output
    remaining = proc.stdout.read()
    print(remaining[:5000])  # Print first 5000 chars
    
    proc.terminate()
    proc.wait()
    
    print("\n" + "=" * 70)
    print("If s4=0x80000000 was found at index 0 or very early,")
    print("it means s4 was NEVER properly initialized!")
    print("This is a BUG in crt0.S or the startup code.")
    print("=" * 70)

if __name__ == '__main__':
    main()
