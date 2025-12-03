#!/usr/bin/env python3
"""
Look at the VERY FIRST trace entries to see s4's initial value
"""

import re
import subprocess
import sys

S4_PATTERN = re.compile(r's4\(x20\)\s*:\s*0x([0-9a-fA-F]+)')

def main():
    print("Looking at first trace entries to see when s4 became 0x80000000...")
    print()
    
    # Run with smaller trace to get to breakpoint faster
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '100000', '--step', 'nethack-3.4.3/src/nethack.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for step prompt
    for line in iter(proc.stdout.readline, ''):
        if '(pyrv32-dbg)' in line:
            # Found prompt
            for _ in range(2):
                proc.stdout.readline()
            break
    
    # Step just 1 instruction to get trace entry 0
    print("Stepping 1 instruction...")
    proc.stdin.write('s 1\n')
    proc.stdin.flush()
    
    # Wait for step complete
    import time
    time.sleep(0.5)
    for _ in range(10):
        proc.stdout.readline()
    
    # Now look at first trace entry (index 0)
    print("Looking at trace entry 0...")
    proc.stdin.write('t 0 1\n')
    proc.stdin.flush()
    time.sleep(1.0)
    
    output = []
    for _ in range(50):
        line = proc.stdout.readline()
        if not line:
            break
        output.append(line)
        print(line.rstrip())
        if '(pyrv32-dbg)' in line:
            break
    
    # Check if s4=0x80000000 in first entry
    found_s4 = False
    for line in output:
        match = S4_PATTERN.search(line)
        if match:
            found_s4 = True
            value = int(match.group(1), 16)
            if value == 0x80000000:
                print("\n" + "=" * 70)
                print("FOUND IT! s4=0x80000000 at trace entry 0!")
                print("This means s4 is set to _start on THE VERY FIRST INSTRUCTION!")
                print("=" * 70)
            elif value == 0:
                print("\n" + "=" * 70)
                print("s4=0 at trace entry 0 (correct initialization)")
                print("Need to find when it changes to 0x80000000")
                print("=" * 70)
    
    # Quit
    try:
        proc.stdin.write('q\n')
        proc.stdin.flush()
        proc.wait(timeout=3)
    except:
        proc.terminate()

if __name__ == '__main__':
    main()
