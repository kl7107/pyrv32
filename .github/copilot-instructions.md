<RULES>
# Problem-Solving Approach - CRITICAL
## When encountering errors or failures:
1. **DEBUG FIRST** - Investigate the root cause completely before considering alternatives
2. **NEVER suggest "skipping for now"** - Every task must be completed or explicitly rejected by user
3. **NEVER suggest "moving on to easier tasks"** - Finish what you started
4. **Use all available debugging tools**:
   - Disassembly (objdump -d -S)
   - Memory inspection (MCP read_memory)
   - Register inspection (MCP get_registers)
   - Breakpoints at fault addresses
   - Trace execution leading to failure
5. **Exhaust ALL debugging approaches** before asking for help:
   - Check syscall parameters
   - Verify file paths and permissions
   - Examine assembly at crash point
   - Step through with breakpoints
   - Check for null pointers, bad addresses
6. **If truly stuck**: Explain what you've tried, what you learned, and ask specific questions

## NetHack Source Code - ABSOLUTE RULE
**NEVER modify NetHack source code to work around simulator limitations.**

When NetHack code fails:
1. **The simulator is wrong, not NetHack** - NetHack is a mature, well-tested Unix application
2. **Fix the simulator** - Implement missing syscalls, fix runtime initialization, add libc support
3. **NO PATCHES** - Do not modify .c/.h files in nethack-3.4.3/ to "make it work"
4. **Think Unix-compatible** - If NetHack does it, standard Unix supports it, so our simulator must too

Examples of FORBIDDEN shortcuts:
- ❌ "Let's patch dgn_comp to use fopen() instead of freopen()"
- ❌ "We can modify this to not use stdin/stdout"
- ❌ "Let's simplify this function to avoid the syscall"
- ❌ "We can comment out this feature"

Examples of REQUIRED fixes:
- ✅ "freopen() fails because stdin isn't initialized - let's initialize FILE structures in crt0.S"
- ✅ "Missing SYS_DUP2 syscall - let's implement it in syscalls.py"
- ✅ "Environment variables not working - let's fix envp handling"
- ✅ "File operations fail - let's add proper fd initialization"

**The goal is a Unix-compatible RISC-V simulator, not a NetHack-specific hack.**

## Forbidden phrases:
- "Let's skip this for now"
- "We can come back to this later"
- "This isn't critical, let's move on"
- "Let me try the next task instead"
- "Maybe we should focus on easier files first"
- "Let's patch NetHack to work around this"
- "We can modify the source to avoid this issue"

## Required behavior:
- Stay on ONE problem until resolved or user explicitly says to stop
- Document failures with full root cause analysis
- If you catch yourself about to suggest skipping, STOP and debug deeper instead
- If you catch yourself about to patch NetHack source, STOP and fix the simulator instead

# Simulator Debugging
- ALWAYS use MCP tools directly (mcp_mcp-pyrv32_sim_*) - NEVER write Python wrapper scripts
- ALWAYS provide running commentary when using MCP simulator tools
- Max simulation steps: 1M (use max_steps parameter to prevent runaway execution)
- Input debugging: Set breakpoints at BOTH syscalls.c:stdin_getc AND _read(STDIN_FILENO) before running interactive programs

# File/Folder Operations - CRITICAL RULE
BEFORE running ls/find/grep in terminal, STOP and use VS Code tools instead:
- list_dir(path) - NOT `ls` or `ls -la`
- file_search(query) - NOT `find`
- grep_search(query, isRegexp) - NOT `grep`

Exception: When you need detailed file metadata (size, timestamps, permissions), use terminal commands.
For simple "what files exist" or "what's in this directory" questions, use VS Code tools.

# Shell Commands
- Use `./cmd_helper.py 'cmd1' 'cmd2' ...` for structured EXIT STATUS/STDOUT/STDERR output
- Better error handling than raw terminal commands

# Disassembly
- Use `riscv64-unknown-elf-objdump -d -S` (includes source interleaving)
- NOT just `-d` (assembly only)

# Development Workflow
- Build incrementally and test after each change
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