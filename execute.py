"""
Instruction Execution - Execute decoded RV32I instructions

Implements the execution logic for RV32I base instruction set.
"""

from decoder import decode_instruction, get_instruction_name, sign_extend_32
from exceptions import EBreakException, ECallException


def execute_instruction(cpu, memory, insn):
    """
    Execute a single instruction.
    
    Args:
        cpu: RV32CPU instance
        memory: Memory instance
        insn: 32-bit instruction word
        
    Returns:
        True if execution should continue, False if program should halt
    """
    decoded = decode_instruction(insn)
    fmt = decoded['format']
    opcode = decoded['opcode']
    
    # Dispatch based on format and opcode
    if fmt == 'R':
        return exec_register_alu(cpu, decoded)
    
    elif fmt == 'I':
        if opcode == 0b0010011:  # Immediate ALU
            return exec_immediate_alu(cpu, decoded)
        elif opcode == 0b0000011:  # Loads
            return exec_load(cpu, memory, decoded)
        elif opcode == 0b1100111:  # JALR
            return exec_jalr(cpu, decoded)
        elif opcode == 0b0001111:  # FENCE
            # FENCE is a no-op in single-core without DMA or reordering
            cpu.pc += 4
            return True
        elif opcode == 0b1110011:  # ECALL/EBREAK
            if decoded['name'] == 'EBREAK':
                raise EBreakException(cpu.pc)
            elif decoded['name'] == 'ECALL':
                raise ECallException(cpu.pc)
            else:
                raise NotImplementedError(
                    f"System instruction not implemented: {decoded['name']}, insn=0x{insn:08x}"
                )
    
    elif fmt == 'S':
        return exec_store(cpu, memory, decoded)
    
    elif fmt == 'B':
        return exec_branch(cpu, decoded)
    
    elif fmt == 'U':
        if opcode == 0b0110111:  # LUI
            return exec_lui(cpu, decoded)
        elif opcode == 0b0010111:  # AUIPC
            return exec_auipc(cpu, decoded)
    
    elif fmt == 'J':
        return exec_jal(cpu, decoded)
    
    # Unknown instruction format or opcode
    raise NotImplementedError(
        f"Unknown instruction: {decoded['name']}, format={decoded['format']}, "
        f"opcode=0x{decoded['opcode']:07b}, insn=0x{insn:08x}"
    )


# ============================================================================
# R-Type Instructions - Register ALU Operations
# ============================================================================

# M Extension helper functions
def exec_mul(rs1_signed, rs2_signed):
    """MUL - Multiply (lower 32 bits)"""
    product = rs1_signed * rs2_signed
    return product & 0xFFFFFFFF


def exec_mulh(rs1_signed, rs2_signed):
    """MULH - Multiply High (upper 32 bits of signed × signed)"""
    product = rs1_signed * rs2_signed
    return (product >> 32) & 0xFFFFFFFF


def exec_mulhsu(rs1_signed, rs2_val):
    """MULHSU - Multiply High Signed-Unsigned"""
    product = rs1_signed * rs2_val
    return (product >> 32) & 0xFFFFFFFF


def exec_mulhu(rs1_val, rs2_val):
    """MULHU - Multiply High Unsigned-Unsigned"""
    product = rs1_val * rs2_val
    return (product >> 32) & 0xFFFFFFFF


def exec_div(rs1_signed, rs2_signed):
    """DIV - Divide Signed"""
    if rs2_signed == 0:
        return 0xFFFFFFFF  # -1
    if rs1_signed == -2147483648 and rs2_signed == -1:
        return 0x80000000  # Overflow case
    quotient = int(rs1_signed / rs2_signed)
    return quotient & 0xFFFFFFFF


def exec_divu(rs1_val, rs2_val):
    """DIVU - Divide Unsigned"""
    if rs2_val == 0:
        return 0xFFFFFFFF
    quotient = rs1_val // rs2_val
    return quotient & 0xFFFFFFFF


def exec_rem(rs1_signed, rs2_signed):
    """REM - Remainder Signed"""
    if rs2_signed == 0:
        return rs1_signed & 0xFFFFFFFF
    if rs1_signed == -2147483648 and rs2_signed == -1:
        return 0
    quotient = int(rs1_signed / rs2_signed)
    remainder = rs1_signed - quotient * rs2_signed
    return remainder & 0xFFFFFFFF


def exec_remu(rs1_val, rs2_val):
    """REMU - Remainder Unsigned"""
    if rs2_val == 0:
        return rs1_val
    remainder = rs1_val % rs2_val
    return remainder & 0xFFFFFFFF


def exec_register_alu(cpu, decoded):
    """Execute R-type ALU operations (ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND, MUL, etc.)"""
    funct3 = decoded['funct3']
    funct7 = decoded['funct7']
    rs1_val = cpu.read_reg(decoded['rs1'])
    rs2_val = cpu.read_reg(decoded['rs2'])
    
    # Convert to signed for comparisons
    rs1_signed = rs1_val if rs1_val < 0x80000000 else rs1_val - 0x100000000
    rs2_signed = rs2_val if rs2_val < 0x80000000 else rs2_val - 0x100000000
    
    result = 0
    
    if funct3 == 0b000:
        if funct7 == 0b0000000:  # ADD
            result = (rs1_val + rs2_val) & 0xFFFFFFFF
        elif funct7 == 0b0100000:  # SUB
            result = (rs1_val - rs2_val) & 0xFFFFFFFF
        elif funct7 == 0b0000001:  # MUL - M extension
            result = exec_mul(rs1_signed, rs2_signed)
    
    elif funct3 == 0b001:
        if funct7 == 0b0000000:  # SLL - Shift Left Logical
            shamt = rs2_val & 0x1F
            result = (rs1_val << shamt) & 0xFFFFFFFF
        elif funct7 == 0b0000001:  # MULH - M extension
            result = exec_mulh(rs1_signed, rs2_signed)
    
    elif funct3 == 0b010:
        if funct7 == 0b0000000:  # SLT - Set Less Than (signed)
            result = 1 if rs1_signed < rs2_signed else 0
        elif funct7 == 0b0000001:  # MULHSU - M extension
            result = exec_mulhsu(rs1_signed, rs2_val)
    
    elif funct3 == 0b011:  # MULHU or SLTU
        if funct7 == 0b0000001:  # MULHU - M extension
            result = exec_mulhu(rs1_val, rs2_val)
        else:  # SLTU - Set Less Than Unsigned
            result = 1 if rs1_val < rs2_val else 0
    
    elif funct3 == 0b100:  # DIV or XOR
        if funct7 == 0b0000001:  # DIV - M extension
            result = exec_div(rs1_signed, rs2_signed)
        else:  # XOR
            result = (rs1_val ^ rs2_val) & 0xFFFFFFFF
    
    elif funct3 == 0b101:
        shamt = rs2_val & 0x1F
        if funct7 == 0b0000000:  # SRL - Shift Right Logical
            result = (rs1_val >> shamt) & 0xFFFFFFFF
        elif funct7 == 0b0100000:  # SRA - Shift Right Arithmetic
            if rs1_val & 0x80000000:
                result = (rs1_val >> shamt) | (0xFFFFFFFF << (32 - shamt))
            else:
                result = (rs1_val >> shamt) & 0xFFFFFFFF
            result &= 0xFFFFFFFF
        elif funct7 == 0b0000001:  # DIVU - M extension
            result = exec_divu(rs1_val, rs2_val)
    
    elif funct3 == 0b110:  # REM or OR
        if funct7 == 0b0000001:  # REM - M extension
            result = exec_rem(rs1_signed, rs2_signed)
        else:  # OR
            result = (rs1_val | rs2_val) & 0xFFFFFFFF
    
    elif funct3 == 0b111:  # REMU or AND
        if funct7 == 0b0000001:  # REMU - M extension
            result = exec_remu(rs1_val, rs2_val)
        else:  # AND
            result = (rs1_val & rs2_val) & 0xFFFFFFFF
    
    cpu.write_reg(decoded['rd'], result)
    cpu.pc += 4
    return True


# ============================================================================
# I-Type Instructions - Immediate Operations, Loads, JALR
# ============================================================================

def exec_immediate_alu(cpu, decoded):
    """Execute I-type ALU operations (ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI)"""
    funct3 = decoded['funct3']
    rs1_val = cpu.read_reg(decoded['rs1'])
    imm = decoded['imm']
    
    # Convert to signed for comparisons
    rs1_signed = rs1_val if rs1_val < 0x80000000 else rs1_val - 0x100000000
    imm_signed = imm if imm < 0x80000000 else imm - 0x100000000
    
    result = 0
    
    if funct3 == 0b000:  # ADDI
        result = (rs1_val + imm) & 0xFFFFFFFF
    
    elif funct3 == 0b010:  # SLTI - Set Less Than Immediate (signed)
        result = 1 if rs1_signed < imm_signed else 0
    
    elif funct3 == 0b011:  # SLTIU - Set Less Than Immediate Unsigned
        result = 1 if rs1_val < (imm & 0xFFFFFFFF) else 0
    
    elif funct3 == 0b100:  # XORI
        result = (rs1_val ^ imm) & 0xFFFFFFFF
    
    elif funct3 == 0b110:  # ORI
        result = (rs1_val | imm) & 0xFFFFFFFF
    
    elif funct3 == 0b111:  # ANDI
        result = (rs1_val & imm) & 0xFFFFFFFF
    
    elif funct3 == 0b001:  # SLLI - Shift Left Logical Immediate
        shamt = imm & 0x1F  # Only lower 5 bits
        result = (rs1_val << shamt) & 0xFFFFFFFF
    
    elif funct3 == 0b101:  # SRLI / SRAI - Shift Right Logical/Arithmetic Immediate
        shamt = imm & 0x1F
        if decoded['funct7'] == 0b0000000:  # SRLI
            result = (rs1_val >> shamt) & 0xFFFFFFFF
        else:  # SRAI
            # Arithmetic shift - preserve sign bit
            if rs1_val & 0x80000000:
                result = (rs1_val >> shamt) | (0xFFFFFFFF << (32 - shamt))
            else:
                result = rs1_val >> shamt
            result &= 0xFFFFFFFF
    
    cpu.write_reg(decoded['rd'], result)
    cpu.pc += 4
    return True


def exec_load(cpu, memory, decoded):
    """Execute I-type load instructions (LB, LH, LW, LBU, LHU)"""
    funct3 = decoded['funct3']
    rs1_val = cpu.read_reg(decoded['rs1'])
    address = (rs1_val + decoded['imm']) & 0xFFFFFFFF
    
    result = 0
    
    if funct3 == 0b000:  # LB - Load Byte (sign-extended)
        byte_val = memory.read_byte(address)
        result = byte_val if byte_val < 128 else (byte_val - 256)
        result &= 0xFFFFFFFF
    
    elif funct3 == 0b001:  # LH - Load Halfword (sign-extended)
        half_val = memory.read_halfword(address)
        result = half_val if half_val < 32768 else (half_val - 65536)
        result &= 0xFFFFFFFF
    
    elif funct3 == 0b010:  # LW - Load Word
        result = memory.read_word(address)
    
    elif funct3 == 0b100:  # LBU - Load Byte Unsigned
        result = memory.read_byte(address)
    
    elif funct3 == 0b101:  # LHU - Load Halfword Unsigned
        result = memory.read_halfword(address)
    
    cpu.write_reg(decoded['rd'], result)
    cpu.pc += 4
    return True


def exec_jalr(cpu, decoded):
    """JALR - Jump and Link Register: rd = pc+4; pc = (rs1 + imm) & ~1"""
    rs1_val = cpu.read_reg(decoded['rs1'])
    target = (rs1_val + decoded['imm']) & 0xFFFFFFFE  # Clear bit 0
    cpu.write_reg(decoded['rd'], (cpu.pc + 4) & 0xFFFFFFFF)
    cpu.pc = target
    return True


# ============================================================================
# S-Type Instructions - Stores
# ============================================================================

def exec_store(cpu, memory, decoded):
    """Execute S-type store instructions (SB, SH, SW)"""
    funct3 = decoded['funct3']
    rs1_val = cpu.read_reg(decoded['rs1'])
    rs2_val = cpu.read_reg(decoded['rs2'])
    address = (rs1_val + decoded['imm']) & 0xFFFFFFFF
    
    if funct3 == 0b000:  # SB - Store Byte
        memory.write_byte(address, rs2_val & 0xFF)
    
    elif funct3 == 0b001:  # SH - Store Halfword
        memory.write_halfword(address, rs2_val & 0xFFFF)
    
    elif funct3 == 0b010:  # SW - Store Word
        memory.write_word(address, rs2_val)
    
    cpu.pc += 4
    return True


# ============================================================================
# B-Type Instructions - Branches
# ============================================================================

def exec_branch(cpu, decoded):
    """Execute B-type branch instructions (BEQ, BNE, BLT, BGE, BLTU, BGEU)"""
    funct3 = decoded['funct3']
    rs1_val = cpu.read_reg(decoded['rs1'])
    rs2_val = cpu.read_reg(decoded['rs2'])
    
    # Convert to signed for signed comparisons
    rs1_signed = rs1_val if rs1_val < 0x80000000 else rs1_val - 0x100000000
    rs2_signed = rs2_val if rs2_val < 0x80000000 else rs2_val - 0x100000000
    
    branch_taken = False
    
    if funct3 == 0b000:  # BEQ
        branch_taken = (rs1_val == rs2_val)
    elif funct3 == 0b001:  # BNE
        branch_taken = (rs1_val != rs2_val)
    elif funct3 == 0b100:  # BLT
        branch_taken = (rs1_signed < rs2_signed)
    elif funct3 == 0b101:  # BGE
        branch_taken = (rs1_signed >= rs2_signed)
    elif funct3 == 0b110:  # BLTU
        branch_taken = (rs1_val < rs2_val)
    elif funct3 == 0b111:  # BGEU
        branch_taken = (rs1_val >= rs2_val)
    
    if branch_taken:
        cpu.pc = (cpu.pc + decoded['imm']) & 0xFFFFFFFF
    else:
        cpu.pc += 4
    
    return True


# ============================================================================
# U-Type Instructions - Upper Immediate
# ============================================================================

def exec_lui(cpu, decoded):
    """LUI - Load Upper Immediate: rd = imm"""
    cpu.write_reg(decoded['rd'], decoded['imm'] & 0xFFFFFFFF)
    cpu.pc += 4
    return True


def exec_auipc(cpu, decoded):
    """AUIPC - Add Upper Immediate to PC: rd = pc + imm"""
    result = (cpu.pc + decoded['imm']) & 0xFFFFFFFF
    cpu.write_reg(decoded['rd'], result)
    cpu.pc += 4
    return True


# ============================================================================
# J-Type Instructions - Jumps
# ============================================================================

def exec_jal(cpu, decoded):
    """JAL - Jump and Link: rd = pc+4; pc = pc + imm"""
    cpu.write_reg(decoded['rd'], (cpu.pc + 4) & 0xFFFFFFFF)
    cpu.pc = (cpu.pc + decoded['imm']) & 0xFFFFFFFF
    return True
