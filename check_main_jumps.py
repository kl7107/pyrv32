#!/usr/bin/env python3
"""Check if there are jumps TO main() address"""
import subprocess

main_addr = 0x801573cc

print(f"Searching for jumps TO main() at 0x{main_addr:08x}...")

# Disassemble entire binary and look for jumps/calls to main
result = subprocess.run(
    ['riscv64-unknown-elf-objdump', '-d', 'nethack-3.4.3/src/nethack.elf'],
    capture_output=True,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

jump_to_main = []
for i, line in enumerate(result.stdout.splitlines()):
    # Look for lines that reference main's address
    if f'{main_addr:x}' in line.lower():
        # Get some context
        lines = result.stdout.splitlines()
        context_start = max(0, i-2)
        context_end = min(len(lines), i+3)
        context = '\n'.join(lines[context_start:context_end])
        jump_to_main.append(context)

print(f"\nFound {len(jump_to_main)} references to main():")
print("=" * 70)

for i, ref in enumerate(jump_to_main[:10], 1):  # Show first 10
    print(f"\nReference {i}:")
    print(ref)
    print("-" * 70)

# Also check the disassembly of main itself
print("\n\nDisassembly of main() function (first 50 instructions):")
print("=" * 70)

result = subprocess.run(
    ['riscv64-unknown-elf-objdump', '-d', '--start-address', f'0x{main_addr:x}',
     '--stop-address', f'0x{main_addr+200:x}', 'nethack-3.4.3/src/nethack.elf'],
    capture_output=True,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

print(result.stdout)
