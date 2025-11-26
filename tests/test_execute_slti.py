"""
Test SLTI instruction execution

SLTI - Set Less Than Immediate (signed)
Format: I-type
Encoding: imm[11:0] | rs1 | 0b010 | rd | 0b0010011
Operation: rd = (rs1 <s sign_extend(imm)) ? 1 : 0

Edge Cases (from execute.py docstring):
- equal values
- positive vs negative
- boundary values
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_slti_equal_values(runner):
    """SLTI with rs1 == imm should set rd = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 100)
    
    # SLTI x1, x2, 100
    # imm=100, rs1=2, funct3=0b010, rd=1, opcode=0b0010011
    insn = (100 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (equal values), got {cpu.read_reg(1)}")


def test_slti_less_than(runner):
    """SLTI with rs1 < imm should set rd = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 50)
    
    # SLTI x1, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (50 < 100), got {cpu.read_reg(1)}")


def test_slti_greater_than(runner):
    """SLTI with rs1 > imm should set rd = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 200)
    
    # SLTI x1, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (200 > 100), got {cpu.read_reg(1)}")


def test_slti_negative_less_than_positive(runner):
    """SLTI with negative rs1 < positive imm should set rd = 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFF9C)  # -100 in two's complement
    
    # SLTI x1, x2, 50
    insn = (50 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (-100 < 50), got {cpu.read_reg(1)}")


def test_slti_positive_not_less_than_negative(runner):
    """SLTI with positive rs1 not < negative imm should set rd = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 100)
    
    # SLTI x1, x2, -50
    # -50 in 12-bit: 0xFCE
    imm_neg50 = 0xFCE
    insn = (imm_neg50 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (100 not < -50), got {cpu.read_reg(1)}")


def test_slti_negative_comparison(runner):
    """SLTI comparing two negative values"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFF38)  # -200 in two's complement
    
    # SLTI x1, x2, -100
    # -100 in 12-bit: 0xF9C
    imm_neg100 = 0xF9C
    insn = (imm_neg100 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (-200 < -100), got {cpu.read_reg(1)}")


def test_slti_min_negative_less_than_zero(runner):
    """SLTI with min negative value < 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x80000000)  # Min negative 32-bit signed
    
    # SLTI x1, x2, 0
    insn = (0 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (0x80000000 < 0), got {cpu.read_reg(1)}")


def test_slti_zero_not_less_than_max_positive_imm(runner):
    """SLTI with 0 not < max positive 12-bit immediate (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0)
    
    # SLTI x1, x2, 2047
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (0 < 2047), got {cpu.read_reg(1)}")


def test_slti_max_positive_not_less_than_min_negative_imm(runner):
    """SLTI with max positive value not < min negative immediate (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x7FFFFFFF)  # Max positive 32-bit signed
    
    # SLTI x1, x2, -2048
    # -2048 in 12-bit: 0x800
    imm_min = 0x800
    insn = (imm_min << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (0x7FFFFFFF not < -2048), got {cpu.read_reg(1)}")


def test_slti_boundary_values(runner):
    """SLTI at boundary: 0x7FFFFFFF not < -1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x7FFFFFFF)
    
    # SLTI x1, x2, -1
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0 (max positive not < -1), got {cpu.read_reg(1)}")


def test_slti_rd_x0(runner):
    """SLTI with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 10)
    
    # SLTI x0, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got {cpu.read_reg(0)}")


def test_slti_rs1_x0(runner):
    """SLTI x1, x0, 1 should set x1=1 (0 < 1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    # SLTI x1, x0, 1
    insn = (1 << 20) | (0 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (0 < 1), got {cpu.read_reg(1)}")


def test_slti_negative_immediate_sign_extension(runner):
    """SLTI should sign-extend immediate: -1 becomes 0xFFFFFFFF"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFFFE)  # -2 in two's complement
    
    # SLTI x1, x2, -1
    # -2 < -1 should be true (1)
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 1:
        runner.test_fail(f"Expected x1=1 (-2 < -1), got {cpu.read_reg(1)}")
