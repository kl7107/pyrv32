# Assembly Test Framework

This directory contains assembly-language test programs for the pyrv32 simulator.

## Philosophy

**Tests are self-documenting.** Each `.s` file contains complete documentation about what it tests, how it works, and what results to expect. The best way to learn the framework is to read the test files themselves.

**Key principles:**
- **Independent Toolchain**: Assembled using `riscv64-unknown-elf-as` for independent verification
- **Automated Verification**: Tests verify their own output against metadata
- **Examples as Documentation**: Read the test files to learn the framework
- **Black Box Testing**: Tests actual binary execution, not Python internals

## Quick Start

```bash
# Build all tests
make

# Run all tests
python3 run_tests.py

# Run specific test (by name, no .s extension)
python3 run_tests.py test_hello

# Run specific category
python3 run_tests.py basic

# Verbose mode (show all output)
python3 run_tests.py -v

# Debug mode (instruction-by-instruction trace)
python3 run_tests.py -d test_hello
```

## Learning by Example

The best way to understand the test framework is to read the test files themselves.
Each test is self-documenting with comprehensive comments:

- **`basic/test_hello.s`** - UART I/O example
- **`basic/test_lui.s`** - Instruction testing example  
- **`basic/test_addi.s`** - Sign extension and immediate testing

Open any `.s` file to see:
- Test metadata format
- Inline documentation
- Instruction usage examples
- Expected results

## Test Metadata Format

Tests use special comment syntax for auto-verification:

```assembly
# TEST: test_name
# DESCRIPTION: What this test verifies
# EXPECTED_OUTPUT: Hello World
# EXPECTED_REGS: x10=0x12345678 x11=0xABCDEF00
```

**Required:**
- `TEST:` - Test identifier
- `DESCRIPTION:` - What is being tested

**Optional:**
- `EXPECTED_OUTPUT:` - Expected UART text
- `EXPECTED_REGS:` - Register values at exit (format: `xN=0xVALUE`)

## Framework Components

### Build System (`Makefile`)

Uses the official RISC-V toolchain:
- `riscv64-unknown-elf-as -march=rv32i -mabi=ilp32` for assembly
- `riscv64-unknown-elf-objcopy` to produce `.bin` binaries from `.s` sources
- Independent verification (not using Python assembler)

Commands:
```bash
make                           # Build all tests
make basic/test_lui.bin        # Build specific test
make clean                     # Clean all binaries
```

### Test Runner (`run_tests.py`)

Automates the test cycle:
1. Discovers `.s` files in subdirectories
2. Parses metadata from comments
3. Loads corresponding `.bin` file
4. Executes in simulator
5. Detects `ebreak` exit instruction (opcode `0x00100073`)
6. Verifies UART output and register values
7. Reports pass/fail results

The test runner automatically checks:
- UART output matches `EXPECTED_OUTPUT`
- Register values match `EXPECTED_REGS`
- No manual verification needed

## Writing a New Test

1. Look at existing tests in `basic/` for examples
2. Create a `.s` file following the pattern:
   - Metadata comments at the top
   - Comprehensive inline documentation
   - Test code
   - Exit with `ebreak` instruction
3. Run `make` to build
4. Run `python3 run_tests.py` to verify

**The existing test files are your template.** They show the style, format, and documentation approach.

## Essential Details

### Exit Convention

All tests **must** end with `ebreak` instruction:
```assembly
    # Test code here
    
    # Exit cleanly
    ebreak
```

The simulator stops when it encounters `ebreak` (opcode `0x00100073`). This is the standard RISC-V mechanism for debugger breakpoints and test termination.

### UART I/O

To output text, write bytes to UART TX at `0x10000000`:
```assembly
lui  x5, 0x10000      # UART base address
li   x6, 'H'          # Load character
sb   x6, 0(x5)        # Output 'H'
```

See `basic/test_hello.s` for a complete UART example.

### Register Conventions

Following RISC-V ABI (for reference, not required):
- `x0` (zero) - Always 0
- `x1` (ra) - Return address
- `x2` (sp) - Stack pointer
- `x5-x7` (t0-t2) - Temporaries
- `x10-x17` (a0-a7) - Arguments/return values

Tests are free to use any registers since they're standalone programs.

### Test Constraints

- Tests must be position-independent or designed to run at `0x80000000`
- Don't assume any initial register state except `x0 = 0`
- Don't rely on unimplemented instructions
- Keep tests focused - one test per instruction or small instruction group

## Debugging

Use `-d` flag for instruction-by-instruction trace:
```bash
python3 run_tests.py -d test_name
```

Shows:
- PC values
- Decoded instructions
- Register changes
- Memory accesses

Useful for understanding why a test fails or how instructions execute.

## Benefits

- **Black Box Testing**: Tests actual binary execution, not Python internals
- **Regression Prevention**: Catch bugs when modifying simulator code
- **Independent Verification**: Official RISC-V toolchain validates correctness
- **Self-Documenting**: Test files explain themselves
- **Easy to Write**: Just assembly + metadata comments
- **Automatic Verification**: No manual checking needed

## Current Status

- ✅ 3 assembly tests passing
- ✅ Tests verify: LUI, ADDI, SB, UART output
- ✅ Framework complete and operational

Add more tests as instructions are implemented!
