"""
Instruction Decoder - Decode RV32IMC instructions

Decodes instruction encoding into opcode, register fields, immediates, etc.

Decoder Coverage vs docs/refs/rv32_instruction_formats.txt:

RV32I Base (40 instructions) - COMPLETE:
  ✓ R-type: ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND
  ✓ I-type: JALR, LB, LH, LW, LBU, LHU, ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI
  ✓ S-type: SB, SH, SW
  ✓ B-type: BEQ, BNE, BLT, BGE, BLTU, BGEU
  ✓ U-type: LUI, AUIPC
  ✓ J-type: JAL
  ✓ FENCE (I-type format)
  ✓ ECALL/EBREAK (I-type format, distinguished by imm field)

RV32M Extension (8 instructions) - COMPLETE:
  ✓ R-type (funct7=1): MUL, MULH, MULHSU, MULHU, DIV, DIVU, REM, REMU

RV32C Compressed Extension - NOT IMPLEMENTED:
  ✗ Not implemented - requires 16-bit instruction handling
  ✗ Missing 9 compressed formats: CR, CI, CSS, CIW, CL, CS, CA, CB, CJ
  See docs/refs/rv_c.txt, rv32_c.txt, rv32_instruction_formats.txt

Note: CSR instructions (Zicsr) and FENCE.I (Zifencei) are separate extensions,
      not part of base RV32I.
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
        - name: Human-readable instruction name (added for execute.py)
    """
    insn = insn & 0xFFFFFFFF
    
    # Common fields
    opcode = insn & 0x7F
    rd = (insn >> 7) & 0x1F
    funct3 = (insn >> 12) & 0x7
    rs1 = (insn >> 15) & 0x1F
    rs2 = (insn >> 20) & 0x1F
    funct7 = (insn >> 25) & 0x7F
    
    # Determine format and decode immediate (order: R, I, S, B, U, J)
    fmt = None
    imm = 0
    
    # R-type: Register ALU operations
    if opcode in [0b0110011, 0b0111011]:
        fmt = 'R'
        imm = 0  # No immediate
    
    # I-type: Immediate ALU, loads, JALR, FENCE, ECALL/EBREAK
    elif opcode in [0b0010011, 0b0000011, 0b1100111, 0b0001111, 0b1110011]:
        fmt = 'I'
        imm = (insn >> 20) & 0xFFF
        # Sign extend from bit 11
        if imm & 0x800:
            imm |= 0xFFFFFFFFFFFFF000
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
    
    # U-type: LUI, AUIPC
    elif opcode in [0b0110111, 0b0010111]:
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
    
    else:
        fmt = 'Unknown'
    
    decoded = {
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
    
    # Add instruction name to avoid re-decoding in execute.py
    decoded['name'] = get_instruction_name(decoded)
    
    return decoded


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
        
    Complete for RV32IM (48 instructions total):
        - 40 RV32I base instructions
        - 8 RV32M extension instructions
    """
    opcode = decoded['opcode']
    funct3 = decoded['funct3']
    funct7 = decoded['funct7']
    
    # R-type - Register ALU (includes M extension via funct7=1)
    if opcode == 0b0110011:
        if funct7 == 1:  # M extension
            if funct3 == 0b000:
                return "MUL"
            elif funct3 == 0b001:
                return "MULH"
            elif funct3 == 0b010:
                return "MULHSU"
            elif funct3 == 0b011:
                return "MULHU"
            elif funct3 == 0b100:
                return "DIV"
            elif funct3 == 0b101:
                return "DIVU"
            elif funct3 == 0b110:
                return "REM"
            elif funct3 == 0b111:
                return "REMU"
        elif funct3 == 0b000:
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
    
    # I-type - JALR
    elif opcode == 0b1100111:
        return "JALR"
    
    # I-type - FENCE
    elif opcode == 0b0001111:
        if funct3 == 0b000:
            return "FENCE"
        # Note: FENCE.I would be funct3=0b001 but that's in Zifencei extension
    
    # I-type - System instructions (ECALL, EBREAK)
    elif opcode == 0b1110011:
        if funct3 == 0b000:
            imm = decoded['imm']
            if imm == 0x000:
                return "ECALL"
            elif imm == 0x001:
                return "EBREAK"
        # Note: CSR instructions (CSRRW, CSRRS, etc.) would be other funct3 values
        # but those are in Zicsr extension, not base RV32I
    
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
    
    # U-type - LUI
    elif opcode == 0b0110111:
        return "LUI"
    
    # U-type - AUIPC
    elif opcode == 0b0010111:
        return "AUIPC"
    
    # J-type - JAL
    elif opcode == 0b1101111:
        return "JAL"
    
    # RV32C - 16-bit compressed instructions not implemented
    # Unknown instruction - raise exception to make it obvious
    raise NotImplementedError(
        f"Unknown/unimplemented instruction: opcode=0b{opcode:07b}, "
        f"funct3=0b{funct3:03b}, funct7=0b{funct7:07b}, raw=0x{decoded['raw']:08x}"
    )
