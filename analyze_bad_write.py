#!/usr/bin/env python3
"""
Analyze the instruction that wrote 0x80000000 to 0x801a3c2c
"""

import sys
sys.path.insert(0, '/home/dev/git/zesarux/pyrv32')

from memory import Memory
from decoder import decode_instruction

# Load binary
mem = Memory()
with open('nethack-3.4.3/src/nethack.bin', 'rb') as f:
    data = f.read()
    for i, byte in enumerate(data):
        mem.write_byte(0x80000000 + i, byte)

# The instruction that wrote the bad value
bad_pc = 0x800005d0

# Read and decode
insn = mem.read_word(bad_pc)
decoded = decode_instruction(insn)

print(f"Instruction at PC=0x{bad_pc:08x}:")
print(f"  Raw: 0x{insn:08x}")
print(f"  Decoded: {decoded}")
print()

# Manual decode for STORE
opcode = insn & 0x7F
rs1 = (insn >> 15) & 0x1F
rs2 = (insn >> 20) & 0x1F
imm_4_0 = (insn >> 7) & 0x1F
imm_11_5 = (insn >> 25) & 0x7F
imm = (imm_11_5 << 5) | imm_4_0
# Sign extend 12-bit
if imm & 0x800:
    imm = imm - 0x1000

reg_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5',
             'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']

if opcode == 0x23:  # STORE
    funct3 = (insn >> 12) & 0x7
    store_ops = ['SB', 'SH', 'SW', '?', '?', '?', '?', '?']
    print(f"Store operation: {store_ops[funct3]}")
    print(f"  Base reg (rs1): x{rs1} ({reg_names[rs1]})")
    print(f"  Value reg (rs2): x{rs2} ({reg_names[rs2]})")
    print(f"  Offset: {imm} (0x{imm & 0xFFF:x})")
    print()
    print(f"Assembly: {store_ops[funct3]} {reg_names[rs2]}, {imm}({reg_names[rs1]})")
    print(f"Meaning: memory[{reg_names[rs1]} + {imm}] = {reg_names[rs2]}")
    print()
    print(f"From previous output, registers at this point were:")
    regs = [0x00000000, 0x80157318, 0x807fffa0, 0x00000000, 
            0x801a3c1a, 0x8016060c, 0xfffffff0, 0x00000000,
            0x801964b8, 0x00000001, 0xffffffff, 0x00000001,
            0x80196563, 0x00000001, 0x00000002, 0x801a3c2a,
            0x801595c8, 0x80159038, 0x00000000, 0x00000000,
            0x00000000, 0x00000000, 0x801c1a08, 0x00000000,
            0x00000000, 0x00000000, 0x00000000, 0x00000000,
            0x00000000, 0x00000000, 0x00000000, 0x00000000]
    
    print(f"  {reg_names[rs1]} = 0x{regs[rs1]:08x}")
    print(f"  {reg_names[rs2]} = 0x{regs[rs2]:08x}")
    print(f"  Address = 0x{regs[rs1]:08x} + {imm} = 0x{regs[rs1] + imm:08x}")
    print(f"  Value written = 0x{regs[rs2]:08x}")
    
    # Verify
    if regs[rs1] + imm == 0x801a3c2c:
        print(f"\n✓ This matches! Wrote to 0x801a3c2c")
    if regs[rs2] == 0x80000000:
        print(f"✓ And wrote value 0x80000000")
        print(f"\n**PROBLEM**: {reg_names[rs2]} contains 0x80000000 (_start address)")
        print(f"This register should contain a valid function pointer, not _start!")
