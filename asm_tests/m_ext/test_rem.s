# TEST: rem_instruction
# DESCRIPTION: Test REM (Remainder Signed) instruction
# EXPECTED_REGS: x10=0x00000000 x11=0x00000001 x12=0x00000064 x13=0x00000000 x14=0x00000000
#
# PURPOSE:
#   Verify REM correctly computes the signed remainder of division.
#
# INSTRUCTION FORMAT:
#   REM rd, rs1, rs2
#   rd = rs1_signed % rs2_signed
#   Both rs1 and rs2 are treated as signed
#
# SPECIAL CASES (per RISC-V spec):
#   1. Division by zero: result = dividend (rs1)
#   2. Overflow (0x80000000 % -1): result = 0
#   3. Remainder has same sign as dividend
#
# TEST CASES:
#   1. Normal: 10 % 2 = 0
#   2. With remainder: 10 % 3 = 1
#   3. Division by zero: 100 % 0 = 100
#   4. Overflow case: 0x80000000 % -1 = 0
#   5. Zero dividend: 0 % 5 = 0
#
# EDGE CASES:
#   - Division by zero returns dividend
#   - Overflow returns 0
#   - Negative dividend: sign follows dividend
#   - Negative divisor: sign follows dividend
#
# EXPECTED RESULTS:
#   x10 = 0 (10 % 2)
#   x11 = 1 (10 % 3)
#   x12 = 100 (100 % 0, division by zero)
#   x13 = 0 (0x80000000 % -1, overflow)
#   x14 = 0 (0 % 5)

.section .text
.globl _start

_start:
    # Test 1: Normal (10 % 2 = 0)
    addi x5, x0, 10
    addi x6, x0, 2
    rem x10, x5, x6
    
    # Test 2: With remainder (10 % 3 = 1)
    addi x5, x0, 10
    addi x6, x0, 3
    rem x11, x5, x6
    
    # Test 3: Division by zero (100 % 0 = 100)
    addi x5, x0, 100
    addi x6, x0, 0
    rem x12, x5, x6
    
    # Test 4: Overflow (0x80000000 % -1 = 0)
    lui  x5, 0x80000      # 0x80000000 (most negative)
    addi x6, x0, -1
    rem x13, x5, x6
    
    # Test 5: Zero dividend (0 % 5 = 0)
    addi x5, x0, 0
    addi x6, x0, 5
    rem x14, x5, x6
    
    # Additional edge cases (not verified, for manual inspection)
    
    # Negative dividend, positive divisor
    # -10 % 3 = -1 (sign follows dividend)
    addi x5, x0, -10
    addi x6, x0, 3
    rem x15, x5, x6       # x15 = -1 (0xFFFFFFFF)
    
    # Positive dividend, negative divisor
    # 10 % -3 = 1 (sign follows dividend)
    addi x5, x0, 10
    addi x6, x0, -3
    rem x16, x5, x6       # x16 = 1
    
    # Negative dividend, negative divisor
    # -10 % -3 = -1 (sign follows dividend)
    addi x5, x0, -10
    addi x6, x0, -3
    rem x17, x5, x6       # x17 = -1 (0xFFFFFFFF)
    
    # 7 % 2 = 1
    addi x5, x0, 7
    addi x6, x0, 2
    rem x18, x5, x6       # x18 = 1
    
    # -7 % 2 = -1
    addi x5, x0, -7
    addi x6, x0, 2
    rem x19, x5, x6       # x19 = -1 (0xFFFFFFFF)
    
    # 7 % -2 = 1
    addi x5, x0, 7
    addi x6, x0, -2
    rem x20, x5, x6       # x20 = 1
    
    # -7 % -2 = -1
    addi x5, x0, -7
    addi x6, x0, -2
    rem x21, x5, x6       # x21 = -1 (0xFFFFFFFF)
    
    # 1000000 % 7 = 1
    lui  x5, 0xF4         # 0xF4000 = 999424
    addi x5, x5, 0x240    # + 576 = 1000000
    addi x6, x0, 7
    rem x22, x5, x6       # x22 = 1
    
    # Exit cleanly
    ebreak
