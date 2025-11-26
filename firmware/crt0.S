/*
 * Minimal C Runtime Startup (crt0) for RV32IM
 * 
 * This is the entry point for C programs. It:
 * 1. Sets up the stack pointer
 * 2. Clears the BSS section
 * 3. Calls main()
 * 4. Halts with EBREAK when main returns
 */

    .section .text.start
    .global _start
    .type _start, @function

_start:
    /* Set up stack pointer (grows downward) */
    lui  sp, %hi(__stack_top)
    addi sp, sp, %lo(__stack_top)
    
    /* Clear BSS section (uninitialized data) */
    lui  t0, %hi(__bss_start)
    addi t0, t0, %lo(__bss_start)
    lui  t1, %hi(__bss_end)
    addi t1, t1, %lo(__bss_end)
    
clear_bss:
    beq  t0, t1, bss_done
    sw   zero, 0(t0)
    addi t0, t0, 4
    j    clear_bss
    
bss_done:
    /* Call main() */
    call main
    
    /* If main returns, halt with EBREAK */
    ebreak

    .size _start, . - _start
