#!/usr/bin/env python3
"""
Check what's at memory address 0x801a3c2c
"""

import sys
sys.path.insert(0, '/home/dev/git/zesarux/pyrv32')

from memory import Memory

# Load NetHack binary
mem = Memory()
with open('nethack-3.4.3/src/nethack.bin', 'rb') as f:
    data = f.read()
    for i, byte in enumerate(data):
        mem.write_byte(0x80000000 + i, byte)

# Read the value at 0x801a3c2c
addr = 0x801a3c2c
value = mem.read_word(addr)

print(f"Memory at 0x{addr:08x} = 0x{value:08x}")
print()

# Check surrounding area
print("Context (16 words around this address):")
for i in range(-8, 8):
    a = addr + i*4
    v = mem.read_word(a)
    marker = " <-- THIS ONE" if i == 0 else ""
    print(f"  0x{a:08x}: 0x{v:08x}{marker}")
