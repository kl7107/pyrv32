# pyrv32 Testing

pyrv32 has two complementary testing approaches:
1. **Unit tests** - Test individual Python functions and modules  
2. **Assembly tests** - Test complete programs using real RISC-V binaries

## Running Tests

### Default (All Tests)

```bash
./pyrv32.py                    # Run all tests (unit + assembly)
```

### Specific Test Suites

```bash
./pyrv32.py --asm-test         # Run assembly tests only
./pyrv32.py --asm-test -v      # Assembly tests with verbose output
```

### Skip Tests

```bash
./pyrv32.py --no-test program.bin   # Run binary without tests
```

## Test Organization

```
pyrv32/
├── tests/              # Unit tests
│   └── test_*.py      # CPU, memory, decoder, execute tests
└── asm_tests/         # Assembly tests
    ├── run_tests.py   # Test runner
    ├── basic/         # RV32I base instruction tests
    └── m_ext/         # M extension tests
```

## Test Features

### Fail-Fast Behavior
Tests exit immediately on the first failure:
- Clear error message showing expected vs actual values
- Log file path for detailed analysis

### Verbose Logging
Unit test output is logged to temporary files:
- File location: `/tmp/pyrv32_test_*.log`
- Contains complete test execution trace
- Persists after program exit for analysis

