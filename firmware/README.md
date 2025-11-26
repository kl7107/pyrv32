# RV32IM Firmware Examples

This directory contains bare-metal C programs for the PyRV32 emulator.

## Prerequisites

You need a RISC-V toolchain installed. Common options:

- **macOS** (Homebrew): `brew install riscv64-elf-gcc`
- **Ubuntu/Debian**: `sudo apt install gcc-riscv64-unknown-elf`
- **Build from source**: https://github.com/riscv-collab/riscv-gnu-toolchain

The toolchain prefix might vary:
- `riscv64-unknown-elf-` (most common)
- `riscv32-unknown-elf-`
- `riscv-none-elf-`

Edit `build.sh` to match your toolchain prefix.

## Building

```bash
cd firmware
./build.sh
```

This will compile `hello.c` with the minimal runtime and produce:
- `hello.elf` - ELF executable with debug info
- `hello.bin` - Raw binary (loadable by emulator)
- `hello.lst` - Disassembly listing

## Running

From the `pyrv32` directory:

```bash
./pyrv32.py --no-test firmware/hello.bin
```

Or with instruction trace:

```bash
./pyrv32.py --no-test -v firmware/hello.bin
```

## Program Structure

1. **crt0.S** - Startup code (sets up stack, clears BSS, calls main)
2. **runtime.c** - Minimal runtime library (UART I/O functions)
3. **hello.c** - Your application code
4. **link.ld** - Linker script (memory layout)

## Memory Map

- `0x80000000` - Program code and data (8MB RAM) - **RISC-V standard DRAM region**
- `0x80800000` - Stack top (grows downward)
- `0x10000000` - UART TX register (memory-mapped I/O) - **Standard peripheral region**

This follows the RISC-V convention where:
- DRAM typically starts at `0x80000000`
- Peripherals (UART, timers, etc.) are in the `0x10000000` range
- This matches QEMU virt machine and other common RISC-V platforms
- 8MB RAM matches target hardware specification

## Available Functions

```c
void uart_putc(char c);           // Write single character
void uart_puts(const char *s);    // Write string
void uart_putln(const char *s);   // Write string + newline
void uart_puthex(unsigned int v); // Write hex value
void uart_putdec(int v);          // Write decimal value
```

## Writing Your Own Programs

1. Copy `hello.c` to a new file (e.g., `myprogram.c`)
2. Edit `build.sh` to change `hello.c` to `myprogram.c`
3. Write your code using the UART functions for output
4. Build and run

## Notes

- No standard library (libc) - we provide minimal runtime only
- No dynamic memory allocation (malloc/free)
- No file I/O or OS features
- UART is the only I/O mechanism
- Use `ebreak` instruction or `return` from main() to halt
- Stack is 8MB, starting at 0x80800000 (top of RAM)
- Follows RISC-V platform conventions (QEMU virt compatible)
- Program is loaded into RAM before execution (no bootloader)

## Example Programs

### Hello World
```c
int main(void) {
    uart_putln("Hello, World!");
    return 0;
}
```

### Fibonacci
```c
int fib(int n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2);
}

int main(void) {
    uart_puts("Fibonacci(10) = ");
    uart_putdec(fib(10));
    uart_putc('\n');
    return 0;
}
```

### LED Blink (conceptual - no actual LEDs)
```c
void delay(int count) {
    for (int i = 0; i < count; i++) {
        __asm__ volatile ("nop");
    }
}

int main(void) {
    for (int i = 0; i < 5; i++) {
        uart_puts("LED ON\n");
        delay(1000);
        uart_puts("LED OFF\n");
        delay(1000);
    }
    return 0;
}
```
