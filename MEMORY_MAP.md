# RISC-V Memory Map Standards and Conventions

## Overview

PyRV32 now follows standard RISC-V platform conventions for memory layout, making it compatible with common RISC-V development tools and practices.

## Standard RISC-V Memory Map

### Our Implementation (Target Hardware Specification)

```
0x00000000 - 0x0FFFFFFF  Reserved / Debug (256 MB)
0x10000000 - 0x10000FFF  UART0 (memory-mapped peripheral)
0x10001000 - 0x7FFFFFFF  Reserved for future peripherals
0x80000000 - 0x807FFFFF  RAM (8 MB, executable)
0x80800000 - 0xFFFFFFFF  Reserved / unmapped
```

### Key Addresses

| Address      | Purpose                    | Standard              |
|--------------|----------------------------|-----------------------|
| `0x80000000` | **Reset Vector / RAM base**| RISC-V platform spec  |
| `0x80800000` | Stack top (our config)     | End of 8MB RAM        |
| `0x10000000` | UART TX/RX register        | Common peripheral base|

**Note:** Program is loaded into RAM before reset (no bootloader). This matches the target hardware where firmware is pre-loaded.

## RISC-V Platform Conventions

### 1. DRAM Region (0x80000000)

**Why 0x80000000?**
- Standard across most RISC-V platforms
- Leaves lower memory for:
  - Debug/trace modules (0x00000000)
  - Boot ROM (0x00001000)
  - Memory-mapped peripherals (0x10000000+)
- Upper bit set helps catch NULL pointer bugs

**Used by:**
- QEMU virt machine
- SiFive HiFive Unleashed
- Kendryte K210
- Most RISC-V development boards

### 2. Peripheral Region (0x10000000)

**Standard peripheral base addresses:**

```
0x02000000  CLINT (Core Local Interruptor)
0x0C000000  PLIC (Platform-Level Interrupt Controller)
0x10000000  UART0
0x10001000  UART1 (if present)
0x10002000  GPIO
0x10003000  SPI
0x10004000  I2C
...
```

PyRV32 uses `0x10000000` for UART, matching:
- QEMU virt machine (`-M virt`)
- SiFive FU540 (HiFive Unleashed)
- Common embedded RISC-V platforms

### 3. Alternative Memory Maps

Some platforms use different conventions:

**SiFive FE310 (HiFive1):**
```
0x00000000  Debug ROM
0x00001000  Boot ROM
0x02000000  CLINT
0x20000000  Mask ROM (16 KB)
0x20400000  One-Time Programmable (OTP)
0x80000000  DTIM (Data Tightly Integrated Memory, 16 KB)
0x10013000  UART0
```

**Spike (RISC-V ISA Simulator):**
```
0x80000000  DRAM base (variable size)
```

**QEMU virt (-M virt):**
```
0x00001000  Boot ROM
0x02000000  CLINT
0x0C000000  PLIC
0x10000000  UART (16550)
0x80000000  DRAM
```

## Why These Conventions Matter

### 1. **Toolchain Compatibility**
Standard linker scripts and startup code expect:
- RAM at `0x80000000`
- Peripherals in `0x10000000` range

### 2. **Debugging Tools**
GDB and OpenOCD work better with standard memory maps:
```gdb
(gdb) x/10i 0x80000000    # Disassemble reset vector
(gdb) x/s 0x80001000      # Examine string in data section
```

### 3. **Operating System Support**
Bootloaders (U-Boot, SBI) and operating systems (Linux, FreeRTOS) expect:
- RAM at `0x80000000`
- Standard peripheral addresses

### 4. **Code Portability**
Programs written for PyRV32 can run on:
- QEMU (`qemu-system-riscv32 -M virt`)
- Real hardware (SiFive boards, etc.)
- Other simulators (Spike, Renode)

## Reset Vector and Boot Process

### Standard RISC-V Boot Sequence

1. **Hardware Reset**: PC = 0x80000000 (or platform-specific)
2. **First-stage bootloader**: Initialize DRAM, load second stage
3. **Second-stage bootloader**: Load kernel/application
4. **Application/OS**: Normal execution

### PyRV32 Simplified Boot

We skip bootloaders for simplicity:

1. **Load binary** at 0x80000000
2. **Set PC** to 0x80000000
3. **Execute** crt0.S (setup stack, clear BSS)
4. **Call** main()
5. **Halt** on ebreak

This matches bare-metal embedded development.

## Memory Layout Details

### Code Sections

```
0x80000000:  _start (crt0.S entry point)
             .text (executable code)
             .rodata (read-only data, strings)
             .data (initialized global variables)
             .bss (uninitialized globals, zeroed by crt0)
             
0x80800000:  Stack top (grows downward toward .bss)
```

### Stack Considerations

**Standard practice:**
- Stack at top of RAM
- Grows downward
- Collision with heap/BSS = stack overflow
- No guard pages (embedded systems)

**Our configuration:**
- 8 MB RAM: 0x80000000 - 0x807FFFFF
- Stack top: 0x80800000
- No heap allocator (no malloc)
- All memory between BSS end and stack is available

## Peripheral Memory-Mapped I/O

### UART at 0x10000000

```c
#define UART_TX_ADDR 0x10000000

void uart_putc(char c) {
    volatile char *uart = (volatile char *)UART_TX_ADDR;
    *uart = c;  // Write to memory-mapped register
}
```

**Why volatile?**
- Prevents compiler optimization
- Ensures every write reaches the peripheral
- Required for memory-mapped I/O

### Future Peripherals

Could add at standard addresses:
```c
#define UART0_BASE   0x10000000
#define UART1_BASE   0x10001000
#define GPIO_BASE    0x10002000
#define SPI_BASE     0x10003000
#define TIMER_BASE   0x10004000
```

## Comparison with Other Architectures

### ARM Cortex-M
```
0x00000000  Flash/Code
0x20000000  SRAM
0x40000000  Peripherals
0xE0000000  System (NVIC, SysTick)
```

### x86 (PC)
```
0x00000000  Real-mode IVT
0x00100000  Kernel load (1 MB)
0xC0000000  Kernel virtual (3 GB)
```

### RISC-V Benefits
- Cleaner separation of regions
- No legacy memory holes
- Flexible peripheral addressing
- Simple MMU configuration

## Verification

Check that programs use correct addresses:

```bash
# View disassembly
riscv64-unknown-elf-objdump -d hello.elf | head -20

# Check section addresses
riscv64-unknown-elf-readelf -S hello.elf

# View symbol table
riscv64-unknown-elf-nm hello.elf
```

Expected output:
```
80000000 T _start
80000028 T main
80800000 A __stack_top
```

## References

- **RISC-V Privileged Spec**: https://riscv.org/specifications/
- **QEMU virt machine**: `qemu-system-riscv32 -M virt,help`
- **SiFive FE310 Manual**: https://sifive.com/documentation
- **Spike source**: https://github.com/riscv-software-src/riscv-isa-sim

## Summary

✅ **PyRV32 Memory Map** (now standard-compliant):
- **0x80000000**: RAM/Reset vector (RISC-V convention)
- **0x10000000**: UART (common peripheral region)
- **0x80800000**: Stack top (8MB RAM matching target hardware)
- **Pre-loaded**: Program loaded into RAM before reset (no bootloader)

This makes PyRV32 compatible with:
- Standard RISC-V toolchains
- QEMU virt machine
- Common development practices
- Most RISC-V platforms

Your programs can now be compiled once and run on PyRV32, QEMU, or real hardware! 🚀
