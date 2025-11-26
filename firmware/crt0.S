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
    
    /* Set up thread pointer for TLS (Thread Local Storage) */
    /* tp points to the start of TLS data area */
    /* For RISC-V, tp should point to end of tdata section */
    lui  tp, %hi(__tdata_end)
    addi tp, tp, %lo(__tdata_end)
    
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
    /* Set up argc/argv for main() */
    /* argc = 1 (program name only) */
    li   a0, 1
    
    /* argv = pointer to argv array */
    /* We'll use a static string "nethack" as argv[0] */
    lui  a1, %hi(argv_array)
    addi a1, a1, %lo(argv_array)
    
    /* Call main(argc, argv) */
    call main
    
    /* If main returns, halt with EBREAK */
    ebreak

    .size _start, . - _start

    /* Static data for argv */
    .section .rodata
    .align 2
prog_name:
    .string "nethack"
    
    .section .data
    .align 2
argv_array:
    .word prog_name    /* argv[0] = "nethack" */
    .word 0            /* argv[1] = NULL */
