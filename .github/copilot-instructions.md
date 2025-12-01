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
   - Always use `sim_run_until_console_status_read()` right after loading NetHack; it manages the 0x10001008 read watchpoint for you and halts exactly when the game polls for input.
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

# Simulator Debugging - ABSOLUTE RULES
## MCP-FIRST DEBUGGING MANDATE
**NEVER EVER write Python scripts for debugging or testing the simulator.**

When you need to debug or test:
1. **STOP** - Do not write a Python script
2. **USE MCP TOOLS** - Use mcp_mcp-pyrv32_sim_* tools directly
3. **If MCP server is down** - Restart it, then use MCP tools
4. **NO EXCEPTIONS** - Even "quick tests" must use MCP

## FORBIDDEN Actions:
- ❌ Creating test_*.py scripts to run the simulator
- ❌ Creating debug_*.py scripts to inspect state
- ❌ Creating play_*.py scripts to automate gameplay
- ❌ Writing ANY Python code that imports pyrv32_system or RV32System
- ❌ "Let me write a quick script to test this"
- ❌ "I'll create a Python script to debug this"

## REQUIRED Actions:
- ✅ Use mcp_mcp-pyrv32_sim_create to start session
- ✅ Use mcp_mcp-pyrv32_sim_load_elf to load ELF files (NOT sim_load - .bin support removed)
- ✅ Use mcp_mcp-pyrv32_sim_run to execute
- ✅ Use mcp_mcp-pyrv32_sim_step for stepping
- ✅ Use mcp_mcp-pyrv32_sim_add_breakpoint for PC breakpoints
- ✅ Use mcp_mcp-pyrv32_sim_add_read_watchpoint for memory read watchpoints
- ✅ Use mcp_mcp-pyrv32_sim_add_write_watchpoint for memory write watchpoints
- ✅ Use mcp_mcp-pyrv32_sim_get_registers to inspect state
- ✅ Use mcp_mcp-pyrv32_sim_read_memory to read memory
- ✅ Use mcp_mcp-pyrv32_sim_console_uart_write for keyboard input

## SYMBOLIC DEBUGGING - ALWAYS USE WHEN DEBUGGING:
- ✅ Use mcp_mcp-pyrv32_sim_lookup_symbol to find function/variable addresses by name
- ✅ Use mcp_mcp-pyrv32_sim_reverse_lookup to get symbol name at exact address
- ✅ Use mcp_mcp-pyrv32_sim_get_symbol_info to get "function+offset" for any PC value
- ✅ Use mcp_mcp-pyrv32_sim_disassemble to show assembly with C source code

**When debugging, ALWAYS:**
1. Use sim_get_symbol_info on the current PC to know what function you're in
2. Use sim_disassemble around the PC to see the actual code with source
3. Use sim_lookup_symbol to find addresses of functions you want to breakpoint
4. Much better than raw hex addresses - use symbols!

## MCP Workflow:
- ALWAYS provide running commentary when using MCP simulator tools
- Max simulation steps: 1M (use max_steps parameter to prevent runaway execution)
- If MCP tools fail, restart the MCP server and try again
- Debug by setting breakpoints and stepping, not by writing scripts

## MCP NetHack Testing Workflow (MANDATORY):
**Execute these steps IN ORDER every time you test NetHack:**
1. Create session (sim_create)
2. Load ELF (sim_load_elf with nethack-3.4.3/src/nethack.elf)
3. **Immediately call sim_run_until_console_status_read()** ← NEVER SKIP THIS STEP
4. When the helper halts on the internal 0x10001008 watchpoint:
   - Check screen (sim_get_screen)
   - Get PC and use sim_get_symbol_info to see what function you're in
   - Use sim_disassemble around PC to see the code
5. Inject input (sim_console_uart_write)
6. Continue from step 3 (run_until again, observe, inject, repeat)

**If you find yourself running sim_run without guarding with sim_run_until_console_status_read(), STOP immediately.**

## Common Mistakes to AVOID:
- ❌ Running sim_run (or any long run) before calling sim_run_until_console_status_read()
- ❌ Running sim_run with no input in buffer when NetHack is waiting for input
- ❌ Enabling trace buffer and then running 500k+ steps (massive overhead)
- ❌ Using max_steps > 1M without a specific reason
- ❌ Forgetting to check the screen after hitting a watchpoint
- ❌ Using sim_add_breakpoint for memory watchpoints (use sim_add_read_watchpoint or sim_add_write_watchpoint)

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

# TODO.md Management - CRITICAL
**ALWAYS update TODO.md immediately after completing tasks or making significant progress.**

When to update TODO.md:
- ✅ **IMMEDIATELY after completing any task listed in the Sprint section**
- ✅ **After implementing any feature or fix**
- ✅ **After discovering new issues that need tracking**
- ✅ **When starting work on a new sprint or phase**

How to update:
- Mark completed tasks with [x] checkbox
- Move completed items to "Recently Completed" section with date
- Add new discovered tasks to appropriate priority sections
- Update "Project Status" section with current state
- Keep it terse, organized, and actionable

**FORBIDDEN:**
- ❌ Completing multiple tasks without updating TODO.md
- ❌ Saying "I'll update TODO later" - update it NOW
- ❌ Creating new MD files instead of using TODO.md for tracking
- ❌ Leaving completed tasks unmarked in the checklist

**Check TODO.md status:**
- Before ending your turn
- After completing each sprint task
- When user asks about progress
</RULES>

<CONTEXT>
This is a Python RISC-V RV32IM simulator for running any RV32 apps, but especially a cross compiled NetHack 3.4.3 port. UART devices (console and debug), Memory-mapped I/O, Linux-compatible syscall interface via ECALL, Model Context Protocol MCP server "mcp-pyrv32" for simulator control. 
MCP stdio frontend is a thin forwarder to the simulator MCP server. 
Start new sim MCP server: `kill $(lsof -ti:5555) 2>/dev/null || true && cd pyrv32_mcp && python3 sim_server_mcp_v2.py >/dev/null 2>&1 &`.
Build firmware: `cd firmware && make`
Setup NetHack: `cd nethack-3.4.3/sys/pyrv32 && ./setup.sh`
Compile NetHack: `cd nethack-3.4.3 && make -j4`

**ELF-Only Workflow (Raw .bin support removed):**
- Load programs: `sim_load_elf` with .elf files only
- All programs built as .elf (firmware/*.elf, nethack-3.4.3/src/nethack.elf)
- ELF files contain symbol tables for debugging

**Symbolic Debugging - Use These Instead of Raw Addresses:**
- `sim_lookup_symbol("main")` → Get function address
- `sim_get_symbol_info(pc)` → Get "function+offset" for any address
- `sim_disassemble(start, end)` → Assembly with C source interleaved
- Makes debugging MUCH easier than hex addresses alone

**Old tools (don't use these anymore):**
- ❌ `riscv64-unknown-elf-nm` - Use sim_lookup_symbol instead
- ❌ Manual objdump - Use sim_disassemble instead
</CONTEXT>