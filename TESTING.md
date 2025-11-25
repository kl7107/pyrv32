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

**Total: 152 tests passing** ✅

### Unit Tests: 141 tests
- **CPU tests**: 12 (register operations, CSRs, reset)
- **Memory tests**: 12 (load/store, UART, alignment)
- **Decoder utilities**: 13 (sign extension, immediate decoding)
- **M Extension**: 104 (13 per instruction × 8 instructions)

### Assembly Tests: 11 tests
- **RV32I Base**: hello_world, lui_instruction, addi_instruction
- **M Extension**: mul, mulh, mulhsu, mulhu, div, divu, rem, remu

**See test files in `tests/` and `asm_tests/` for details. Instruction edge cases and RISC-V spec compliance documented in `execute.py` docstrings.**

## Test Organization

```
pyrv32/
├── tests/                      # Unit tests (141 tests)
│   ├── test_cpu.py            # CPU register tests (12)
│   ├── test_memory.py         # Memory and UART tests (12)
│   ├── test_decoder_utils.py  # Decoder utilities (13)
│   └── test_execute_*.py      # M extension tests (104 = 13×8)
└── asm_tests/                 # Assembly tests (11 tests)
    ├── run_tests.py           # Test runner
    ├── basic/                 # RV32I base tests
    │   ├── test_hello.s
    │   ├── test_lui.s
    │   └── test_addi.s
    └── m_ext/                 # M extension tests
        ├── test_mul.s
        ├── test_mulh.s
        ├── test_mulhsu.s
        ├── test_mulhu.s
        ├── test_div.s
        ├── test_divu.s
        ├── test_rem.s
        └── test_remu.s
```

## Running Tests

### All Tests (Automatic)

```bash
python3 pyrv32.py
```

Runs all 141 unit tests, then the demo program.

### Assembly Tests

```bash
cd asm_tests
python3 run_tests.py           # Run all tests
python3 run_tests.py -v         # Verbose mode
python3 run_tests.py test_mul   # Run specific test
```

See `asm_tests/README.md` for assembly test framework details.

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

