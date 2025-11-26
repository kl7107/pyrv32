#!/usr/bin/env python3
"""
Test the tsr (trace search reverse) command with NetHack.
"""

import sys
import subprocess
import time

def test_tsr():
    """Test trace search reverse command"""
    
    # Build command with large trace buffer and breakpoint at vfprintf crash point
    cmd = [
        'python3', 'pyrv32.py',
        '--trace-size', '100000',
        '-b', '0x80162c98',  # vfprintf+0x96c where it crashes
        'nethack-3.4.3/build/nethack'
    ]
    
    print("Starting NetHack with breakpoint at vfprintf+0x96c (0x80162c98)...")
    print("Will use 'tsr s4 0x80000000' to find when s4 was set to _start")
    print()
    
    # Start process
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    try:
        # Wait for first breakpoint hit
        print("Waiting for breakpoint...")
        output = []
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            output.append(line)
            print(line, end='')
            
            if 'Breakpoint' in line and 'hit' in line:
                print("\n=== Breakpoint hit! ===\n")
                break
        
        # Now send tsr command to search backwards for s4=0x80000000
        print("Sending command: tsr s4 0x80000000")
        proc.stdin.write("tsr s4 0x80000000\n")
        proc.stdin.flush()
        
        # Read result
        print("\n=== TSR Command Output ===\n")
        for _ in range(50):  # Read up to 50 lines of output
            line = proc.stdout.readline()
            if not line:
                break
            print(line, end='')
            if 'debug>' in line:
                break
        
        # Also try searching for when s4 was NOT 0x80000000
        print("\n\nNow searching for s4 != 0x80000000 (should find initialization)...")
        print("Sending command: r")
        proc.stdin.write("r\n")
        proc.stdin.flush()
        
        for _ in range(20):
            line = proc.stdout.readline()
            if not line:
                break
            print(line, end='')
            if 'debug>' in line:
                break
        
        # Quit
        print("\nQuitting...")
        proc.stdin.write("q\n")
        proc.stdin.flush()
        
        # Wait for exit
        proc.wait(timeout=5)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        proc.terminate()
    except Exception as e:
        print(f"\nError: {e}")
        proc.terminate()
    
    print("\nTest complete!")

if __name__ == '__main__':
    test_tsr()
