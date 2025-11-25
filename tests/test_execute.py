"""
Unit Tests for Decoder and Execution

Tests instruction decoding and execution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cpu import RV32CPU
from memory import Memory
from decoder import decode_instruction, get_instruction_name
from execute import execute_instruction


def test_lui_decode_and_execute(runner):
    """LUI (Load Upper Immediate) decode and execute"""
    # lui x10, 0x12345 -> 0x12345000 into x10
    insn = 0x12345537  # opcode=0x37, rd=10, imm=0x12345000
    decoded = decode_instruction(insn)
    name = get_instruction_name(decoded)
    runner.log(f"  Instruction: 0x{insn:08x}")
    runner.log(f"  Name: {name}")
    runner.log(f"  rd={decoded['rd']}, imm=0x{decoded['imm']:08x}")
    
    if name != "LUI":
        runner.test_fail("LUI decode name", "LUI", name)
    if decoded['rd'] != 10:
        runner.test_fail("LUI rd", "10", str(decoded['rd']))
    if decoded['imm'] != 0x12345000:
        runner.test_fail("LUI imm", "0x12345000", f"0x{decoded['imm']:08x}")
    
    cpu = RV32CPU()
    mem = Memory()
    cpu.pc = 0x1000
    execute_instruction(cpu, mem, insn)
    result = cpu.read_reg(10)
    runner.log(f"  After execute: x10=0x{result:08x}, PC=0x{cpu.pc:08x}")
    if result != 0x12345000:
        runner.test_fail("LUI execute", "0x12345000", f"0x{result:08x}")
    if cpu.pc != 0x1004:
        runner.test_fail("LUI PC increment", "0x1004", f"0x{cpu.pc:08x}")


def test_addi_decode_and_execute(runner):
    """ADDI (Add Immediate) decode and execute"""
    # addi x11, x0, 72 -> x11 = 72 (ASCII 'H')
    insn = 0x04800593  # opcode=0x13, rd=11, rs1=0, imm=72
    decoded = decode_instruction(insn)
    name = get_instruction_name(decoded)
    runner.log(f"  Instruction: 0x{insn:08x}")
    runner.log(f"  Name: {name}")
    runner.log(f"  rd={decoded['rd']}, rs1={decoded['rs1']}, imm={decoded['imm']}")
    
    if name != "ADDI":
        runner.test_fail("ADDI decode name", "ADDI", name)
    if decoded['imm'] != 72:
        runner.test_fail("ADDI imm", "72", str(decoded['imm']))
    
    cpu = RV32CPU()
    mem = Memory()
    cpu.reset()
    cpu.pc = 0x1000
    execute_instruction(cpu, mem, insn)
    result = cpu.read_reg(11)
    runner.log(f"  After execute: x11=0x{result:08x} ({result}), PC=0x{cpu.pc:08x}")
    if result != 72:
        runner.test_fail("ADDI execute", "72", str(result))


def test_sb_to_uart(runner):
    """SB (Store Byte) to UART"""
    # sb x11, 0(x10) -> store byte from x11 to address in x10
    insn = 0x00B50023  # opcode=0x23, funct3=0, rs1=10, rs2=11, imm=0
    decoded = decode_instruction(insn)
    name = get_instruction_name(decoded)
    runner.log(f"  Instruction: 0x{insn:08x}")
    runner.log(f"  Name: {name}")
    runner.log(f"  rs1={decoded['rs1']}, rs2={decoded['rs2']}, imm={decoded['imm']}")
    
    if name != "SB":
        runner.test_fail("SB decode name", "SB", name)
    
    cpu = RV32CPU()
    mem = Memory()
    cpu.reset()
    mem.reset()
    cpu.write_reg(10, 0x10000000)  # UART address
    cpu.write_reg(11, ord('A'))     # Character to write
    cpu.pc = 0x1000
    
    runner.log(f"  Before: x10=0x{cpu.read_reg(10):08x}, x11=0x{cpu.read_reg(11):02x}")
    execute_instruction(cpu, mem, insn)
    uart_output = mem.get_uart_output()
    runner.log(f"  After execute: UART output = '{uart_output}'")
    
    if uart_output != "A":
        runner.test_fail("SB to UART", "'A'", f"'{uart_output}'")


def test_full_program_output_hi(runner):
    """Full sequence - output 'Hi' to UART"""
    cpu = RV32CPU()
    mem = Memory()
    cpu.reset()
    mem.reset()
    cpu.pc = 0x80000000
    
    # Program: LUI + ADDI to set up UART addr, then ADDI+SB for each char
    program = [
        0x10000537,  # lui  x10, 0x10000  -> x10 = 0x10000000
        0x04800593,  # addi x11, x0, 72   -> x11 = 'H'
        0x00B50023,  # sb   x11, 0(x10)   -> UART = 'H'
        0x06900593,  # addi x11, x0, 105  -> x11 = 'i'
        0x00B50023,  # sb   x11, 0(x10)   -> UART = 'i'
    ]
    
    mem.load_program(cpu.pc, 
                     [b for insn in program for b in [
                         insn & 0xFF, 
                         (insn >> 8) & 0xFF,
                         (insn >> 16) & 0xFF,
                         (insn >> 24) & 0xFF
                     ]])
    
    runner.log(f"  Loaded {len(program)} instructions at 0x{cpu.pc:08x}")
    
    for i in range(len(program)):
        insn = mem.read_word(cpu.pc)
        decoded = decode_instruction(insn)
        name = get_instruction_name(decoded)
        runner.log(f"  Step {i+1}: {name} (0x{insn:08x})")
        execute_instruction(cpu, mem, insn)
    
    uart_output = mem.get_uart_output()
    runner.log(f"  Final UART output: '{uart_output}'")
    runner.log(f"  Final PC: 0x{cpu.pc:08x}")
    
    if uart_output != "Hi":
        runner.test_fail("Full program UART", "'Hi'", f"'{uart_output}'")

