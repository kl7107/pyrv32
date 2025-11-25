# Example RV32I Assembly Programs

## Hello World to UART

This is the simplest possible program to output "Hello\n" to UART.
No loops - just linear code for maximum clarity.

### Assembly Code

```assembly
# UART is at address 0x10000000
# Strategy: Load UART address once, then repeatedly load chars and store

    # Load UART address into x10
    lui  x10, 0x10000        # x10 = 0x10000000

    # Output 'H' (ASCII 72)
    addi x11, x0, 72         # x11 = 72
    sb   x11, 0(x10)         # UART = x11

    # Output 'e' (ASCII 101)
    addi x11, x0, 101        # x11 = 101
    sb   x11, 0(x10)         # UART = x11

    # Output 'l' (ASCII 108)
    addi x11, x0, 108        # x11 = 108
    sb   x11, 0(x10)         # UART = x11

    # Output 'l' (ASCII 108)
    addi x11, x0, 108        # x11 = 108
    sb   x11, 0(x10)         # UART = x11

    # Output 'o' (ASCII 111)
    addi x11, x0, 111        # x11 = 111
    sb   x11, 0(x10)         # UART = x11

    # Output newline (ASCII 10)
    addi x11, x0, 10         # x11 = 10
    sb   x11, 0(x10)         # UART = x11
```

### Machine Code

```
0x10000537  # lui  x10, 0x10000
0x04800593  # addi x11, x0, 72
0x00B50023  # sb   x11, 0(x10)
0x06500593  # addi x11, x0, 101
0x00B50023  # sb   x11, 0(x10)
0x06C00593  # addi x11, x0, 108
0x00B50023  # sb   x11, 0(x10)
0x06C00593  # addi x11, x0, 108
0x00B50023  # sb   x11, 0(x10)
0x06F00593  # addi x11, x0, 111
0x00B50023  # sb   x11, 0(x10)
0x00A00593  # addi x11, x0, 10
0x00B50023  # sb   x11, 0(x10)
```

### Explanation

**Why this approach?**
- **No loops**: Makes the code extremely simple to understand
- **Inefficient but clear**: Each character requires 2 instructions (ADDI + SB)
- **Uses only 3 instruction types**: LUI, ADDI, SB

**Instruction breakdown:**
1. `LUI x10, 0x10000` - Load upper 20 bits → x10 = 0x10000000 (UART address)
2. For each character:
   - `ADDI x11, x0, <char>` - Load character into x11
   - `SB x11, 0(x10)` - Store byte to UART (address in x10 + offset 0)

**Why ADDI from x0?**
- x0 is hardwired to 0
- `ADDI x11, x0, 72` effectively means x11 = 0 + 72 = 72
- Simple way to load small immediates into registers

## Memory Map

```
0x80000000 - 0x8FFFFFFF : Program memory (standard RISC-V boot address)
0x10000000              : UART TX (write-only, memory-mapped I/O)
```

## Running

The demo is built into pyrv32.py:
```bash
python3 pyrv32.py
```

Output shows:
- All unit tests passing
- Instruction-by-instruction execution trace
- UART output: "Hello\n"
- Final register state
