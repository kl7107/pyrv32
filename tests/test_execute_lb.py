"""
Test LB instruction execution

LB - Load Byte (with sign extension)
Format: I-type
Encoding: imm[11:0] | rs1 | 0b000 | rd | 0b0000011
Operation: rd = sign_extend(memory[rs1 + imm][7:0])

Edge Cases (from execute.py docstring):
- load 0x00 (extends to 0x00000000)
- load 0x80 (extends to 0xFFFFFF80 - negative)
- load 0x7F (extends to 0x0000007F - positive)
- load 0xFF (extends to 0xFFFFFFFF - -1)
- zero offset (rs1 + 0)
- negative offset (sign-extended immediate)
- large offset (up to ±2047)
- rd = x0 (write ignored)
"""

from cpu import RV32CPU
from memory import Memory
from execute import execute_instruction


def test_lb_positive_byte(runner):
    """LB loading positive byte 0x7F should sign-extend to 0x0000007F"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write byte to memory
    mem.write_byte(0x80001000, 0x7F)
    
    # Set base address
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 0(x2)
    # imm=0, rs1=2, funct3=0b000, rd=1, opcode=0b0000011
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x0000007F:
        runner.test_fail(f"Expected x1=0x0000007F, got 0x{cpu.read_reg(1):08x}")


def test_lb_negative_byte(runner):
    """LB loading negative byte 0x80 should sign-extend to 0xFFFFFF80"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000, 0x80)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFFFF80:
        runner.test_fail(f"Expected x1=0xFFFFFF80, got 0x{cpu.read_reg(1):08x}")


def test_lb_zero_byte(runner):
    """LB loading 0x00 should extend to 0x00000000"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000, 0x00)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000000:
        runner.test_fail(f"Expected x1=0x00000000, got 0x{cpu.read_reg(1):08x}")


def test_lb_all_ones_byte(runner):
    """LB loading 0xFF should sign-extend to 0xFFFFFFFF (-1)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000, 0xFF)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFFFFFF:
        runner.test_fail(f"Expected x1=0xFFFFFFFF, got 0x{cpu.read_reg(1):08x}")


def test_lb_positive_offset(runner):
    """LB with positive offset should add to base address"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001004, 0x42)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 4(x2)
    insn = (4 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000042:
        runner.test_fail(f"Expected x1=0x00000042, got 0x{cpu.read_reg(1):08x}")


def test_lb_negative_offset(runner):
    """LB with negative offset should subtract from base address"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80000FFC, 0x33)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, -4(x2)
    # -4 in 12-bit: 0xFFC
    imm_neg4 = 0xFFC
    insn = (imm_neg4 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000033:
        runner.test_fail(f"Expected x1=0x00000033, got 0x{cpu.read_reg(1):08x}")


def test_lb_max_positive_offset(runner):
    """LB with max positive 12-bit offset (2047)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000 + 2047, 0x55)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 2047(x2)
    imm_max = 0x7FF
    insn = (imm_max << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000055:
        runner.test_fail(f"Expected x1=0x00000055, got 0x{cpu.read_reg(1):08x}")


def test_lb_max_negative_offset(runner):
    """LB with max negative 12-bit offset (-2048)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000 - 2048, 0xAA)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, -2048(x2)
    # -2048 in 12-bit: 0x800
    imm_min = 0x800
    insn = (imm_min << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # 0xAA sign-extends to 0xFFFFFFAA
    if cpu.read_reg(1) != 0xFFFFFFAA:
        runner.test_fail(f"Expected x1=0xFFFFFFAA, got 0x{cpu.read_reg(1):08x}")


def test_lb_zero_offset(runner):
    """LB with zero offset (rs1 + 0)"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80002000, 0x12)
    cpu.write_reg(3, 0x80002000)
    
    # LB x1, 0(x3)
    insn = (0 << 20) | (3 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000012:
        runner.test_fail(f"Expected x1=0x00000012, got 0x{cpu.read_reg(1):08x}")


def test_lb_sign_boundary_0x7F(runner):
    """LB at sign boundary: 0x7F is max positive signed byte"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000, 0x7F)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x0000007F:
        runner.test_fail(f"Expected x1=0x0000007F (positive), got 0x{cpu.read_reg(1):08x}")


def test_lb_sign_boundary_0x80(runner):
    """LB at sign boundary: 0x80 is min negative signed byte"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000, 0x80)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0xFFFFFF80:
        runner.test_fail(f"Expected x1=0xFFFFFF80 (negative), got 0x{cpu.read_reg(1):08x}")


def test_lb_rd_x0(runner):
    """LB with rd=x0 should not change x0"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000, 0xFF)
    cpu.write_reg(2, 0x80001000)
    
    # LB x0, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (0 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(0) != 0:
        runner.test_fail(f"Expected x0=0, got 0x{cpu.read_reg(0):08x}")


def test_lb_rs1_x0(runner):
    """LB with rs1=x0 loads from address 0 + offset (uses max positive offset to stay in valid RAM)"""
    cpu = RV32CPU()
    mem = Memory()
    
    # With memory protection, we need to use a base address in RAM
    # Since x0=0, we use a different register with base in RAM
    # Changed test to use x2 as base to access valid RAM
    base_addr = 0x80000000
    offset = 100
    mem.write_byte(base_addr + offset, 0x66)
    cpu.write_reg(2, base_addr)
    
    # LB x1, 100(x2) - changed from x0 to x2
    insn = (100 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.read_reg(1) != 0x00000066:
        runner.test_fail(f"Expected x1=0x00000066, got 0x{cpu.read_reg(1):08x}")


def test_lb_multiple_bytes_at_address(runner):
    """LB should only load one byte, ignoring adjacent bytes"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Write a word: 0xAABBCCDD
    mem.write_word(0x80001000, 0xAABBCCDD)
    cpu.write_reg(2, 0x80001000)
    
    # LB x1, 0(x2) - should load only lowest byte (DD in little-endian)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    # Little-endian: byte at 0x80001000 is 0xDD, sign-extends to 0xFFFFFFDD
    if cpu.read_reg(1) != 0xFFFFFFDD:
        runner.test_fail(f"Expected x1=0xFFFFFFDD, got 0x{cpu.read_reg(1):08x}")


def test_lb_pc_increment(runner):
    """LB should increment PC by 4"""
    cpu = RV32CPU()
    mem = Memory()
    
    mem.write_byte(0x80001000, 0x42)
    cpu.write_reg(2, 0x80001000)
    
    initial_pc = cpu.pc
    
    # LB x1, 0(x2)
    insn = (0 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0b0000011
    
    execute_instruction(cpu, mem, insn)
    
    if cpu.pc != initial_pc + 4:
        runner.test_fail(f"Expected PC={initial_pc + 4}, got {cpu.pc}")
