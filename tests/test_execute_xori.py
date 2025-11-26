"""
Test XORI instruction execution

XORI - XOR Immediate
Format: I-type
Encoding: imm[11:0] | rs1 | 0b100 | rd | 0b0010011
Operation: rd = rs1 ^ sign_extend(imm)

Edge Cases (from execute.py docstring):
- XOR with 0 (identity)
- XOR with -1 (bitwise NOT)
- bit patterns
- Note: XORI rd, rs1, -1 is bitwise NOT
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_xori_with_zero(runner):
    """XORI with 0 is identity (rs1 ^ 0 = rs1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # XORI x1, x2, 0
    # imm=0, rs1=2, funct3=0b100, rd=1, opcode=0b0010011
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("XORI", f" x1=0x12345678, got 0x{cpu.read_reg(1):08x}")


def test_xori_bitwise_not(runner):
    """XORI with -1 produces bitwise NOT"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # XORI x1, x2, -1
    # -1 in 12-bit: 0xFFF
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # ~0x12345678 = 0xEDCBA987
    if cpu.read_reg(1) != 0xEDCBA987:
        runner.test_fail("XORI", f" x1=0xEDCBA987, got 0x{cpu.read_reg(1):08x}")


def test_xori_flip_bits(runner):
    """XORI flips specified bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xAAAAAAAA)  # 10101010...
    
    # XORI x1, x2, 0xFF (flip lower 8 bits)
    insn = (0xFF << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xAAAAAAAA ^ 0x000000FF = 0xAAAAAA55
    if cpu.read_reg(1) != 0xAAAAAA55:
        runner.test_fail("XORI", f" x1=0xAAAAAA55, got 0x{cpu.read_reg(1):08x}")


def test_xori_same_value_gives_zero(runner):
    """XORI with same bits gives zero for those bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x000000FF)
    
    # XORI x1, x2, 0xFF
    insn = (0xFF << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFF ^ 0xFF = 0x00
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail("XORI", f" x1=0x00000000, got 0x{cpu.read_reg(1):08x}")


def test_xori_positive_immediate(runner):
    """XORI with positive immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # XORI x1, x2, 0x123
    insn = (0x123 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x12345678 ^ 0x00000123 = 0x1234575B
    if cpu.read_reg(1) != 0x1234575B:
        runner.test_fail("XORI", f" x1=0x1234575B, got 0x{cpu.read_reg(1):08x}")


def test_xori_negative_immediate_sign_extends(runner):
    """XORI with negative immediate sign-extends to 32 bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x00000000)
    
    # XORI x1, x2, -2
    # -2 in 12-bit: 0xFFE, sign-extends to 0xFFFFFFFE
    imm_neg2 = 0xFFE
    insn = (imm_neg2 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x00000000 ^ 0xFFFFFFFE = 0xFFFFFFFE
    if cpu.read_reg(1) != 0xFFFFFFFE:
        runner.test_fail("XORI", f" x1=0xFFFFFFFE, got 0x{cpu.read_reg(1):08x}")


def test_xori_max_positive_immediate(runner):
    """XORI with max positive 12-bit immediate (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # XORI x1, x2, 2047
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF ^ 0x000007FF = 0xFFFFF800
    if cpu.read_reg(1) != 0xFFFFF800:
        runner.test_fail("XORI", f" x1=0xFFFFF800, got 0x{cpu.read_reg(1):08x}")


def test_xori_alternating_bits(runner):
    """XORI with alternating bit pattern"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xAAAAAAAA)
    
    # XORI x1, x2, 0x555 (alternating pattern in 12 bits)
    insn = (0x555 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xAAAAAAAA ^ 0x00000555 = 0xAAAAAFFF
    if cpu.read_reg(1) != 0xAAAAAFFF:
        runner.test_fail("XORI", f" x1=0xAAAAAFFF, got 0x{cpu.read_reg(1):08x}")


def test_xori_rd_x0(runner):
    """XORI with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # XORI x0, x2, -1
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b100 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail("XORI", f" x0=0, got 0x{cpu.read_reg(0):08x}")


def test_xori_rs1_x0(runner):
    """XORI x1, x0, imm gives sign-extended immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    # XORI x1, x0, 0x123
    insn = (0x123 << 20) | (0 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0 ^ 0x123 = 0x123
    if cpu.read_reg(1) != 0x00000123:
        runner.test_fail("XORI", f" x1=0x00000123, got 0x{cpu.read_reg(1):08x}")


def test_xori_toggle_specific_bits(runner):
    """XORI to toggle specific bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xF0F0F0F0)
    
    # XORI x1, x2, 0xF0F (toggle specific bits)
    insn = (0xF0F << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xF0F0F0F0 ^ 0xFFFFFF0F = 0x0F0F0FFF (0xF0F sign-extends!)
    if cpu.read_reg(1) != 0x0F0F0FFF:
        runner.test_fail("XORI", "0x0F0F0FFF", f"0x{cpu.read_reg(1):08x}")


def test_xori_pc_increment(runner):
    """XORI should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    initial_pc = cpu.pc
    
    # XORI x1, x2, 0
    insn = (0 << 20) | (2 << 15) | (0b100 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail("XORI", f" PC={initial_pc + 4}, got {cpu.pc}")
