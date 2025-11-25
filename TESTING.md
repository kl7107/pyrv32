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

**Total: 106 tests passing** ✅

### Unit Tests: 102 tests
- **CPU tests**: 12 tests (100% coverage)
- **Memory tests**: 12 tests (100% coverage)
- **Decoder utilities**: 13 tests (100% coverage)
- **MUL tests**: 13 tests (100% coverage - M extension)
- **MULH tests**: 13 tests (100% coverage - M extension)
- **MULHSU tests**: 13 tests (100% coverage - M extension)
- **MULHU tests**: 13 tests (100% coverage - M extension)
- **DIV tests**: 13 tests (100% coverage - M extension)

### Assembly Tests: 8 tests
- **hello_world**: UART output test
- **lui_instruction**: LUI instruction test
- **addi_instruction**: ADDI instruction test
- **mul_instruction**: MUL instruction test (M extension)
- **mulh_instruction**: MULH instruction test (M extension)
- **mulhsu_instruction**: MULHSU instruction test (M extension)
- **mulhu_instruction**: MULHU instruction test (M extension)
- **div_instruction**: DIV instruction test (M extension)

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

### MUL Instruction (`test_execute_mul.py` - 13 tests)

1. **Positive × Positive** - 2 × 3 = 6
2. **Positive × Negative** - 2 × -3 = -6
3. **Zero Multiplication** - 0 × 5 = 0
4. **One Multiplication** - 1 × 1 = 1
5. **Negative × Positive** - -2 × 1 = -2
6. **Negative × Negative** - -1 × -1 = 1
7. **Max Positive** - 0x7FFFFFFF × 1 = 0x7FFFFFFF
8. **Max Negative** - 0x80000000 × 1 = 0x80000000
9. **Overflow** - 0x10000 × 0x10000 lower bits = 0
10. **Large Numbers** - 0xFFFF × 0x10001 = 0xFFFFFFFF
11. **Powers of Two** - 8 × 16 = 128
12. **Write to x0** - Result discarded, x0 stays 0
13. **Same Register** - x5 × x5 = 49 (7 × 7)

**M Extension Progress**: 1/8 instructions implemented (MUL complete)

### MULH Instruction (`test_execute_mulh.py` - 13 tests)

1. **Small Positive × Positive**: 2 × 3, upper bits = 0
2. **Large Positive × Negative**: 0x7FFFFFFF × -2, upper = 0xFFFFFFFF
3. **Medium Values**: 100 × 200, upper bits = 0
4. **Max Positive Squared**: 0x7FFFFFFF × 0x7FFFFFFF, upper = 0x3FFFFFFF
5. **Max Negative Squared**: 0x80000000 × 0x80000000, upper = 0x40000000
6. **Negative × Negative**: -1 × -1, upper bits = 0
7. **Positive × Negative Medium**: 0x10000 × -0x10000, upper = 0xFFFFFFFF
8. **Large Positive Squared**: 0x40000000 × 0x40000000, upper = 0x10000000
9. **-1 × Max Positive**: -1 × 0x7FFFFFFF, upper = 0xFFFFFFFF
10. **Zero**: 0 × 5, upper bits = 0
11. **Write to x0**: Result discarded
12. **Same Register**: 0x8000 × 0x8000, upper bits = 0
13. **One**: 1 × 1, upper bits = 0

**M Extension Progress**: 2/8 instructions implemented (MUL, MULH complete)

### MULHSU Instruction (`test_execute_mulhsu.py` - 13 tests)

1. **Small Positive**: 2 × 3, upper bits = 0
2. **Medium Values**: 100 × 200, upper bits = 0
3. **Negative × Max Unsigned**: -1 × 0xFFFFFFFF, upper = 0xFFFFFFFF
4. **Max Positive × Max Unsigned**: 0x7FFFFFFF × 0xFFFFFFFF, upper = 0x7FFFFFFE
5. **Min Negative × Max Unsigned**: 0x80000000 × 0xFFFFFFFF, upper = 0x80000000
6. **Positive × Large Unsigned**: 0x40000000 × 0x80000000, upper = 0x20000000
7. **Negative Two**: -2 × 0x7FFFFFFF, upper = 0xFFFFFFFF
8. **One × Max Unsigned**: 1 × 0xFFFFFFFF, upper = 0
9. **Negative 0x10000**: -0x10000 × 0x10000, upper = 0xFFFFFFFF
10. **Zero**: 0 × 5, upper bits = 0
11. **Write to x0**: Result discarded
12. **Same Register**: -100 × 0xFFFFFF9C, upper = 0xFFFFFF9C
13. **-1 × 1**: Upper = 0xFFFFFFFF

**M Extension Progress**: 3/8 instructions implemented (MUL, MULH, MULHSU complete)

### MULHU Instruction (`test_execute_mulhu.py` - 13 tests)

**File**: `tests/test_execute_mulhu.py`

**Coverage**:
1. **Small Values**: 2 × 3, upper = 0
2. **Medium Values**: 100 × 200, upper = 0
3. **Max Unsigned Squared**: 0xFFFFFFFF × 0xFFFFFFFF, upper = 0xFFFFFFFE
4. **Large × 2**: 0x80000000 × 2, upper = 1
5. **0x80000000 Squared**: 0x80000000 × 0x80000000, upper = 0x40000000
6. **0x40000000 Squared**: 0x40000000 × 0x40000000, upper = 0x10000000
7. **Max Unsigned × 1**: 0xFFFFFFFF × 1, upper = 0
8. **0x10000 Squared**: 0x10000 × 0x10000, upper = 1
9. **Max × 0x80000000**: 0xFFFFFFFF × 0x80000000, upper = 0x7FFFFFFF
10. **0xFFFF Squared**: 0xFFFF × 0xFFFF, upper = 0
11. **Zero**: 0 × anything = 0
12. **Commutative**: Verifies a × b == b × a
13. **Power of Two**: 0x1000000 × 0x100, upper = 1

**Assembly Test**: `asm_tests/m_ext/test_mulhu.s`
- 5 verified results: x10=0, x11=0, x12=0xFFFFFFFE, x13=1, x14=0x40000000
- Additional edge cases for manual inspection

**M Extension Progress**: 4/8 instructions implemented (MUL, MULH, MULHSU, MULHU complete)

### DIV Instruction (`test_execute_div.py` - 13 tests)

**File**: `tests/test_execute_div.py`

**Coverage**:
1. **Normal Division**: 10 / 2 = 5
2. **Negative Result**: 10 / -2 = -5
3. **Division by Zero**: 100 / 0 = -1 (RISC-V spec)
4. **Overflow**: 0x80000000 / -1 = 0x80000000 (RISC-V spec)
5. **Zero Dividend**: 0 / 5 = 0
6. **Negative / Negative**: -10 / -2 = 5
7. **Truncate Positive**: 7 / 2 = 3 (not 4)
8. **Truncate Negative**: -7 / 2 = -3 (not -4, towards zero)
9. **Division by 1**: 12345 / 1 = 12345
10. **Division by -1**: 100 / -1 = -100 (non-overflow)
11. **Large Numbers**: 1000000 / 3 = 333333
12. **Max Positive**: 0x7FFFFFFF / 2 = 0x3FFFFFFF
13. **Max Negative**: 0x80000000 / 2 = 0xC0000000

**Assembly Test**: `asm_tests/m_ext/test_div.s`
- 5 verified results: x10=5, x11=-5, x12=-1, x13=0x80000000, x14=0
- Additional edge cases: truncation, sign combinations, large values

**M Extension Progress**: 5/8 instructions implemented (MUL, MULH, MULHSU, MULHU, DIV complete)

## Test Organization

```
pyrv32/
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_cpu.py            # CPU register tests
│   ├── test_memory.py         # Memory and UART tests
│   ├── test_decoder_utils.py  # Decoder utilities
│   ├── test_execute.py        # Execution tests (RV32I)
│   ├── test_execute_mul.py    # MUL instruction tests (M ext)
│   └── test_execute_mulh.py   # MULH instruction tests (M ext)
└── asm_tests/                 # Assembly tests
    ├── README.md              # Framework documentation
    ├── Makefile               # Build system
    ├── run_tests.py           # Test runner
    ├── basic/                 # RV32I tests
    │   ├── test_hello.s
    │   ├── test_lui.s
    │   └── test_addi.s
    └── m_ext/                 # M extension tests
        ├── test_mul.s
        ├── test_mulh.s
        ├── test_mulhsu.s
        ├── test_mulhu.s
        └── test_div.s
```

## Running Tests

### All Tests (Automatic)

```bash
python3 pyrv32.py
```

This runs all 102 unit tests, then the demo program.

### Individual Unit Test Modules

```bash
python3 tests/test_cpu.py
python3 tests/test_memory.py
python3 tests/test_decoder_utils.py
python3 tests/test_execute_mul.py
python3 tests/test_execute_mulh.py
python3 tests/test_execute_mulhsu.py
python3 tests/test_execute_mulhu.py
python3 tests/test_execute_div.py
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
| decoder.py (main) | 2 | 0 | 0% | ⏸️ Phase 2 |
| execute.py (RV32I) | ~40 insns | 4 | ~15% | ⏸️ Phases 2-6 |
| execute.py (M ext) | 8 insns | 39 | 37.5% | 🔄 In Progress |

**Foundation complete**: Core utilities are bulletproof ✅
**M Extension**: MUL, MULH, MULHSU implemented (3/8 instructions) 🔄

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
