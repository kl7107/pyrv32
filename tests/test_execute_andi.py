"""
Test ANDI instruction execution

ANDI - AND Immediate
Format: I-type
Encoding: imm[11:0] | rs1 | 0b111 | rd | 0b0010011
Operation: rd = rs1 & sign_extend(imm)

Edge Cases (from execute.py docstring):
- AND with 0 (clears all)
- AND with -1 (identity)
- bit masking
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_andi_with_zero(runner):
    """ANDI with 0 clears all bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ANDI x1, x2, 0
    # imm=0, rs1=2, funct3=0b111, rd=1, opcode=0b0010011
    insn = (0 << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # rs1 & 0 = 0
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail("ANDI", "0x00000000", f"0x{cpu.read_reg(1):08x}")


def test_andi_with_minus_one(runner):
    """ANDI with -1 is identity (rs1 & 0xFFFFFFFF = rs1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ANDI x1, x2, -1
    # -1 in 12-bit: 0xFFF, sign-extends to 0xFFFFFFFF
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # rs1 & 0xFFFFFFFF = rs1
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("ANDI", "0x12345678", f"0x{cpu.read_reg(1):08x}")


def test_andi_bit_masking(runner):
    """ANDI masks specific bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # ANDI x1, x2, 0xFF (mask lower 8 bits)
    insn = (0xFF << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF & 0x000000FF = 0x000000FF
    if cpu.read_reg(1) != 0x000000FF:
        runner.test_fail("ANDI", "0x000000FF", f"0x{cpu.read_reg(1):08x}")


def test_andi_extract_bits(runner):
    """ANDI extracts specific bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ANDI x1, x2, 0x70F (extract bits - positive immediate)
    insn = (0x70F << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x12345678 & 0x0000070F = 0x00000608
    if cpu.read_reg(1) != 0x00000608:
        runner.test_fail("ANDI", "0x00000608", f"0x{cpu.read_reg(1):08x}")


def test_andi_clear_upper_bits(runner):
    """ANDI clears upper bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xABCDEF01)
    
    # ANDI x1, x2, 0x7FF (keep only lower 11 bits)
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xABCDEF01 & 0x000007FF = 0x00000701
    if cpu.read_reg(1) != 0x00000701:
        runner.test_fail("ANDI", "0x00000701", f"0x{cpu.read_reg(1):08x}")


def test_andi_negative_immediate_sign_extends(runner):
    """ANDI with negative immediate sign-extends to 32 bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ANDI x1, x2, -2
    # -2 in 12-bit: 0xFFE, sign-extends to 0xFFFFFFFE
    imm_neg2 = 0xFFE
    insn = (imm_neg2 << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x12345678 & 0xFFFFFFFE = 0x12345678 (clears LSB)
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("ANDI", "0x12345678", f"0x{cpu.read_reg(1):08x}")


def test_andi_clear_lsb(runner):
    """ANDI to clear least significant bit"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345679)  # Odd number
    
    # ANDI x1, x2, -2 (0xFFFFFFFE - clears LSB)
    imm_neg2 = 0xFFE
    insn = (imm_neg2 << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x12345679 & 0xFFFFFFFE = 0x12345678 (even)
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("ANDI", "0x12345678", f"0x{cpu.read_reg(1):08x}")


def test_andi_zero_result(runner):
    """ANDI with no overlapping bits gives zero"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFF0000)
    
    # ANDI x1, x2, 0xFF (lower 8 bits)
    insn = (0xFF << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFF0000 & 0x000000FF = 0x00000000
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail("ANDI", "0x00000000", f"0x{cpu.read_reg(1):08x}")


def test_andi_rd_x0(runner):
    """ANDI with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # ANDI x0, x2, -1
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b111 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail("ANDI", "0", f"0x{cpu.read_reg(0):08x}")


def test_andi_rs1_x0(runner):
    """ANDI x1, x0, imm always gives 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    # ANDI x1, x0, 0x7FF
    imm_max = 0x7FF
    insn = (imm_max << 20) | (0 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0 & anything = 0
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail("ANDI", "0x00000000", f"0x{cpu.read_reg(1):08x}")


def test_andi_alternating_bits(runner):
    """ANDI with alternating bit pattern"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xAAAAAAAA)
    
    # ANDI x1, x2, 0x555 (alternating pattern)
    insn = (0x555 << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xAAAAAAAA & 0x00000555 = 0x00000000 (no overlap)
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail("ANDI", "0x00000000", f"0x{cpu.read_reg(1):08x}")


def test_andi_partial_mask(runner):
    """ANDI with partial bit mask"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x0F0F0F0F)
    
    # ANDI x1, x2, 0x70F (positive immediate)
    insn = (0x70F << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x0F0F0F0F & 0x0000070F = 0x0000070F
    if cpu.read_reg(1) != 0x0000070F:
        runner.test_fail("ANDI", "0x0000070F", f"0x{cpu.read_reg(1):08x}")


def test_andi_pc_increment(runner):
    """ANDI should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    initial_pc = cpu.pc
    
    # ANDI x1, x2, -1
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b111 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail("PC", f"{initial_pc + 4}", f"{cpu.pc}")
