# MCP Regression Coverage Inventory (Dec 3, 2025)

This document captures the current state of automated regression coverage for MCP + simulator features, highlighting where `run_sim_tests.py` already exercises behavior and where gaps remain. It will guide the work needed to satisfy the Immediate Requirement of having regression tests for every MCP/simulator/debugger feature.

## Legend
- **Covered** – Exercised today by `tests/`, `asm_tests/`, or `tests/c` and fails if the feature regresses.
- **Partial** – Some coverage exists (usually at the RV32System layer) but the MCP tool path is untested or critical scenarios are missing.
- **Missing** – No automated test exists; regressions would only be caught manually.

## Coverage Matrix

| Area | MCP Tools / Features | Current Status | Notes |
| --- | --- | --- | --- |
| Session lifecycle | `sim_create`, `sim_destroy`, `sim_reset`, `sim_set_cwd`, `sim_get_status`, lock cleanup | **Partial** | `tests/test_mcp_regression.py::test_session_manager_lifecycle_and_lock_cleanup` now boots a SessionManager, exercises cwd/fs_root, and verifies stale lock cleanup; remaining MCP JSON wiring still untested.
| ELF loader metadata | `sim_load_elf`, `sim_get_load_info` | **Missing** | `RV32System.load_elf()` works (manual validation) but zero tests assert PT_LOAD mapping, entry point, or symbol counts.
| Execution control | `sim_step`, `sim_run`, `sim_run_until_output`, `sim_run_until_console_status_read` | **Partial** | `test_rv32_system.py` still covers `step`/`run`; the new `test_run_until_console_status_read_triggers_watchpoint` program confirms the RX-status helper halts on the MMIO byte, but `sim_run_until_output` remains untested.
| UART console/debug I/O | `sim_console_uart_*`, `sim_debug_uart_*`, newline normalization (CR→LF) | **Partial** | UART TX/RX buffering is unit-tested (`test_memory.py`, `test_rv32_system.py`), but no MCP-level test ensures console injections/logging behave identically.
| VT100 screen helpers | `sim_get_screen`, `sim_dump_screen` | **Partial** | `test_vt100_screen_helpers_capture_tx_output` validates the underlying VT100 screen/dump outputs, but the MCP JSON tools still need end-to-end coverage.
| Input injection | `sim_console_uart_write` aliasing + LF handling | **Partial** | Low-level API tested indirectly; verifying the consolidated MCP path requires an end-to-end test.
| Register access | `sim_get_registers`, `sim_get_register`, `sim_set_register` | **Covered** | `test_register_accessor_handles_abi_and_pc` now verifies ABI aliases, zero-reg immutability, and PC reporting through the MCP interface.
| Memory access | `sim_read_memory`, `sim_write_memory`, `sim_fill_memory`? (if any) | **Covered** | `test_memory_read_write_roundtrip_exposes_ram_to_cpu` proves memory writes made through RV32System persist in RAM and drive program-visible UART output; only the JSON tooling glue remains untested.
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
- ✅ SessionManager lifecycle coverage landed via `test_session_manager_lifecycle_and_lock_cleanup`.
- ✅ Register accessor regression tests landed via `test_register_accessor_handles_abi_and_pc`.
- ✅ VT100 screen helper smoke coverage landed via `test_vt100_screen_helpers_capture_tx_output` (MCP tool path still pending).
- ✅ Memory tool coverage landed via `test_memory_read_write_roundtrip_exposes_ram_to_cpu`; watchpoint/breakpoint MCP wiring is up next.

### Detailed Test Plan
| Test Name (planned) | Coverage Goal |
| --- | --- |
| `test_mcp_session_lifecycle` | ✅ Implemented as `test_session_manager_lifecycle_and_lock_cleanup`; validates `sim_create`, `sim_set_cwd`, `sim_get_status`, `sim_reset`, and `sim_destroy`, including fs_root lock cleanup logging. |
| `test_mcp_load_elf_metadata` | Load `firmware/hello.elf` via `sim_load_elf` and assert `sim_get_load_info` reports entry point, segments, and symbol counts. |
| `test_mcp_run_until_console_status_read` | ✅ Implemented as `test_run_until_console_status_read_triggers_watchpoint`; ensures the helper halts precisely at the UART status read. |
| `test_mcp_console_uart_roundtrip` | Inject mixed `\n`/`\r` input via `sim_console_uart_write`, resume execution, and verify normalized output through `sim_console_uart_read`. |
| `test_mcp_vt100_screen_dump` | ✅ Implemented as `test_vt100_screen_helpers_capture_tx_output`; validates pyte-backed screen/dump output (MCP tool wrapper still pending). |
| `test_mcp_register_access` | ✅ Implemented as `test_register_accessor_handles_abi_and_pc`; exercises ABI names, `pc`, and zero register protection. |
| `test_mcp_memory_access` | ✅ Implemented as `test_memory_read_write_roundtrip_exposes_ram_to_cpu`; writes payload via `write_memory`, confirms `read_memory`, and verifies CPU-visible UART output driven by the stored bytes. |
| `test_mcp_breakpoints_watchpoints` | Add/remove/list breakpoints and read/write watchpoints, then run until each triggers. |
| `test_mcp_symbol_and_disasm` | Load NetHack symbols, assert `sim_lookup_symbol`/`sim_reverse_lookup`/`sim_get_symbol_info`, and verify cached disassembly text matches objdump output. |
| `test_mcp_trace_buffer` | Enable trace buffer, execute a few instructions, and confirm `sim_get_trace` formatting. |
| `test_mcp_syscall_error_reporting` | Run a firmware binary that intentionally fails a syscall and ensure MCP response surfaces errno/message (to be implemented alongside improved reporting). |
