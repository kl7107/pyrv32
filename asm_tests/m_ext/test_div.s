# TEST: div_instruction
# DESCRIPTION: Test DIV (Divide Signed) instruction
# EXPECTED_REGS: x10=0x00000005 x11=0xfffffffb x12=0xffffffff x13=0x80000000 x14=0x00000000
#
# PURPOSE:
#   Verify DIV correctly performs signed division of two 32-bit integers.
#
# INSTRUCTION FORMAT:
#   DIV rd, rs1, rs2
#   rd = rs1_signed / rs2_signed
#   Both rs1 and rs2 are treated as signed
#
# SPECIAL CASES (per RISC-V spec):
#   1. Division by zero: result = -1 (0xFFFFFFFF)
#   2. Overflow: 0x80000000 / -1 = 0x80000000 (not -0x80000000)
#
# TEST CASES:
#   1. Normal division: 10 / 2 = 5
#   2. Negative result: 10 / -2 = -5
#   3. Division by zero: 100 / 0 = -1
#   4. Overflow case: 0x80000000 / -1 = 0x80000000
#   5. Divide zero: 0 / 5 = 0
#
# EDGE CASES:
#   - Division by zero returns -1
#   - Overflow returns 0x80000000
#   - Negative / positive = negative
#   - Positive / negative = negative
#   - Truncation towards zero
#
# EXPECTED RESULTS:
#   x10 = 5 (10 / 2)
#   x11 = -5 (10 / -2)
#   x12 = -1 (100 / 0, division by zero)
#   x13 = 0x80000000 (overflow case)
#   x14 = 0 (0 / 5)

.section .text
.globl _start

_start:
    # Test 1: Normal division (10 / 2 = 5)
    addi x5, x0, 10
    addi x6, x0, 2
    div x10, x5, x6
    
    # Test 2: Negative result (10 / -2 = -5)
    addi x5, x0, 10
    addi x6, x0, -2
    div x11, x5, x6
    
    # Test 3: Division by zero (100 / 0 = -1)
    addi x5, x0, 100
    addi x6, x0, 0
    div x12, x5, x6
    
    # Test 4: Overflow (0x80000000 / -1 = 0x80000000)
    lui  x5, 0x80000      # 0x80000000 (most negative)
    addi x6, x0, -1
    div x13, x5, x6
    
    # Test 5: Divide zero (0 / 5 = 0)
    addi x5, x0, 0
    addi x6, x0, 5
    div x14, x5, x6
    
    # Additional edge cases (not verified, for manual inspection)
    
    # Negative / negative = positive
    # -10 / -2 = 5
    addi x5, x0, -10
    addi x6, x0, -2
    div x15, x5, x6       # x15 = 5
    
    # Large positive / small positive
    # 1000000 / 3 = 333333
    lui  x5, 0xF4         # 0xF4000 = 999424
    addi x5, x5, 0x240    # + 576 = 1000000
    addi x6, x0, 3
    div x16, x5, x6       # x16 = 333333 (0x51615)
    
    # Truncation towards zero
    # 7 / 2 = 3 (not 4)
    addi x5, x0, 7
    addi x6, x0, 2
    div x17, x5, x6       # x17 = 3
    
    # Negative truncation towards zero
    # -7 / 2 = -3 (not -4)
    addi x5, x0, -7
    addi x6, x0, 2
    div x18, x5, x6       # x18 = -3
    
    # 7 / -2 = -3
    addi x5, x0, 7
    addi x6, x0, -2
    div x19, x5, x6       # x19 = -3
    
    # -7 / -2 = 3
    addi x5, x0, -7
    addi x6, x0, -2
    div x20, x5, x6       # x20 = 3
    
    # Division by 1
    # 12345 / 1 = 12345
    lui  x5, 0x3
    addi x5, x5, 0x39     # 0x3039 = 12345
    addi x6, x0, 1
    div x21, x5, x6       # x21 = 12345
    
    # Division by -1 (normal case, not overflow)
    # 100 / -1 = -100
    addi x5, x0, 100
    addi x6, x0, -1
    div x22, x5, x6       # x22 = -100
    
    # Exit cleanly
    ebreak
