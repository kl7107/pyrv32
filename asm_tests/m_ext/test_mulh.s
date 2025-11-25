# TEST: mulh_instruction
# DESCRIPTION: Test MULH (Multiply High Signed) - upper 32 bits of signed multiplication
# EXPECTED_REGS: x10=0x00000000 x11=0xFFFFFFFF x12=0x00000000 x13=0x3FFFFFFF x14=0x40000000
#
# PURPOSE:
#   Verify MULH correctly multiplies two 32-bit signed integers and returns
#   the upper 32 bits of the 64-bit result.
#
# INSTRUCTION FORMAT:
#   MULH rd, rs1, rs2
#   rd = (rs1 * rs2)[63:32]  (upper 32 bits of signed product)
#
# TEST CASES:
#   1. Small positive × positive: 2 × 3 = 6, upper bits = 0
#   2. Large positive × negative: 0x7FFFFFFF × -2 = 0xFFFFFFFF00000002
#      Upper 32 bits = 0xFFFFFFFF (-1)
#   3. Small values: 100 × 200 = 20000, upper bits = 0
#   4. Max positive × max positive: 0x7FFFFFFF × 0x7FFFFFFF
#      Result = 0x3FFFFFFF00000001, upper = 0x3FFFFFFF
#   5. Max negative × max negative: 0x80000000 × 0x80000000
#      Result = 0x4000000000000000, upper = 0x40000000
#
# EDGE CASES:
#   - Multiplication requiring sign extension
#   - Results that overflow into upper 32 bits
#   - Negative × negative = positive high bits
#   - Negative × positive = negative high bits
#   - Maximum boundary values
#
# EXPECTED RESULTS:
#   x10 = 0 (2 × 3, upper bits)
#   x11 = 0xFFFFFFFF (0x7FFFFFFF × -2, upper bits = -1)
#   x12 = 0 (100 × 200, upper bits)
#   x13 = 0x3FFFFFFF (0x7FFFFFFF × 0x7FFFFFFF, upper bits)
#   x14 = 0x40000000 (0x80000000 × 0x80000000, upper bits)

.section .text
.globl _start

_start:
    # Test 1: Small positive × positive (2 × 3 = 6)
    # Upper 32 bits should be 0
    addi x5, x0, 2
    addi x6, x0, 3
    mulh x10, x5, x6
    
    # Test 2: Large positive × negative
    # 0x7FFFFFFF × -2 = 0xFFFFFFFF00000002
    # Upper 32 bits = 0xFFFFFFFF (-1)
    lui  x5, 0x80000      # 0x80000000
    addi x5, x5, -1       # 0x7FFFFFFF (max positive)
    addi x6, x0, -2       # -2
    mulh x11, x5, x6
    
    # Test 3: Small values (100 × 200 = 20000)
    # Upper 32 bits should be 0
    addi x5, x0, 100
    addi x6, x0, 200
    mulh x12, x5, x6
    
    # Test 4: Max positive × max positive
    # 0x7FFFFFFF × 0x7FFFFFFF = 0x3FFFFFFF00000001
    # Upper 32 bits = 0x3FFFFFFF
    lui  x5, 0x80000      # 0x80000000
    addi x5, x5, -1       # 0x7FFFFFFF
    lui  x6, 0x80000      # 0x80000000
    addi x6, x6, -1       # 0x7FFFFFFF
    mulh x13, x5, x6
    
    # Test 5: Max negative × max negative
    # 0x80000000 × 0x80000000 = 0x4000000000000000
    # Upper 32 bits = 0x40000000
    lui  x5, 0x80000      # 0x80000000 (min negative)
    lui  x6, 0x80000      # 0x80000000 (min negative)
    mulh x14, x5, x6
    
    # Additional edge cases (not verified, for manual inspection)
    
    # Positive × negative (medium values)
    # 0x10000 × -0x10000 = -0x100000000
    # Upper 32 bits = 0xFFFFFFFF (-1)
    lui  x5, 0x10         # 0x10000
    lui  x6, 0xFFFF0      # 0xFFFF0000
    mulh x15, x5, x6      # x15 = 0xFFFFFFFF
    
    # -1 × -1 = 1
    # Upper 32 bits = 0
    addi x5, x0, -1
    addi x6, x0, -1
    mulh x16, x5, x6      # x16 = 0
    
    # Large positive × positive
    # 0x40000000 × 0x40000000 = 0x1000000000000000
    # Upper 32 bits = 0x10000000
    lui  x5, 0x40000      # 0x40000000
    lui  x6, 0x40000      # 0x40000000
    mulh x17, x5, x6      # x17 = 0x10000000
    
    # -1 × max positive = -0x7FFFFFFF
    # Upper 32 bits = 0xFFFFFFFF
    addi x5, x0, -1
    lui  x6, 0x80000
    addi x6, x6, -1       # 0x7FFFFFFF
    mulh x18, x5, x6      # x18 = 0xFFFFFFFF
    
    # Exit cleanly
    ebreak
