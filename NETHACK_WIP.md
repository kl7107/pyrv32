# NetHack 3.4.3 Port - Work in Progress

## Current Status

**Phase:** Build successful, debugging infinite loop  
**Last Updated:** 2024-11-26

### Build Complete ✅

**NetHack 3.4.3 successfully compiled for RV32IM:**
- Binary size: 1.7MB (1,765,704 bytes)
- Text+data: 1.77MB, BSS: 77KB
- All 114+ source files compiled
- Full syscall stubs implemented (600+ lines)
- Runtime initialization working (BSS clear, argc/argv setup)

**What Works:**
- ✅ Compilation and linking successful
- ✅ crt0.S correctly clears BSS (77KB in ~78K instructions)
- ✅ argc/argv passed to main() correctly
- ✅ main() is called at correct address (0x801573cc)
- ✅ All syscall stubs tested and functional

**Current Issue:**
- NetHack enters infinite loop during initialization
- Likely waiting for data files or stuck in error handling
- Need debugger to find exact location

---

## Debugging Plan: Simulator Enhancements

**Problem:** NetHack recompilation takes too long for debug iteration cycles.  
**Solution:** Add full debugging capabilities to the simulator.

### Feature Roadmap

#### 1. Hardware Breakpoints ⭐ **Priority 1**
**Goal:** Set breakpoints without modifying code

**Implementation:**
- Breakpoint manager class (set/delete/list)
- Check breakpoint set before each instruction
- Interactive CLI with command history (Python `readline` or `prompt_toolkit`)

**Commands:**
```
b <address>         Set breakpoint at address (hex or decimal)
b <symbol>          Set breakpoint at symbol (requires ELF)
d <num>             Delete breakpoint by number
d *                 Delete all breakpoints
l                   List all breakpoints
i                   Show breakpoint info (hit count, condition)
c                   Continue execution
```

**CLI Features:**
- Command history (up/down arrows)
- History search (Ctrl+R)
- Tab completion for commands
- Colored output for clarity

**Unit Tests:**
- Add/delete/list breakpoints
- Breakpoint triggering
- Multiple breakpoints
- Breakpoint persistence across continue

**Estimate:** 2-3 hours

---

#### 2. Single Stepping ⭐ **Priority 2**
**Goal:** Step through code instruction by instruction

**Implementation:**
- `--step` flag to start in step mode
- Step mode flag in execution loop
- Interactive step commands

**Commands:**
```
s                   Step one instruction
s <N>               Step N instructions
n                   Next (step over calls - TBD)
c                   Continue to next breakpoint
r                   Run to function return (TBD)
```

**Unit Tests:**
- Single step execution
- Step N instructions
- Step + breakpoint interaction
- Step mode state persistence

**Estimate:** 1 hour

---

#### 3. Compact Register Dumps ⭐ **Priority 3**
**Goal:** Track register state during execution

**Format Design:**

FROM THE USER: PLEASE ADD OPTION FOR SINGLE LINE OUTPUT - perhaps even colored changed values if in the cli, and with room for '*' around changed values since last step.

```
[   1234] PC=0x80001000  ra=0x80000040 sp=0x80800000 gp=0x801a0000 tp=0x801a3c1a
          a0=0x00000001 a1=0x801a3c1c a2=0x00000000 a3=0x00000000 a4=0x00000000
          t0=0x801af148 t1=0x801c21a0 s0=0x00000000 s1=0x00000000
```

**Implementation:**
- Single-line format with aligned columns
- Optional: dump before each instruction
- Output to stdout and/or file
- Configurable verbosity (all regs vs non-zero only) -- NOT USEFUL TO DUMP NON-ZERO - but maybe just output changes since last cli prompt?

**Options:**
```
--reg-trace              Enable register dumps per instruction
--reg-trace-file <file>  Save register trace to file
--reg-nonzero            Only show non-zero registers
```

**Unit Tests:**
- Register dump formatting
- File output
- Non-zero filtering
- Format consistency over multiple steps

**Estimate:** 1-2 hours

---

#### 4. ELF Support + Source-Level Debugging ⭐ **Priority 4**
**Goal:** Debug with C source code visibility

**Implementation:**
- Accept `.elf` file as input (auto-detect by extension)
- Run `objcopy -O binary` to extract binary
- Run `objdump -d -S -l` for mixed source/assembly
- Cache objdump output in temp file
- Parse objdump to build PC → source line mapping
- During single-step: display current location context

**Display Format:**
```
[   1234] PC=0x80001000  In function: main  File: unixmain.c:87

Source:
    85:     hname = argv[0];
    86:     hackpid = getpid();
 => 87:     (void) umask(0777 & ~FCMASK);
    88:
    89:     choose_windows(DEFAULT_WINDOW_SYS);

Assembly:
    80001000:  lui   a5,0x10000
    80001004:  addi  a0,a5,777
 => 80001008:  call  umask
    8000100c:  lui   a0,0x80100

Registers:
    PC=0x80001008  ra=0x80000040 sp=0x80800000 a0=0x000001ff
```

**Options:**
```
--elf <file>            Use ELF file (auto-convert to binary)
--source-lines <N>      Show N lines of source context (default: 5)
--asm-lines <N>         Show N lines of assembly context (default: 3)
--no-source             Disable source display
```

**Features:**
- Symbol lookup (function names, variables)
- Source file + line number display
- Mixed C/assembly view
- Demangling support (if C++) -- NOT NEEDED, C ONLY

**Unit Tests:**
- ELF file loading
- objcopy execution
- objdump parsing
- PC → source mapping
- Context display formatting

**Estimate:** 3-4 hours

---

### Implementation Plan

**Phase 1: Core Debugging (4-5 hours)**
1. Breakpoints (2-3h)
2. Single stepping (1h)
3. Register tracing (1-2h)

**Milestone:** Can set breakpoint at NetHack main, step through initialization, watch registers

**Phase 2: Source-Level Debugging (3-4 hours)**
4. ELF support + objdump integration

**Milestone:** Can step through NetHack with C source visible

**Phase 3: NetHack Debugging (2-4 hours)**
5. Find infinite loop location
6. Analyze C source
7. Identify root cause
8. Implement fix

**Total Estimate:** 9-13 hours

---

### Testing Strategy

**Unit Tests to Add:**
- `test_breakpoints.py`: Breakpoint operations
- `test_stepping.py`: Single-step behavior
- `test_regdump.py`: Register dump formatting
- `test_elf_loader.py`: ELF loading + objdump parsing

**Integration Tests:**
- Set breakpoint in hello.c main, verify stop
- Step through first 10 instructions of dhrystone
- Trace registers during malloc call
- Display source+asm for libc_test.c

**Test Approach:**
- Small test programs with known behavior
- Verify debugger shows expected state
- Test each feature independently
- Then test feature combinations

---

## NetHack Build Details

### Symlink Architecture
Master runtime files in `firmware/`, symlinked from NetHack:
```
nethack-3.4.3/sys/pyrv32/
├── crt0.S -> ../../../firmware/crt0.S
├── syscalls.c -> ../../../firmware/syscalls.c
└── link.ld -> ../../../firmware/link.ld
```

**Benefits:**
- Single source of truth
- Changes automatically apply to both projects
- Easy to test syscalls independently

### Configuration (sys/pyrv32/pyrv32conf.h)
```c
#define UNIX                    // Unix-like system
#include "unixconf.h"           // Base Unix config

// Override Unix defaults for bare-metal
#undef MAIL                     // No mail daemon
#undef SHELL                    // No shell escape  
#undef DEF_PAGER                // No external pager
#undef SELECTSAVED              // No saved game selection
#undef SYSCF                    // No system config file
#undef PANICLOG                 // No panic log
#undef RECORD                   // No score file
#undef TIMED_DELAY              // No precise timing

#define TTY_GRAPHICS            // Text terminal only
#define ANSI_DEFAULT            // Hardcoded VT100 sequences
#define TEXTCOLOR               // VT100 colors
```

**Patched Files:**
- `include/tcap.h`: Don't define TERMLIB when ANSI_DEFAULT is set

### Syscalls Implemented (600+ lines)
**File operations:** open, close, read, write, lseek, fstat, creat, unlink, access, rename, link, chmod, stat  
**Process operations:** fork, wait, execl, execv, getpid, umask, sleep, dosuspend  
**User operations:** getuid, geteuid, getgid, getegid, setuid, setgid, getlogin, getpwuid, getpwnam  
**Directory operations:** chdir, getcwd  
**Terminal operations:** isatty, getioctls, setioctls, fpathconf  
**Termcap support:** ospeed variable, tputs function

All return appropriate errors for bare-metal environment (ENOENT, ENOSYS, etc.)

### Build Process
```bash
cd pyrv32/nethack-3.4.3
./build-pyrv32.sh

# Steps:
# 1. Build host utilities (makedefs)
# 2. Generate headers (pm.h, onames.h, date.h)
# 3. Generate sources (monstr.c, vis_tab.c)
# 4. Compile runtime (crt0.o, syscalls.o from symlinks)
# 5. Cross-compile all NetHack sources (114+ files)
# 6. Link with -nostartfiles -nodefaultlibs
# 7. Create binary with objcopy

# Output:
# - nethack.elf (1.77MB with debug symbols)
# - nethack.bin (1.7MB raw binary)
# - nethack.map (linker map)
```

### Memory Layout
```
0x80000000  _start (crt0.S entry point)
0x80000030  bss_done (after BSS clear)
0x80000040  main call
...
0x801573cc  main() function
0x801a3c0c  .tdata (TLS initialized data, 14 bytes)
0x801a3c1a  .tbss (TLS uninitialized, 56 bytes)
0x801af148  .bss start (77,952 bytes)
0x801c21a0  .bss end
0x807FF000  Stack (1MB, grows down)
0x80800000  RAM end (8MB total)
```

---

## Debugging Observations

### What We Know (via PC tracing)

**Using `python3 pyrv32.py --pc-trace 10000 firmware/nethack.bin`:**

1. **Startup (instructions 0-8):**
   - Sets sp = 0x80800000 (stack top)
   - Sets tp = 0x801a3c1a (TLS pointer)
   - Initializes t0 = 0x801af148 (BSS start)
   - Initializes t1 = 0x801c21a0 (BSS end)

2. **BSS Clear Loop (instructions 8-78,141):**
   - Loop at 0x80000020-0x8000002c
   - Clears 77,952 bytes (19,488 words)
   - ~4 instructions per word = ~78K instructions
   - Takes <1 second at 100 KIPS
   - **This works correctly!**

3. **Main Call (instruction 78,141):**
   - Sets argc (a0) = 1
   - Sets argv (a1) = 0x801a3c1c
   - Calls main at 0x801573cc via jalr
   - **Main is entered successfully!**

4. **Inside Main (instruction 78,141+):**
   - PC enters NetHack code
   - No UART output produced
   - No exceptions or crashes
   - PC cycles through various addresses
   - **Stuck in silent execution loop**

### Hypothesis
NetHack initialization is:
1. Successfully running
2. Trying to access files (open, fopen, access)
3. Getting errors (ENOENT)
4. Either waiting/retrying or stuck in error handler
5. Never reaching the point where it would output to console

**Most likely locations:**
- File I/O in `files.c`
- Configuration file loading
- Data file access
- Lock file creation

**Need debugger to:**
- Set breakpoint at first fopen/open call
- See what file it's trying to open
- Follow code path after error
- Find the loop

---

## Infrastructure Status ✅

- **RV32IM Emulator**: 8MB RAM, ~100 KIPS
- **Picolibc 1.8.6-2**: Full C library with FILE* I/O
- **TLS Support**: errno, rand/srand, strtok
- **Dual UART**: Debug @ 0x10000000, Console @ 0x10001000-0x10001008
- **Real-Time Clock**: Unix time + nanoseconds
- **Complete Syscalls**: All picolibc + NetHack requirements
- **PC Tracing**: `--pc-trace N` samples PC every N instructions
- **Testing**: 186+ tests passing

---

## Memory Map

```
RAM:
0x80000000 - 0x807FFFFF    8MB RAM

I/O Registers:
0x10000000                 Debug UART TX
0x10000004                 Timer (milliseconds)
0x10000008                 Unix time (seconds)
0x1000000C                 Nanoseconds
0x10001000                 Console UART TX
0x10001004                 Console UART RX
0x10001008                 Console UART RX Status
```

---

## Performance

- **Simulator**: ~100 KIPS (100,000 instructions/second)
- **BSS Clear**: 78K instructions in <1 second
- **NetHack Binary**: 1.7MB loads instantly

---

## Next Session Plan

1. **Start with breakpoints** (highest value)
   - Create `debugger.py` module
   - Add Breakpoint class
   - Integrate into execution loop
   - Add CLI with readline
   - Test with hello.c

2. **Add single stepping**
   - Minimal changes to execution loop
   - Interactive step command
   - Test stepping through dhrystone

3. **Add register tracing**
   - Design compact format
   - Add to step mode
   - Test with libc_test

4. **ELF support** (when basic debugging works)
   - objcopy/objdump integration
   - Source line mapping
   - Context display

5. **Debug NetHack**
   - Find the loop
   - Fix the issue
   - Play the game!

