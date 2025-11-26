OUTPUT_ARCH( "riscv" )
ENTRY(_start)

MEMORY
{
  RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 16M
  UART (w)  : ORIGIN = 0x10000000, LENGTH = 4
}

SECTIONS
{
  . = 0x00000000;
  
  .text : {
    *(.text.start)   /* Startup code first */
    *(.text*)        /* All other code */
  } > RAM
  
  .rodata : {
    *(.rodata*)      /* Read-only data (strings, etc.) */
  } > RAM
  
  .data : {
    *(.data*)        /* Initialized data */
  } > RAM
  
  .bss : {
    __bss_start = .;
    *(.bss*)         /* Uninitialized data */
    *(COMMON)
    __bss_end = .;
  } > RAM
  
  /* Stack grows downward from end of RAM */
  . = ALIGN(16);
  __stack_top = 0x00100000;  /* 1MB */
  
  /DISCARD/ : {
    *(.comment)
    *(.note*)
    *(.eh_frame*)
  }
}
