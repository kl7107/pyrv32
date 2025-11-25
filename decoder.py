"""
Instruction Decoder - Decode RV32IMC instructions

Decodes instruction encoding into opcode, register fields, immediates, etc.
"""


def decode_instruction(insn):
    """
    Decode a 32-bit RISC-V instruction.
    
    Args:
        insn: 32-bit instruction word
        
    Returns:
        Dictionary with decoded fields:
        - opcode: 7-bit opcode
        - rd: Destination register (0-31)
        - funct3: 3-bit function code
        - rs1: Source register 1 (0-31)
        - rs2: Source register 2 (0-31)
        - funct7: 7-bit function code
        - imm: Immediate value (sign-extended for relevant types)
        - format: Instruction format (R, I, S, B, U, J)
    """
    insn = insn & 0xFFFFFFFF
    
    # Common fields
    opcode = insn & 0x7F
    rd = (insn >> 7) & 0x1F
    funct3 = (insn >> 12) & 0x7
    rs1 = (insn >> 15) & 0x1F
    rs2 = (insn >> 20) & 0x1F
    funct7 = (insn >> 25) & 0x7F
    
    # Determine format and decode immediate
    fmt = None
    imm = 0
    
    # U-type: LUI, AUIPC
    if opcode in [0b0110111, 0b0010111]:
        fmt = 'U'
        imm = insn & 0xFFFFF000  # Upper 20 bits already in position
        # Sign extend from bit 31
        if imm & 0x80000000:
            imm |= 0xFFFFFFFF00000000
    
    # J-type: JAL
    elif opcode == 0b1101111:
        fmt = 'J'
        imm_20 = (insn >> 31) & 0x1
        imm_10_1 = (insn >> 21) & 0x3FF
        imm_11 = (insn >> 20) & 0x1
        imm_19_12 = (insn >> 12) & 0xFF
        imm = (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1)
        # Sign extend from bit 20
        if imm & 0x100000:
            imm |= 0xFFFFFFFFFFE00000
        imm = sign_extend_32(imm)
    
    # B-type: Branch instructions
    elif opcode == 0b1100011:
        fmt = 'B'
        imm_12 = (insn >> 31) & 0x1
        imm_10_5 = (insn >> 25) & 0x3F
        imm_4_1 = (insn >> 8) & 0xF
        imm_11 = (insn >> 7) & 0x1
        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
        # Sign extend from bit 12
        if imm & 0x1000:
            imm |= 0xFFFFFFFFFFFFE000
        imm = sign_extend_32(imm)
    
    # S-type: Store instructions
    elif opcode == 0b0100011:
        fmt = 'S'
        imm_11_5 = (insn >> 25) & 0x7F
        imm_4_0 = (insn >> 7) & 0x1F
        imm = (imm_11_5 << 5) | imm_4_0
        # Sign extend from bit 11
        if imm & 0x800:
            imm |= 0xFFFFFFFFFFFFF000
        imm = sign_extend_32(imm)
    
    # I-type: Immediate ALU, loads, JALR, etc.
    elif opcode in [0b0010011, 0b0000011, 0b1100111, 0b0001111, 0b1110011]:
        fmt = 'I'
        imm = (insn >> 20) & 0xFFF
        # Sign extend from bit 11
        if imm & 0x800:
            imm |= 0xFFFFFFFFFFFFF000
        imm = sign_extend_32(imm)
    
    # R-type: Register ALU operations
    elif opcode in [0b0110011, 0b0111011]:
        fmt = 'R'
        imm = 0  # No immediate
    
    else:
        fmt = 'Unknown'
    
    return {
        'opcode': opcode,
        'rd': rd,
        'funct3': funct3,
        'rs1': rs1,
        'rs2': rs2,
        'funct7': funct7,
        'imm': imm,
        'format': fmt,
        'raw': insn
    }


def sign_extend_32(value):
    """
    Sign-extend a value to 32 bits.
    
    Args:
        value: Integer value (may be larger than 32 bits)
        
    Returns:
        32-bit sign-extended value (masked to lower 32 bits)
    """
    # Simply mask to 32 bits - Python will handle the sign correctly
    # when the value is used in signed operations
    return value & 0xFFFFFFFF


def get_instruction_name(decoded):
    """
    Get a human-readable name for an instruction.
    
    Args:
        decoded: Decoded instruction dict from decode_instruction()
        
    Returns:
        String name of instruction (e.g., "LUI", "ADDI", "SB")
    """
    opcode = decoded['opcode']
    funct3 = decoded['funct3']
    funct7 = decoded['funct7']
    
    # U-type
    if opcode == 0b0110111:
        return "LUI"
    elif opcode == 0b0010111:
        return "AUIPC"
    
    # J-type
    elif opcode == 0b1101111:
        return "JAL"
    
    # I-type - Immediate ALU
    elif opcode == 0b0010011:
        if funct3 == 0b000:
            return "ADDI"
        elif funct3 == 0b010:
            return "SLTI"
        elif funct3 == 0b011:
            return "SLTIU"
        elif funct3 == 0b100:
            return "XORI"
        elif funct3 == 0b110:
            return "ORI"
        elif funct3 == 0b111:
            return "ANDI"
        elif funct3 == 0b001:
            return "SLLI"
        elif funct3 == 0b101:
            return "SRLI" if funct7 == 0 else "SRAI"
    
    # I-type - Loads
    elif opcode == 0b0000011:
        if funct3 == 0b000:
            return "LB"
        elif funct3 == 0b001:
            return "LH"
        elif funct3 == 0b010:
            return "LW"
        elif funct3 == 0b100:
            return "LBU"
        elif funct3 == 0b101:
            return "LHU"
    
    # S-type - Stores
    elif opcode == 0b0100011:
        if funct3 == 0b000:
            return "SB"
        elif funct3 == 0b001:
            return "SH"
        elif funct3 == 0b010:
            return "SW"
    
    # B-type - Branches
    elif opcode == 0b1100011:
        if funct3 == 0b000:
            return "BEQ"
        elif funct3 == 0b001:
            return "BNE"
        elif funct3 == 0b100:
            return "BLT"
        elif funct3 == 0b101:
            return "BGE"
        elif funct3 == 0b110:
            return "BLTU"
        elif funct3 == 0b111:
            return "BGEU"
    
    # R-type - Register ALU
    elif opcode == 0b0110011:
        if funct3 == 0b000:
            return "ADD" if funct7 == 0 else "SUB"
        elif funct3 == 0b001:
            return "SLL"
        elif funct3 == 0b010:
            return "SLT"
        elif funct3 == 0b011:
            return "SLTU"
        elif funct3 == 0b100:
            return "XOR"
        elif funct3 == 0b101:
            return "SRL" if funct7 == 0 else "SRA"
        elif funct3 == 0b110:
            return "OR"
        elif funct3 == 0b111:
            return "AND"
    
    # JALR
    elif opcode == 0b1100111:
        return "JALR"
    
    return "UNKNOWN"
