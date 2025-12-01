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
    /* RISC-V TLS expects TP to point to the start of the TLS block */
    /* so that each symbol uses tp-relative positive offsets */
    lui  tp, %hi(__tdata_start)
    addi tp, tp, %lo(__tdata_start)
    
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
    /* Set up argc/argv/envp for main() */
    /* If a0 (argc) is already non-zero, assume argc/argv were pre-set by loader */
    /* This allows the simulator to pass custom arguments */
    bnez a0, use_preset_args
    
    /* Default: argc = 1 (program name only) */
    li   a0, 1
    
    /* argv = pointer to argv array */
    /* We'll use a static string "nethack" as argv[0] */
    lui  a1, %hi(argv_array)
    addi a1, a1, %lo(argv_array)
    
use_preset_args:
    /* envp = pointer to environment array */
    /* If a2 is already set (non-zero), keep it; otherwise use static env_array */
    bnez a2, envp_already_set
    
    /* Use static env_array (empty environment) */
    lui  a2, %hi(env_array)
    addi a2, a2, %lo(env_array)
    
envp_already_set:
    /* Set global environ variable */
    lui  t0, %hi(environ)
    addi t0, t0, %lo(environ)
    sw   a2, 0(t0)
    
    /* Call main(argc, argv, envp) - envp is optional but supported */
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

env_array:
    .word 0            /* envp[0] = NULL (empty environment) */

    /* Global environ variable (required by getenv()) */
    .section .bss
    .align 2
    .global environ
environ:
    .word 0
