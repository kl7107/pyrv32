# TEST: hello_world
# DESCRIPTION: Basic test that outputs "Hello World" to UART
# EXPECTED_OUTPUT: Hello World
#
# PURPOSE:
#   Demonstrates basic UART I/O by writing characters to memory-mapped UART.
#   Tests: LUI, ADDI (via LI pseudo-instruction), SB (store byte)
#
# UART MEMORY MAP:
#   0x10000000 - UART TX (write-only)
#   Writing a byte to this address transmits it via UART
#
# TECHNIQUE:
#   1. Load UART base address once into x5 using LUI
#   2. For each character: load ASCII value into x6, store to UART
#   3. Exit with ebreak instruction
#
# NOTE: LI is a pseudo-instruction that expands to ADDI rd, x0, imm

.section .text
.globl _start

_start:
    # Load UART base address into x5
    lui x5, 0x10000          # x5 = 0x10000000 (UART base)
    
    # Output 'H'
    li x6, 72                # 'H' = 72
    sb x6, 0(x5)
    
    # Output 'e'
    li x6, 101               # 'e' = 101
    sb x6, 0(x5)
    
    # Output 'l'
    li x6, 108               # 'l' = 108
    sb x6, 0(x5)
    
    # Output 'l'
    sb x6, 0(x5)
    
    # Output 'o'
    li x6, 111               # 'o' = 111
    sb x6, 0(x5)
    
    # Output ' '
    li x6, 32                # ' ' = 32
    sb x6, 0(x5)
    
    # Output 'W'
    li x6, 87                # 'W' = 87
    sb x6, 0(x5)
    
    # Output 'o'
    li x6, 111               # 'o' = 111
    sb x6, 0(x5)
    
    # Output 'r'
    li x6, 114               # 'r' = 114
    sb x6, 0(x5)
    
    # Output 'l'
    li x6, 108               # 'l' = 108
    sb x6, 0(x5)
    
    # Output 'd'
    li x6, 100               # 'd' = 100
    sb x6, 0(x5)
    
    # Exit cleanly
    ebreak
