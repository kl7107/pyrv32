#!/usr/bin/env python3
"""
Automated debugging: Find where s4 becomes 0x80000000
"""

import re
import subprocess
import time
import sys

S4_MATCH = re.compile(r's4\(x20\)\s*:\s*0x([0-9a-fA-F]+)')

def main():
    print("=" * 70)
    print("AUTOMATED DEBUGGING: Finding where s4 becomes 0x80000000")
    print("=" * 70)
    print()
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--trace-size', '200000', '--step', 'nethack-3.4.3/src/nethack.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for step prompt
    print("Waiting for debugger to start...")
    output = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        output.append(line)
        if '(pyrv32-dbg)' in line:
            print("✓ Debugger ready")
            break
    
    # Set conditional breakpoint
    print("\nSetting conditional breakpoint: bcond s4 0x80000000")
    proc.stdin.write('bcond s4 0x80000000\n')
    proc.stdin.flush()
    time.sleep(0.3)
    
    # Read confirmation
    for _ in range(5):
        line = proc.stdout.readline()
        if 'Breakpoint' in line:
            print(f"✓ {line.strip()}")
            break
    
    # Continue execution
    print("\n" + "=" * 70)
    print("Running until s4=0x80000000...")
    print("=" * 70)
    proc.stdin.write('c\n')
    proc.stdin.flush()
    
    # Wait for breakpoint hit
    breakpoint_found = False
    bp_pc = None
    step_num = None
    
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        
        if 'Breakpoint' in line and 'hit' in line:
            print(f"\n✓ {line.strip()}")
            breakpoint_found = True
        elif breakpoint_found and 'PC=' in line:
            match = S4_MATCH.search(line)
            if match and int(match.group(1), 16) == 0x80000000:
                if 'PC=0x' in line:
                    pc_start = line.index('PC=0x') + 5
                    bp_pc = line[pc_start:pc_start+8]
                print(line.strip())
        elif breakpoint_found and '0x' in line and ':' in line and '(' in line:
            # This is the instruction line
            print(line.strip())
        elif breakpoint_found and '(pyrv32-dbg)' in line:
            break
    
    if not breakpoint_found:
        print("\n✗ Breakpoint never hit! s4 never becomes 0x80000000 in trace")
        proc.terminate()
        return
    
    print("\n" + "=" * 70)
    print("ANALYZING THE INSTRUCTION")
    print("=" * 70)
    
    # Show disassembly
    proc.stdin.write('x\n')
    proc.stdin.flush()
    time.sleep(0.2)
    
    for _ in range(5):
        line = proc.stdout.readline()
        if '0x' in line and ':' in line:
            print(f"\nInstruction: {line.strip()}")
            break
    
    # Show last 5 trace entries
    print("\n" + "=" * 70)
    print("LAST 5 INSTRUCTIONS BEFORE s4 WAS SET")
    print("=" * 70)
    proc.stdin.write('t 5\n')
    proc.stdin.flush()
    time.sleep(1.0)
    
    trace_lines = []
    for _ in range(100):
        line = proc.stdout.readline()
        if not line:
            break
        trace_lines.append(line)
        if '(pyrv32-dbg)' in line:
            break
    
    # Print trace
    for line in trace_lines:
        if line.strip() and not line.strip().startswith('(pyrv32-dbg)'):
            print(line.rstrip())
    
    # Get full register dump
    print("\n" + "=" * 70)
    print("ALL REGISTERS AT BREAKPOINT")
    print("=" * 70)
    proc.stdin.write('r\n')
    proc.stdin.flush()
    time.sleep(0.2)
    
    for _ in range(20):
        line = proc.stdout.readline()
        if not line:
            break
        if line.strip() and not line.strip().startswith('(pyrv32-dbg)'):
            print(line.rstrip())
        if '(pyrv32-dbg)' in line:
            break
    
    # Quit
    proc.stdin.write('q\n')
    proc.stdin.flush()
    
    try:
        proc.wait(timeout=2)
    except:
        proc.terminate()
    
    print("\n" + "=" * 70)
    print("DEBUGGING COMPLETE")
    print("=" * 70)
    if bp_pc:
        print(f"\n✓ Found: s4 was set to 0x80000000 at PC=0x{bp_pc}")
        print(f"  Check the instruction and trace above to see exactly what happened!")

if __name__ == '__main__':
    main()
