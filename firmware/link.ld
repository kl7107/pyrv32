OUTPUT_ARCH( "riscv" )
ENTRY(_start)

MEMORY
{
  RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 8M
  UART (w)  : ORIGIN = 0x10000000, LENGTH = 4K
}

SECTIONS
{
  . = 0x80000000;
  
  .text : {
    *(.text.start)   /* Startup code first */
    *(.text*)        /* All other code */
  } > RAM
  
  .rodata : {
    *(.rodata*)      /* Read-only data (strings, etc.) */
  } > RAM
  
  /* Thread Local Storage - for rand/srand and other TLS variables */
  /* Must come BEFORE .data to avoid overlap issues */
  .tdata : {
    __tdata_start = .;
    *(.tdata .tdata.*)
    . = ALIGN(8);     /* Align to 8 bytes for proper tp setup */
    __tdata_end = .;
  } > RAM
  
  .tbss (NOLOAD) : {
    __tbss_start = .;
    *(.tbss .tbss.*)
    . = ALIGN(8);
    __tbss_end = .;
  } > RAM  
  
  __tls_size = __tbss_end - __tdata_start;
  
  /* 
   * ld.bfd does not advance the location counter for NOLOAD sections like .tbss.
   * However, we need memory allocated for .tbss because we use it for the initial
   * TLS storage at runtime (accessed via tp register with negative offsets).
   * Without this spacer, .data would overlap with .tbss at the same VMA, causing
   * runtime corruption. This is the standard solution used by picolibc.
   */
  .tls_spacer : {
    . = . + __tls_size;
  } > RAM
  
  .data : {
    *(.data*)        /* Initialized data */
  } > RAM
  
  .bss : {
    __bss_start = .;
    *(.sbss*)        /* Small BSS (for small data model) */
    *(.bss*)         /* Uninitialized data */
    *(COMMON)
    . = ALIGN(16);
    __bss_end = .;
  } > RAM
  
  /* Heap starts after BSS (for picolibc) */
  . = ALIGN(16);
  _end = .;            /* Heap start (legacy) */
  __heap_start = .;    /* Picolibc heap start */
  
  /* Reserve 1MB for stack at top of RAM */
  __heap_end = 0x80800000 - 0x100000;  /* RAM end - 1MB stack */
  
  /* Stack grows downward from end of RAM */
  __stack_top = 0x80800000;  /* RAM base + 8MB */
  
  /DISCARD/ : {
    *(.comment)
    *(.note*)
    *(.eh_frame*)
  }
}
