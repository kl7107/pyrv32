#!/usr/bin/env python3
"""
Simpler automation - using expect
"""

import pexpect
import sys

def main():
    print("=" * 70)
    print("AUTOMATED DEBUGGING: Finding where s4 becomes 0x80000000")
    print("=" * 70)
    print()
    
    # Start with pexpect
    cmd = 'python3 pyrv32.py --trace-size 200000 --step nethack-3.4.3/src/nethack.bin'
    
    print("Starting debugger...")
    child = pexpect.spawn(cmd, encoding='utf-8', timeout=120)
    child.logfile = sys.stdout
    
    # Wait for prompt
    child.expect(r'\(pyrv32-dbg\)')
    print("\n✓ Debugger ready\n")
    
    # Set conditional breakpoint
    print("Setting conditional breakpoint...")
    child.sendline('bcond s4 0x80000000')
    child.expect(r'\(pyrv32-dbg\)')
    print("\n✓ Breakpoint set\n")
    
    # Continue
    print("Continuing execution (this may take 30-60 seconds)...")
    child.sendline('c')
    
    # Wait for breakpoint
    index = child.expect([r'Breakpoint.*hit', pexpect.TIMEOUT, pexpect.EOF], timeout=120)
    
    if index == 0:
        print("\n✓ BREAKPOINT HIT!\n")
        child.expect(r'\(pyrv32-dbg\)')
        
        # Show last trace
        print("\nGetting trace history...")
        child.sendline('t 10')
        child.expect(r'\(pyrv32-dbg\)')
        
        print("\n" + "=" * 70)
        print("DEBUGGING COMPLETE")
        print("=" * 70)
    else:
        print("\n✗ No breakpoint hit or timeout")
    
    child.sendline('q')
    child.close()

if __name__ == '__main__':
    main()
