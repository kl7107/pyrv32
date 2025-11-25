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

# Run all tests (from pyrv32/ directory)
../pyrv32.py --asm-test

# Run with verbose output
../pyrv32.py --asm-test -v

# Run specific test directly
python3 run_tests.py test_hello
python3 run_tests.py -v         # Verbose mode
python3 run_tests.py -d         # Debug mode (instruction trace)
```

## Learning by Example

The best way to understand the test framework is to read the test files themselves.
Each test is self-documenting with comprehensive comments:

- **`basic/test_hello.s`** - UART I/O example
- **`basic/test_lui.s`** - Instruction testing example  
- **`basic/test_addi.s`** - Sign extension and immediate testing
- **`m_ext/test_mul.s`** - M extension example

Open any `.s` file to see the test metadata format and inline documentation.

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

## Writing a New Test

1. Look at existing tests in `basic/` or `m_ext/` for examples
2. Create a `.s` file following the pattern:
   - Metadata comments at the top
   - Test code
   - Exit with `ebreak` instruction
3. Run `make` to build
4. Run `../pyrv32.py --asm-test` to verify

**The existing test files are your template.**

## Essential Details

### Exit Convention

All tests **must** end with `ebreak`:
```assembly
    # Test code here
    
    ebreak          # Exit cleanly
```

### UART I/O

To output text, write bytes to UART TX at `0x10000000`:
```assembly
lui  x5, 0x10000      # UART base address
li   x6, 'H'          # Load character
sb   x6, 0(x5)        # Output 'H'
```

See `basic/test_hello.s` for a complete example.

### Debugging

Use `-d` flag for instruction-by-instruction trace:
```bash
python3 run_tests.py -d test_name
```

Shows PC values, decoded instructions, register changes, and memory accesses.
