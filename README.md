# pyrv32 - Simple RV32IMC Instruction Simulator

A simple, easy-to-understand RISC-V RV32IMC instruction simulator in Python.
Not cycle-accurate. Designed for simulating user-space programs.

## RV32IMC Registers

### General Purpose Registers (x0-x31)
- **x0**: Always hardwired to zero (reads always return 0, writes are ignored)
- **x1-x31**: 32-bit general purpose registers
- Common ABI names:
  - x0 = zero
  - x1 = ra (return address)
  - x2 = sp (stack pointer)
  - x3 = gp (global pointer)
  - x4 = tp (thread pointer)
  - x5-x7 = t0-t2 (temporaries)
  - x8 = s0/fp (saved register / frame pointer)
  - x9 = s1 (saved register)
  - x10-x11 = a0-a1 (function arguments / return values)
  - x12-x17 = a2-a7 (function arguments)
  - x18-x27 = s2-s11 (saved registers)
  - x28-x31 = t3-t6 (temporaries)

### Program Counter (PC)
- 32-bit register pointing to the current instruction
- Increments by 4 for normal instructions (2 for compressed)
- Modified by branches, jumps, and exceptions

### CSRs (Control and Status Registers)
For a simple user-space simulator, minimal CSR set:
- **mstatus** (0x300): Machine status register
- **mtvec** (0x305): Machine trap-vector base-address
- **mepc** (0x341): Machine exception program counter
- **mcause** (0x342): Machine trap cause
- **mie** (0x304): Machine interrupt-enable
- **mip** (0x344): Machine interrupt-pending

## Python Representation

### General Purpose Registers
- Simple list: `regs = [0] * 32`
- Direct indexing with register numbers (0-31)
- x0 hardwired to zero via special handling in read/write methods

### Program Counter
- Plain integer: `pc = 0`

### CSRs
- Dictionary mapping address to value: `csrs = {0x300: 0, ...}`

## Project Structure

```
pyrv32/
├── README.md           # This file
├── pyrv32.py           # Main entry point
├── cpu.py              # CPU register state (x0-x31, PC, CSRs)
├── memory.py           # Byte-addressable memory with UART
├── uart.py             # UART transmitter module
├── decoder.py          # Instruction decoder
├── execute.py          # Instruction execution engine
├── tests/              # Unit tests
│   └── test_*.py       # CPU, memory, decoder, execute tests
└── asm_tests/          # Assembly test framework
    ├── run_tests.py    # Test runner with auto-verification
    ├── Makefile        # Build using riscv64-unknown-elf toolchain
    ├── basic/          # RV32I base instruction tests
    └── m_ext/          # M extension tests
```

## Features Implemented

### CPU (cpu.py)
- 32 general purpose registers (x0-x31)
- Program counter (PC)
- Control and Status Registers (CSRs)
- x0 hardwired to zero

### Memory (memory.py)
- Sparse byte-addressable memory (dict-based)
- Little-endian word/halfword access
- Memory-mapped UART TX at **0x10000000**
- UART module (uart.py) writes raw binary output

### Decoder & Executor (decoder.py, execute.py)
- Instruction decoder extracts opcode, funct3, funct7, registers, immediates
- Executor implements RV32I base ISA (~95% complete)
- Full M extension support (multiply/divide) - 8/8 instructions (100%) ✅
- See source files for detailed instruction listings and implementation notes

## Quick Start

Run the simulator (includes all tests):
```bash
python3 pyrv32.py
```

This will:
1. Run all unit tests (CPU, memory, decoder, execute)
2. Run all assembly tests (basic + M extension)
3. Display results

Run binary file:
```bash
python3 pyrv32.py program.bin          # Run with all tests first
python3 pyrv32.py --no-test prog.bin   # Run without tests
python3 pyrv32.py -v program.bin       # Run with instruction trace
```

Run only assembly tests:
```bash
python3 pyrv32.py --asm-test           # Assembly tests only
python3 pyrv32.py --asm-test -v        # Verbose mode
```

## Design Principles

1. **Clarity over performance**: Code should be easy to read and understand
2. **Explicit over implicit**: Make operations obvious
3. **Simple data structures**: Use lists and basic types
4. **Minimal abstraction**: Don't over-engineer
5. **Modular organization**: Separate files by logical function
6. **Comprehensive testing**: Unit tests + assembly tests
