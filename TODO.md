# TODO - PyRV32 NetHack Project

## 📖 Instructions (Read-Only - User Maintained)

You must work independently to get all the way to the end goal: A fully functional and playable NetHack.

You must verify this yourself. That is, you must play the game until you have descended to the Level 2 dungeon. It's up to you to take the end goal and break it down. plan, do, check, act!

Do not stop working with comments like these: "NetHack is fully built and ready to play! The game works - it's just waiting for interactive input which doesn't exist in headless mode."

When testing NetHack, always use MCP, not scripts.

**CRITICAL: AFTER sim_load_elf immediately call sim_run_until_console_status_read()**
This helper now owns the 0x10001008 watchpoint lifecycle for you and halts exactly when NetHack polls for input.
Using it as the very next command prevents the simulator from burning millions of cycles in the polling loop and keeps the RX prompt workflow deterministic.
Skipping this step will leave you blind to input requests and waste 500k-1M instructions doing nothing.

**ALWAYS USE SYMBOLIC DEBUGGING WHEN DEBUGGING:**
- `sim_get_symbol_info(pc)` - See "function+offset" instead of raw hex
- `sim_lookup_symbol("main")` - Get address by function name
- `sim_disassemble(start, end)` - View assembly with C source code
- Makes debugging MUCH easier - you see what function you're in!

**Use separate tools for PC breakpoints vs memory watchpoints:**
- `sim_add_breakpoint` - PC breakpoints (code execution)
- `sim_add_read_watchpoint` - Memory read watchpoints (any address)
- `sim_add_write_watchpoint` - Memory write watchpoints (any address)
- Watchpoints work in RAM, MMIO, anywhere in memory space

Always keep this TODO.md file updated, focused, clean, organized and terse. Do not litter the repo with tons of new MD files. New MD files are OK if they add value, but so far we have 20x as many as we should.

Always keep going — GO GO GO!

**END OF READ-ONLY USER INSTRUCTIONS**

---

## 🎯 Sprint: Play NetHack to Level 2

**Goal:** Play NetHack from start through Level 1 to descending stairs to Level 2

- [x] **Implement pyte VT100 terminal emulation** - 80x24 virtual screen in simulator ✅ COMPLETE
- [x] **Add screen dump commands** - CLI/MCP commands to view terminal state ✅ COMPLETE
- [x] **Add logging** - /tmp logs for console TX/RX and screen dumps ✅ COMPLETE
- [x] **Fix stdin/stdout syscall redirection** - Route fd 0/1/2 to console UART ✅ COMPLETE
- [x] **Add auto screen dumps on RX poll** - Rate-limited dumps when waiting for input ✅ COMPLETE
- [x] **CRITICAL FIX: stdin_read() blocking behavior** - Fixed Dec 1, 2025 ✅ COMPLETE
  * ROOT CAUSE: stdin_read() was blocking waiting for ALL requested bytes (e.g., 512)
  * When only partial input available (e.g., "Hero\n" = 5 bytes), would hang forever
  * SOLUTION: Read first byte blocking, remaining bytes non-blocking, return actual count
  * Matches Unix read() semantics - partial reads are normal and expected
  * NetHack now proceeds correctly after name input (tested with 4 additional steps)
- [x] **CRITICAL FIX: run_until_output() wrong UART** - Fixed Dec 1, 2025 ✅ COMPLETE
  * Was checking debug UART (self.memory.uart) instead of console UART
  * NetHack writes to console UART, so run_until_output() never detected output
  * Changed to check self.memory.console_uart.get_output_text()
- [x] **CRITICAL FIX: get_status() console_has_output** - Fixed Dec 1, 2025 ✅ COMPLETE
  * Was referencing non-existent self.console_uart
  * Changed to check self.memory.console_uart.get_output_text()
- [x] **NEW FUNCTION: run_until_console_status_read()** - Added Dec 1, 2025 ✅ COMPLETE
  * Runs until read instruction accesses 0x10001008 (Console UART RX Status)
  * Detects when program polls for input (NetHack polling pattern)
  * Automatically adds/removes read watchpoint as needed
  * MCP tool: sim_run_until_console_status_read
- [ ] **Complete NetHack character creation** - Automate full character creation sequence
  * Use sim_run_until_console_status_read to detect input prompts
  * Inject name, role, race, gender, alignment inputs
  * Verify character creation completes successfully
  * Regenerated `include/onames.h` with PYRV32 config and rebuilt NetHack to fix init_objects prob mismatch
  * Fixed TLS thread-pointer setup in `firmware/crt0.S` so libc TLS buffers (errno/localtime) stop trampling env data
  * Added ELF loading support to `pyrv32.py` CLI so PTY runs can execute NetHack ELF directly (Dec 2, 2025)
- [ ] **Play through to Level 2** - Character creation → explore Level 1 → descend stairs

---

## 🔥 High Priority

- [x] Verify shared ELF loader via CLI and MCP ✅ Dec 2, 2025
  * Confirmed NetHack loads identically via `pyrv32.py --step` (auto-quit) and via MCP `sim_load_elf` followed by `sim_run_until_console_status_read`.
- [x] Surface ELF metadata through MCP ✅ Dec 2, 2025
  * Added `sim_get_load_info` MCP tool plus symbol-count reporting in `sim_load_elf`, backed by cached metadata in `RV32System`.
- [x] Debug NetHack save/restore failure ✅ Dec 2, 2025
  * MCP automation reproduced the "Saving... Cannot open save file" error; root cause was missing `usr/games/lib/nethackdir/save/` directory in `pyrv32_sim_fs`.
  * Added the directory and verified that saving now creates `save/0Saver_` and launching a new session restores the save (console shows "Restoring save file...").
- [x] Add `argv`/`envp` support to MCP tools (CLI has it, MCP doesn't)
  * `sim_load_elf` now accepts optional `argv`/`envp` arrays and `RV32System.load_elf()` wires them into memory/registers just like the CLI path.
  * Metadata surfaced via `sim_load_elf`/`sim_get_load_info` includes argc/argv/envp, and `firmware/test_argvenvp.elf` passes under MCP with injected arguments/env values.
- [ ] Update main README with NetHack build/play instructions
- [ ] Document syscall implementation status matrix
- [ ] Review MCP server console UART write/inject path for redundancy
- [x] Fix NetHack perm locking (identify stuck lock file, implement proper file locking semantics so character creation can proceed)

---

## ⚠️ Medium Priority

- [x] Cache objdump -d -S output for MCP
  * Added `objdump_cache.py` helper that materializes full `objdump -d -S` output keyed by ELF path, size, and mtime, then slices the cached text so repeated lookups avoid re-running objdump.
  * Integrated `DisasmCache` into `RV32System` and exposed `disassemble_cached()` so both CLI and MCP layers can reuse the same logic.
  * Cache snapshots now build immediately when an ELF is loaded and stay fixed until another `sim_load_elf`, so MCP lookups never trigger objdump reruns mid-session even if the file changes on disk.
  * Added `sim_disasm_cached` MCP tool for fast range lookups using the cached disassembly output, returning the matching lines directly to clients.
- [ ] Clean up temporary debug scripts (analyze_*.py, debug_*.py, etc.)
- [ ] Add regression tests for freopen() and stdio buffering
- [ ] Improve MCP error reporting for syscall failures
- [ ] Review all NetHack patches in `sys/pyrv32/`

---

## 💡 Future Ideas

- [ ] Color support (TEXTCOLOR)
- [ ] GDB remote protocol support
- [ ] Network syscalls for multiplayer
- [ ] Performance counters and profiling tools
- [ ] Signal handling (SIGINT, SIGTERM)

---

## 📦 By Component

### NetHack Integration
- [x] Build all utilities (makedefs, lev_comp, dgn_comp)
- [x] Generate all 126 runtime files
- [x] Compile NetHack binary (1.7MB)
- [ ] Color support (TEXTCOLOR patch)
- [ ] Window size detection (CO/LI)
- [ ] Wizard mode support

### Core Simulator
- [x] RV32IM instruction set
- [x] Memory-mapped UART devices
- [x] Basic syscall interface
- [ ] Performance profiling infrastructure
- [ ] Memory access optimization
- [ ] Instruction cache/decode optimization
- [ ] Function call tracing
- [ ] Memory watchpoints with conditions
- [ ] Save/restore simulator state

### MCP Server
- [x] Session management
- [x] Binary loading
- [x] Step/run execution
- [x] Register/memory inspection
- [x] Breakpoint support
- [ ] argv/envp parameter support
- [ ] Breakpoint condition support
- [ ] Better error reporting
- [ ] Performance metrics API

### Firmware / Syscalls
- [x] File I/O (open, read, write, close, lseek)
- [x] Standard I/O with buffering (stdio-bufio.h)
- [x] freopen() support
- [x] Terminal control (tcgetattr, tcsetattr, ioctl)
- [x] argc/argv/envp handling (CLI only, not MCP)
- [ ] Add missing syscalls as discovered
- [ ] Optimize stdio buffering if needed
- [ ] Signal handling (kill, signal, sigaction)
- [ ] Network syscalls (socket, etc.)
- [ ] IPC syscalls (pipe, mmap, etc.)
- [ ] Advanced file ops (fcntl, select, poll)

### Testing & Quality
- [x] test_argvenvp.c (argc/argv/envp validation)
- [x] test_stdio_streams.c (FILE operations)
- [ ] Regression test for freopen()
- [ ] Test all makedefs modes
- [ ] Automated NetHack build pipeline test
- [ ] Edge case testing (long filenames, etc.)
- [ ] Performance regression tests
- [ ] Fuzzing infrastructure

### Documentation
- [x] NETHACK_READY.md (build status)
- [x] NETHACK_UTIL_FILES.md (runtime files)
- [x] copilot-instructions.md (AI guidelines)
- [ ] Troubleshooting guide
- [ ] Two-step dungeon generation docs

---

## ✅ Recently Completed (Dec 2, 2025)

### NetHack Rebuild Validation
- Rebuilt `nethack-3.4.3/src` after the toolchain consolidation, confirming the shared `toolchain.mk` overrides select the RV32 cross tools even when environment variables are unset; `nethack.elf` now links cleanly and `riscv64-unknown-elf-size` publishes the final image size without manual intervention.

### Unified ELF Handling
- Added `elf_loader.py` helper to centralize ELF parsing, segment loading, and symbol extraction.
- Updated `pyrv32.py` CLI loader and `RV32System.load_elf()` to consume the shared helper so both paths enforce the same RISC-V/ELF32 validation and expose consistent segment metadata.

### Loader Parity Validation
- Verified NetHack loads identically via the CLI (`pyrv32.py --step nethack.elf`) and MCP (`sim_load_elf` + `sim_run_until_console_status_read`), ensuring the shared loader behaves the same across entry points.

### MCP Load Metadata Tooling
- Added cached load metadata inside `RV32System` plus a `sim_get_load_info` MCP tool (and symbol-count reporting in `sim_load_elf`) so assistants can query entry point, segment layout, and symbol counts on demand.

### Save/Restore Path Stabilization
- Identified the missing `usr/games/lib/nethackdir/save/` directory that caused NetHack to print "Saving... Cannot open save file" and prevented restores.
- Created the directory inside `pyrv32_sim_fs`, confirmed NetHack now writes `save/0Saver_`, and verified a fresh session prints "Restoring save file..." when the same hero name is entered.

### NetHack Makefile Consolidation
- Introduced `sys/pyrv32/toolchain.mk` so all PyRV32 builds share toolchain paths, runtime object lists, and default CFLAGS/LDFLAGS instead of duplicating them across `Makefile.src` and `Makefile.utl`.
- Updated the src and util makefiles to include the shared fragment (using `realpath`-aware includes for symlink safety), trimmed redundant variables, and reused the common runtime object list when linking.
- Verified the refactor by running `make clean` in both `nethack-3.4.3/src` and `nethack-3.4.3/util`, confirming the new include path parses correctly.

### Cached Disassembly for MCP
- Implemented `objdump_cache.py` to cache `objdump -d -S` output per ELF file and serve address slices without re-running objdump.
- Wired the cache into `RV32System.disassemble_cached()` and added the `sim_disasm_cached` MCP tool so assistants can fetch disassembly ranges quickly during debugging.

## ✅ Recently Completed (Dec 1, 2025)

### Perm Lock Cleanup Automation (Dec 1, 2025)
- Added fs_root tracking in `RV32System` and automatic `_lock` cleanup in `SessionManager` before creating new sessions.
- Removes stale `perm_lock` hard links under `usr/games/lib/nethackdir/`, preventing NetHack from stalling on character creation retries after an unclean shutdown.

### ELF-only NetHack Makefiles (Dec 1, 2025)
- Updated `sys/pyrv32/Makefile.top`, `Makefile.src`, and `Makefile.utl` to drop `.bin` targets entirely and point all messaging/cleanup at the `.elf` deliverables.
- Utility `generated-files` target now reuses archived data via `install` without producing unused binaries.
- Top-level build instructions now direct MCP users to load `src/nethack.elf`, matching the simulator's ELF-only workflow.

### stdin_read CR→LF Normalization (Dec 1, 2025)
- Console injection path only delivers carriage returns, so the firmware now translates `\r` to `\n` before handing bytes to newlib.
- Ensures NetHack sees proper newline terminators during character creation prompts without requiring MCP-side hacks.

---

## ✅ Recently Completed (Nov 30, 2025)

### VT100 Terminal Emulation (Nov 30, 2025)
- [x] Installed pyte library (python3-pyte via apt)
- [x] Integrated pyte Screen(80,24) and Stream into ConsoleUART class
- [x] Added /tmp/console_tx.log, /tmp/console_rx.log, /tmp/screen_dump.log
- [x] Implemented get_screen_display(), get_screen_text(), dump_screen() methods
- [x] Added inject_input() for automated keyboard input
- [x] Created RV32System VT100 API wrapper methods
- [x] Added MCP tools: sim_get_screen, sim_dump_screen, sim_inject_input
- [x] Validated VT100 emulation with test suite (all tests passed)
- [x] Fixed syscall stdin/stdout redirection to console UART
  - read(fd=0) now reads from console UART RX buffer
  - write(fd=1,2) now writes to console UART TX
- [x] Successfully tested NetHack via MCP - game loads, displays prompts
- [x] VT100 screen correctly shows "Who are you?" prompt

### NetHack Build System
- [x] Fixed freopen() implementation with buffered I/O (stdio-bufio.h)
- [x] Implemented proper stdin/stdout/stderr FILE structures
- [x] Reverted all NetHack source patches (using original code)
- [x] Built all utilities: makedefs, lev_comp, dgn_comp
- [x] Generated all 126 runtime files:
  - 6 core data files (data, dungeon, oracles, options, quest.dat, rumors)
  - 113 level files (.lev from all .des sources)
  - 7 help files (cmdhelp, help, hh, history, license, opthelp, wizhelp)
- [x] Compiled NetHack binary (1.7MB)

### Infrastructure
- [x] Added argv/envp support to pyrv32.py CLI
- [x] Fixed crt0.S envp handling (conditional preservation)
- [x] Created comprehensive test suite:
  - test_argvenvp.c (validates argc/argv/envp/environ)
  - test_stdio_streams.c (validates FILE operations, freopen)
- [x] Implemented two-step dungeon generation (makedefs -e → dgn_comp)
- [x] Created batch level generation script (generate_all_levels.py)

### Documentation
- [x] Created NETHACK_READY.md status document
- [x] Updated copilot-instructions.md with NetHack source rule
- [x] Documented problem-solving approach (no skipping, fix root cause)

---

### Symbolic Debugging Support (Nov 30, 2025)
- **Symbol table extraction** - Parse and store ELF symbols for debugging
  * Extract .symtab section during ELF loading
  * Store symbols dictionary (name → address) and reverse map (address → name)
  * Loaded 3,002 symbols from NetHack ELF
  * Prefer function symbols (STT_FUNC) in reverse lookups
- **Symbol lookup methods** - Query symbols by name or address
  * `lookup_symbol(name)` - Get address by symbol name
  * `reverse_lookup(address)` - Get symbol name at exact address
  * `get_symbol_info(address)` - Get nearest symbol + offset for any address
- **MCP tools for symbolic debugging**
  * `sim_lookup_symbol` - Look up function/variable address by name
  * `sim_reverse_lookup` - Get symbol name at address
  * `sim_get_symbol_info` - Get "function+offset" for any address
  * `sim_disassemble` - Disassemble with source using objdump -d -S
- **Disassembly with source interleaving**
  * Calls `riscv64-unknown-elf-objdump -d -S` on loaded ELF file
  * Shows assembly instructions with C source code
  * Accepts start/end address range
- **Testing** - Full validation with NetHack
  * Symbol lookup: main → 0x8015154c, _start → 0x80000000
  * Reverse lookup: 0x80000000 → _start
  * Symbol info: 0x80000100 → stdio_lseek+24
  * Disassembly shows source-interleaved assembly

### .bin File Support Removal (Nov 30, 2025)
- **Removed raw binary file support** - ELF-only workflow
  * Removed `load_binary()` and `load_binary_data()` from `pyrv32_system.py`
  * Removed `sim_load` MCP tool - only `sim_load_elf` remains
  * Updated `firmware/Makefile` - builds .elf only, no .bin generation
  * Updated `nethack-3.4.3/src/Makefile` - builds nethack.elf only
  * Deprecated `make run` - use MCP tools instead
- **Rebuilt all firmware** - Verified ELF-only builds
  * All 18 firmware programs rebuilt as .elf
  * Tested hello.elf, fibonacci.elf, printf_test.elf with MCP
  * All programs execute correctly when loaded via ELF

### ELF File Loading Support (Nov 30, 2025)
- **Added ELF parsing with pyelftools** - Native ELF file loading capability
  * Installed `python3-pyelftools` package
  * Added `load_elf()` method to `RV32System` class
  * Parses ELF header, validates RISC-V 32-bit architecture
  * Loads all PT_LOAD segments at correct virtual addresses
  * Zero-fills BSS sections (memsz > filesz)
  * Sets PC to ELF entry point automatically
  * Returns comprehensive load information (bytes, segments, entry point)
- **MCP tool: sim_load_elf** - Load ELF files via MCP protocol
  * Added tool definition in `pyrv32_mcp/sim_server_mcp_v2.py`
  * Tool handler displays segment information and load statistics
  * Verified with NetHack ELF (1.8MB, entry 0x80000000)
- **Testing** - Comprehensive validation
  * Direct Python API: `test_elf_simple.py` - Loads and executes NetHack ELF
  * MCP protocol: `test_elf_mcp.py` - Full JSON-RPC integration test
  * Both tests confirm correct loading and execution
- **Benefits** - Better debugging and development workflow
  * Symbol tables preserved (for future objdump/nm integration)
  * Section information available
  * Proper segment permissions (RWX flags)
  * Single-file distribution (no separate .bin files needed)

### Watchpoint Infrastructure Fix - Deferred Checking (Nov 30, 2025)
- **Fixed watchpoint PC advancement issue** - Watchpoints now checked AFTER instruction completes
  * Problem: Watchpoints raised exception during memory access, before instruction finished
  * PC never advanced past watchpoint location, stuck in infinite loop
  * Solution: Record watchpoint hits in `memory.pending_watchpoints` list during access
  * Check list AFTER instruction executes in `step()` function
  * PC advances correctly, then system halts with proper error message
  * Tested: PC advances from 0x80000080 → 0x80000084 after read watchpoint
- **Clean halt behavior** - System properly resumes after watchpoint with `run()` or `step()`
  * Removed early `if self.halted` checks from `run()` and `step()`
  * Each run/step clears halted flag automatically for resumption

### Memory Watchpoint Infrastructure
- **Separated PC breakpoints from memory watchpoints** - Clean architecture
  * `sim_add_breakpoint` - PC breakpoints only (code execution)
  * `sim_add_read_watchpoint` - Memory read watchpoints
  * `sim_add_write_watchpoint` - Memory write watchpoints
  * `sim_list_watchpoints` - List all read/write watchpoints
  * `sim_remove_read_watchpoint` / `sim_remove_write_watchpoint` - Remove watchpoints
- **Fixed watchpoint checking order** - Now checked BEFORE MMIO/memory access
- **Watchpoints now break execution** - Raise EBreakException to halt simulator
- **Works in any memory space** - RAM, MMIO, code space - watchpoints work everywhere
- **Comprehensive testing** - Verified add/remove/list for both read and write watchpoints
- **Updated copilot-instructions.md** - Workflow now uses `sim_add_read_watchpoint` for 0x10001008

---

## 📊 Project Status

### Build Status
- **NetHack Binary:** ✅ 1.7MB (1.69M text + 46K data + 80K BSS)
- **Runtime Files:** ✅ 126/126 complete
- **Utilities:** ✅ All built and tested
- **Infrastructure:** ✅ Fully functional

### What Works
- ✅ Complete Unix-compatible runtime environment
- ✅ File I/O (open, read, write, close, lseek, freopen)
- ✅ Terminal control (tcgetattr, tcsetattr, ioctl)
- ✅ Command-line arguments (argc/argv/envp)
- ✅ Standard I/O with buffering
- ✅ All NetHack data file generation

### Known Status
- ⏸️ **NetHack awaits interactive input** - Game initializes correctly but needs terminal I/O
- ✅ No crashes or errors during initialization
- ✅ All data files load successfully
- ⚠️ Interactive mode not yet tested

----

## 📝 Notes

### Key Files
- `NETHACK_READY.md` - Build completion status
- `NETHACK_UTIL_FILES.md` - Runtime file generation tracking
- `copilot-instructions.md` - AI workflow guidelines
- `play_nethack.py` - Interactive launcher script
- `firmware/syscalls.c` - System call implementations
- `nethack-3.4.3/sys/pyrv32/` - PyRV32-specific patches

### Important Decisions
- **Never modify NetHack source code** - Fix simulator/runtime instead
- **Unix compatibility first** - NetHack is a mature Unix app, make simulator compatible
- **Debug thoroughly before skipping** - Exhaust all debugging before moving on
- **Use original NetHack code** - All patches were reverted after proper freopen() fix

### Performance Notes
- Level generation: ~10-15 minutes CPU time for 113 files
- Each lev_comp run: 200K-500K instructions
- makedefs utilities: 50K-1M instructions depending on mode
- Dungeon generation: 491K (makedefs -e) + 628K (dgn_comp) instructions
