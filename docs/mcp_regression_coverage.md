# MCP Regression Coverage Inventory (Dec 4, 2025)

This document captures the current state of automated regression coverage for MCP + simulator features, highlighting where `run_sim_tests.py` already exercises behavior and where gaps remain. It will guide the work needed to satisfy the Immediate Requirement of having regression tests for every MCP/simulator/debugger feature.

## Legend
- **Covered** – Exercised today by `tests/`, `asm_tests/`, or `tests/c` and fails if the feature regresses.
- **Partial** – Some coverage exists (usually at the RV32System layer) but the MCP tool path is untested or critical scenarios are missing.
- **Missing** – No automated test exists; regressions would only be caught manually.

## Coverage Matrix

| Area | MCP Tools / Features | Current Status | Notes |
| --- | --- | --- | --- |
| Session lifecycle | `sim_create`, `sim_destroy`, `sim_reset`, `sim_set_cwd`, `sim_get_status`, lock cleanup | **Covered** | `test_session_manager_lifecycle_and_lock_cleanup` plus the MCP-facing tests (console, VT100, trace, load-info, breakpoints, watchpoints) now call `sim_create/destroy/reset` in anger and confirm stale-lock cleanup and cwd propagation each time.
| ELF loader metadata | `sim_load_elf`, `sim_get_load_info` | **Covered** | `test_mcp_load_elf_metadata_and_get_load_info` asserts segment listings, entry point, symbol counts, and cache readiness through the MCP tool responses.
| Execution control | `sim_step`, `sim_run`, `sim_run_until_output`, `sim_run_until_console_status_read` | **Covered** | `test_mcp_console_uart_write_and_run_until_output`, `test_mcp_vt100_screen_tools_capture_output`, `test_mcp_trace_buffer_reporting`, `test_run_until_console_status_read_triggers_watchpoint`, and the new `test_mcp_step_single_instruction` now cover every execution helper exposed through MCP.
| UART console/debug I/O | `sim_console_uart_*`, `sim_debug_uart_*`, newline normalization (CR→LF) | **Partial** | `test_mcp_console_uart_write_and_run_until_output` covers console injection/has-data/read paths plus LF normalization; debug UART variants remain untested.
| VT100 screen helpers | `sim_get_screen`, `sim_dump_screen` | **Covered** | `test_mcp_vt100_screen_tools_capture_output` drives a program through MCP, then validates both tool responses include the VT100 text and dump notification.
| Input injection | `sim_console_uart_write` aliasing + LF handling | **Covered** | Verified end-to-end via `test_mcp_console_uart_write_and_run_until_output`, including CR-only injection semantics and RX-status polling.
| Register access | `sim_get_registers`, `sim_get_register`, `sim_set_register` | **Covered** | `test_register_accessor_handles_abi_and_pc` now verifies ABI aliases, zero-reg immutability, and PC reporting through the MCP interface.
| Memory access | `sim_read_memory`, `sim_write_memory`, `sim_fill_memory`? (if any) | **Covered** | `_write_program_via_tools` drives `sim_write_memory`, and the new `test_mcp_read_memory_tool` validates the read path before and after CPU-modified contents; no fill helper exists yet.
| Breakpoints & watchpoints | `sim_add_breakpoint`, `sim_remove_breakpoint`, `sim_list_breakpoints`, `sim_add_read_watchpoint`, `sim_add_write_watchpoint`, watchpoint hit flow | **Covered** | `tests/test_mcp_regression.py::test_mcp_breakpoint_tools_cover_add_list_remove` and `test_mcp_watchpoint_tools_cover_read_and_write` now cover both breakpoint and watchpoint MCP paths, including halted execution when trips occur.
| Disassembly + symbols | `sim_disassemble`, `sim_lookup_symbol`, `sim_reverse_lookup`, `sim_get_symbol_info`, objdump cache | **Covered** | `test_mcp_symbol_and_disassembly_tools` now compares MCP outputs against a reference RV32System load for lookup, reverse lookup, symbol info, and cached disassembly text.
| ELF/trace metadata | `sim_get_trace`, trace buffer sizing (if exposed) | **Covered** | `test_mcp_trace_buffer_reporting` enables tracing, checks the empty message, runs the program, and confirms PC entries show up when requested via MCP.
| Syscall surfacing | Error propagation (errno, syscall tracing) | **Missing** | Existing C tests cover functionality but not MCP error reporting helpers.
| Filesystem helpers | `sim_set_cwd`, fs_root handling, stale lock cleanup | **Partial** | SessionManager tests hit cwd propagation, but the MCP `sim_set_cwd` wrapper still needs an explicit regression.

## Next Actions
1. **Close the remaining tool gaps** – add MCP-level regressions for `sim_debug_uart_*` and `sim_set_cwd` so every exposed control path is exercised.
2. **Implement syscall error surfacing tests** once the improved MCP error reporting lands, so failing syscalls return errno/arguments in a verifiable format.
3. **Document the new coverage in how-to guides** so future assistants know how to replay the MCP harness locally (README/TESTING updates pending).

### Current Focus (Dec 4, 2025)
- ✅ Session lifecycle, register, and memory API foundations covered via `test_session_manager_lifecycle_and_lock_cleanup`, `test_register_accessor_handles_abi_and_pc`, and `test_memory_read_write_roundtrip_exposes_ram_to_cpu`.
- ✅ MCP tooling now covers console UART injection/output, VT100 screen helpers, ELF metadata, symbol/disassembly helpers, and trace buffer reporting via the new regression tests.
- ✅ Breakpoint and watchpoint JSON glue remain locked down through `test_mcp_breakpoint_tools_cover_add_list_remove` and `test_mcp_watchpoint_tools_cover_read_and_write`.
- 🔄 Outstanding gaps: `sim_debug_uart_*`, `sim_set_cwd`, syscall error surfacing, and documentation refresh still pending.

### Detailed Test Plan
| Test Name | Status | Coverage Goal |
| --- | --- | --- |
| `test_session_manager_lifecycle_and_lock_cleanup` | ✅ Landed | Exercises SessionManager plus `sim_create/destroy/reset` glue, ensuring stale locks are removed and cwd propagates. |
| `test_mcp_load_elf_metadata_and_get_load_info` | ✅ Landed | Verifies `sim_load_elf` and `sim_get_load_info` output entry point, bytes loaded, segment listings, and symbol counts. |
| `test_run_until_console_status_read_triggers_watchpoint` | ✅ Landed | Confirms the helper halts at the UART status register and removes the temporary watchpoint. |
| `test_mcp_console_uart_write_and_run_until_output` | ✅ Landed | Covers console input injection, CR-only normalization, `sim_run_until_output`, and RX/TX MCP helpers. |
| `test_mcp_vt100_screen_tools_capture_output` | ✅ Landed | Validates `sim_get_screen` and `sim_dump_screen` text/dump responses after running a VT100-printing program. |
| `test_register_accessor_handles_abi_and_pc` | ✅ Landed | Ensures ABI aliases, PC updates, and zero-register protections via MCP register tools. |
| `test_memory_read_write_roundtrip_exposes_ram_to_cpu` | ✅ Landed (foundation) | Uses the direct API to confirm RAM writes are visible to the CPU; a dedicated `sim_read_memory` MCP test remains planned. |
| `test_mcp_breakpoint_tools_cover_add_list_remove` | ✅ Landed | Covers add/list/remove plus breakpoint-triggered halts through MCP. |
| `test_mcp_watchpoint_tools_cover_read_and_write` | ✅ Landed | Validates both read/write watchpoints and the resulting halt/error text. |
| `test_mcp_symbol_and_disassembly_tools` | ✅ Landed | Cross-checks MCP symbol lookups, reverse lookups, symbol info, and cached disassembly against a reference load. |
| `test_mcp_trace_buffer_reporting` | ✅ Landed | Confirms the trace buffer reports empty vs. populated states and lists recent PCs. |
| `test_mcp_step_single_instruction` | ✅ Landed | Verifies `sim_step` advances the PC deterministically for multi-step calls and halts with zero instruction count when ebreak triggers. |
| `test_mcp_debug_uart_loopback` | 🔄 Planned | Drive bytes through `sim_debug_uart_*` to confirm the debug UART mirrors console expectations. |
| `test_mcp_set_cwd_tool` | 🔄 Planned | Call `sim_set_cwd` over MCP and assert subsequent filesystem operations honor the new working directory. |
| `test_mcp_read_memory_tool` | ✅ Landed | Uses both `sim_write_memory` and `sim_read_memory` to check round-trips before and after CPU-modified RAM bytes. |
| `test_mcp_syscall_error_reporting` | 🔄 Planned | Run a firmware binary that intentionally fails a syscall and ensure MCP responses surface errno/arguments once the improved reporting lands. |
