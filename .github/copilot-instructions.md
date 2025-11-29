<RULES>
CRITICAL GLOBAL RULE: Use VS Code tools to list folders, files, and search for text.
CRITICAL GLOBAL RULE: Use `./cmd_helper.py 'cmd1' 'cmd2' ...` to run shell commands with structured EXIT STATUS, STDOUT, STDERR output.
CRITICAL GLOBAL RULE: Always use the MCP tool directly for simulator debugging; do NOT write Python wrapper code.
Build incrementally and test after each change
</RULES>

<CONTEXT>
This is a Python RISC-V RV32IM simulator for running any RV32 apps, but especially a cross compiled NetHack 3.4.3 port. UART devices (console and debug), Memory-mapped I/O, Linux-compatible syscall interface via ECALL, Model Context Protocol MCP server "mcp-pyrv32" for simulator control. MCP stdio frontend is a thin forwarder to the simulator MCP server. Start new sim MCP server: `kill $(lsof -ti:5555) 2>/dev/null || true && cd pyrv32_mcp && python3 sim_server_mcp_v2.py >/dev/null 2>&1 &`.
Build firmware: `cd firmware && make`
Setup NetHack: `cd nethack-3.4.3/sys/pyrv32 && ./setup.sh`
Compile NetHack: `cd nethack-3.4.3 && make -j4`
Run NetHack: mcp-pyrv32 tool (source in `./pyrv32_mcp/`) "sim_load" cmd using `nethack-3.4.3/src/nethack.bin`. Breakpoints and memory inspection are powerful diagnostic tools.
`riscv64-unknown-elf-objdump` and `riscv64-unknown-elf-nm` to Disassemble code, Find symbol addresses, Check compiled output
</CONTEXT>

**Strategic Breakpoints**: Set breakpoints at key points to observe execution:
   - `stdin_getc()` polling loop
   - Memory addresses for global variables
   - Function entry points

### NetHack Build System
- `nethack-3.4.3/sys/unix/Makefile.top` - Top-level build
- `nethack-3.4.3/sys/unix/Makefile.src` - Source build rules
- `nethack-3.4.3/sys/pyrv32/Makefile.src` - Platform-specific overrides

### Python Simulator Architecture
- `RV32System` - High-level interface (load binary, run, syscalls)
- `CPU` - Execution engine (fetch-decode-execute)
- `Memory` - Address space management
- `UART` - Memory-mapped I/O devices
