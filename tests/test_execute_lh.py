"""
Test LH instruction execution

LH - Load Halfword (with sign extension)
Format: I-type
Encoding: imm[11:0] | rs1 | 0b001 | rd | 0b0000011
Operation: rd = sign_extend(memory[rs1 + imm][15:0])

Edge Cases (from execute.py docstring):
- load 0x0000 (extends to 0x00000000)
- load 0x8000 (extends to 0xFFFF8000 - negative)
- load 0x7FFF (extends to 0x00007FFF - max positive)
- load 0xFFFF (extends to 0xFFFFFFFF - -1)
- misaligned address (implementation-defined, we handle it)
- zero offset, negative offset, large offset
- rd = x0 (write ignored)
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_lh_positive_halfword(runner):
    """LH loading positive halfword 0x7FFF should sign-extend to 0x00007FFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write halfword to memory
    mem.write_halfword(0x1000, 0x7FFF)
    
    # Set base address
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 0(x2)
    # imm=0, rs1=2, funct3=0b001, rd=1, opcode=0b0000011
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00007FFF:
        runner.test_fail(f"Expected x1=0x00007FFF, got 0x{cpu.read_reg(1):08x}")


def test_lh_negative_halfword(runner):
    """LH loading negative halfword 0x8000 should sign-extend to 0xFFFF8000"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000, 0x8000)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFF8000:
        runner.test_fail(f"Expected x1=0xFFFF8000, got 0x{cpu.read_reg(1):08x}")


def test_lh_zero_halfword(runner):
    """LH loading 0x0000 should extend to 0x00000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000, 0x0000)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail(f"Expected x1=0x00000000, got 0x{cpu.read_reg(1):08x}")


def test_lh_all_ones_halfword(runner):
    """LH loading 0xFFFF should sign-extend to 0xFFFFFFFF (-1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000, 0xFFFF)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail(f"Expected x1=0xFFFFFFFF, got 0x{cpu.read_reg(1):08x}")


def test_lh_positive_offset(runner):
    """LH with positive offset should add to base address"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1004, 0x1234)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 4(x2)
    insn = (4 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00001234:
        runner.test_fail(f"Expected x1=0x00001234, got 0x{cpu.read_reg(1):08x}")


def test_lh_negative_offset(runner):
    """LH with negative offset should subtract from base address"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x0FFE, 0x5678)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, -2(x2)
    # -2 in 12-bit: 0xFFE
    imm_neg2 = 0xFFE
    insn = (imm_neg2 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00005678:
        runner.test_fail(f"Expected x1=0x00005678, got 0x{cpu.read_reg(1):08x}")


def test_lh_max_positive_offset(runner):
    """LH with max positive 12-bit offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000 + 2047, 0x4242)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 2047(x2)
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00004242:
        runner.test_fail(f"Expected x1=0x00004242, got 0x{cpu.read_reg(1):08x}")


def test_lh_max_negative_offset(runner):
    """LH with max negative 12-bit offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000 - 2048, 0xABCD)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, -2048(x2)
    # -2048 in 12-bit: 0x800
    imm_min = 0x800
    insn = (imm_min << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xABCD sign-extends to 0xFFFFABCD (negative)
    if cpu.read_reg(1) != 0xFFFFABCD:
        runner.test_fail(f"Expected x1=0xFFFFABCD, got 0x{cpu.read_reg(1):08x}")


def test_lh_zero_offset(runner):
    """LH with zero offset (rs1 + 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x2000, 0x1122)
    cpu.write_reg(3, 0x2000)
    
    # LH x1, 0(x3)
    insn = (0 << 20) | (3 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00001122:
        runner.test_fail(f"Expected x1=0x00001122, got 0x{cpu.read_reg(1):08x}")


def test_lh_sign_boundary_0x7FFF(runner):
    """LH at sign boundary: 0x7FFF is max positive signed halfword"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000, 0x7FFF)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00007FFF:
        runner.test_fail(f"Expected x1=0x00007FFF (positive), got 0x{cpu.read_reg(1):08x}")


def test_lh_sign_boundary_0x8000(runner):
    """LH at sign boundary: 0x8000 is min negative signed halfword"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000, 0x8000)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFF8000:
        runner.test_fail(f"Expected x1=0xFFFF8000 (negative), got 0x{cpu.read_reg(1):08x}")


def test_lh_misaligned_odd_address(runner):
    """LH with misaligned address (odd address) - implementation handles it"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write bytes manually at odd address
    mem.write_byte(0x1001, 0x34)
    mem.write_byte(0x1002, 0x12)
    cpu.write_reg(2, 0x1001)
    
    # LH x1, 0(x2) - load from odd address 0x1001
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Little-endian: 0x1234
    if cpu.read_reg(1) != 0x00001234:
        runner.test_fail(f"Expected x1=0x00001234, got 0x{cpu.read_reg(1):08x}")


def test_lh_rd_x0(runner):
    """LH with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000, 0xFFFF)
    cpu.write_reg(2, 0x1000)
    
    # LH x0, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (0 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got 0x{cpu.read_reg(0):08x}")


def test_lh_rs1_x0(runner):
    """LH with rs1=x0 loads from address 0 + offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(100, 0x9ABC)
    
    # LH x1, 100(x0)
    insn = (100 << 20) | (0 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x9ABC sign-extends to 0xFFFF9ABC
    if cpu.read_reg(1) != 0xFFFF9ABC:
        runner.test_fail(f"Expected x1=0xFFFF9ABC, got 0x{cpu.read_reg(1):08x}")


def test_lh_from_word(runner):
    """LH should load 2 bytes from a word, ignoring upper bytes"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write a word: 0xAABBCCDD
    mem.write_word(0x1000, 0xAABBCCDD)
    cpu.write_reg(2, 0x1000)
    
    # LH x1, 0(x2) - should load lower 16 bits
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Little-endian: lower 16 bits at 0x1000 are 0xCCDD, sign-extends to 0xFFFFCCDD
    if cpu.read_reg(1) != 0xFFFFCCDD:
        runner.test_fail(f"Expected x1=0xFFFFCCDD, got 0x{cpu.read_reg(1):08x}")


def test_lh_pc_increment(runner):
    """LH should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_halfword(0x1000, 0x1234)
    cpu.write_reg(2, 0x1000)
    
    initial_pc = cpu.pc
    
    # LH x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b001 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail(f"Expected PC={initial_pc + 4}, got {cpu.pc}")
