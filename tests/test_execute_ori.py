"""
Test ORI instruction execution

ORI - OR Immediate
Format: I-type
Encoding: imm[11:0] | rs1 | 0b110 | rd | 0b0010011
Operation: rd = rs1 | sign_extend(imm)

Edge Cases (from execute.py docstring):
- OR with 0 (identity)
- OR with -1 (all 1s)
- bit setting
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_ori_with_zero(runner):
    """ORI with 0 is identity (rs1 | 0 = rs1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ORI x1, x2, 0
    # imm=0, rs1=2, funct3=0b110, rd=1, opcode=0b0010011
    insn = (0 << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x12345678:
        runner.test_fail("ORI", "0x12345678", f"0x{cpu.read_reg(1):08x}")


def test_ori_with_minus_one(runner):
    """ORI with -1 produces all 1s (0xFFFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ORI x1, x2, -1
    # -1 in 12-bit: 0xFFF, sign-extends to 0xFFFFFFFF
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # rs1 | 0xFFFFFFFF = 0xFFFFFFFF
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail("ORI", "0xFFFFFFFF", f"0x{cpu.read_reg(1):08x}")


def test_ori_set_bits(runner):
    """ORI sets specified bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x00000000)
    
    # ORI x1, x2, 0xFF (set lower 8 bits)
    insn = (0xFF << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x00000000 | 0x000000FF = 0x000000FF
    if cpu.read_reg(1) != 0x000000FF:
        runner.test_fail("ORI", "0x000000FF", f"0x{cpu.read_reg(1):08x}")


def test_ori_combine_bits(runner):
    """ORI combines bits from rs1 and immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12340000)
    
    # ORI x1, x2, 0x678
    insn = (0x678 << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x12340000 | 0x00000678 = 0x12340678
    if cpu.read_reg(1) != 0x12340678:
        runner.test_fail("ORI", "0x12340678", f"0x{cpu.read_reg(1):08x}")


def test_ori_idempotent(runner):
    """ORI with bits already set doesn't change them"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # ORI x1, x2, 0x123
    insn = (0x123 << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF | anything = 0xFFFFFFFF
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail("ORI", "0xFFFFFFFF", f"0x{cpu.read_reg(1):08x}")


def test_ori_negative_immediate_sign_extends(runner):
    """ORI with negative immediate sign-extends to 32 bits"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x00001234)
    
    # ORI x1, x2, -2
    # -2 in 12-bit: 0xFFE, sign-extends to 0xFFFFFFFE
    imm_neg2 = 0xFFE
    insn = (imm_neg2 << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x00001234 | 0xFFFFFFFE = 0xFFFFFFFE
    if cpu.read_reg(1) != 0xFFFFFFFE:
        runner.test_fail("ORI", "0xFFFFFFFE", f"0x{cpu.read_reg(1):08x}")


def test_ori_max_positive_immediate(runner):
    """ORI with max positive 12-bit immediate (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFF000)
    
    # ORI x1, x2, 2047
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFF000 | 0x000007FF = 0xFFFFF7FF
    if cpu.read_reg(1) != 0xFFFFF7FF:
        runner.test_fail("ORI", "0xFFFFF7FF", f"0x{cpu.read_reg(1):08x}")


def test_ori_set_specific_bits(runner):
    """ORI to set specific bits while preserving others"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xAAAAAAAA)
    
    # ORI x1, x2, 0x555 (set additional bits)
    insn = (0x555 << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xAAAAAAAA | 0x00000555 = 0xAAAAAFFF
    if cpu.read_reg(1) != 0xAAAAAFFF:
        runner.test_fail("ORI", "0xAAAAAFFF", f"0x{cpu.read_reg(1):08x}")


def test_ori_rd_x0(runner):
    """ORI with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ORI x0, x2, 0xFF
    insn = (0xFF << 20) | (2 << 15) | (0b110 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail("ORI", "0", f"0x{cpu.read_reg(0):08x}")


def test_ori_rs1_x0(runner):
    """ORI x1, x0, imm gives sign-extended immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    # ORI x1, x0, 0x321
    insn = (0x321 << 20) | (0 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0 | 0x321 = 0x321
    if cpu.read_reg(1) != 0x00000321:
        runner.test_fail("ORI", "0x00000321", f"0x{cpu.read_reg(1):08x}")


def test_ori_partial_bits(runner):
    """ORI with partial bit overlap"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x00000F00)
    
    # ORI x1, x2, 0x70F (positive immediate)
    insn = (0x70F << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x00000F00 | 0x0000070F = 0x00000F0F
    if cpu.read_reg(1) != 0x00000F0F:
        runner.test_fail("ORI", "0x00000F0F", f"0x{cpu.read_reg(1):08x}")


def test_ori_pc_increment(runner):
    """ORI should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    initial_pc = cpu.pc
    
    # ORI x1, x2, 0
    insn = (0 << 20) | (2 << 15) | (0b110 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail("PC", f"{initial_pc + 4}", f"{cpu.pc}")
