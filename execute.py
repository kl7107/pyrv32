"""
Instruction Execution - Execute decoded RV32I instructions

Implements the execution logic for RV32I base instruction set.
"""

from decoder import decode_instruction, get_instruction_name, sign_extend_32


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
    opcode = decoded['opcode']
    
    # LUI - Load Upper Immediate
    if opcode == 0b0110111:
        return exec_lui(cpu, decoded)
    
    # AUIPC - Add Upper Immediate to PC
    elif opcode == 0b0010111:
        return exec_auipc(cpu, decoded)
    
    # I-type - Immediate ALU operations
    elif opcode == 0b0010011:
        return exec_immediate_alu(cpu, decoded)
    
    # S-type - Store instructions
    elif opcode == 0b0100011:
        return exec_store(cpu, memory, decoded)
    
    # I-type - Load instructions
    elif opcode == 0b0000011:
        return exec_load(cpu, memory, decoded)
    
    # R-type - Register ALU operations
    elif opcode == 0b0110011:
        return exec_register_alu(cpu, decoded)
    
    # JAL - Jump and Link
    elif opcode == 0b1101111:
        return exec_jal(cpu, decoded)
    
    # JALR - Jump and Link Register
    elif opcode == 0b1100111:
        return exec_jalr(cpu, decoded)
    
    # B-type - Branch instructions
    elif opcode == 0b1100011:
        return exec_branch(cpu, decoded)
    
    # Unknown instruction - halt
    else:
        print(f"Unknown instruction: 0x{insn:08x}")
        return False


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


def exec_immediate_alu(cpu, decoded):
    """Execute I-type ALU operations (ADDI, SLTI, XORI, ORI, ANDI, etc.)"""
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


# ============================================================================
# M Extension - Multiply/Divide Instructions
# ============================================================================

def exec_mul(rs1_signed, rs2_signed):
    """
    MUL - Multiply (lower 32 bits of signed multiplication)
    
    Encoding: R-type, funct3=0b000, funct7=0b0000001
    Format: mul rd, rs1, rs2
    
    Performs signed multiplication of two 32-bit values and returns
    the lower 32 bits of the 64-bit result.
    
    Args:
        rs1_signed: First operand (signed 32-bit integer)
        rs2_signed: Second operand (signed 32-bit integer)
        
    Returns:
        Lower 32 bits of the multiplication result (as unsigned 32-bit)
        
    Note:
        Lower 32 bits are the same whether operands are treated as
        signed or unsigned. No overflow exceptions.
    """
    # Perform 64-bit signed multiplication
    product = rs1_signed * rs2_signed
    
    # Return lower 32 bits as unsigned
    return product & 0xFFFFFFFF


def exec_mulh(rs1_signed, rs2_signed):
    """
    MULH - Multiply High (upper 32 bits of signed × signed multiplication)
    
    Encoding: R-type, funct3=0b001, funct7=0b0000001
    Format: mulh rd, rs1, rs2
    
    Performs signed multiplication of two 32-bit values and returns
    the upper 32 bits of the 64-bit result.
    
    Args:
        rs1_signed: First operand (signed 32-bit integer)
        rs2_signed: Second operand (signed 32-bit integer)
        
    Returns:
        Upper 32 bits of the multiplication result (as unsigned 32-bit)
        
    Note:
        Both operands treated as signed. Use MULHU for unsigned×unsigned,
        MULHSU for signed×unsigned.
    """
    # Perform 64-bit signed multiplication
    product = rs1_signed * rs2_signed
    
    # Return upper 32 bits as unsigned (shift right by 32)
    return (product >> 32) & 0xFFFFFFFF


def exec_mulhsu(rs1_signed, rs2_val):
    """
    MULHSU - Multiply High Signed-Unsigned (upper 32 bits of signed × unsigned)
    
    Performs multiplication of a signed 32-bit value with an unsigned 32-bit value
    and returns the upper 32 bits of the 64-bit result.
    
    Args:
        rs1_signed: First operand (signed 32-bit integer)
        rs2_val: Second operand (unsigned 32-bit integer)
        
    Returns:
        Upper 32 bits of the multiplication result (as unsigned 32-bit)
    """
    # rs2_val is already unsigned (0 to 0xFFFFFFFF)
    # rs1_signed is signed (-0x80000000 to 0x7FFFFFFF)
    # Python handles the mixed sign multiplication correctly
    product = rs1_signed * rs2_val
    
    # Return upper 32 bits as unsigned
    return (product >> 32) & 0xFFFFFFFF


def exec_mulhu(rs1_val, rs2_val):
    """
    MULHU - Multiply High Unsigned-Unsigned (upper 32 bits of unsigned × unsigned)
    
    Performs unsigned multiplication of two 32-bit values and returns
    the upper 32 bits of the 64-bit result.
    
    Args:
        rs1_val: First operand (unsigned 32-bit integer)
        rs2_val: Second operand (unsigned 32-bit integer)
        
    Returns:
        Upper 32 bits of the multiplication result (as unsigned 32-bit)
    """
    # Both operands are unsigned (0 to 0xFFFFFFFF)
    product = rs1_val * rs2_val
    
    # Return upper 32 bits as unsigned
    return (product >> 32) & 0xFFFFFFFF


def exec_div(rs1_signed, rs2_signed):
    """
    DIV - Divide Signed
    
    Performs signed division of two 32-bit integers.
    
    Special cases per RISC-V specification:
    - Division by zero: returns -1 (0xFFFFFFFF)
    - Overflow (0x80000000 / -1): returns 0x80000000
    
    Args:
        rs1_signed: Dividend (signed 32-bit integer)
        rs2_signed: Divisor (signed 32-bit integer)
        
    Returns:
        Quotient as unsigned 32-bit value
    """
    # Division by zero
    if rs2_signed == 0:
        return 0xFFFFFFFF  # -1
    
    # Overflow case: most negative / -1
    # In two's complement, -(-2^31) cannot be represented
    if rs1_signed == -2147483648 and rs2_signed == -1:
        return 0x80000000  # Return dividend unchanged
    
    # Signed division with truncation towards zero (not floor division)
    # Python's // operator does floor division, but RISC-V DIV truncates towards zero
    # Use int() to truncate towards zero
    quotient = int(rs1_signed / rs2_signed)
    
    # Convert to unsigned 32-bit
    return quotient & 0xFFFFFFFF


def exec_divu(rs1_val, rs2_val):
    """
    DIVU - Divide Unsigned
    
    Performs unsigned division of two 32-bit integers.
    
    Special cases per RISC-V specification:
    - Division by zero: returns 0xFFFFFFFF (all 1s)
    
    Args:
        rs1_val: Dividend (unsigned 32-bit integer)
        rs2_val: Divisor (unsigned 32-bit integer)
        
    Returns:
        Quotient as unsigned 32-bit value
    """
    # Division by zero
    if rs2_val == 0:
        return 0xFFFFFFFF  # All 1s
    
    # Unsigned division (straightforward)
    quotient = rs1_val // rs2_val
    
    # Already unsigned 32-bit
    return quotient & 0xFFFFFFFF


def exec_rem(rs1_signed, rs2_signed):
    """
    REM - Remainder Signed
    
    Computes the signed remainder of division.
    
    Special cases per RISC-V specification:
    - Division by zero: returns dividend (rs1)
    - Overflow (0x80000000 % -1): returns 0
    - Remainder has same sign as dividend
    
    Args:
        rs1_signed: Dividend (signed 32-bit integer)
        rs2_signed: Divisor (signed 32-bit integer)
        
    Returns:
        Remainder as unsigned 32-bit value
    """
    # Division by zero
    if rs2_signed == 0:
        return rs1_signed & 0xFFFFFFFF  # Return dividend
    
    # Overflow case: most negative % -1
    if rs1_signed == -2147483648 and rs2_signed == -1:
        return 0  # Per RISC-V spec
    
    # Signed remainder
    # Python's % operator gives remainder with sign of divisor,
    # but RISC-V REM gives remainder with sign of dividend
    # Use: a % b = a - (a / b) * b where / truncates towards zero
    quotient = int(rs1_signed / rs2_signed)
    remainder = rs1_signed - quotient * rs2_signed
    
    # Convert to unsigned 32-bit
    return remainder & 0xFFFFFFFF


def exec_remu(rs1_val, rs2_val):
    """
    REMU - Remainder Unsigned
    
    Computes the unsigned remainder of division.
    
    Special cases per RISC-V specification:
    - Division by zero: returns dividend (rs1)
    
    Args:
        rs1_val: Dividend (unsigned 32-bit integer)
        rs2_val: Divisor (unsigned 32-bit integer)
        
    Returns:
        Remainder as unsigned 32-bit value
    """
    # Division by zero
    if rs2_val == 0:
        return rs1_val  # Return dividend
    
    # Unsigned remainder (straightforward)
    remainder = rs1_val % rs2_val
    
    # Already unsigned 32-bit
    return remainder & 0xFFFFFFFF


def exec_register_alu(cpu, decoded):
    """Execute R-type ALU operations (ADD, SUB, AND, OR, XOR, MUL, etc.)"""
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


def exec_jal(cpu, decoded):
    """JAL - Jump and Link: rd = pc+4; pc = pc + imm"""
    cpu.write_reg(decoded['rd'], (cpu.pc + 4) & 0xFFFFFFFF)
    cpu.pc = (cpu.pc + decoded['imm']) & 0xFFFFFFFF
    return True


def exec_jalr(cpu, decoded):
    """JALR - Jump and Link Register: rd = pc+4; pc = (rs1 + imm) & ~1"""
    rs1_val = cpu.read_reg(decoded['rs1'])
    target = (rs1_val + decoded['imm']) & 0xFFFFFFFE  # Clear bit 0
    cpu.write_reg(decoded['rd'], (cpu.pc + 4) & 0xFFFFFFFF)
    cpu.pc = target
    return True


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
