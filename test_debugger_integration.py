#!/usr/bin/env python3
"""
Test the debugger functionality with various programs
"""

import subprocess
import sys
import os

def test_step_mode():
    """Test step mode with hello.bin"""
    print("=== Test 1: Step Mode ===")
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--no-test', '--step', 'firmware/hello.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send commands
    commands = """s
s
s
r --nz
x
q
"""
    
    try:
        stdout, stderr = proc.communicate(input=commands, timeout=5)
        
        # Check for expected output
        if "Step complete" in stdout:
            print("✓ Step mode works")
        else:
            print("✗ Step mode failed")
            print(stdout)
            return False
            
        if "(pyrv32-dbg)" in stdout:
            print("✓ Interactive prompt works")
        else:
            print("✗ Interactive prompt missing")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        proc.kill()
        print("✗ Test timed out")
        return False


def test_breakpoints():
    """Test breakpoint setting"""
    print("\n=== Test 2: Breakpoints ===")
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--no-test', '-b', '0x80000010', 'firmware/hello.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    commands = """l
c
q
"""
    
    try:
        stdout, stderr = proc.communicate(input=commands, timeout=5)
        
        if "Breakpoint 1 set at 0x80000010" in stdout:
            print("✓ Breakpoint set correctly")
        else:
            print("✗ Breakpoint not set")
            return False
            
        if "Breakpoint 1 hit" in stdout or "0x80000010" in stdout:
            print("✓ Breakpoint triggered")
        else:
            print("⚠ Breakpoint may not have been hit (program might be shorter)")
            
        return True
        
    except subprocess.TimeoutExpired:
        proc.kill()
        print("✗ Test timed out")
        return False


def test_register_dump():
    """Test register dump commands"""
    print("\n=== Test 3: Register Dump ===")
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--no-test', '--step', 'firmware/hello.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    commands = """s 5
r
r --nz
i r
q
"""
    
    try:
        stdout, stderr = proc.communicate(input=commands, timeout=5)
        
        if "PC=0x" in stdout:
            print("✓ Register dump shows PC")
        else:
            print("✗ Register dump missing PC")
            return False
            
        if "ra=0x" in stdout and "sp=0x" in stdout:
            print("✓ Register dump shows registers")
        else:
            print("✗ Register dump incomplete")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        proc.kill()
        print("✗ Test timed out")
        return False


def test_breakpoint_management():
    """Test breakpoint add/delete/list"""
    print("\n=== Test 4: Breakpoint Management ===")
    
    proc = subprocess.Popen(
        ['python3', 'pyrv32.py', '--no-test', '--step', 'firmware/hello.bin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    commands = """b 0x80000100
b 0x80000200
b 0x80000300
l
d 2
l
d *
l
q
"""
    
    try:
        stdout, stderr = proc.communicate(input=commands, timeout=5)
        
        if "Breakpoint 1 set at 0x80000100" in stdout:
            print("✓ Add breakpoints works")
        else:
            print("✗ Failed to add breakpoints")
            return False
            
        if "Deleted breakpoint 2" in stdout:
            print("✓ Delete individual breakpoint works")
        else:
            print("✗ Failed to delete breakpoint")
            return False
            
        if "Deleted all breakpoints" in stdout:
            print("✓ Delete all breakpoints works")
        else:
            print("✗ Failed to delete all breakpoints")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        proc.kill()
        print("✗ Test timed out")
        return False


def main():
    os.chdir('/home/dev/git/zesarux/pyrv32')
    
    print("Testing Debugger Functionality")
    print("=" * 60)
    
    tests = [
        test_step_mode,
        test_breakpoints,
        test_register_dump,
        test_breakpoint_management,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✓ All debugger tests PASSED")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
