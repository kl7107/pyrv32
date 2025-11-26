#!/usr/bin/env python3
"""Step through NetHack main() initialization"""
import subprocess

main_addr = 0x801573cc

print("Stepping through NetHack main()...")

# Create input commands
commands = f"""b 0x{main_addr:08x}
c
s 20
q
"""

print("Commands:")
print(commands)

# Run the debugger
proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

stdout, _ = proc.communicate(input=commands, timeout=30)

print("\nOutput (last 100 lines):")
lines = stdout.splitlines()
for line in lines[-100:]:
    print(line)
