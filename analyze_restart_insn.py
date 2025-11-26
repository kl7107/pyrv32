#!/usr/bin/env python3
"""Disassemble the instruction that causes the restart"""
import subprocess

restart_pc = 0x80162c98
restart_insn = 0x000a00e7

print(f"Analyzing restart instruction at PC=0x{restart_pc:08x}")
print(f"Instruction: 0x{restart_insn:08x}")
print()

# Decode JALR instruction
# Format: jalr rd, offset(rs1)
# 0x000a00e7 = 0000 0000 0000 1010 0000 0000 1110 0111
#              imm[11:0]   rs1   000   rd    1100111
# Bits [31:20] = imm = 0x000
# Bits [19:15] = rs1 = 0x14 = 20 (s4)
# Bits [14:12] = funct3 = 000
# Bits [11:7]  = rd = 0x00 (zero register, so no return address saved!)
# Bits [6:0]   = opcode = 1100111 (JALR)

opcode = restart_insn & 0x7F
rd = (restart_insn >> 7) & 0x1F
funct3 = (restart_insn >> 12) & 0x7
rs1 = (restart_insn >> 15) & 0x1F
imm = (restart_insn >> 20) & 0xFFF

# Sign extend imm
if imm & 0x800:
    imm = imm - 0x1000

reg_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2',
             's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5',
             'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7',
             's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']

print(f"Decoded instruction:")
print(f"  Opcode: {opcode:07b} (JALR)")
print(f"  rd: x{rd} ({reg_names[rd]})")
print(f"  rs1: x{rs1} ({reg_names[rs1]})")
print(f"  imm: {imm}")
print(f"  Assembly: jalr {reg_names[rd]}, {imm}({reg_names[rs1]})")
print()

# From trace, s4=0x80000000 at step 78620
print("From trace buffer:")
print("  s4 = 0x80000000 at step 78620")
print(f"  Target address: s4 + {imm} = 0x80000000 + {imm} = 0x{0x80000000 + imm:08x}")
print()
print("This is a jump to _start! (s4 contains the address of _start)")
print()

# Disassemble around this address
print("Disassembling context:")
result = subprocess.run(
    ['riscv64-unknown-elf-objdump', '-d', '--start-address', f'0x{restart_pc-16:x}',
     '--stop-address', f'0x{restart_pc+32:x}', 'nethack-3.4.3/src/nethack.elf'],
    capture_output=True,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

print(result.stdout)

# Find function name
print("\nFinding function name...")
result = subprocess.run(
    ['riscv64-unknown-elf-nm', '-n', 'nethack-3.4.3/src/nethack.elf'],
    capture_output=True,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

symbols = []
for line in result.stdout.splitlines():
    parts = line.split()
    if len(parts) >= 3 and parts[1] in ['T', 't']:
        addr = int(parts[0], 16)
        name = ' '.join(parts[2:])
        symbols.append((addr, name))

symbols.sort()

func_name = "unknown"
func_addr = 0
for addr, name in symbols:
    if addr <= restart_pc:
        func_name = name
        func_addr = addr
    else:
        break

offset = restart_pc - func_addr
print(f"\nFunction: {func_name}")
print(f"Function address: 0x{func_addr:08x}")
print(f"Offset in function: +0x{offset:x}")
print(f"\nThis is a jump from {func_name}+0x{offset:x} to _start!")
