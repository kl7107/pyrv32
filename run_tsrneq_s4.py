#!/usr/bin/env python3
"""
Automated script to find when s4 was NOT 0x80000000
"""

import re
import subprocess
import time

S4_PATTERN = re.compile(r's4\(x20\)\s*:\s*0x([0-9a-fA-F]+)')

def main():
    print("=" * 70)
    print("Automated tsrneq search for valid s4 value")
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
    print("Waiting for breakpoint to hit...")
    output_lines = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        output_lines.append(line)
        
        if 'Breakpoint 1 hit' in line:
            print(f"✓ {line.strip()}")
            # Read a few more lines to get past the breakpoint message
            for _ in range(5):
                line = proc.stdout.readline()
                output_lines.append(line)
            break
    
    # Now send tsrneq command
    print("\nSending command: tsrneq s4 0x80000000")
    print("(This may take a moment to search through 78K+ trace entries...)")
    proc.stdin.write('tsrneq s4 0x80000000\n')
    proc.stdin.flush()
    time.sleep(5.0)  # Give it more time to search
    
    # Read result
    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    
    result_lines = []
    for _ in range(60):  # Read up to 60 lines
        line = proc.stdout.readline()
        if not line:
            break
        result_lines.append(line)
        print(line, end='')
        if 'debug>' in line.lower() or '(pyrv32-dbg)' in line:
            break
    
    # Quit
    try:
        proc.stdin.write('q\n')
        proc.stdin.flush()
    except BrokenPipeError:
        pass
    
    try:
        proc.wait(timeout=5)
    except:
        proc.terminate()
    
    print("\n" + "=" * 70)
    print("Analysis:")
    print("=" * 70)
    
    # Parse result
    for line in result_lines:
        if 'Found s4!=' in line and '0x80000000' in line:
            print(f"\n✓ {line.strip()}")
            # Extract the actual s4 value
            match = S4_PATTERN.search(line)
            if match:
                value = match.group(1)
                print(f"\n  The CORRECT s4 value should be: 0x{value}")
                print(f"  But it was corrupted to: 0x80000000 (_start)")
                print(f"\n  This is the function pointer vfprintf should call!")
            break
    else:
        print("\nSearching through output...")
        for line in result_lines[:10]:
            print(f"  {line.rstrip()}")

if __name__ == '__main__':
    main()
