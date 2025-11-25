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
├── TESTING.md          # Testing documentation and status
├── EXAMPLES.md         # Assembly code examples
├── docs/               # Detailed documentation
│   ├── UART.md         # UART module reference
│   └── README.md       # Documentation index
├── pyrv32.py           # Main entry point
├── cpu.py              # CPU register state (x0-x31, PC, CSRs)
├── memory.py           # Byte-addressable memory with UART
├── uart.py             # UART transmitter module
├── decoder.py          # Instruction decoder
├── execute.py          # Instruction execution engine
├── tests/              # Unit tests (76 tests)
│   ├── __init__.py
│   ├── test_cpu.py         # CPU tests (9)
│   ├── test_memory.py      # Memory/UART tests (15)
│   ├── test_decoder_utils.py # Decoder utilities (9)
│   ├── test_execute.py     # Execution tests - RV32I (4)
│   ├── test_execute_mul.py # MUL instruction tests - M ext (13)
│   ├── test_execute_mulh.py # MULH instruction tests - M ext (13)
│   └── test_execute_mulhsu.py # MULHSU instruction tests - M ext (13)
└── asm_tests/          # Assembly test framework (6 tests)
    ├── README.md       # Framework documentation
    ├── Makefile        # Build using riscv64-unknown-elf toolchain
    ├── run_tests.py    # Test runner with auto-verification
    ├── basic/          # RV32I test collection
    │   ├── test_hello.s
    │   ├── test_lui.s
    │   └── test_addi.s
    └── m_ext/          # M extension tests
        ├── test_mul.s
        ├── test_mulh.s
        └── test_mulhsu.s
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
- See `docs/UART.md` for UART details

### Instructions (execute.py)

#### RV32I Base Instructions (~95% complete)
- **LUI** - Load Upper Immediate
- **AUIPC** - Add Upper Immediate to PC
- **ADDI** - Add Immediate
- **SLTI/SLTIU** - Set Less Than Immediate
- **XORI/ORI/ANDI** - Bitwise operations with immediate
- **SLLI/SRLI/SRAI** - Shift operations
- **SB/SH/SW** - Store Byte/Halfword/Word
- **LB/LH/LW/LBU/LHU** - Load operations
- **ADD/SUB** - Add/Subtract
- **AND/OR/XOR** - Bitwise operations
- **SLL/SRL/SRA** - Shift operations
- **SLT/SLTU** - Set Less Than
- **JAL/JALR** - Jump and Link
- **BEQ/BNE/BLT/BGE/BLTU/BGEU** - Branch operations

#### M Extension (Multiply/Divide) - In Progress
- **MUL** ✅ - Multiply (lower 32 bits)
- **MULH** ✅ - Multiply High (signed × signed, upper 32 bits)
- **MULHSU** ✅ - Multiply High (signed × unsigned, upper 32 bits)
- **MULHU** - Multiply High (unsigned × unsigned, upper 32 bits)
- **DIV** - Divide (signed)
- **DIVU** - Divide Unsigned
- **REM** - Remainder (signed)
- **REMU** - Remainder Unsigned

**M Extension Progress**: 3/8 instructions (37.5%)

## Quick Start

Run the simulator (includes all tests and demo):
```bash
python3 pyrv32.py
```

This will:
1. Run all 76 unit tests (CPU, memory, decoder utilities, execution, MUL, MULH, MULHSU)
2. Run demo program that outputs "Hello\n" to UART
3. Display results and register state

**All 80 tests passing** ✅ (76 unit + 6 assembly)

### Assembly Tests

```bash
cd asm_tests
python3 run_tests.py         # Run all assembly tests
python3 run_tests.py -v      # Verbose mode
```

See `asm_tests/README.md` for details.

## Design Principles

1. **Clarity over performance**: Code should be easy to read and understand
2. **Explicit over implicit**: Make operations obvious
3. **Simple data structures**: Use lists and basic types
4. **Minimal abstraction**: Don't over-engineer
5. **Modular organization**: Separate files by logical function
6. **Extensive unit testing**: 
   - Test every function and behavior
   - Tests run automatically at program start
   - Verbose logging to temp files for analysis
   - Fail-fast: exit immediately on first test failure
   - Makes debugging easier and prevents regressions
