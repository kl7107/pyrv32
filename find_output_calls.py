#!/usr/bin/env python3
"""Find where NetHack calls write() for console output"""
import subprocess

# Find the address of the write() syscall
result = subprocess.run(
    ['riscv64-unknown-elf-nm', 'nethack-3.4.3/src/nethack.elf'],
    capture_output=True,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

write_addr = None
for line in result.stdout.splitlines():
    if ' write' in line or line.endswith(' write'):
        parts = line.split()
        if len(parts) >= 3 and parts[2] == 'write':
            write_addr = int(parts[0], 16)
            print(f"Found write() at 0x{write_addr:08x}")
            break

if not write_addr:
    print("ERROR: Could not find write() function!")
    exit(1)

# Also find putchar, puts, printf
print("\nSearching for output functions...")
for func_name in ['putchar', 'puts', 'printf', 'putc', 'fputc', 'fputs']:
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2] == func_name:
            addr = int(parts[0], 16)
            print(f"  {func_name:10s} at 0x{addr:08x}")
            break

print(f"\n\nSetting breakpoint at write() and stepping through NetHack...")

commands = f"""b 0x801573cc
c
b 0x{write_addr:08x}
c
i
q
"""

print("Commands:")
print(commands)

proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

stdout, _ = proc.communicate(input=commands, timeout=60)

print("\n" + "=" * 70)
print("Debugger output (last 60 lines):")
print("=" * 70)
lines = stdout.splitlines()
for line in lines[-60:]:
    print(line)
