# TEST: divu_instruction
# DESCRIPTION: Test DIVU (Divide Unsigned) instruction
# EXPECTED_REGS: x10=0x00000005 x11=0x40000000 x12=0xffffffff x13=0x00000000 x14=0x00000001
#
# PURPOSE:
#   Verify DIVU correctly performs unsigned division of two 32-bit integers.
#
# INSTRUCTION FORMAT:
#   DIVU rd, rs1, rs2
#   rd = rs1_unsigned / rs2_unsigned
#   Both rs1 and rs2 are treated as unsigned
#
# SPECIAL CASES (per RISC-V spec):
#   1. Division by zero: result = 0xFFFFFFFF (all 1s)
#
# TEST CASES:
#   1. Normal division: 10 / 2 = 5
#   2. Large unsigned: 0x80000000 / 2 = 0x40000000
#   3. Division by zero: 100 / 0 = 0xFFFFFFFF
#   4. Divide zero: 0 / 5 = 0
#   5. Max unsigned / max: 0xFFFFFFFF / 0xFFFFFFFF = 1
#
# EDGE CASES:
#   - Division by zero returns 0xFFFFFFFF (all 1s)
#   - Large values treated as unsigned (no sign bit)
#   - 0x80000000 is just a large positive number
#
# EXPECTED RESULTS:
#   x10 = 5 (10 / 2)
#   x11 = 0x40000000 (0x80000000 / 2)
#   x12 = 0xFFFFFFFF (100 / 0, division by zero)
#   x13 = 0 (0 / 5)
#   x14 = 1 (0xFFFFFFFF / 0xFFFFFFFF)

.section .text
.globl _start

_start:
    # Test 1: Normal division (10 / 2 = 5)
    addi x5, x0, 10
    addi x6, x0, 2
    divu x10, x5, x6
    
    # Test 2: Large unsigned (0x80000000 / 2 = 0x40000000)
    # 0x80000000 is 2147483648 unsigned (negative in signed)
    lui  x5, 0x80000      # 0x80000000
    addi x6, x0, 2
    divu x11, x5, x6
    
    # Test 3: Division by zero (100 / 0 = 0xFFFFFFFF)
    addi x5, x0, 100
    addi x6, x0, 0
    divu x12, x5, x6
    
    # Test 4: Divide zero (0 / 5 = 0)
    addi x5, x0, 0
    addi x6, x0, 5
    divu x13, x5, x6
    
    # Test 5: Max / max (0xFFFFFFFF / 0xFFFFFFFF = 1)
    addi x5, x0, -1       # 0xFFFFFFFF
    addi x6, x0, -1       # 0xFFFFFFFF
    divu x14, x5, x6
    
    # Additional edge cases (not verified, for manual inspection)
    
    # Max unsigned / 2
    # 0xFFFFFFFF / 2 = 0x7FFFFFFF (2147483647)
    addi x5, x0, -1       # 0xFFFFFFFF
    addi x6, x0, 2
    divu x15, x5, x6      # x15 = 0x7FFFFFFF
    
    # Large / small
    # 0xFFFFFFFF / 3 = 0x55555555
    addi x5, x0, -1       # 0xFFFFFFFF
    addi x6, x0, 3
    divu x16, x5, x6      # x16 = 0x55555555
    
    # Division by 1
    # 12345 / 1 = 12345
    lui  x5, 0x3
    addi x5, x5, 0x39     # 0x3039 = 12345
    addi x6, x0, 1
    divu x17, x5, x6      # x17 = 12345
    
    # Truncation
    # 7 / 2 = 3
    addi x5, x0, 7
    addi x6, x0, 2
    divu x18, x5, x6      # x18 = 3
    
    # 1000000 / 3 = 333333
    lui  x5, 0xF4         # 0xF4000 = 999424
    addi x5, x5, 0x240    # + 576 = 1000000
    addi x6, x0, 3
    divu x19, x5, x6      # x19 = 333333
    
    # Very large / very large
    # 0xFFFFFFFE / 0xFFFFFFFF = 0
    addi x5, x0, -2       # 0xFFFFFFFE
    addi x6, x0, -1       # 0xFFFFFFFF
    divu x20, x5, x6      # x20 = 0
    
    # Exit cleanly
    ebreak
