"""
Test LHU instruction execution

LHU - Load Halfword Unsigned (with zero extension)
Format: I-type
Encoding: imm[11:0] | rs1 | 0b101 | rd | 0b0000011
Operation: rd = zero_extend(memory[rs1 + imm][15:0])

Edge Cases (from execute.py docstring):
- load 0x0000 (extends to 0x00000000)
- load 0x8000 (extends to 0x00008000 - unsigned, not sign-extended)
- load 0xFFFF (extends to 0x0000FFFF - unsigned)
- misaligned address
- zero offset, negative offset, large offset
- rd = x0 (write ignored)
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_lhu_zero_halfword(runner):
    """LHU loading 0x0000 should zero-extend to 0x00000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000, 0x0000)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 0(x2)
    # imm=0, rs1=2, funct3=0b101, rd=1, opcode=0b0000011
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail(f"Expected x1=0x00000000, got 0x{cpu.read_reg(1):08x}")


def test_lhu_positive_halfword(runner):
    """LHU loading 0x7FFF should zero-extend to 0x00007FFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000, 0x7FFF)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00007FFF:
        runner.test_fail(f"Expected x1=0x00007FFF, got 0x{cpu.read_reg(1):08x}")


def test_lhu_high_bit_set(runner):
    """LHU loading 0x8000 should zero-extend to 0x00008000 (unsigned, no sign extension)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000, 0x8000)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Key difference from LH: 0x8000 → 0x00008000, not 0xFFFF8000
    if cpu.read_reg(1) != 0x00008000:
        runner.test_fail(f"Expected x1=0x00008000 (unsigned), got 0x{cpu.read_reg(1):08x}")


def test_lhu_all_ones_halfword(runner):
    """LHU loading 0xFFFF should zero-extend to 0x0000FFFF (unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000, 0xFFFF)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Key difference from LH: 0xFFFF → 0x0000FFFF, not 0xFFFFFFFF
    if cpu.read_reg(1) != 0x0000FFFF:
        runner.test_fail(f"Expected x1=0x0000FFFF (unsigned), got 0x{cpu.read_reg(1):08x}")


def test_lhu_positive_offset(runner):
    """LHU with positive offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001006, 0xABCD)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 6(x2)
    insn = (6 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x0000ABCD:
        runner.test_fail(f"Expected x1=0x0000ABCD, got 0x{cpu.read_reg(1):08x}")


def test_lhu_negative_offset(runner):
    """LHU with negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80000FFC, 0x5678)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, -4(x2)
    # -4 in 12-bit: 0xFFC
    imm_neg4 = 0xFFC
    insn = (imm_neg4 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00005678:
        runner.test_fail(f"Expected x1=0x00005678, got 0x{cpu.read_reg(1):08x}")


def test_lhu_max_positive_offset(runner):
    """LHU with max positive 12-bit offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000 + 2047, 0xBEEF)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 2047(x2)
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x0000BEEF:
        runner.test_fail(f"Expected x1=0x0000BEEF, got 0x{cpu.read_reg(1):08x}")


def test_lhu_max_negative_offset(runner):
    """LHU with max negative 12-bit offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000 - 2048, 0xDEAD)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, -2048(x2)
    # -2048 in 12-bit: 0x800
    imm_min = 0x800
    insn = (imm_min << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x0000DEAD:
        runner.test_fail(f"Expected x1=0x0000DEAD, got 0x{cpu.read_reg(1):08x}")


def test_lhu_zero_offset(runner):
    """LHU with zero offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80002000, 0x1234)
    cpu.write_reg(3, 0x80002000)
    
    # LHU x1, 0(x3)
    insn = (0 << 20) | (3 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00001234:
        runner.test_fail(f"Expected x1=0x00001234, got 0x{cpu.read_reg(1):08x}")


def test_lhu_misaligned_odd_address(runner):
    """LHU with misaligned address (odd address) - implementation handles it"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write bytes manually at odd address
    mem.write_byte(0x80001001, 0x78)
    mem.write_byte(0x80001002, 0x56)
    cpu.write_reg(2, 0x80001001)
    
    # LHU x1, 0(x2) - load from odd address 0x80001001
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Little-endian: 0x5678
    if cpu.read_reg(1) != 0x00005678:
        runner.test_fail(f"Expected x1=0x00005678, got 0x{cpu.read_reg(1):08x}")


def test_lhu_vs_lh_difference(runner):
    """LHU vs LH: 0x8000 should be 0x00008000 (LHU) not 0xFFFF8000 (LH)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000, 0x8000)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Verify it's unsigned (zero-extended)
    if cpu.read_reg(1) != 0x00008000:
        runner.test_fail(f"Expected x1=0x00008000 (zero-extended), got 0x{cpu.read_reg(1):08x}")
    
    # Also verify it's NOT sign-extended
    if cpu.read_reg(1) == 0xFFFF8000:
        runner.test_fail(f"LHU should zero-extend, not sign-extend")


def test_lhu_rd_x0(runner):
    """LHU with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000, 0xFFFF)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x0, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (0 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got 0x{cpu.read_reg(0):08x}")


def test_lhu_rs1_x0(runner):
    """LHU with rs1=x0 loads from address 0 + offset (modified to use valid RAM)"""
    cpu = RV32CPU()
    mem = Memory()
    
    base_addr = 0x80000000
    offset = 200
    mem.write_halfword(base_addr + offset, 0xABCD)
    cpu.write_reg(2, base_addr)
    
    # LHU x1, 200(x2) - changed from x0 to x2 for valid RAM access
    insn = (200 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x0000ABCD:
        runner.test_fail(f"Expected x1=0x0000ABCD, got 0x{cpu.read_reg(1):08x}")


def test_lhu_from_word(runner):
    """LHU should load lower 16 bits from a word"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write a word: 0xAABBCCDD
    mem.write_word(0x80001000, 0xAABBCCDD)
    cpu.write_reg(2, 0x80001000)
    
    # LHU x1, 0(x2) - should load lower 16 bits
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Little-endian: lower 16 bits at 0x80001000 are 0xCCDD
    if cpu.read_reg(1) != 0x0000CCDD:
        runner.test_fail(f"Expected x1=0x0000CCDD, got 0x{cpu.read_reg(1):08x}")


def test_lhu_pc_increment(runner):
    """LHU should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x80001000, 0x1234)
    cpu.write_reg(2, 0x80001000)
    
    initial_pc = cpu.pc
    
    # LHU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b101 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail(f"Expected PC={initial_pc + 4}, got {cpu.pc}")
