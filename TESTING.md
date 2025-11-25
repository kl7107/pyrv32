# pyrv32 Testing

pyrv32 has two complementary testing approaches:
1. **Unit tests** - Test individual Python functions and modules
2. **Assembly tests** - Test complete programs using real RISC-V binaries

## Test Philosophy

All unit tests run automatically at program start. This ensures:
- No regressions when making changes
- Immediate feedback on any issues
- Tests are always executed, never forgotten

## Test Features

### Fail-Fast Behavior
Tests exit immediately on the first failure, making debugging easier:
- Clear error message showing expected vs actual values
- Context about what was being tested
- Log file path for detailed analysis

### Verbose Logging
All test output is logged to temporary files:
- File location: `/tmp/pyrv32_test_*.log`
- Contains complete test execution trace
- Persists after program exit for analysis
- File output only (keeps console clean)

## Current Test Status

**Total: 40 tests passing** ✅

### Unit Tests: 37 tests
- **CPU tests**: 9 tests (100% coverage)
- **Memory tests**: 15 tests (100% coverage)
- **Decoder utilities**: 9 tests (100% coverage)
- **Execute tests**: 4 tests (~15% coverage)

### Assembly Tests: 3 tests
- **hello_world**: UART output test
- **lui_instruction**: LUI instruction test
- **addi_instruction**: ADDI instruction test

## Unit Test Coverage

### CPU Module (`test_cpu.py` - 9 tests)

1. **x0 Hardwired to Zero (Read)** - Reading x0 always returns 0
2. **x0 Write Ignored** - Writes to x0 are silently ignored
3. **Normal Register Read/Write** - Registers x1-x31 work correctly
4. **32-bit Value Masking** - Values properly masked to 32 bits
5. **CSR Read/Write** - CSR operations work correctly
6. **CSR 32-bit Masking** - CSRs properly masked
7. **Unimplemented CSR Returns 0** - Non-existent CSRs return 0
8. **Reset Functionality** - Reset clears all state
9. **All Registers Accessible** - All 32 registers work

### Memory Module (`test_memory.py` - 15 tests)

1. **Read Unwritten Memory** - Returns 0
2. **Write and Read Byte** - Byte operations
3. **Write and Read Halfword** - 16-bit little-endian operations
4. **Write and Read Word** - 32-bit little-endian operations
5. **UART TX Writes** - UART output works
6. **UART Read Returns 0** - No RX implemented
7. **Load Program** - Bulk loading works
8. **Memory Sparseness** - Dict-based memory
9. **Clear UART** - Buffer clearing works
10. **UART Raw Binary** - Writes actual bytes (not escape sequences)
11. **UART Invalid UTF-8** - Handles decode errors gracefully
12. **Address Wraparound** - 32-bit boundary handling
13. **Misaligned Halfword** - Implementation allows it
14. **Misaligned Word** - Implementation allows it
15. **Reset** - Clears memory and UART

### Decoder Utilities (`test_decoder_utils.py` - 9 tests)

1. **Sign Extend Positive 32-bit** - Positive values unchanged
2. **Sign Extend Negative 32-bit** - Bit 31 set preserved
3. **Sign Extend 64-bit Positive** - Masked to 32 bits
4. **Sign Extend 64-bit Negative** - Masked correctly
5. **Sign Extend Zero** - Zero handling
6. **Sign Extend All Ones** - -1 handling
7. **Sign Extend Boundaries** - Around bit 31
8. **Sign Extend Idempotency** - Applying twice safe
9. **Sign Extend Decoder Values** - I/B/J-type immediates

**Critical Bug Found**: `sign_extend_32()` was returning 64-bit values, now fixed.

### Execute Module (`test_execute.py` - 4 tests)

1. **LUI Execute** - Load upper immediate
2. **ADDI Execute** - Add immediate
3. **SB to UART** - Store byte to memory-mapped UART
4. **Full Sequence** - Multi-instruction integration

## Test Organization

```
pyrv32/
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_cpu.py            # CPU register tests
│   ├── test_memory.py         # Memory and UART tests
│   ├── test_decoder_utils.py  # Decoder utilities
│   └── test_execute.py        # Execution tests
└── asm_tests/                 # Assembly tests
    ├── README.md              # Framework documentation
    ├── Makefile               # Build system
    ├── run_tests.py           # Test runner
    └── basic/                 # Test collection
        ├── test_hello.s
        ├── test_lui.s
        └── test_addi.s
```

## Running Tests

### All Tests (Automatic)

```bash
python3 pyrv32.py
```

This runs all 37 unit tests, then the demo program.

### Individual Unit Test Modules

```bash
python3 tests/test_cpu.py
python3 tests/test_memory.py
python3 tests/test_decoder_utils.py
python3 tests/test_execute.py
```

### Assembly Tests

```bash
cd asm_tests
python3 run_tests.py           # Run all
python3 run_tests.py test_hello  # Run specific test
python3 run_tests.py -v         # Verbose mode
python3 run_tests.py -d test_lui # Debug mode
```

See `asm_tests/README.md` for complete assembly testing documentation.

## Test Results

All tests pass with verbose logging:
```
Running CPU tests...
Running Memory tests...
Running Execution tests...
Running Decoder Utility tests...
All tests PASSED ✓
```

On failure:
- Exits with code 1
- Detailed error message
- Log file path for analysis

## Coverage Summary

| Module | Functions | Tests | Coverage | Status |
|--------|-----------|-------|----------|--------|
| cpu.py | 7 | 9 | 100% | ✅ Complete |
| memory.py | 11 | 15 | 100% | ✅ Complete |
| uart.py | 5 | (via memory) | 100% | ✅ Complete |
| decoder.py (utils) | 1 | 9 | 100% | ✅ Complete |
| decoder.py (main) | 2 | 0 | 0% | ⚠️ Phase 2 |
| execute.py | ~40 insns | 4 | ~15% | ⚠️ Phases 2-6 |

**Foundation complete**: Core utilities are bulletproof ✅

## Future Testing Plans

Additional test phases will cover:
- Decoder instruction format testing (6 formats)
- Remaining instruction execution (~36 instructions)
- Edge cases and error conditions
- Performance benchmarks

Estimated: ~140-160 additional tests planned

## See Also

- `docs/ASSEMBLY_TESTS.md` - Assembly test framework guide
- `docs/UART.md` - UART module documentation
- `EXAMPLES.md` - Code examples
