#!/usr/bin/env python3
"""
Automated debugging with expect-like interface
"""

import subprocess
import time
import select
import sys

def send_command(proc, cmd, wait=0.5):
    """Send command and wait"""
    try:
        proc.stdin.write(cmd + '\n')
        proc.stdin.flush()
        time.sleep(wait)
        return True
    except:
        return False

def read_until(proc, marker, timeout=5.0):
    """Read output until marker found or timeout"""
    output = []
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            output.append(line)
            if marker in line:
                return output, True
        except:
            break
    
    return output, False

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
    
    # Wait for prompt
    print("Waiting for debugger...")
    output, found = read_until(proc, '(pyrv32-dbg)', timeout=10.0)
    if not found:
        print("✗ Debugger didn't start")
        proc.terminate()
        return
    print("✓ Debugger ready\n")
    
    # Set conditional breakpoint
    print("Setting: bcond s4 0x80000000")
    if not send_command(proc, 'bcond s4 0x80000000', wait=1.0):
        print("✗ Failed to send command")
        proc.terminate()
        return
    
    # Read confirmation
    output, found = read_until(proc, '(pyrv32-dbg)', timeout=2.0)
    for line in output:
        if 'Breakpoint' in line:
            print(f"✓ {line.strip()}")
    
    # Continue
    print("\nContinuing execution...")
    if not send_command(proc, 'c', wait=2.0):
        print("✗ Failed to continue")
        proc.terminate()
        return
    
    # Wait for breakpoint (this might take a while)
    print("Waiting for s4=0x80000000... (this may take 30-60 seconds)")
    output, found = read_until(proc, '(pyrv32-dbg)', timeout=120.0)
    
    if not found:
        print("✗ Timeout or no breakpoint hit")
        proc.terminate()
        return
    
    # Check if breakpoint was hit
    bp_hit = False
    for line in output:
        print(line.rstrip())
        if 'Breakpoint' in line and 'hit' in line:
            bp_hit = True
    
    if not bp_hit:
        print("\n✗ s4 never became 0x80000000")
        proc.terminate()
        return
    
    print("\n" + "=" * 70)
    print("SUCCESS! Analyzing...")
    print("=" * 70)
    
    # Show last 5 trace entries
    print("\nGetting trace history...")
    send_command(proc, 't 5', wait=2.0)
    output, _ = read_until(proc, '(pyrv32-dbg)', timeout=5.0)
    for line in output:
        if line.strip() and '(pyrv32-dbg)' not in line:
            print(line.rstrip())
    
    # Quit
    send_command(proc, 'q', wait=0.5)
    proc.wait(timeout=2)
    
    print("\n" + "=" * 70)
    print("DEBUGGING COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()
