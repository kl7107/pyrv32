"""
Test LBU instruction execution

LBU - Load Byte Unsigned (with zero extension)
Format: I-type
Encoding: imm[11:0] | rs1 | 0b100 | rd | 0b0000011
Operation: rd = zero_extend(memory[rs1 + imm][7:0])

Edge Cases (from execute.py docstring):
- load 0x00 (extends to 0x00000000)
- load 0x80 (extends to 0x00000080 - unsigned, not sign-extended)
- load 0xFF (extends to 0x000000FF - unsigned)
- zero offset, negative offset, large offset
- rd = x0 (write ignored)
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_lbu_zero_byte(runner):
    """LBU loading 0x00 should zero-extend to 0x00000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000, 0x00)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 0(x2)
    # imm=0, rs1=2, funct3=0b100, rd=1, opcode=0b0000011
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail(f"Expected x1=0x00000000, got 0x{cpu.read_reg(1):08x}")


def test_lbu_positive_byte(runner):
    """LBU loading 0x7F should zero-extend to 0x0000007F"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000, 0x7F)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x0000007F:
        runner.test_fail(f"Expected x1=0x0000007F, got 0x{cpu.read_reg(1):08x}")


def test_lbu_high_bit_set(runner):
    """LBU loading 0x80 should zero-extend to 0x00000080 (unsigned, no sign extension)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000, 0x80)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Key difference from LB: 0x80 → 0x00000080, not 0xFFFFFF80
    if cpu.read_reg(1) != 0x00000080:
        runner.test_fail(f"Expected x1=0x00000080 (unsigned), got 0x{cpu.read_reg(1):08x}")


def test_lbu_all_ones_byte(runner):
    """LBU loading 0xFF should zero-extend to 0x000000FF (unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000, 0xFF)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Key difference from LB: 0xFF → 0x000000FF, not 0xFFFFFFFF
    if cpu.read_reg(1) != 0x000000FF:
        runner.test_fail(f"Expected x1=0x000000FF (unsigned), got 0x{cpu.read_reg(1):08x}")


def test_lbu_positive_offset(runner):
    """LBU with positive offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1005, 0xAB)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 5(x2)
    insn = (5 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x000000AB:
        runner.test_fail(f"Expected x1=0x000000AB, got 0x{cpu.read_reg(1):08x}")


def test_lbu_negative_offset(runner):
    """LBU with negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x0FFE, 0xCD)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, -2(x2)
    # -2 in 12-bit: 0xFFE
    imm_neg2 = 0xFFE
    insn = (imm_neg2 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x000000CD:
        runner.test_fail(f"Expected x1=0x000000CD, got 0x{cpu.read_reg(1):08x}")


def test_lbu_max_positive_offset(runner):
    """LBU with max positive 12-bit offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000 + 2047, 0xEF)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 2047(x2)
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x000000EF:
        runner.test_fail(f"Expected x1=0x000000EF, got 0x{cpu.read_reg(1):08x}")


def test_lbu_max_negative_offset(runner):
    """LBU with max negative 12-bit offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000 - 2048, 0x99)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, -2048(x2)
    # -2048 in 12-bit: 0x800
    imm_min = 0x800
    insn = (imm_min << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000099:
        runner.test_fail(f"Expected x1=0x00000099, got 0x{cpu.read_reg(1):08x}")


def test_lbu_zero_offset(runner):
    """LBU with zero offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x2000, 0x42)
    cpu.write_reg(3, 0x2000)
    
    # LBU x1, 0(x3)
    insn = (0 << 20) | (3 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000042:
        runner.test_fail(f"Expected x1=0x00000042, got 0x{cpu.read_reg(1):08x}")


def test_lbu_vs_lb_difference(runner):
    """LBU vs LB: 0x80 should be 0x00000080 (LBU) not 0xFFFFFF80 (LB)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000, 0x80)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Verify it's unsigned (zero-extended)
    if cpu.read_reg(1) != 0x00000080:
        runner.test_fail(f"Expected x1=0x00000080 (zero-extended), got 0x{cpu.read_reg(1):08x}")
    
    # Also verify it's NOT sign-extended
    if cpu.read_reg(1) == 0xFFFFFF80:
        runner.test_fail(f"LBU should zero-extend, not sign-extend")


def test_lbu_rd_x0(runner):
    """LBU with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000, 0xFF)
    cpu.write_reg(2, 0x1000)
    
    # LBU x0, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (0 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got 0x{cpu.read_reg(0):08x}")


def test_lbu_rs1_x0(runner):
    """LBU with rs1=x0 loads from address 0 + offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(150, 0xBE)
    
    # LBU x1, 150(x0)
    insn = (150 << 20) | (0 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x000000BE:
        runner.test_fail(f"Expected x1=0x000000BE, got 0x{cpu.read_reg(1):08x}")


def test_lbu_from_word(runner):
    """LBU should load only one byte from a word"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write a word: 0xAABBCCDD
    mem.write_word(0x1000, 0xAABBCCDD)
    cpu.write_reg(2, 0x1000)
    
    # LBU x1, 0(x2) - should load only lowest byte
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Little-endian: byte at 0x1000 is 0xDD
    if cpu.read_reg(1) != 0x000000DD:
        runner.test_fail(f"Expected x1=0x000000DD, got 0x{cpu.read_reg(1):08x}")


def test_lbu_pc_increment(runner):
    """LBU should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x1000, 0x42)
    cpu.write_reg(2, 0x1000)
    
    initial_pc = cpu.pc
    
    # LBU x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail(f"Expected PC={initial_pc + 4}, got {cpu.pc}")
