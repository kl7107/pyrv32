# PyRV32 Implementation Status

## RV32I Base ISA - ✅ COMPLETE (40 instructions)

### R-Type (Register-Register ALU)
- ✅ ADD - Add
- ✅ SUB - Subtract  
- ✅ SLL - Shift Left Logical
- ✅ SLT - Set Less Than (signed)
- ✅ SLTU - Set Less Than Unsigned
- ✅ XOR - Exclusive OR
- ✅ SRL - Shift Right Logical
- ✅ SRA - Shift Right Arithmetic
- ✅ OR - Bitwise OR
- ✅ AND - Bitwise AND

### I-Type (Immediate ALU)
- ✅ ADDI - Add Immediate
- ✅ SLTI - Set Less Than Immediate (signed)
- ✅ SLTIU - Set Less Than Immediate Unsigned
- ✅ XORI - XOR Immediate
- ✅ ORI - OR Immediate
- ✅ ANDI - AND Immediate
- ✅ SLLI - Shift Left Logical Immediate
- ✅ SRLI - Shift Right Logical Immediate
- ✅ SRAI - Shift Right Arithmetic Immediate

### I-Type (Loads)
- ✅ LB - Load Byte (sign-extended)
- ✅ LH - Load Halfword (sign-extended)
- ✅ LW - Load Word
- ✅ LBU - Load Byte Unsigned
- ✅ LHU - Load Halfword Unsigned

### I-Type (Jumps)
- ✅ JALR - Jump and Link Register

### I-Type (System/Fence)
- ✅ FENCE - Memory ordering (no-op in single-core simulator)
- ✅ ECALL - Environment Call (raises ECallException)
- ✅ EBREAK - Environment Break (raises EBreakException for normal program termination)

### S-Type (Stores)
- ✅ SB - Store Byte
- ✅ SH - Store Halfword
- ✅ SW - Store Word

### B-Type (Branches)
- ✅ BEQ - Branch if Equal
- ✅ BNE - Branch if Not Equal
- ✅ BLT - Branch if Less Than (signed)
- ✅ BGE - Branch if Greater or Equal (signed)
- ✅ BLTU - Branch if Less Than Unsigned
- ✅ BGEU - Branch if Greater or Equal Unsigned

### U-Type (Upper Immediate)
- ✅ LUI - Load Upper Immediate
- ✅ AUIPC - Add Upper Immediate to PC

### J-Type (Jumps)
- ✅ JAL - Jump and Link

**Total RV32I: 40/40 implemented** ✅ COMPLETE

---

## RV32M Extension - ✅ COMPLETE (8 instructions)

### Multiply Instructions
- ✅ MUL - Multiply (lower 32 bits)
- ✅ MULH - Multiply High (signed × signed)
- ✅ MULHSU - Multiply High (signed × unsigned)
- ✅ MULHU - Multiply High (unsigned × unsigned)

### Divide Instructions
- ✅ DIV - Divide (signed)
- ✅ DIVU - Divide Unsigned
- ✅ REM - Remainder (signed)
- ✅ REMU - Remainder Unsigned

**Total RV32M: 8/8 implemented**

---

## RV32C Extension - ❌ NOT IMPLEMENTED

The compressed instruction extension (16-bit instructions) is not implemented.
Attempting to execute a compressed instruction will raise `NotImplementedError`.

**Instruction Formats:** CR, CI, CSS, CIW, CL, CS, CA, CB, CJ (9 formats)

---

## Exception Handling

### Custom Exceptions

**EBreakException** - Raised when EBREAK instruction is executed
- Used for normal program termination
- Includes PC address for debugging
- Caught by top-level execution loop

**ECallException** - Raised when ECALL instruction is executed  
- Represents environment/system calls
- Currently reports as unimplemented and exits
- Includes PC address for debugging

### NotImplementedError

Standard Python exception raised for:
- Unknown instruction opcodes in decoder
- Unrecognized instruction formats
- Future extensions not yet implemented (e.g., RV32C)

Example:
```
NotImplementedError: Unknown/unimplemented instruction: opcode=0b1111111, 
funct3=0b111, funct7=0b1111111, raw=0xffffffff
```

### Implementation Notes

- **FENCE**: Implemented as no-op (just increments PC) - sufficient for single-core without DMA or out-of-order execution
- **EBREAK**: Raises `EBreakException` for clean program termination
- **ECALL**: Raises `ECallException` - not implemented for user-space simulation

---

## Testing Status

- **Unit Tests:** 141 tests - ✅ ALL PASSING
- **Assembly Tests:** 11 tests - ✅ ALL PASSING
- **Total:** 152 tests

### Coverage
- CPU register operations
- Memory operations (byte, halfword, word)
- All implemented ALU operations
- All multiply/divide operations
- Branch/jump instructions
- UART I/O device

---

## Architecture

### Decoder (`decoder.py`)
- Single source of truth for instruction decoding
- Returns complete decoded information including:
  - Instruction name (e.g., "ADDI", "MUL")
  - Format type ('R', 'I', 'S', 'B', 'U', 'J')
  - All fields (opcode, rd, rs1, rs2, funct3, funct7, imm)
- Ordered following RISC-V standard: R → I → S → B → U → J

### Execute (`execute.py`)
- Dispatches based on decoded format and opcode
- Function definitions match dispatch order for readability
- No redundant decoding - uses decoder output directly
- Clean format-based dispatch structure

---

## Documentation

Reference files in `docs/refs/`:
- `rv_i.txt` - Base integer instructions from riscv-opcodes
- `rv_m.txt` - M extension instructions from riscv-opcodes
- `rv_c.txt` - Compressed instructions reference
- `rv32_i.txt` - RV32-specific integer instructions
- `rv32_c.txt` - RV32-specific compressed instructions
- `rv32_instruction_formats.txt` - Custom format reference with diagrams

---

## Summary

**Total Instructions Implemented: 48/48 RV32IM** ✅ COMPLETE
- RV32I: 40/40 (100%)
- RV32M: 8/8 (100%)
- RV32C: 0/? (Not implemented)

All RV32I and RV32M instructions are fully implemented and tested.
