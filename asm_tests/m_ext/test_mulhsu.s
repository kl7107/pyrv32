# TEST: mulhsu_instruction
# DESCRIPTION: Test MULHSU (Multiply High Signed-Unsigned) - upper 32 bits of signed × unsigned multiplication
# EXPECTED_REGS: x10=0x00000000 x11=0x00000000 x12=0xFFFFFFFF x13=0x7FFFFFFE x14=0x80000000
#
# PURPOSE:
#   Verify MULHSU correctly multiplies a signed 32-bit integer with an unsigned
#   32-bit integer and returns the upper 32 bits of the 64-bit result.
#
# INSTRUCTION FORMAT:
#   MULHSU rd, rs1, rs2
#   rd = (rs1_signed * rs2_unsigned)[63:32]  (upper 32 bits)
#   rs1 is treated as signed, rs2 is treated as unsigned
#
# TEST CASES:
#   1. Positive signed × unsigned: 2 × 3 = 6, upper bits = 0
#   2. Small positive × unsigned: 100 × 200 = 20000, upper bits = 0
#   3. Negative signed × unsigned: -1 × 0xFFFFFFFF
#      Result = -0xFFFFFFFF = 0xFFFFFFFF00000001
#      Upper 32 bits = 0xFFFFFFFF (-1)
#   4. Max positive signed × max unsigned: 0x7FFFFFFF × 0xFFFFFFFF
#      Result = 0x7FFFFFFE80000001
#      Upper 32 bits = 0x7FFFFFFE
#   5. Min negative signed × max unsigned: 0x80000000 × 0xFFFFFFFF
#      Result = 0x8000000080000000
#      Upper 32 bits = 0x80000000
#
# EDGE CASES:
#   - Negative signed value with large unsigned value
#   - Positive signed value with large unsigned value
#   - Sign extension of rs1 vs zero extension of rs2
#
# EXPECTED RESULTS:
#   x10 = 0 (2 × 3, upper bits)
#   x11 = 0 (100 × 200, upper bits)
#   x12 = 0xFFFFFFFF (-1 × 0xFFFFFFFF, upper bits)
#   x13 = 0x7FFFFFFE (0x7FFFFFFF × 0xFFFFFFFF, upper bits)
#   x14 = 0x80000000 (0x80000000 × 0xFFFFFFFF, upper bits)

.section .text
.globl _start

_start:
    # Test 1: Positive signed × unsigned (2 × 3 = 6)
    # Upper 32 bits should be 0
    addi x5, x0, 2
    addi x6, x0, 3
    mulhsu x10, x5, x6
    
    # Test 2: Small positive × unsigned (100 × 200 = 20000)
    # Upper 32 bits should be 0
    addi x5, x0, 100
    addi x6, x0, 200
    mulhsu x11, x5, x6
    
    # Test 3: Negative signed × max unsigned
    # -1 × 0xFFFFFFFF = -0xFFFFFFFF = 0xFFFFFFFF00000001
    # Upper 32 bits = 0xFFFFFFFF
    addi x5, x0, -1       # -1 (signed)
    addi x6, x0, -1       # 0xFFFFFFFF (unsigned)
    mulhsu x12, x5, x6
    
    # Test 4: Max positive signed × max unsigned
    # 0x7FFFFFFF × 0xFFFFFFFF = 0x7FFFFFFE80000001
    # Upper 32 bits = 0x7FFFFFFE
    lui  x5, 0x80000      # 0x80000000
    addi x5, x5, -1       # 0x7FFFFFFF (max positive signed)
    addi x6, x0, -1       # 0xFFFFFFFF (max unsigned)
    mulhsu x13, x5, x6
    
    # Test 5: Min negative signed × max unsigned
    # 0x80000000 (as signed -0x80000000) × 0xFFFFFFFF
    # Result = 0x8000000080000000
    # Upper 32 bits = 0x80000000
    lui  x5, 0x80000      # 0x80000000 (min negative signed)
    addi x6, x0, -1       # 0xFFFFFFFF (max unsigned)
    mulhsu x14, x5, x6
    
    # Additional edge cases (not verified, for manual inspection)
    
    # Positive signed × large unsigned
    # 0x40000000 × 0x80000000 = 0x2000000000000000
    # Upper 32 bits = 0x20000000
    lui  x5, 0x40000      # 0x40000000
    lui  x6, 0x80000      # 0x80000000 (large unsigned)
    mulhsu x15, x5, x6
    
    # -2 × 0x7FFFFFFF
    # Result = -0xFFFFFFFE = 0xFFFFFFFF00000002
    # Upper 32 bits = 0xFFFFFFFF
    addi x5, x0, -2       # -2 (signed)
    lui  x6, 0x80000
    addi x6, x6, -1       # 0x7FFFFFFF (unsigned)
    mulhsu x16, x5, x6
    
    # 1 × max unsigned
    # 1 × 0xFFFFFFFF = 0xFFFFFFFF
    # Upper 32 bits = 0
    addi x5, x0, 1
    addi x6, x0, -1       # 0xFFFFFFFF
    mulhsu x17, x5, x6
    
    # -0x10000 × 0x10000
    # Result = -0x100000000
    # Upper 32 bits = 0xFFFFFFFF
    lui  x5, 0xFFFF0      # 0xFFFF0000 = -0x10000 (signed)
    lui  x6, 0x10         # 0x10000 (unsigned)
    mulhsu x18, x5, x6
    
    # Exit cleanly
    ebreak
