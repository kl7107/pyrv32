# TODO

## Project Status
**Last Audit: Complete**
- RV32IM: 48/48 instructions implemented ✓
- Python unit tests: 98% coverage on execute.py ✓
- Assembly tests: 11/11 passing ✓
- C runtime tests: 9/9 passing ✓
- Firmware programs: 19/19 build successfully ✓
- MCP server: 41 tools, fully operational ✓

## Recently Completed
- [x] Repository cleanup - moved 60+ debug scripts to `_archive/`
- [x] Created missing test files: test_execute_sb.py, test_execute_lui.py, test_execute_ebreak.py
- [x] Fixed asm_tests/Makefile to use rv32im for M extension support
- [x] Archived old MCP files (pyrv32_server.py, sim_client.py, etc.)
- [x] Updated pyrv32_mcp/README.md with current architecture
- [x] Added MCP convenience tools: sim_run_until_input_consumed, sim_send_input_and_run, sim_run_until_idle, sim_interactive_step

## Active Development
- [ ] NetHack gameplay testing and debugging
- [ ] Add more syscalls as needed for applications

## Future Ideas
- [ ] RV32C compressed instruction support
- [ ] Floating point (RV32F) soft-float
- [ ] GDB remote debugging protocol
- [ ] Performance optimization

## Known Limitations
- No MMU/virtual memory
- Single-threaded only
- No interrupts (polling-based I/O)
