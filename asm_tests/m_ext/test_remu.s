# TEST: remu_instruction
# DESCRIPTION: Test REMU (Remainder Unsigned) instruction
# EXPECTED_REGS: x10=0x00000000 x11=0x00000001 x12=0x00000064 x13=0x00000000 x14=0x00000001
#
# PURPOSE:
#   Verify REMU correctly computes the unsigned remainder of division.
#
# INSTRUCTION FORMAT:
#   REMU rd, rs1, rs2
#   rd = rs1_unsigned % rs2_unsigned
#   Both rs1 and rs2 are treated as unsigned
#
# SPECIAL CASES (per RISC-V spec):
#   1. Division by zero: result = dividend (rs1)
#
# TEST CASES:
#   1. Normal: 10 % 2 = 0
#   2. With remainder: 10 % 3 = 1
#   3. Division by zero: 100 % 0 = 100
#   4. Large unsigned: 0 % 5 = 0
#   5. Max % 2: 0xFFFFFFFF % 2 = 1
#
# EDGE CASES:
#   - Division by zero returns dividend
#   - All values treated as unsigned (no negative remainders)
#   - 0x80000000 is just a large positive number
#
# EXPECTED RESULTS:
#   x10 = 0 (10 % 2)
#   x11 = 1 (10 % 3)
#   x12 = 100 (100 % 0, division by zero)
#   x13 = 0 (0 % 5)
#   x14 = 1 (0xFFFFFFFF % 2)

.section .text
.globl _start

_start:
    # Test 1: Normal (10 % 2 = 0)
    addi x5, x0, 10
    addi x6, x0, 2
    remu x10, x5, x6
    
    # Test 2: With remainder (10 % 3 = 1)
    addi x5, x0, 10
    addi x6, x0, 3
    remu x11, x5, x6
    
    # Test 3: Division by zero (100 % 0 = 100)
    addi x5, x0, 100
    addi x6, x0, 0
    remu x12, x5, x6
    
    # Test 4: Zero dividend (0 % 5 = 0)
    addi x5, x0, 0
    addi x6, x0, 5
    remu x13, x5, x6
    
    # Test 5: Max % 2 (0xFFFFFFFF % 2 = 1)
    addi x5, x0, -1       # 0xFFFFFFFF
    addi x6, x0, 2
    remu x14, x5, x6
    
    # Additional edge cases (not verified, for manual inspection)
    
    # Max % 3
    # 0xFFFFFFFF % 3 = 0
    addi x5, x0, -1       # 0xFFFFFFFF
    addi x6, x0, 3
    remu x15, x5, x6      # x15 = 0
    
    # Large % small
    # 0x80000000 % 3 = 2
    lui  x5, 0x80000      # 0x80000000
    addi x6, x0, 3
    remu x16, x5, x6      # x16 = 2
    
    # 7 % 2 = 1
    addi x5, x0, 7
    addi x6, x0, 2
    remu x17, x5, x6      # x17 = 1
    
    # 1000000 % 7 = 1
    lui  x5, 0xF4         # 0xF4000 = 999424
    addi x5, x5, 0x240    # + 576 = 1000000
    addi x6, x0, 7
    remu x18, x5, x6      # x18 = 1
    
    # Max % max
    # 0xFFFFFFFF % 0xFFFFFFFF = 0
    addi x5, x0, -1       # 0xFFFFFFFF
    addi x6, x0, -1       # 0xFFFFFFFF
    remu x19, x5, x6      # x19 = 0
    
    # (Max - 1) % max
    # 0xFFFFFFFE % 0xFFFFFFFF = 0xFFFFFFFE
    addi x5, x0, -2       # 0xFFFFFFFE
    addi x6, x0, -1       # 0xFFFFFFFF
    remu x20, x5, x6      # x20 = 0xFFFFFFFE
    
    # Power of two
    # 0x12345678 % 0x100 = 0x78
    lui  x5, 0x12345
    addi x5, x5, 0x678
    addi x6, x0, 0x100
    remu x21, x5, x6      # x21 = 0x78
    
    # Exit cleanly
    ebreak
