"""
Test SLTIU instruction execution

SLTIU - Set Less Than Immediate Unsigned
Format: I-type
Encoding: imm[11:0] | rs1 | 0b011 | rd | 0b0010011
Operation: rd = (rs1 <u sign_extend(imm)) ? 1 : 0

Edge Cases (from execute.py docstring):
- equal values
- 0 vs 0xFFFFFFFF
- boundary values
- SLTIU rd, rs1, 1 sets rd=1 if rs1==0, rd=0 otherwise (compare to zero)
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_sltiu_equal_values(runner):
    """SLTIU with rs1 == imm should set rd = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 100)
    
    # SLTIU x1, x2, 100
    # imm=100, rs1=2, funct3=0b011, rd=1, opcode=0b0010011
    insn = (100 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (equal values), got {cpu.read_reg(1)}")


def test_sltiu_less_than(runner):
    """SLTIU with rs1 < imm should set rd = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 50)
    
    # SLTIU x1, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (50 < 100), got {cpu.read_reg(1)}")


def test_sltiu_greater_than(runner):
    """SLTIU with rs1 > imm should set rd = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 200)
    
    # SLTIU x1, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (200 > 100), got {cpu.read_reg(1)}")


def test_sltiu_zero_less_than_any_nonzero(runner):
    """SLTIU with 0 < any non-zero should set rd = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0)
    
    # SLTIU x1, x2, 1
    insn = (1 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (0 < 1 unsigned), got {cpu.read_reg(1)}")


def test_sltiu_compare_to_zero_check(runner):
    """SLTIU rd, rs1, 1 sets rd=1 if rs1==0 (idiom for checking zero)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0)
    
    # SLTIU x1, x2, 1
    insn = (1 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (rs1==0), got {cpu.read_reg(1)}")


def test_sltiu_compare_to_zero_check_nonzero(runner):
    """SLTIU rd, rs1, 1 sets rd=0 if rs1!=0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 42)
    
    # SLTIU x1, x2, 1
    insn = (1 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (rs1!=0), got {cpu.read_reg(1)}")


def test_sltiu_unsigned_vs_signed_negative(runner):
    """SLTIU treats negative as large unsigned (0xFFFFFFFF > 100)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)  # -1 as signed, max as unsigned
    
    # SLTIU x1, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (0xFFFFFFFF > 100 unsigned), got {cpu.read_reg(1)}")


def test_sltiu_negative_imm_sign_extended(runner):
    """SLTIU with negative immediate sign-extends to large unsigned value"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80000000)  # 2^31
    
    # SLTIU x1, x2, -1
    # -1 in 12-bit: 0xFFF, sign-extends to 0xFFFFFFFF (max unsigned)
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x80000000 < 0xFFFFFFFF (unsigned) should be true
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (0x80000000 < 0xFFFFFFFF unsigned), got {cpu.read_reg(1)}")


def test_sltiu_max_unsigned_not_less_than_anything(runner):
    """SLTIU with max unsigned value not < any value"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFF)
    
    # SLTIU x1, x2, -1
    # -1 sign-extends to 0xFFFFFFFF
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xFFFFFFFF < 0xFFFFFFFF is false
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (0xFFFFFFFF == 0xFFFFFFFF), got {cpu.read_reg(1)}")


def test_sltiu_high_bit_comparison(runner):
    """SLTIU with high bit set (unsigned interpretation)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80000000)  # High bit set
    
    # SLTIU x1, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # 0x80000000 (unsigned) > 100, so result is 0
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (0x80000000 > 100 unsigned), got {cpu.read_reg(1)}")


def test_sltiu_boundary_max_positive_imm(runner):
    """SLTIU with max positive 12-bit immediate (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 1000)
    
    # SLTIU x1, x2, 2047
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (1000 < 2047), got {cpu.read_reg(1)}")


def test_sltiu_rd_x0(runner):
    """SLTIU with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 10)
    
    # SLTIU x0, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b011 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got {cpu.read_reg(0)}")


def test_sltiu_rs1_x0_vs_positive(runner):
    """SLTIU x1, x0, 100 should set x1=1 (0 < 100)"""
    cpu = RV32CPU()
    mem = Memory()
    
    # SLTIU x1, x0, 100
    insn = (100 << 20) | (0 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (0 < 100), got {cpu.read_reg(1)}")


def test_sltiu_rs1_x0_vs_negative_imm(runner):
    """SLTIU x1, x0, -1 should set x1=1 (0 < 0xFFFFFFFF unsigned)"""
    cpu = RV32CPU()
    mem = Memory()
    
    # SLTIU x1, x0, -1
    # -1 in 12-bit: 0xFFF, sign-extends to 0xFFFFFFFF
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (0 << 15) | (0b011 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (0 < 0xFFFFFFFF), got {cpu.read_reg(1)}")
