# PyRV32 Test Implementation Status

## RV32I Base ISA

### R-Type (Register-Register ALU)
- ADD - ✅
- SUB - ✅
- SLL - ✅
- SLT - ✅
- SLTU - ✅
- XOR - ✅
- SRL - ✅
- SRA - ✅
- OR - ✅
- AND - ✅

### I-Type (Immediate ALU)
- ADDI - ✅
- SLTI - ✅
- SLTIU - ✅
- XORI - ✅
- ORI - ✅
- ANDI - ✅
- SLLI - ✅
- SRLI - ✅
- SRAI - ✅

### I-Type (Loads)
- LB - ✅
- LH - ✅
- LW - ✅
- LBU - ✅
- LHU - ✅

### I-Type (Jumps)
- JALR - ✅

### I-Type (System/Fence)
- FENCE - ✅
- ECALL - ✅
- EBREAK - ✅

### S-Type (Stores)
- SB - ✅
- SH - ✅
- SW - ✅

### B-Type (Branches)
- BEQ - ✅
- BNE - ✅
- BLT - ✅
- BGE - ✅
- BLTU - ✅
- BGEU - ✅

### U-Type (Upper Immediate)
- LUI - ✅
- AUIPC - ✅

### J-Type (Jumps)
- JAL - ✅

---

## RV32M Extension

### Multiply
- MUL - ✅
- MULH - ✅
- MULHSU - ✅
- MULHU - ✅

### Divide
- DIV - ✅
- DIVU - ✅
- REM - ✅
- REMU - ✅
