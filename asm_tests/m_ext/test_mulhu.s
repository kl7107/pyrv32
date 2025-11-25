# TEST: mulhu_instruction
# DESCRIPTION: Test MULHU (Multiply High Unsigned) - upper 32 bits of unsigned × unsigned multiplication
# EXPECTED_REGS: x10=0x00000000 x11=0x00000000 x12=0xFFFFFFFE x13=0x00000001 x14=0x40000000
#
# PURPOSE:
#   Verify MULHU correctly multiplies two unsigned 32-bit integers and returns
#   the upper 32 bits of the 64-bit result.
#
# INSTRUCTION FORMAT:
#   MULHU rd, rs1, rs2
#   rd = (rs1_unsigned * rs2_unsigned)[63:32]  (upper 32 bits)
#   Both rs1 and rs2 are treated as unsigned
#
# TEST CASES:
#   1. Small unsigned × unsigned: 2 × 3 = 6, upper bits = 0
#   2. Medium values: 100 × 200 = 20000, upper bits = 0
#   3. Max unsigned × max unsigned: 0xFFFFFFFF × 0xFFFFFFFF
#      Result = 0xFFFFFFFE00000001
#      Upper 32 bits = 0xFFFFFFFE
#   4. Large × 2: 0x80000000 × 2 = 0x100000000, upper = 1
#   5. 0x80000000 × 0x80000000 = 0x4000000000000000, upper = 0x40000000
#
# EDGE CASES:
#   - Both operands treated as unsigned (no sign extension)
#   - Maximum unsigned values
#   - Powers of two
#
# EXPECTED RESULTS:
#   x10 = 0 (2 × 3, upper bits)
#   x11 = 0 (100 × 200, upper bits)
#   x12 = 0xFFFFFFFE (0xFFFFFFFF × 0xFFFFFFFF, upper bits)
#   x13 = 1 (0x80000000 × 2, upper bits)
#   x14 = 0x40000000 (0x80000000 × 0x80000000, upper bits)

.section .text
.globl _start

_start:
    # Test 1: Small unsigned × unsigned (2 × 3 = 6)
    # Upper 32 bits should be 0
    addi x5, x0, 2
    addi x6, x0, 3
    mulhu x10, x5, x6
    
    # Test 2: Medium values (100 × 200 = 20000)
    # Upper 32 bits should be 0
    addi x5, x0, 100
    addi x6, x0, 200
    mulhu x11, x5, x6
    
    # Test 3: Max unsigned × max unsigned
    # 0xFFFFFFFF × 0xFFFFFFFF = 0xFFFFFFFE00000001
    # Upper 32 bits = 0xFFFFFFFE
    addi x5, x0, -1       # 0xFFFFFFFF (max unsigned)
    addi x6, x0, -1       # 0xFFFFFFFF (max unsigned)
    mulhu x12, x5, x6
    
    # Test 4: Large × 2
    # 0x80000000 × 2 = 0x100000000
    # Upper 32 bits = 1
    lui  x5, 0x80000      # 0x80000000
    addi x6, x0, 2
    mulhu x13, x5, x6
    
    # Test 5: 0x80000000 × 0x80000000
    # 0x80000000 × 0x80000000 = 0x4000000000000000
    # Upper 32 bits = 0x40000000
    lui  x5, 0x80000      # 0x80000000
    lui  x6, 0x80000      # 0x80000000
    mulhu x14, x5, x6
    
    # Additional edge cases (not verified, for manual inspection)
    
    # 0x40000000 × 0x40000000 = 0x1000000000000000
    # Upper 32 bits = 0x10000000
    lui  x5, 0x40000      # 0x40000000
    lui  x6, 0x40000      # 0x40000000
    mulhu x15, x5, x6     # x15 = 0x10000000
    
    # 0xFFFFFFFF × 1 = 0xFFFFFFFF
    # Upper 32 bits = 0
    addi x5, x0, -1       # 0xFFFFFFFF
    addi x6, x0, 1
    mulhu x16, x5, x6     # x16 = 0
    
    # 0x10000 × 0x10000 = 0x100000000
    # Upper 32 bits = 1
    lui  x5, 0x10         # 0x10000
    lui  x6, 0x10         # 0x10000
    mulhu x17, x5, x6     # x17 = 1
    
    # 0xFFFFFFFF × 0x80000000 = 0x7FFFFFFF80000000
    # Upper 32 bits = 0x7FFFFFFF
    addi x5, x0, -1       # 0xFFFFFFFF
    lui  x6, 0x80000      # 0x80000000
    mulhu x18, x5, x6     # x18 = 0x7FFFFFFF
    
    # 0xFFFF × 0xFFFF = 0xFFFE0001
    # Upper 32 bits = 0
    lui  x5, 0x10
    addi x5, x5, -1       # 0xFFFF
    lui  x6, 0x10
    addi x6, x6, -1       # 0xFFFF
    mulhu x19, x5, x6     # x19 = 0
    
    # Exit cleanly
    ebreak
