<RULES>
CRITICAL GLOBAL RULE: Use VS Code tools to list folders, files, and search for text.
CRITICAL GLOBAL RULE: Use `./cmd_helper.py 'cmd1' 'cmd2' ...` to run shell commands with structured EXIT STATUS, STDOUT, STDERR output.
CRITICAL GLOBAL RULE: Always use the MCP tool directly for simulator debugging; do NOT write Python wrapper code.
CRITICAL GLOBAL RULE: ALWAYS KEEP 2 breakpoints at BOTH syscalls.c:stdin_getc AND _read(STDIN_FILENO) to stop when waiting for user input. 
CRITICAL GLOBAL RULE: NEVER let the sim run for more than 1M steps.
CRITICAL GLOBAL RULE: ALWAYS do a running commentary when using the MCP tool to debug using the sim.
CRITICAL GLOBAL RULE: Use "objdump -d -S", not just "-d".
Build incrementally and test after each change
</RULES>

<CONTEXT>
This is a Python RISC-V RV32IM simulator for running any RV32 apps, but especially a cross compiled NetHack 3.4.3 port. UART devices (console and debug), Memory-mapped I/O, Linux-compatible syscall interface via ECALL, Model Context Protocol MCP server "mcp-pyrv32" for simulator control. 
MCP stdio frontend is a thin forwarder to the simulator MCP server. 
Start new sim MCP server: `kill $(lsof -ti:5555) 2>/dev/null || true && cd pyrv32_mcp && python3 sim_server_mcp_v2.py >/dev/null 2>&1 &`.
Build firmware: `cd firmware && make`
Setup NetHack: `cd nethack-3.4.3/sys/pyrv32 && ./setup.sh`
Compile NetHack: `cd nethack-3.4.3 && make -j4`
Run NetHack: mcp-pyrv32 tool (source in `./pyrv32_mcp/`) "sim_load" cmd using `nethack-3.4.3/src/nethack.bin`. PC and mem R/W breakpoints and memory inspection are powerful diagnostic tools. Use the sim instruction trace to understand how we reached a certain state.
`riscv64-unknown-elf-objdump` and `riscv64-unknown-elf-nm` to Disassemble code, Find symbol addresses, Check compiled output.
</CONTEXT>