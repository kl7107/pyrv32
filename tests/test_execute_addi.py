"""
Test ADDI instruction execution

ADDI - Add Immediate
Format: I-type
Encoding: imm[11:0] | rs1 | 0b000 | rd | 0b0010011
Operation: rd = rs1 + sign_extend(imm)

Edge Cases (from execute.py docstring):
- zero+zero
- overflow wrapping
- negative immediate
- max/min values
- ADDI with rd=x0 (NOP)
- ADDI x0, rs1, imm (write to x0 ignored)
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_addi_zero_plus_zero(runner):
    """ADDI x1, x0, 0 should set x1 = 0"""
    cpu = RV32CPU()
    mem = Memory()
    
    # ADDI x1, x0, 0
    # imm=0, rs1=0, funct3=0b000, rd=1, opcode=0b0010011
    insn = (0 << 20) | (0 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0:
        runner.test_fail(f"Expected x1=0, got {cpu.read_reg(1)}")


def test_addi_zero_plus_positive(runner):
    """ADDI x1, x0, 42 should set x1 = 42"""
    cpu = RV32CPU()
    mem = Memory()
    
    # ADDI x1, x0, 42
    insn = (42 << 20) | (0 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 42:
        runner.test_fail(f"Expected x1=42, got {cpu.read_reg(1)}")


def test_addi_positive_plus_zero(runner):
    """ADDI x1, x2, 0 should set x1 = x2 (register copy)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 12345)
    
    # ADDI x1, x2, 0
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 12345:
        runner.test_fail(f"Expected x1=12345, got {cpu.read_reg(1)}")


def test_addi_positive_plus_positive(runner):
    """ADDI x1, x2, 100 with x2=200 should set x1 = 300"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 200)
    
    # ADDI x1, x2, 100
    insn = (100 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 300:
        runner.test_fail(f"Expected x1=300, got {cpu.read_reg(1)}")


def test_addi_overflow_wrapping(runner):
    """ADDI with overflow should wrap around (0x7FFFFFFF + 1 = 0x80000000)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x7FFFFFFF)  # Max positive 32-bit signed
    
    # ADDI x1, x2, 1
    insn = (1 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x80000000:
        runner.test_fail(f"Expected x1=0x80000000, got 0x{cpu.read_reg(1):08x}")


def test_addi_negative_immediate(runner):
    """ADDI x1, x2, -50 should subtract 50 from x2"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 100)
    
    # ADDI x1, x2, -50
    # -50 in 12-bit two's complement: 0xFCE (0b111111001110)
    imm_neg50 = 0xFCE
    insn = (imm_neg50 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 50:
        runner.test_fail(f"Expected x1=50, got {cpu.read_reg(1)}")


def test_addi_negative_immediate_all_ones(runner):
    """ADDI x1, x2, -1 should set x1 = x2 - 1"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0x12345678)
    
    # ADDI x1, x2, -1
    # -1 in 12-bit two's complement: 0xFFF
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x12345677:
        runner.test_fail(f"Expected x1=0x12345677, got 0x{cpu.read_reg(1):08x}")


def test_addi_underflow_wrapping(runner):
    """ADDI with underflow should wrap around (0 + (-1) = 0xFFFFFFFF)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0)
    
    # ADDI x1, x2, -1
    imm_neg1 = 0xFFF
    insn = (imm_neg1 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail(f"Expected x1=0xFFFFFFFF, got 0x{cpu.read_reg(1):08x}")


def test_addi_max_positive_immediate(runner):
    """ADDI with max positive 12-bit immediate (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 100)
    
    # ADDI x1, x2, 2047
    # Max positive 12-bit: 0x7FF (2047)
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 2147:
        runner.test_fail(f"Expected x1=2147, got {cpu.read_reg(1)}")


def test_addi_max_negative_immediate(runner):
    """ADDI with max negative 12-bit immediate (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 3000)
    
    # ADDI x1, x2, -2048
    # Min 12-bit signed: 0x800 (-2048)
    imm_min = 0x800
    insn = (imm_min << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 952:
        runner.test_fail(f"Expected x1=952, got {cpu.read_reg(1)}")


def test_addi_rd_x0_nop(runner):
    """ADDI x0, x1, 42 should not change x0 (always 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(1, 100)
    
    # ADDI x0, x1, 42
    insn = (42 << 20) | (1 << 15) | (0b000 << 12) | (0 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got {cpu.read_reg(0)}")


def test_addi_rs1_x0_load_immediate(runner):
    """ADDI x1, x0, -100 should load sign-extended immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    # ADDI x1, x0, -100
    # -100 in 12-bit two's complement: 0xF9C
    imm_neg100 = 0xF9C
    insn = (imm_neg100 << 20) | (0 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # -100 sign-extended to 32 bits is 0xFFFFFF9C
    if cpu.read_reg(1) != 0xFFFFFF9C:
        runner.test_fail(f"Expected x1=0xFFFFFF9C, got 0x{cpu.read_reg(1):08x}")


def test_addi_negative_plus_negative(runner):
    """ADDI with negative register and negative immediate"""
    cpu = RV32CPU()
    mem = Memory()
    
    cpu.write_reg(2, 0xFFFFFF00)  # -256 in 32-bit two's complement
    
    # ADDI x1, x2, -16
    # -16 in 12-bit: 0xFF0
    imm_neg16 = 0xFF0
    insn = (imm_neg16 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    # -256 + (-16) = -272 = 0xFFFFFEF0
    if cpu.read_reg(1) != 0xFFFFFEF0:
        runner.test_fail(f"Expected x1=0xFFFFFEF0, got 0x{cpu.read_reg(1):08x}")


def test_addi_pc_increment(runner):
    """ADDI should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    initial_pc = cpu.pc
    
    # ADDI x1, x0, 1
    insn = (1 << 20) | (0 << 15) | (0b000 << 12) | (1 << 7) | 0b0010011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail(f"Expected PC={initial_pc + 4}, got {cpu.pc}")
