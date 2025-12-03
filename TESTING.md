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

# Unified Test & Coverage Workflow

PyRV32 now has a single entry point, `run_sim_tests.py`, that exercises every
simulator/MCP regression suite under coverage. This replaces the legacy
`pyrv32.py --asm-test` helpers and ensures nothing is skipped.

## Prerequisites

- `python3-coverage` (or `coverage`) must be on `PATH`. Install via apt with
    `sudo apt install python3-coverage`.
- The standard RISC-V cross toolchain must be available so the C runtime tests
    can build their binaries automatically.
- Run `make` inside `asm_tests/` if you want the optional MUL/DIV tests; missing
    binaries are skipped with a warning.

## Run Everything

```bash
python3 run_sim_tests.py --fail-under 70
```

The runner performs the following steps:

1. Erases any previous coverage artifacts.
2. Runs `tests/` (Python unit tests) under coverage in parallel mode.
3. Runs `asm_tests/run_tests.py` to execute the assembly instruction suite.
4. Builds and executes the C runtime/syscall tests via `run_c_tests.py`.
5. Combines coverage data and enforces the configured threshold (default 70%).

Coverage is enabled by default. Use `--no-coverage` if you only need a red/green
result (not recommended for CI).

## Selective Execution & Flags

- `--list` – enumerate all registered steps.
- `--only <step>` – run a subset in declaration order (may be repeated).
- `--skip <step>` – run everything except the named step (may be repeated).
- `--fail-under N` – override the coverage gate for a single run (also respects
    `PYRV32_COVERAGE_FAIL_UNDER`).

Every step executes from the repository root and inherits your current
environment, so filesystem changes made by previous steps carry over.

## Coverage Details

- `.coveragerc` scopes measurement to the simulator core modules
    (`cpu`, `decoder`, `execute`, `memory`, `pyrv32_system`, `syscalls`). Add more
    modules once their dedicated tests exist.
- Coverage data (`.coverage.*`) is written to the repo root while the run is in
    progress. The runner combines and removes them automatically; delete the base
    `.coverage` file manually if a run aborts.
- `python3 run_sim_tests.py --fail-under 70` currently reports ~72% coverage. If
    the report falls below the threshold the script exits non-zero and prints the
    diff so you can investigate immediately.
- You may see `CoverageWarning: Module ... was never imported` during the
    assembly or C steps. These warnings occur because the helper scripts do not
    import the simulator core and can be ignored unless a module truly vanishes
    from all steps.

## Artifacts & Logs

- All simulator invocations inherit the VT100 console logging, so
    `/tmp/console_tx.log`, `/tmp/console_rx.log`, and `/tmp/screen_dump.log` keep
    the UART output for debugging.
- Coverage reports print directly to stdout for easy CI archiving.

Always run the unified script before touching NetHack or MCP automation work so
regressions surface immediately.

