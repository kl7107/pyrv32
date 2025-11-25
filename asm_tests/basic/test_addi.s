# TEST: addi_instruction
# DESCRIPTION: Test ADDI (Add Immediate) instruction
# EXPECTED_REGS: x10=0x0000002A x11=0xFFFFFFFF x12=0x00000000 x13=0x000007FF
#
# PURPOSE:
#   Verify ADDI correctly adds sign-extended 12-bit immediate to register.
#   Tests positive, negative, zero, and boundary immediates.
#
# INSTRUCTION FORMAT:
#   ADDI rd, rs1, imm12
#   rd = rs1 + sign_extend(imm12)
#
# TEST CASES:
#   1. ADDI with positive immediate (42)
#   2. ADDI with -1 (tests sign extension: 0xFFF → 0xFFFFFFFF)
#   3. ADDI with zero immediate
#   4. ADDI with max positive 12-bit immediate (2047 = 0x7FF)
#   5. ADDI with register source (not x0)
#   6. ADDI with negative immediate (-20)
#
# EXPECTED RESULTS:
#   x10 = 42 (0 + 42)
#   x11 = 0xFFFFFFFF (0 + sign_extend(0xFFF))
#   x12 = 0 (0 + 0)
#   x13 = 2047 (0 + 2047)
#   x14 = 52 (42 + 10) - computed but not checked
#   x15 = 22 (42 - 20) - computed but not checked

.section .text
.globl _start

_start:
    # Test ADDI with various immediate values
    
    # ADDI x10, x0, 42 -> x10 = 42
    addi x10, x0, 42
    
    # ADDI x11, x0, -1 -> x11 = 0xFFFFFFFF
    addi x11, x0, -1
    
    # ADDI x12, x0, 0 -> x12 = 0
    addi x12, x0, 0
    
    # ADDI x13, x0, 2047 -> x13 = 0x7FF (max positive 12-bit immediate)
    addi x13, x0, 2047
    
    # ADDI with register source
    # x14 = x10 + 10 = 42 + 10 = 52
    addi x14, x10, 10
    
    # ADDI with negative immediate
    # x15 = x10 + (-20) = 42 - 20 = 22
    addi x15, x10, -20
    
    # Verify x14 and x15
    # x14 should be 52 = 0x34
    # x15 should be 22 = 0x16
    
    # Exit cleanly
    ebreak
