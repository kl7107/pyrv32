#!/usr/bin/env python3
"""
Capture exact state when writing to 0x801a3c2c
"""

import sys
sys.path.insert(0, '/home/dev/git/zesarux/pyrv32')

from cpu import RV32CPU
from memory import Memory  
from execute import execute_instruction
from decoder import decode_instruction

mem = Memory()
cpu = RV32CPU()

# Load binary
with open('nethack-3.4.3/src/nethack.bin', 'rb') as f:
    data = f.read()
    for i, byte in enumerate(data):
        mem.write_byte(0x80000000 + i, byte)

cpu.pc = 0x80000000

target_addr = 0x801a3c2c

print(f"Looking for write to 0x{target_addr:08x}...")
instruction_count = 0

while instruction_count < 100000:
    old_value = mem.read_word(target_addr)
    
    # Save state before execution
    saved_pc = cpu.pc
    saved_regs = cpu.regs.copy()
    
    # Read and execute
    insn = mem.read_word(cpu.pc)
    execute_instruction(cpu, mem, insn)
    
    new_value = mem.read_word(target_addr)
    
    # Check if this write made it 0x80000000
    if new_value != old_value and new_value == 0x80000000:
        print(f"\n{'='*70}")
        print(f"FOUND THE BAD WRITE!")
        print(f"{'='*70}")
        print(f"Instruction #{instruction_count}")
        print(f"PC: 0x{saved_pc:08x}")
        print(f"Instruction: 0x{insn:08x}")
        
        decoded = decode_instruction(insn)
        print(f"Decoded: {decoded}")
        print()
        
        # Decode store instruction
        opcode = insn & 0x7F
        rs1 = (insn >> 15) & 0x1F
        rs2 = (insn >> 20) & 0x1F
        imm_4_0 = (insn >> 7) & 0x1F
        imm_11_5 = (insn >> 25) & 0x7F
        imm = (imm_11_5 << 5) | imm_4_0
        if imm & 0x800:
            imm = imm - 0x1000
            
        reg_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5',
                     'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']
        
        print(f"Store details:")
        print(f"  Base reg: {reg_names[rs1]} = 0x{saved_regs[rs1]:08x}")
        print(f"  Value reg: {reg_names[rs2]} = 0x{saved_regs[rs2]:08x}")
        print(f"  Offset: {imm}")
        print(f"  Target address: 0x{saved_regs[rs1] + imm:08x}")
        print(f"  Written value: 0x{saved_regs[rs2]:08x}")
        print()
        print(f"Old value at 0x{target_addr:08x}: 0x{old_value:08x}")
        print(f"New value at 0x{target_addr:08x}: 0x{new_value:08x}")
        
        break
    
    instruction_count += 1
    if instruction_count % 10000 == 0:
        print(f"  {instruction_count} instructions...")

print(f"\nDone after {instruction_count} instructions")
