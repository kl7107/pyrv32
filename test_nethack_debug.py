#!/usr/bin/env python3
"""Test debugger with NetHack - set breakpoint at main()"""
import subprocess
import time

# NetHack main() is at 0x801573cc
main_addr = 0x801573cc

print("Testing debugger with NetHack...")
print(f"Setting breakpoint at main: 0x{main_addr:08x}")

# Create input commands for the debugger
commands = f"""b 0x{main_addr:08x}
c
i
q
"""

print("\nCommands to send:")
print(commands)
print("\nStarting debugger...")

# Run the debugger
proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

# Send commands
stdout, _ = proc.communicate(input=commands, timeout=30)

print("\nOutput:")
print(stdout)

# Check if we hit the breakpoint
if f'0x{main_addr:08x}' in stdout and 'Breakpoint' in stdout:
    print("\n✅ SUCCESS: Breakpoint at main() was hit!")
else:
    print("\n❌ FAILED: Breakpoint not hit or not detected")
