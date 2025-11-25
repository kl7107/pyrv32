"""
Unit Tests for Decoder and Execution

Tests instruction decoding and execution.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cpu import RV32CPU
from memory import Memory
from decoder import decode_instruction, get_instruction_name
from execute import execute_instruction


def run_decoder_tests():
    """Run decoder and execution tests."""
    log_file = tempfile.NamedTemporaryFile(mode='w', delete=False,
                                           prefix='pyrv32_test_decoder_', suffix='.log')
    log_path = log_file.name
    
    def log(msg):
        log_file.write(msg + '\n')
        log_file.flush()
    
    def test_fail(test_name, expected, actual, context=""):
        log(f"\n{'=' * 60}")
        log(f"TEST FAILED: {test_name}")
        log(f"Expected: {expected}")
        log(f"Actual:   {actual}")
        if context:
            log(f"Context:  {context}")
        log(f"Log file: {log_path}")
        log(f"{'=' * 60}\n")
        log_file.close()
        print(f"\n{'=' * 60}")
        print(f"TEST FAILED: {test_name}")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        if context:
            print(f"Context:  {context}")
        print(f"Log file: {log_path}")
        print(f"{'=' * 60}\n")
        sys.exit(1)
    
    log("=" * 60)
    log("Running Decoder/Execute Unit Tests")
    log(f"Log file: {log_path}")
    log("=" * 60)
    
    # Test 1: LUI instruction decode and execute
    log("\nTest 1: LUI (Load Upper Immediate)")
    # lui x10, 0x12345 -> 0x12345000 into x10
    insn = 0x12345537  # opcode=0x37, rd=10, imm=0x12345000
    decoded = decode_instruction(insn)
    name = get_instruction_name(decoded)
    log(f"  Instruction: 0x{insn:08x}")
    log(f"  Name: {name}")
    log(f"  rd={decoded['rd']}, imm=0x{decoded['imm']:08x}")
    
    if name != "LUI":
        test_fail("LUI decode name", "LUI", name)
    if decoded['rd'] != 10:
        test_fail("LUI rd", "10", str(decoded['rd']))
    if decoded['imm'] != 0x12345000:
        test_fail("LUI imm", "0x12345000", f"0x{decoded['imm']:08x}")
    
    cpu = RV32CPU()
    mem = Memory()
    cpu.pc = 0x1000
    execute_instruction(cpu, mem, insn)
    result = cpu.read_reg(10)
    log(f"  After execute: x10=0x{result:08x}, PC=0x{cpu.pc:08x}")
    if result != 0x12345000:
        test_fail("LUI execute", "0x12345000", f"0x{result:08x}")
    if cpu.pc != 0x1004:
        test_fail("LUI PC increment", "0x1004", f"0x{cpu.pc:08x}")
    log("  ✓ PASS")
    
    # Test 2: ADDI instruction decode and execute
    log("\nTest 2: ADDI (Add Immediate)")
    # addi x11, x0, 72 -> x11 = 72 (ASCII 'H')
    insn = 0x04800593  # opcode=0x13, rd=11, rs1=0, imm=72
    decoded = decode_instruction(insn)
    name = get_instruction_name(decoded)
    log(f"  Instruction: 0x{insn:08x}")
    log(f"  Name: {name}")
    log(f"  rd={decoded['rd']}, rs1={decoded['rs1']}, imm={decoded['imm']}")
    
    if name != "ADDI":
        test_fail("ADDI decode name", "ADDI", name)
    if decoded['imm'] != 72:
        test_fail("ADDI imm", "72", str(decoded['imm']))
    
    cpu.reset()
    cpu.pc = 0x1000
    execute_instruction(cpu, mem, insn)
    result = cpu.read_reg(11)
    log(f"  After execute: x11=0x{result:08x} ({result}), PC=0x{cpu.pc:08x}")
    if result != 72:
        test_fail("ADDI execute", "72", str(result))
    log("  ✓ PASS")
    
    # Test 3: SB (Store Byte) instruction and UART
    log("\nTest 3: SB (Store Byte) to UART")
    # sb x11, 0(x10) -> store byte from x11 to address in x10
    insn = 0x00B50023  # opcode=0x23, funct3=0, rs1=10, rs2=11, imm=0
    decoded = decode_instruction(insn)
    name = get_instruction_name(decoded)
    log(f"  Instruction: 0x{insn:08x}")
    log(f"  Name: {name}")
    log(f"  rs1={decoded['rs1']}, rs2={decoded['rs2']}, imm={decoded['imm']}")
    
    if name != "SB":
        test_fail("SB decode name", "SB", name)
    
    cpu.reset()
    mem.reset()
    cpu.write_reg(10, 0x10000000)  # UART address
    cpu.write_reg(11, ord('A'))     # Character to write
    cpu.pc = 0x1000
    
    log(f"  Before: x10=0x{cpu.read_reg(10):08x}, x11=0x{cpu.read_reg(11):02x}")
    execute_instruction(cpu, mem, insn)
    uart_output = mem.get_uart_output()
    log(f"  After execute: UART output = '{uart_output}'")
    
    if uart_output != "A":
        test_fail("SB to UART", "'A'", f"'{uart_output}'")
    log("  ✓ PASS")
    
    # Test 4: Full sequence - output "Hi"
    log("\nTest 4: Full sequence - output 'Hi' to UART")
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
    
    log(f"  Loaded {len(program)} instructions at 0x{cpu.pc:08x}")
    
    for i in range(len(program)):
        insn = mem.read_word(cpu.pc)
        decoded = decode_instruction(insn)
        name = get_instruction_name(decoded)
        log(f"  Step {i+1}: {name} (0x{insn:08x})")
        execute_instruction(cpu, mem, insn)
    
    uart_output = mem.get_uart_output()
    log(f"  Final UART output: '{uart_output}'")
    log(f"  Final PC: 0x{cpu.pc:08x}")
    
    if uart_output != "Hi":
        test_fail("Full program UART", "'Hi'", f"'{uart_output}'")
    log("  ✓ PASS")
    
    log("\n" + "=" * 60)
    log("ALL DECODER/EXECUTE TESTS PASSED ✓")
    log(f"Log file: {log_path}")
    log("=" * 60 + "\n")
    
    log_file.close()
    return log_path


if __name__ == "__main__":
    log_path = run_decoder_tests()
    print(f"Decoder/Execute tests PASSED ✓ (log: {log_path})")
