#!/usr/bin/env python3
"""
Watch all writes around 0x801a3c2c
"""

import sys
sys.path.insert(0, '/home/dev/git/zesarux/pyrv32')

from cpu import RV32CPU
from memory import Memory  
from execute import execute_instruction

mem = Memory()
cpu = RV32CPU()

# Load binary
with open('nethack-3.4.3/src/nethack.bin', 'rb') as f:
    data = f.read()
    for i, byte in enumerate(data):
        mem.write_byte(0x80000000 + i, byte)

cpu.pc = 0x80000000

# Watch a range around target
watch_start = 0x801a3c20
watch_end = 0x801a3c40

print(f"Watching memory 0x{watch_start:08x} - 0x{watch_end:08x}")
print(f"Looking for when 0x801a3c2c becomes 0x80000000")
print()

instruction_count = 0
write_count = 0

# Save initial state
old_mem = {}
for addr in range(watch_start, watch_end, 4):
    old_mem[addr] = mem.read_word(addr)

while instruction_count < 100000:
    insn = mem.read_word(cpu.pc)
    pc_before = cpu.pc
    execute_instruction(cpu, mem, insn)
    
    # Check all watched addresses
    for addr in range(watch_start, watch_end, 4):
        new_val = mem.read_word(addr)
        if new_val != old_mem[addr]:
            write_count += 1
            print(f"[{instruction_count:6d}] Write at 0x{addr:08x}: 0x{old_mem[addr]:08x} -> 0x{new_val:08x}  (PC=0x{pc_before:08x})")
            old_mem[addr] = new_val
            
            # Check if this made 0x801a3c2c become 0x80000000
            target_val = mem.read_word(0x801a3c2c)
            if target_val == 0x80000000 and write_count <= 20:
                print(f"  >>> 0x801a3c2c is now 0x80000000!")
                print()
                print("Current memory state:")
                for a in range(watch_start, watch_end, 4):
                    v = mem.read_word(a)
                    marker = " <-- TARGET" if a == 0x801a3c2c else ""
                    print(f"  0x{a:08x}: 0x{v:08x}{marker}")
                
                if write_count == 20:
                    print("\nStopping after 20 writes...")
                    print(f"Instruction count: {instruction_count}")
                    sys.exit(0)
    
    instruction_count += 1
    if instruction_count % 10000 == 0:
        print(f"  ... {instruction_count} instructions ...")

print(f"\nDone after {instruction_count} instructions, {write_count} writes detected")
