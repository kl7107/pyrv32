#!/usr/bin/env python3
"""
Find when 0x801a3c2c is written
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

# Target address
target_addr = 0x801a3c2c

# Check initial value
initial_value = mem.read_word(target_addr)
print(f"Initial value at 0x{target_addr:08x}: 0x{initial_value:08x}")
print(f"Looking for when it becomes 0x80000000...")
print()

instruction_count = 0
max_instructions = 100000

while instruction_count < max_instructions:
    old_value = mem.read_word(target_addr)
    
    # Execute
    try:
        insn = mem.read_word(cpu.pc)
        execute_instruction(cpu, mem, insn)
    except Exception as e:
        print(f"Exception at instruction {instruction_count}: {e}")
        break
    
    new_value = mem.read_word(target_addr)
    
    # Check if changed
    if new_value != old_value:
        print(f"[{instruction_count:6d}] WRITE DETECTED!")
        print(f"  PC: 0x{cpu.pc - 4:08x}")  # PC already advanced
        print(f"  Old value: 0x{old_value:08x}")
        print(f"  New value: 0x{new_value:08x}")
        
        if new_value == 0x80000000:
            print(f"\n{'='*70}")
            print(f"FOUND IT! Address 0x{target_addr:08x} was set to 0x80000000")
            print(f"{'='*70}")
            print(f"This happened at instruction {instruction_count}")
            print(f"PC: 0x{cpu.pc - 4:08x}")
            print()
            print("Registers:")
            for i in range(0, 32, 4):
                print(f"  x{i:2d}-x{i+3:2d}: {cpu.regs[i]:08x} {cpu.regs[i+1]:08x} {cpu.regs[i+2]:08x} {cpu.regs[i+3]:08x}")
            break
    
    instruction_count += 1
    if instruction_count % 10000 == 0:
        print(f"  {instruction_count} instructions...")

print(f"\nExecuted {instruction_count} instructions")
