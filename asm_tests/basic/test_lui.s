# TEST: lui_instruction
# DESCRIPTION: Test LUI (Load Upper Immediate) instruction
# EXPECTED_REGS: x10=0x12345000 x11=0xABCDE000 x12=0x00000000
#
# PURPOSE:
#   Verify LUI correctly loads 20-bit immediate into upper 20 bits of register.
#   Lower 12 bits should be zeros.
#
# INSTRUCTION FORMAT:
#   LUI rd, imm20
#   rd = imm20 << 12
#
# TEST CASES:
#   1. LUI with arbitrary value (0x12345)
#   2. LUI with large value (0xABCDE)
#   3. LUI with zero
#   4. LUI to x0 (should be ignored, x0 stays zero)
#
# EXPECTED RESULTS:
#   x10 = 0x12345000 (0x12345 << 12)
#   x11 = 0xABCDE000 (0xABCDE << 12)
#   x12 = 0x00000000 (0 << 12 = 0)
#   x0  = 0x00000000 (hardwired to zero, write ignored)

.section .text
.globl _start

_start:
    # Test LUI with various immediate values
    
    # LUI x10, 0x12345 -> x10 = 0x12345000
    lui x10, 0x12345
    
    # LUI x11, 0xABCDE -> x11 = 0xABCDE000
    lui x11, 0xABCDE
    
    # LUI x12, 0 -> x12 = 0x00000000
    lui x12, 0
    
    # LUI x0, 0x99999 -> x0 should stay 0 (hardwired)
    lui x0, 0x99999
    
    # Exit cleanly
    ebreak
