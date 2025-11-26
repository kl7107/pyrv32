#!/usr/bin/env python3
"""
Run to breakpoint and check memory
"""

import sys
sys.path.insert(0, '/home/dev/git/zesarux/pyrv32')

from cpu import RV32CPU
from memory import Memory
from debugger import Debugger, Breakpoint

# Setup
mem = Memory()
cpu = RV32CPU()
cpu.mem = mem  # RV32CPU doesn't take mem in __init__

# Load binary
with open('nethack-3.4.3/src/nethack.bin', 'rb') as f:
    data = f.read()
    for i, byte in enumerate(data):
        mem.write_byte(0x80000000 + i, byte)

cpu.pc = 0x80000000

# Create breakpoint: stop when s4 becomes 0x80000000
dbg = Debugger(cpu, mem, trace_size=200000)
dbg.bpm.add(Breakpoint(reg_name='s4', reg_value=0x80000000))

print("Running until s4=0x80000000...")
instruction_count = 0

while True:
    should_stop, reason = dbg.should_break(cpu.pc, False, cpu.regs)
    
    if should_stop:
        print(f"\n{'='*70}")
        print(f"STOPPED: {reason}")
        print(f"{'='*70}")
        print(f"Instruction count: {instruction_count}")
        print(f"PC: 0x{cpu.pc:08x}")
        print(f"s4: 0x{cpu.regs[20]:08x}")
        print(f"a0: 0x{cpu.regs[10]:08x}")
        print()
        
        # Check what's at a0+8
        addr = cpu.regs[10] + 8
        value = mem.read_word(addr)
        print(f"Memory at a0+8 (0x{addr:08x}): 0x{value:08x}")
        print()
        
        # Show context
        print("Memory context:")
        for i in range(-4, 4):
            a = addr + i*4
            v = mem.read_word(a)
            marker = " <-- a0+8" if i == 0 else ""
            print(f"  0x{a:08x}: 0x{v:08x}{marker}")
        
        break
    
    cpu.step()
    instruction_count += 1
    dbg.trace_buffer.add(cpu)
    
    if instruction_count % 10000 == 0:
        print(f"  {instruction_count} instructions...")
    
    if instruction_count > 100000:
        print("Timeout")
        break

print("\nDone")
