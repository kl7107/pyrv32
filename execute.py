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
    """
    MUL - Multiply (lower 32 bits)
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b000, opcode=0b0110011
    Syntax: mul rd, rs1, rs2
    
    Operation: rd = (rs1 × rs2)[31:0]
    
    Description:
        Performs signed multiplication of two 32-bit values and returns
        the lower 32 bits of the 64-bit result. The lower 32 bits are
        the same whether operands are treated as signed or unsigned.
    
    Edge Cases to Test:
        - Zero × Zero = 0
        - Zero × Any = 0
        - One × Any = Any
        - Positive × Positive (no overflow)
        - Positive × Positive (with overflow) - keep lower 32 bits
        - Negative × Negative (result positive)
        - Positive × Negative (result negative)
        - Negative × Positive (result negative)
        - Max positive × Max positive (0x7FFFFFFF × 0x7FFFFFFF)
        - Max negative × Max negative (0x80000000 × 0x80000000)
        - Powers of two (verify shift-like behavior)
        - rd = x0 (write ignored, x0 stays 0)
        - rs1 = rs2 (squaring)
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Multiplication Operations
    """
    product = rs1_signed * rs2_signed
    return product & 0xFFFFFFFF


def exec_mulh(rs1_signed, rs2_signed):
    """
    MULH - Multiply High (upper 32 bits of signed × signed)
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b001, opcode=0b0110011
    Syntax: mulh rd, rs1, rs2
    
    Operation: rd = (rs1 × rs2)[63:32] (signed × signed)
    
    Description:
        Performs signed multiplication of two 32-bit values and returns
        the upper 32 bits of the 64-bit result. Both operands are treated
        as signed two's complement integers.
    
    Edge Cases to Test:
        - Small positive × Small positive (upper bits = 0)
        - Large positive × Large positive (verify upper bits)
        - Negative × Negative (result positive, verify upper bits)
        - Positive × Negative (result negative, verify sign extension)
        - Max positive × Max positive (0x7FFFFFFF × 0x7FFFFFFF)
        - Max negative × Max negative (0x80000000 × 0x80000000)
        - Max positive × -1 (should give -1 in upper bits)
        - Medium values (e.g., 0x40000000 × 0x40000000)
        - Zero × Any = 0
        - One × Any = 0 (since result fits in lower 32 bits)
        - rd = x0 (write ignored)
        - rs1 = rs2 (squaring)
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Multiplication Operations
    """
    product = rs1_signed * rs2_signed
    return (product >> 32) & 0xFFFFFFFF


def exec_mulhsu(rs1_signed, rs2_val):
    """
    MULHSU - Multiply High Signed-Unsigned
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b010, opcode=0b0110011
    Syntax: mulhsu rd, rs1, rs2
    
    Operation: rd = (rs1 × rs2)[63:32] (signed × unsigned)
    
    Description:
        Performs multiplication where rs1 is treated as signed and rs2
        is treated as unsigned. Returns the upper 32 bits of the 64-bit
        result. Useful for signed arithmetic with large unsigned offsets.
    
    Edge Cases to Test:
        - Small positive × Small unsigned (upper bits = 0)
        - Positive × Large unsigned (verify upper bits)
        - Negative × Large unsigned (verify sign handling)
        - Max positive × Max unsigned (0x7FFFFFFF × 0xFFFFFFFF)
        - Max negative × Max unsigned (0x80000000 × 0xFFFFFFFF)
        - Negative × 0x10000 (verify sign extension vs zero extension)
        - -1 × 1 (should handle sign correctly)
        - -2 × Large unsigned
        - 1 × Max unsigned (should give 0 in upper bits)
        - Zero × Any = 0
        - rd = x0 (write ignored)
        - rs1 = rs2 (same register, sign vs unsigned interpretation)
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Multiplication Operations
    """
    product = rs1_signed * rs2_val
    return (product >> 32) & 0xFFFFFFFF


def exec_mulhu(rs1_val, rs2_val):
    """
    MULHU - Multiply High Unsigned-Unsigned
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b011, opcode=0b0110011
    Syntax: mulhu rd, rs1, rs2
    
    Operation: rd = (rs1 × rs2)[63:32] (unsigned × unsigned)
    
    Description:
        Performs unsigned multiplication of two 32-bit values and returns
        the upper 32 bits of the 64-bit result. Both operands are treated
        as unsigned integers.
    
    Edge Cases to Test:
        - Small values (upper bits = 0)
        - Medium values (e.g., 0x10000 × 0x10000 = 0x00000001_00000000)
        - Max unsigned × Max unsigned (0xFFFFFFFF × 0xFFFFFFFF)
        - Max unsigned × 1 (should give 0)
        - Max unsigned × 2 (should give 1)
        - Max unsigned × 0x80000000 (test high bit handling)
        - 0x80000000 × 0x80000000 (power of 2)
        - 0x40000000 × 0x40000000
        - 0xFFFF × 0xFFFF
        - Powers of two (verify expected shift behavior)
        - Zero × Any = 0
        - Commutativity (a × b = b × a)
        - No negative results (all unsigned)
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Multiplication Operations
    """
    product = rs1_val * rs2_val
    return (product >> 32) & 0xFFFFFFFF


def exec_div(rs1_signed, rs2_signed):
    """
    DIV - Divide Signed
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b100, opcode=0b0110011
    Syntax: div rd, rs1, rs2
    
    Operation: rd = rs1 ÷ rs2 (signed, truncated toward zero)
    
    Description:
        Performs signed division. Quotient is rounded toward zero (truncation).
        Special cases per RISC-V spec:
        - Division by zero: returns -1 (0xFFFFFFFF)
        - Overflow (MIN_INT ÷ -1): returns MIN_INT (0x80000000)
    
    Edge Cases to Test:
        - Normal division (positive ÷ positive)
        - Negative ÷ positive (negative result)
        - Positive ÷ negative (negative result)
        - Negative ÷ negative (positive result)
        - Division by zero (any ÷ 0 = -1)
        - Overflow: -2147483648 ÷ -1 = -2147483648 (MIN_INT unchanged)
        - Zero dividend (0 ÷ any = 0)
        - Division by 1 (identity)
        - Division by -1 (negation, except overflow case)
        - Truncation toward zero: 7 ÷ 2 = 3, -7 ÷ 2 = -3
        - Large numbers divided
        - Max positive ÷ various divisors
        - Max negative ÷ various divisors
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Division Operations
    """
    if rs2_signed == 0:
        return 0xFFFFFFFF  # -1
    if rs1_signed == -2147483648 and rs2_signed == -1:
        return 0x80000000  # Overflow case
    quotient = int(rs1_signed / rs2_signed)
    return quotient & 0xFFFFFFFF


def exec_divu(rs1_val, rs2_val):
    """
    DIVU - Divide Unsigned
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b101, opcode=0b0110011
    Syntax: divu rd, rs1, rs2
    
    Operation: rd = rs1 ÷ rs2 (unsigned)
    
    Description:
        Performs unsigned division. Both operands treated as unsigned.
        Special case per RISC-V spec:
        - Division by zero: returns 0xFFFFFFFF (all bits set)
    
    Edge Cases to Test:
        - Normal division
        - Large unsigned ÷ small value
        - Division by zero (any ÷ 0 = 0xFFFFFFFF)
        - Zero dividend (0 ÷ any = 0)
        - Division by 1 (identity)
        - Max unsigned ÷ 2, ÷ 3, etc.
        - Max unsigned ÷ Max unsigned = 1
        - (Max unsigned - 1) ÷ Max unsigned = 0
        - Powers of two (should behave like right shift)
        - Truncation (7 ÷ 2 = 3)
        - Large numbers
        - No overflow case (unlike signed division)
        - No negative results (all unsigned)
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Division Operations
    """
    if rs2_val == 0:
        return 0xFFFFFFFF
    quotient = rs1_val // rs2_val
    return quotient & 0xFFFFFFFF


def exec_rem(rs1_signed, rs2_signed):
    """
    REM - Remainder Signed
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b110, opcode=0b0110011
    Syntax: rem rd, rs1, rs2
    
    Operation: rd = rs1 % rs2 (signed, remainder has sign of dividend)
    
    Description:
        Computes the remainder of signed division. The remainder has the
        same sign as the dividend (rs1). Follows the identity:
        dividend = divisor × quotient + remainder
        
        Special cases per RISC-V spec:
        - Division by zero: returns dividend (rs1)
        - Overflow (MIN_INT % -1): returns 0
    
    Edge Cases to Test:
        - Normal remainder (positive % positive)
        - With remainder (7 % 2 = 1)
        - Division by zero (any % 0 = dividend)
        - Overflow: -2147483648 % -1 = 0
        - Zero dividend (0 % any = 0)
        - Negative dividend, positive divisor (remainder negative)
        - Positive dividend, negative divisor (remainder positive)
        - Negative dividend, negative divisor (remainder negative)
        - Sign of remainder follows dividend: -7 % 2 = -1, 7 % -2 = 1
        - Large numbers
        - Max positive % various divisors
        - Max negative % various divisors
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Division Operations
    """
    if rs2_signed == 0:
        return rs1_signed & 0xFFFFFFFF
    if rs1_signed == -2147483648 and rs2_signed == -1:
        return 0
    quotient = int(rs1_signed / rs2_signed)
    remainder = rs1_signed - quotient * rs2_signed
    return remainder & 0xFFFFFFFF


def exec_remu(rs1_val, rs2_val):
    """
    REMU - Remainder Unsigned
    
    Format: R-type
    Encoding: funct7=0b0000001, funct3=0b111, opcode=0b0110011
    Syntax: remu rd, rs1, rs2
    
    Operation: rd = rs1 % rs2 (unsigned)
    
    Description:
        Computes the remainder of unsigned division. Both operands are
        treated as unsigned integers.
        
        Special case per RISC-V spec:
        - Division by zero: returns dividend (rs1)
    
    Edge Cases to Test:
        - Normal remainder
        - With remainder (7 % 2 = 1)
        - Division by zero (any % 0 = dividend)
        - Zero dividend (0 % any = 0)
        - Max unsigned % 2, % 3, etc.
        - Large % small
        - Powers of two (should behave like AND mask)
        - Max unsigned % Max unsigned = 0
        - (Max unsigned - 1) % Max unsigned = Max unsigned - 1
        - Large numbers
        - No negative results (all unsigned)
    
    RISC-V Spec Reference:
        RV32M Standard Extension, Version 2.0
        Section: Division Operations
    """
    if rs2_val == 0:
        return rs1_val
    remainder = rs1_val % rs2_val
    return remainder & 0xFFFFFFFF


def exec_register_alu(cpu, decoded):
    """
    Execute R-type ALU operations (ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND, MUL, etc.)
    
    R-Type Format:
        funct7 (7) | rs2 (5) | rs1 (5) | funct3 (3) | rd (5) | opcode (7)
    
    RV32I Base Instructions (funct7=0b0000000 or 0b0100000):
    
    ADD (funct7=0b0000000, funct3=0b000):
        Operation: rd = rs1 + rs2
        Description: Add two registers, ignore overflow
        Edge Cases: zero+zero, overflow wrapping, max values, negative addition
    
    SUB (funct7=0b0100000, funct3=0b000):
        Operation: rd = rs1 - rs2
        Description: Subtract rs2 from rs1, ignore overflow
        Edge Cases: zero-zero, underflow wrapping, max-min, negative subtraction
    
    SLL (funct7=0b0000000, funct3=0b001):
        Operation: rd = rs1 << rs2[4:0]
        Description: Shift left logical, shift amount is lower 5 bits of rs2
        Edge Cases: shift by 0, shift by 31, shift by >31 (uses only lower 5 bits)
    
    SLT (funct7=0b0000000, funct3=0b010):
        Operation: rd = (rs1 <s rs2) ? 1 : 0
        Description: Set if less than (signed comparison)
        Edge Cases: equal values, max positive vs negative, boundary values
    
    SLTU (funct7=0b0000000, funct3=0b011):
        Operation: rd = (rs1 <u rs2) ? 1 : 0
        Description: Set if less than (unsigned comparison)
        Edge Cases: equal values, 0xFFFFFFFF vs 0, boundary values
    
    XOR (funct7=0b0000000, funct3=0b100):
        Operation: rd = rs1 ^ rs2
        Description: Bitwise exclusive OR
        Edge Cases: same values (result 0), all 1s XOR all 0s, bit patterns
    
    SRL (funct7=0b0000000, funct3=0b101):
        Operation: rd = rs1 >> rs2[4:0]
        Description: Shift right logical (zero extension)
        Edge Cases: shift by 0, shift by 31, negative values (no sign extend)
    
    SRA (funct7=0b0100000, funct3=0b101):
        Operation: rd = rs1 >>s rs2[4:0]
        Description: Shift right arithmetic (sign extension)
        Edge Cases: shift positive (fill with 0), shift negative (fill with 1)
    
    OR (funct7=0b0000000, funct3=0b110):
        Operation: rd = rs1 | rs2
        Description: Bitwise OR
        Edge Cases: same values, all 0s, all 1s, bit patterns
    
    AND (funct7=0b0000000, funct3=0b111):
        Operation: rd = rs1 & rs2
        Description: Bitwise AND
        Edge Cases: same values, all 0s (result 0), all 1s, bit masking
    
    RV32M Extension (funct7=0b0000001): See individual exec_mul/div/rem functions
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.4: Integer Computational Instructions
        RV32M Standard Extension, Version 2.0
    """
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
    """
    Execute I-type ALU operations (ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI)
    
    I-Type Format:
        imm[11:0] (12) | rs1 (5) | funct3 (3) | rd (5) | opcode (7)
    Opcode: 0b0010011
    
    ADDI (funct3=0b000):
        Operation: rd = rs1 + sign_extend(imm)
        Description: Add sign-extended 12-bit immediate to register
        Edge Cases: zero+zero, overflow wrapping, negative immediate, max/min values
        Note: ADDI with rd=x0 is NOP; ADDI x0, rs1, imm also valid (write to x0 ignored)
    
    SLTI (funct3=0b010):
        Operation: rd = (rs1 <s sign_extend(imm)) ? 1 : 0
        Description: Set if less than immediate (signed)
        Edge Cases: equal values, positive vs negative, boundary values
    
    SLTIU (funct3=0b011):
        Operation: rd = (rs1 <u sign_extend(imm)) ? 1 : 0
        Description: Set if less than immediate (unsigned)
        Edge Cases: equal values, 0 vs 0xFFFFFFFF, boundary values
        Note: SLTIU rd, rs1, 1 sets rd=1 if rs1==0, rd=0 otherwise (compare to zero)
    
    XORI (funct3=0b100):
        Operation: rd = rs1 ^ sign_extend(imm)
        Description: Bitwise XOR with immediate
        Edge Cases: XOR with 0 (identity), XOR with -1 (bitwise NOT), bit patterns
        Note: XORI rd, rs1, -1 is bitwise NOT
    
    ORI (funct3=0b110):
        Operation: rd = rs1 | sign_extend(imm)
        Description: Bitwise OR with immediate
        Edge Cases: OR with 0 (identity), OR with -1 (all 1s), bit setting
    
    ANDI (funct3=0b111):
        Operation: rd = rs1 & sign_extend(imm)
        Description: Bitwise AND with immediate
        Edge Cases: AND with 0 (clears all), AND with -1 (identity), bit masking
    
    SLLI (funct3=0b001, imm[11:5]=0b0000000):
        Operation: rd = rs1 << shamt (shamt = imm[4:0])
        Description: Shift left logical immediate
        Edge Cases: shift by 0, shift by 31, shift out all bits
        Note: imm[11:5] must be 0, imm[4:0] is shift amount (0-31)
    
    SRLI (funct3=0b101, imm[11:5]=0b0000000):
        Operation: rd = rs1 >> shamt (shamt = imm[4:0])
        Description: Shift right logical immediate (zero extension)
        Edge Cases: shift by 0, shift by 31, negative values (no sign extend)
    
    SRAI (funct3=0b101, imm[11:5]=0b0100000):
        Operation: rd = rs1 >>s shamt (shamt = imm[4:0])
        Description: Shift right arithmetic immediate (sign extension)
        Edge Cases: shift positive (fill 0), shift negative (fill 1), shift by 31
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.4: Integer Computational Instructions
    """
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
    """
    Execute I-type load instructions (LB, LH, LW, LBU, LHU)
    
    I-Type Format:
        imm[11:0] (12) | rs1 (5) | funct3 (3) | rd (5) | opcode (7)
    Opcode: 0b0000011
    
    LB (funct3=0b000):
        Operation: rd = sign_extend(memory[rs1 + imm][7:0])
        Description: Load byte with sign extension
        Edge Cases: load 0x00 (extends to 0x00000000), load 0x80 (extends to 0xFFFFFF80),
                    load 0x7F (extends to 0x0000007F), load 0xFF (extends to 0xFFFFFFFF)
    
    LH (funct3=0b001):
        Operation: rd = sign_extend(memory[rs1 + imm][15:0])
        Description: Load halfword (16-bit) with sign extension
        Edge Cases: load 0x0000, load 0x8000 (extends to 0xFFFF8000),
                    load 0x7FFF, load 0xFFFF (extends to 0xFFFFFFFF),
                    misaligned address (implementation-defined, we handle it)
    
    LW (funct3=0b010):
        Operation: rd = memory[rs1 + imm][31:0]
        Description: Load word (32-bit)
        Edge Cases: load all 0s, load all 1s, load max positive/negative,
                    misaligned address, load from different memory regions
    
    LBU (funct3=0b100):
        Operation: rd = zero_extend(memory[rs1 + imm][7:0])
        Description: Load byte with zero extension
        Edge Cases: load 0x00, load 0x80 (extends to 0x00000080 - unsigned),
                    load 0xFF (extends to 0x000000FF)
    
    LHU (funct3=0b101):
        Operation: rd = zero_extend(memory[rs1 + imm][15:0])
        Description: Load halfword with zero extension
        Edge Cases: load 0x0000, load 0x8000 (extends to 0x00008000 - unsigned),
                    load 0xFFFF (extends to 0x0000FFFF)
    
    Common Edge Cases:
        - Zero offset (rs1 + 0)
        - Negative offset (sign-extended immediate)
        - Large offset (up to ±2047)
        - Address wraparound (0xFFFFFFFF + positive offset)
        - Load from UART region (0x10000000)
        - rd = x0 (write ignored)
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.6: Load and Store Instructions
    """
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
    """
    JALR - Jump and Link Register
    
    I-Type Format:
        imm[11:0] (12) | rs1 (5) | funct3 (3) | rd (5) | opcode (7)
    Opcode: 0b1100111, funct3: 0b000
    
    Operation:
        t = pc + 4
        pc = (rs1 + sign_extend(imm)) & ~1
        rd = t
    
    Description:
        Indirect jump to address (rs1 + offset), setting LSB to 0, save return address.
        Unlike JAL, target address is computed from register + offset.
    
    Edge Cases to Test:
        - Return from function (JALR x0, 0(x1) or ret pseudo-instruction)
        - Indirect function call (JALR x1, 0(rs1))
        - Jump with offset (JALR rd, offset(rs1))
        - Jump with zero offset (JALR rd, 0(rs1))
        - Negative offset
        - Large offset (±2047)
        - rd = x0 (discard return address, indirect jump)
        - rd = rs1 (overwrites base register with return address)
        - rs1 = x0 (jump to absolute address = sign_extend(imm))
        - LSB of target = 1 (should be cleared to 0)
        - Target address calculation overflow/wraparound
        - Jump to misaligned address (LSB cleared handles this)
    
    Common Usage:
        - JALR x0, 0(x1): Return from function (ret pseudo-instruction)
        - JALR x1, 0(rs1): Indirect function call
        - JALR x0, 0(rs1): Indirect jump
        - JALR rd, offset(rs1): Computed jump with link
    
    Implementation Note:
        The LSB of the computed address is always cleared (& ~1) to ensure
        2-byte alignment, even though RV32I only supports 4-byte instructions.
        This is for forward compatibility with the C extension.
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.5: Control Transfer Instructions
    """
    rs1_val = cpu.read_reg(decoded['rs1'])
    target = (rs1_val + decoded['imm']) & 0xFFFFFFFE  # Clear bit 0
    cpu.write_reg(decoded['rd'], (cpu.pc + 4) & 0xFFFFFFFF)
    cpu.pc = target
    return True


# ============================================================================
# S-Type Instructions - Stores
# ============================================================================

def exec_store(cpu, memory, decoded):
    """
    Execute S-type store instructions (SB, SH, SW)
    
    S-Type Format:
        imm[11:5] (7) | rs2 (5) | rs1 (5) | funct3 (3) | imm[4:0] (5) | opcode (7)
    Opcode: 0b0100011
    
    SB (funct3=0b000):
        Operation: memory[rs1 + imm][7:0] = rs2[7:0]
        Description: Store byte (lower 8 bits of rs2)
        Edge Cases: store 0x00, store 0xFF, store from register with upper bits set,
                    store to UART (0x10000000), store to different addresses
    
    SH (funct3=0b001):
        Operation: memory[rs1 + imm][15:0] = rs2[15:0]
        Description: Store halfword (lower 16 bits of rs2)
        Edge Cases: store 0x0000, store 0xFFFF, store from register with upper bits set,
                    misaligned address, store to different memory regions
    
    SW (funct3=0b010):
        Operation: memory[rs1 + imm][31:0] = rs2[31:0]
        Description: Store word (full 32 bits of rs2)
        Edge Cases: store 0x00000000, store 0xFFFFFFFF, store max positive/negative,
                    misaligned address, store to different memory regions
    
    Common Edge Cases:
        - Zero offset (rs1 + 0)
        - Negative offset (sign-extended immediate)
        - Large offset (up to ±2047)
        - Address wraparound
        - Store to UART region (0x10000000) - special I/O handling
        - Store then load (verify persistence)
        - rs1 = x0 (uses value 0 as base address)
        - rs2 = x0 (stores value 0)
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.6: Load and Store Instructions
    """
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
    """
    Execute B-type branch instructions (BEQ, BNE, BLT, BGE, BLTU, BGEU)
    
    B-Type Format:
        imm[12|10:5] (7) | rs2 (5) | rs1 (5) | funct3 (3) | imm[4:1|11] (5) | opcode (7)
    Opcode: 0b1100011
    
    BEQ (funct3=0b000):
        Operation: if (rs1 == rs2) pc += sign_extend(imm)
        Description: Branch if equal
        Edge Cases: equal values (branch taken), unequal (not taken), zero values,
                    max positive, max negative, forward/backward branches
    
    BNE (funct3=0b001):
        Operation: if (rs1 != rs2) pc += sign_extend(imm)
        Description: Branch if not equal
        Edge Cases: equal values (not taken), unequal (taken), zero vs non-zero,
                    small difference, max difference
    
    BLT (funct3=0b100):
        Operation: if (rs1 <s rs2) pc += sign_extend(imm)
        Description: Branch if less than (signed)
        Edge Cases: rs1 < rs2 (taken), rs1 >= rs2 (not taken), negative < positive,
                    positive < negative (not taken), max negative < 0, 0 < max positive
    
    BGE (funct3=0b101):
        Operation: if (rs1 >=s rs2) pc += sign_extend(imm)
        Description: Branch if greater than or equal (signed)
        Edge Cases: rs1 >= rs2 (taken), rs1 < rs2 (not taken), equal values (taken),
                    negative >= positive (not taken), 0 >= max negative (taken)
    
    BLTU (funct3=0b110):
        Operation: if (rs1 <u rs2) pc += sign_extend(imm)
        Description: Branch if less than (unsigned)
        Edge Cases: rs1 < rs2 (taken), rs1 >= rs2 (not taken), 0 < anything (taken),
                    0xFFFFFFFF > anything (not taken), boundary values
    
    BGEU (funct3=0b111):
        Operation: if (rs1 >=u rs2) pc += sign_extend(imm)
        Description: Branch if greater than or equal (unsigned)
        Edge Cases: rs1 >= rs2 (taken), rs1 < rs2 (not taken), equal values (taken),
                    0xFFFFFFFF >= anything (taken), anything >= 0 (taken)
    
    Common Edge Cases:
        - Zero offset (infinite loop if condition true)
        - Forward branch (positive offset)
        - Backward branch (negative offset)
        - Maximum offset (±4094 bytes, ±2047 instructions)
        - Branch to misaligned address (implementation-defined)
        - rs1 = rs2 = same register (always equal)
        - rs1 or rs2 = x0 (compare to zero)
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.5: Control Transfer Instructions
    """
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
    """
    LUI - Load Upper Immediate
    
    U-Type Format:
        imm[31:12] (20) | rd (5) | opcode (7)
    Opcode: 0b0110111
    
    Operation:
        rd = imm << 12
    
    Description:
        Load 20-bit immediate into upper 20 bits of rd, lower 12 bits set to 0.
        Used to build 32-bit constants in combination with ADDI.
    
    Edge Cases to Test:
        - Zero immediate (LUI rd, 0 → rd = 0x00000000)
        - All ones (LUI rd, 0xFFFFF → rd = 0xFFFFF000)
        - Positive values (LUI rd, 0x12345 → rd = 0x12345000)
        - Bit patterns (LUI rd, 0xAAAAA → rd = 0xAAAAA000)
        - Maximum value (LUI rd, 0xFFFFF → rd = 0xFFFFF000 = -4096 signed)
        - rd = x0 (write ignored, effectively NOP)
        - Build 32-bit constant: LUI + ADDI sequence
        - Build address: LUI for upper bits, ADDI for offset
    
    Common Usage:
        - LUI rd, %hi(symbol): Load upper 20 bits of address
        - LUI + ADDI: Build full 32-bit constant
          Example: Load 0x12345678:
            LUI rd, 0x12346  (rd = 0x12346000)
            ADDI rd, rd, 0x678 (rd = 0x12345678)
        - LUI + load/store: Access memory at absolute address
    
    Note on 32-bit Constants:
        When building constants with negative lower 12 bits (bit 11 set),
        must add 1 to upper 20 bits to compensate for sign extension:
        - Want: 0x87654321
        - Lower 12: 0x321 (positive, no adjustment)
        - LUI x10, 0x87654; ADDI x10, x10, 0x321
        - Want: 0x87654FFF
        - Lower 12: 0xFFF (negative -1, adjust upper)
        - LUI x10, 0x87655; ADDI x10, x10, -1
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.4: Integer Computational Instructions
    """
    cpu.write_reg(decoded['rd'], decoded['imm'] & 0xFFFFFFFF)
    cpu.pc += 4
    return True


def exec_auipc(cpu, decoded):
    """
    AUIPC - Add Upper Immediate to PC
    
    U-Type Format:
        imm[31:12] (20) | rd (5) | opcode (7)
    Opcode: 0b0010111
    
    Operation:
        rd = pc + (imm << 12)
    
    Description:
        Add sign-extended 20-bit immediate (shifted left 12 bits) to current PC.
        Used for PC-relative addressing, typically combined with load/store or JALR.
    
    Edge Cases to Test:
        - Zero immediate (AUIPC rd, 0 → rd = PC)
        - Positive immediate (forward address calculation)
        - Negative immediate (backward address calculation, imm[19]=1)
        - Maximum positive offset (0x7FFFF000 from PC)
        - Maximum negative offset (0x80000000 from PC)
        - PC wraparound (PC near 0xFFFFFFFF with positive offset)
        - rd = x0 (write ignored, effectively NOP)
        - Different PC values (verify PC-relative nature)
    
    Common Usage:
        - AUIPC rd, %pcrel_hi(symbol): Get PC-relative address
        - AUIPC + ADDI: Build PC-relative address
          Example: Access data at PC+offset:
            AUIPC x10, %pcrel_hi(data)  (x10 = PC + upper 20 bits)
            ADDI x10, x10, %pcrel_lo(data) (adjust with lower 12 bits)
        - AUIPC + JALR: PC-relative function call
          Example: Call function at PC+offset:
            AUIPC x1, %pcrel_hi(func)
            JALR x1, %pcrel_lo(func)(x1)
        - Position-independent code (PIC)
    
    Comparison with LUI:
        - LUI: rd = imm << 12 (absolute value)
        - AUIPC: rd = PC + (imm << 12) (PC-relative value)
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.4: Integer Computational Instructions
    """
    result = (cpu.pc + decoded['imm']) & 0xFFFFFFFF
    cpu.write_reg(decoded['rd'], result)
    cpu.pc += 4
    return True


# ============================================================================
# J-Type Instructions - Jumps
# ============================================================================

def exec_jal(cpu, decoded):
    """
    JAL - Jump and Link
    
    J-Type Format:
        imm[20|10:1|11|19:12] (20) | rd (5) | opcode (7)
    Opcode: 0b1101111
    
    Operation:
        rd = pc + 4
        pc += sign_extend(imm)
    
    Description:
        Unconditional jump to PC-relative offset, save return address (PC+4) in rd.
        Offset is sign-extended and must be a multiple of 2 bytes.
    
    Edge Cases to Test:
        - Forward jump (positive offset)
        - Backward jump (negative offset)
        - Zero offset (rd = PC+4, PC = PC+0, effectively just save PC+4)
        - Maximum offset (±1 MiB range: ±524288 instructions)
        - Minimum offset (jump to next instruction: offset=4)
        - Jump to misaligned address (offset not multiple of 4)
        - rd = x0 (discard return address, unconditional jump)
        - rd = x1 (ra register, typical function call)
        - rd = x5 (t0 register, alternate link register)
        - JAL to self (infinite loop: jal x0, 0)
        - Jump across memory boundaries
    
    Common Usage:
        - JAL x1, offset: Function call (save return in ra)
        - JAL x0, offset: Unconditional jump (discard return)
        - JAL rd, 0: Save PC+4 to rd without jumping
    
    RISC-V Spec Reference:
        RV32I Base Integer Instruction Set, Version 2.1
        Section 2.5: Control Transfer Instructions
    """
    cpu.write_reg(decoded['rd'], (cpu.pc + 4) & 0xFFFFFFFF)
    cpu.pc = (cpu.pc + decoded['imm']) & 0xFFFFFFFF
    return True
