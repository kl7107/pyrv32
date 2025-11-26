#!/usr/bin/env python3
"""Check what code is at the addresses where NetHack appears stuck"""
import subprocess

print("Disassembling addresses where NetHack appears stuck...\n")

addresses = [
    (0x80000020, "Most common stuck address"),
    (0x80000024, "2nd address in pattern"),
    (0x80000028, "3rd address in pattern"),
    (0x8000002c, "4th address in pattern"),
    (0x801605f0, "NetHack code address seen"),
]

for addr, desc in addresses:
    print(f"\n{'='*70}")
    print(f"{desc}: 0x{addr:08x}")
    print('='*70)
    
    # Disassemble with context
    result = subprocess.run(
        ['riscv64-unknown-elf-objdump', '-d', '--start-address', f'0x{addr-8:x}',
         '--stop-address', f'0x{addr+24:x}', 'nethack-3.4.3/src/nethack.elf'],
        capture_output=True,
        text=True,
        cwd='/home/dev/git/zesarux/pyrv32'
    )
    
    if result.returncode == 0:
        # Find the section with our address
        lines = result.stdout.splitlines()
        in_function = False
        for line in lines:
            if line.strip() and not line.startswith('nethack'):
                print(line)
                if f'{addr:08x}' in line:
                    print(" " * 40 + "^^^^^  <<< THIS ADDRESS")
    else:
        print(f"Error disassembling: {result.stderr}")

# Also check what function these addresses belong to
print(f"\n\n{'='*70}")
print("Finding function names...")
print('='*70)

result = subprocess.run(
    ['riscv64-unknown-elf-nm', '-n', 'nethack-3.4.3/src/nethack.elf'],
    capture_output=True,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

if result.returncode == 0:
    symbols = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            try:
                addr_val = int(parts[0], 16)
                symbol_type = parts[1]
                symbol_name = ' '.join(parts[2:])
                if symbol_type in ['T', 't']:  # Text symbols
                    symbols.append((addr_val, symbol_name))
            except:
                pass
    
    # Find which function each address belongs to
    symbols.sort()
    for check_addr, desc in addresses:
        func_name = "unknown"
        func_addr = 0
        for addr_val, name in symbols:
            if addr_val <= check_addr:
                func_name = name
                func_addr = addr_val
            elif addr_val > check_addr:
                break
        
        offset = check_addr - func_addr
        print(f"\n0x{check_addr:08x} ({desc}):")
        print(f"  In function: {func_name} + 0x{offset:x}")
        print(f"  Function starts at: 0x{func_addr:08x}")
