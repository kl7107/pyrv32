"""
Test LW instruction execution

LW - Load Word (32-bit)
Format: I-type
Encoding: imm[11:0] | rs1 | 0b010 | rd | 0b0000011
Operation: rd = memory[rs1 + imm][31:0]

Edge Cases (from execute.py docstring):
- load all 0s
- load all 1s
- load max positive/negative
- misaligned address (implementation handles it)
- load from different memory regions
- zero offset, negative offset, large offset
- rd = x0 (write ignored)
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_lw_all_zeros(runner):
    """LW loading 0x00000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000, 0x00000000)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, 0(x2)
    # imm=0, rs1=2, funct3=0b010, rd=1, opcode=0b0000011
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail(f"Expected x1=0x00000000, got 0x{cpu.read_reg(1):08x}")


def test_lw_all_ones(runner):
    """LW loading 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000, 0xFFFFFFFF)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail(f"Expected x1=0xFFFFFFFF, got 0x{cpu.read_reg(1):08x}")


def test_lw_max_positive(runner):
    """LW loading max positive 32-bit value (0x7FFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000, 0x7FFFFFFF)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x7FFFFFFF:
        runner.test_fail(f"Expected x1=0x7FFFFFFF, got 0x{cpu.read_reg(1):08x}")


def test_lw_max_negative(runner):
    """LW loading max negative 32-bit value (0x80000000)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000, 0x80000000)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x80000000:
        runner.test_fail(f"Expected x1=0x80000000, got 0x{cpu.read_reg(1):08x}")


def test_lw_positive_offset(runner):
    """LW with positive offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1008, 0x12345678)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, 8(x2)
    insn = (8 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail(f"Expected x1=0x12345678, got 0x{cpu.read_reg(1):08x}")


def test_lw_negative_offset(runner):
    """LW with negative offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x0FFC, 0xABCDEF00)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, -4(x2)
    # -4 in 12-bit: 0xFFC
    imm_neg4 = 0xFFC
    insn = (imm_neg4 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xABCDEF00:
        runner.test_fail(f"Expected x1=0xABCDEF00, got 0x{cpu.read_reg(1):08x}")


def test_lw_max_positive_offset(runner):
    """LW with max positive 12-bit offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000 + 2047, 0xDEADBEEF)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, 2047(x2)
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xDEADBEEF:
        runner.test_fail(f"Expected x1=0xDEADBEEF, got 0x{cpu.read_reg(1):08x}")


def test_lw_max_negative_offset(runner):
    """LW with max negative 12-bit offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000 - 2048, 0xCAFEBABE)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, -2048(x2)
    # -2048 in 12-bit: 0x800
    imm_min = 0x800
    insn = (imm_min << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xCAFEBABE:
        runner.test_fail(f"Expected x1=0xCAFEBABE, got 0x{cpu.read_reg(1):08x}")


def test_lw_zero_offset(runner):
    """LW with zero offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x2000, 0x11223344)
    cpu.write_reg(3, 0x2000)
    
    # LW x1, 0(x3)
    insn = (0 << 20) | (3 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x11223344:
        runner.test_fail(f"Expected x1=0x11223344, got 0x{cpu.read_reg(1):08x}")


def test_lw_misaligned_address(runner):
    """LW with misaligned address (not multiple of 4) - implementation handles it"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write word at misaligned address
    mem.write_byte(0x1001, 0x78)
    mem.write_byte(0x1002, 0x56)
    mem.write_byte(0x1003, 0x34)
    mem.write_byte(0x1004, 0x12)
    cpu.write_reg(2, 0x1001)
    
    # LW x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Little-endian: 0x12345678
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail(f"Expected x1=0x12345678, got 0x{cpu.read_reg(1):08x}")


def test_lw_rd_x0(runner):
    """LW with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000, 0xFFFFFFFF)
    cpu.write_reg(2, 0x1000)
    
    # LW x0, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got 0x{cpu.read_reg(0):08x}")


def test_lw_rs1_x0(runner):
    """LW with rs1=x0 loads from address 0 + offset"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(200, 0x99887766)
    
    # LW x1, 200(x0)
    insn = (200 << 20) | (0 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x99887766:
        runner.test_fail(f"Expected x1=0x99887766, got 0x{cpu.read_reg(1):08x}")


def test_lw_pattern(runner):
    """LW with specific bit pattern"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000, 0xA5A5A5A5)
    cpu.write_reg(2, 0x1000)
    
    # LW x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xA5A5A5A5:
        runner.test_fail(f"Expected x1=0xA5A5A5A5, got 0x{cpu.read_reg(1):08x}")


def test_lw_pc_increment(runner):
    """LW should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_word(0x1000, 0x12345678)
    cpu.write_reg(2, 0x1000)
    
    initial_pc = cpu.pc
    
    # LW x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail(f"Expected PC={initial_pc + 4}, got {cpu.pc}")
