# MCP Regression Coverage Inventory (Dec 3, 2025)

This document captures the current state of automated regression coverage for MCP + simulator features, highlighting where `run_sim_tests.py` already exercises behavior and where gaps remain. It will guide the work needed to satisfy the Immediate Requirement of having regression tests for every MCP/simulator/debugger feature.

## Legend
- **Covered** – Exercised today by `tests/`, `asm_tests/`, or `tests/c` and fails if the feature regresses.
- **Partial** – Some coverage exists (usually at the RV32System layer) but the MCP tool path is untested or critical scenarios are missing.
- **Missing** – No automated test exists; regressions would only be caught manually.

## Coverage Matrix

| Area | MCP Tools / Features | Current Status | Notes |
| --- | --- | --- | --- |
| Session lifecycle | `sim_create`, `sim_destroy`, `sim_reset`, `sim_set_cwd`, `sim_get_status`, lock cleanup | **Missing** | No automated test spins up a SessionManager via MCP; lock cleanup + cwd handling only observed manually.
| ELF loader metadata | `sim_load_elf`, `sim_get_load_info` | **Missing** | `RV32System.load_elf()` works (manual validation) but zero tests assert PT_LOAD mapping, entry point, or symbol counts.
| Execution control | `sim_step`, `sim_run`, `sim_run_until_output`, `sim_run_until_console_status_read` | **Partial** | `test_rv32_system.py` validates `step`/`run` behavior directly; helper MCP tools and the RX-watchpoint wrapper lack coverage.
| UART console/debug I/O | `sim_console_uart_*`, `sim_debug_uart_*`, newline normalization (CR→LF) | **Partial** | UART TX/RX buffering is unit-tested (`test_memory.py`, `test_rv32_system.py`), but no MCP-level test ensures console injections/logging behave identically.
| VT100 screen helpers | `sim_get_screen`, `sim_dump_screen` | **Missing** | pyte integration is untested; regressions would only appear interactively.
| Input injection | `sim_console_uart_write` aliasing + LF handling | **Partial** | Low-level API tested indirectly; verifying the consolidated MCP path requires an end-to-end test.
| Register access | `sim_get_registers`, `sim_get_register`, `sim_set_register` | **Partial** | Core register APIs have unit tests, but MCP JSON wiring and ABI name handling aren’t covered.
| Memory access | `sim_read_memory`, `sim_write_memory`, `sim_fill_memory`? (if any) | **Partial** | Memory read/write is tested via RV32System; MCP tool argument parsing and RAII validations missing.
| Breakpoints & watchpoints | `sim_add_breakpoint`, `sim_remove_breakpoint`, `sim_list_breakpoints`, `sim_add_read_watchpoint`, `sim_add_write_watchpoint`, watchpoint hit flow | **Partial/Missing** | RV32System breakpoint APIs tested; memory watchpoints + MCP tool actions lack automated coverage.
| Disassembly + symbols | `sim_disassemble`, `sim_lookup_symbol`, `sim_reverse_lookup`, `sim_get_symbol_info`, objdump cache | **Missing** | No regression tests assert symbol lookup accuracy or cached disassembly output.
| ELF/trace metadata | `sim_get_trace`, trace buffer sizing (if exposed) | **Missing** | Not currently validated.
| Syscall surfacing | Error propagation (errno, syscall tracing) | **Missing** | Existing C tests cover functionality but not MCP error reporting helpers.
| Filesystem helpers | `sim_set_cwd`, fs_root handling, stale lock cleanup | **Missing** | Behavior only verified manually when launching NetHack.

## Next Actions
1. **Create MCP integration harness** inside `tests/` that talks to a SessionManager instance directly (without TCP) so we can test tools deterministically.
2. **Add targeted tests** for the missing/partial areas above, prioritizing session lifecycle, ELF loader metadata, execution helpers, UART/VT100 paths, register/memory tools, and watchpoints.
3. **Hook the new tests into `run_sim_tests.py`** so CI enforces the coverage going forward.

### Current Focus (Dec 4, 2025)
- Implement SessionManager lifecycle coverage (lock cleanup, cwd propagation, session counters).
- Add register accessor regression tests (ABI name support, `pc` handling, zero register immutability).

### Detailed Test Plan
| Test Name (planned) | Coverage Goal |
| --- | --- |
| `test_mcp_session_lifecycle` | Validate `sim_create`, `sim_set_cwd`, `sim_get_status`, `sim_reset`, and `sim_destroy`, including fs_root lock cleanup logging. |
| `test_mcp_load_elf_metadata` | Load `firmware/hello.elf` via `sim_load_elf` and assert `sim_get_load_info` reports entry point, segments, and symbol counts. |
| `test_mcp_run_until_console_status_read` | Use `sim_run_until_console_status_read` with `echo_test.elf` to ensure the RX watchdog halts precisely at the UART status read. |
| `test_mcp_console_uart_roundtrip` | Inject mixed `\n`/`\r` input via `sim_console_uart_write`, resume execution, and verify normalized output through `sim_console_uart_read`. |
| `test_mcp_vt100_screen_dump` | Confirm `sim_get_screen`/`sim_dump_screen` return pyte output after the firmware clears the screen. |
| `test_mcp_register_access` | Exercise `sim_get_registers`, `sim_get_register`, and `sim_set_register` (ABI names + numbers) and ensure zero register protection. |
| `test_mcp_memory_access` | Use `sim_read_memory`/`sim_write_memory` to modify RAM and confirm results via subsequent reads. |
| `test_mcp_breakpoints_watchpoints` | Add/remove/list breakpoints and read/write watchpoints, then run until each triggers. |
| `test_mcp_symbol_and_disasm` | Load NetHack symbols, assert `sim_lookup_symbol`/`sim_reverse_lookup`/`sim_get_symbol_info`, and verify cached disassembly text matches objdump output. |
| `test_mcp_trace_buffer` | Enable trace buffer, execute a few instructions, and confirm `sim_get_trace` formatting. |
| `test_mcp_syscall_error_reporting` | Run a firmware binary that intentionally fails a syscall and ensure MCP response surfaces errno/message (to be implemented alongside improved reporting). |
