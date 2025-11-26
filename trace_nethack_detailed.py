#!/usr/bin/env python3
"""Trace NetHack execution in detail after main()"""
import subprocess

print("Testing NetHack with detailed tracing after main()...")

commands = """b 0x801573cc
c
s 500
q
"""

proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

stdout, _ = proc.communicate(input=commands, timeout=30)

# Show output
lines = stdout.splitlines()
print("\n" + "=" * 70)
print("Output (last 100 lines):")
print("=" * 70)
for line in lines[-100:]:
    print(line)

# Look for getenv calls
print("\n" + "=" * 70)
print("Analyzing function calls...")
print("=" * 70)

getenv_calls = 0
other_calls = {}

for line in lines:
    if 'PC=0x801605f' in line:  # getenv is at 0x801605f0
        getenv_calls += 1
    if 'PC=0x' in line and 'Step complete' in line:
        try:
            pc = int(line.split('PC=0x')[1].split()[0], 16)
            if 0x80160000 <= pc < 0x80170000:  # Library functions area
                other_calls[pc] = other_calls.get(pc, 0) + 1
        except:
            pass

print(f"\ngetenv() calls detected: {getenv_calls}")
print(f"\nOther library function PCs seen:")
for pc, count in sorted(other_calls.items())[:20]:
    print(f"  0x{pc:08x}: {count} times")
