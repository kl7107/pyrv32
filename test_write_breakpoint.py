#!/usr/bin/env python3
"""Set breakpoint at write() and see if NetHack calls it"""
import subprocess

write_addr = 0x80000098
main_addr = 0x801573cc

print(f"Testing if NetHack calls write() at 0x{write_addr:08x}...")

commands = f"""b 0x{main_addr:08x}
c
s 1
b 0x{write_addr:08x}
c
q
"""

print("Commands:")
print(commands)
print()

proc = subprocess.Popen(
    ['timeout', '60', 'python3', 'pyrv32.py', '--step', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

try:
    stdout, _ = proc.communicate(timeout=65)
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, _ = proc.communicate()
    print("TIMEOUT! NetHack never called write()")
    exit(1)

lines = stdout.splitlines()

# Check if we hit the write breakpoint
write_hit = False
for line in lines:
    if 'Breakpoint 2 hit' in line and f'0x{write_addr:08x}' in line:
        write_hit = True
        break

if write_hit:
    print("✅ SUCCESS! NetHack called write()!")
    print("\nLast 40 lines of output:")
    for line in lines[-40:]:
        print(line)
else:
    print("❌ NetHack did NOT call write() within timeout")
    print("\nLast 40 lines of output:")
    for line in lines[-40:]:
        print(line)
    
    # Check what breakpoints were hit
    bp_hits = [line for line in lines if 'Breakpoint' in line and 'hit' in line]
    print(f"\n\nBreakpoints hit: {len(bp_hits)}")
    for hit in bp_hits[-5:]:
        print(f"  {hit}")
