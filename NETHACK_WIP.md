# NetHack 3.4.3 Port - Work in Progress

## Current Status

**Phase:** Infrastructure complete, ready for NetHack port  
**Last Updated:** 2024-11-26

### Infrastructure Complete ✅

- **RV32IM Emulator**: 8MB RAM, 100 KIPS performance
- **Picolibc 1.8.6-2**: Full C library (malloc, printf, string, time, etc.)
- **TLS Support**: Thread-local storage for errno, rand/srand, strtok
- **Dual UART System**:
  - Debug UART @ 0x10000000 (diagnostics)
  - Console UART @ 0x10001000-0x10001008 (user I/O with TX/RX/Status)
  - PTY mode available for xterm/terminal emulation
- **Real-Time Clock**: Unix time + nanoseconds @ 0x10000008/0x1000000C
- **Millisecond Timer**: @ 0x10000004
- **Complete Syscalls**: FILE* I/O, gettimeofday, all picolibc requirements
- **Comprehensive Testing**: 186+ tests passing (libc, TLS, clock, assembly, unit tests)

### NetHack 3.4.3 Analysis Complete

- **Source**: 255K lines, 106 core C files
- **Memory**: ~7.4MB total (fits in 8MB)
- **Interface**: TTY windowing (4,548 lines) - simplest option
- **Dependencies**: Standard libc (✅ have), termcap (need to evaluate)

### Next Steps

1. **Interactive Terminal Test**
   - Test Console UART RX with real keyboard input
   - Verify VT100 escape sequences work
   - Test PTY mode with screen/minicom

2. **Begin NetHack Port** ⭐ Ready to start
   - **Terminal mode: ANSI_DEFAULT** (hardcoded VT100, no termcap library)
   - Create `sys/pyrv32/` config directory
   - Create `pyrv32config.h` with feature flags
   - Adapt Unix Makefiles for RV32IM cross-compilation
   - Build with TTY_GRAPHICS only, minimal features

---

## Memory Map

```
RAM:
0x80000000 - 0x807FFFFF    8MB RAM
  └─ .text, .data, .bss, heap (7MB), stack (1MB)

I/O Registers:
0x10000000                 Debug UART TX (diagnostics, write-only)
0x10000004                 Timer (milliseconds since start, read-only)
0x10000008                 Unix time (seconds since epoch, read-only)
0x1000000C                 Nanoseconds within second (read-only)
0x10001000                 Console UART TX (user output, write-only)
0x10001004                 Console UART RX (user input, 0xFF if empty)
0x10001008                 Console UART RX Status (0=empty, 1=data ready)
```

## Testing Status

| Test Suite | Status | Count | Notes |
|------------|--------|-------|-------|
| CPU Unit Tests | ✅ | 50+ | All RV32IM instructions |
| Assembly Tests | ✅ | 11 | mul, div, rem, etc. |
| Memory Tests | ✅ | 25 | Read/write, UART, faults |
| libc Test | ✅ | 102 | String, memory, malloc, sprintf, qsort, rand |
| TLS Test | ✅ | 23 | errno, rand, strtok, isolation |
| Clock Test | ✅ | 15 | Unix time, nanoseconds, gettimeofday |
| Printf Test | ✅ | 10 | Picolibc integration |
| Dhrystone | ✅ | - | 280 Dhrystones/sec, 100.8 KIPS |
| **Total** | **✅** | **186+** | **All passing** |

---

## Porting Strategy

### Phase 1: Infrastructure ✅ **COMPLETE**

All libc, syscalls, I/O, and timing infrastructure ready.

### Phase 2: NetHack Port (1-2 weeks)

**Source Adaptation:**
- Create `sys/pyrv32/` directory with config
- Copy/modify Unix config files  
- Create `pyrv32config.h` with:
  - `#define TTY_GRAPHICS` (text terminal only)
  - `#define ANSI_DEFAULT` (hardcoded VT100 escape codes)
  - `#undef TERMLIB` (no termcap library)
  - Disable: tiles, sounds, wizard mode, save/load (Phase 1)
- No changes needed to `win/tty/` - ANSI_DEFAULT mode already supported

**Build Configuration:**
- Cross-compile with riscv64-unknown-elf-gcc -march=rv32im
- Build host utilities (makedefs, etc.) for data generation
- Enable: TTY only, minimal features
- Disable: File save/load (Phase 1), complex features
- Memory limits for 8MB system

**File I/O Strategy:**
- Phase 1: Stub out file operations (no save/load)
- Phase 2: In-memory filesystem if save/load needed
- Data files: Embed nhdat at compile time

### Phase 3: Testing & Optimization (1+ week)

- Boot test
- Fix linker/runtime errors
- Memory profiling
- Performance optimization
- Gameplay testing

---

## Alternative: VT100 Test / Quick Roguelike Demo

### Option A: VT100 Terminal Test (Recommended first step)

**Simple test program to validate Console UART with VT100:**
- Clear screen, move cursor, print colored text
- Test reverse video, bold, underline
- Read keyboard input (arrow keys, letters)
- ~100 lines of code

**Purpose:** Verify our UART works with VT100 before NetHack

**Estimate:** 1-2 hours

### Option B: Quick Roguelike Demo

**Before full NetHack, validate infrastructure (1-2 days):**
- Simple dungeon (10x10 grid)
- Player movement (@ character)
- Random monsters
- Basic combat
- UART display with VT100

**Purpose:** Prove libc, UART, memory management work end-to-end

**Estimate:** ~500 lines

---

## Technical Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-11-26 | NetHack 3.4.3 vs 3.6.7 | Smaller, simpler, better docs |
| 2024-11-26 | TTY interface only | Simplest (4.5K lines vs full curses) |
| 2024-11-26 | Picolibc vs custom | Well-tested, 50-150KB, Ubuntu package |
| 2024-11-26 | Dual UART | Separate debug/user I/O |
| 2024-11-26 | FILE* function pointers | Picolibc uses put/get/flush |
| 2024-11-26 | TLS support | Required for errno, rand, strtok |
| 2024-11-26 | Real-time clock | Unix time + nanoseconds for timestamps |
| 2024-11-26 | ANSI_DEFAULT terminal | No termcap library, hardcoded VT100 sequences |

**Resolved:**
1. ✅ **Terminal mode: ANSI_DEFAULT** - Hardcoded VT100 escape sequences, no termcap library needed
   - NetHack's termcap.c supports this mode natively
   - Perfect for embedded systems
   - See TERMINAL_OPTIONS.md for full analysis

**Open Questions:**
1. File I/O: Stub or implement in-memory filesystem?
2. Data files: Embed nhdat or implement loading?

---

## Resources

### File Locations
```
pyrv32/
├── nethack-3.4.3/          NetHack source code
├── firmware/
│   ├── crt0.S              Startup code with TLS init
│   ├── link.ld             Linker script with TLS sections
│   ├── syscalls.c          Complete picolibc syscalls (440+ lines)
│   ├── libc_test.c         Comprehensive tests (102/102 passing)
│   ├── tls_test.c          TLS validation (23/23 passing)
│   ├── clock_test.c        Clock tests (15/15 passing)
│   └── Makefile            Build system
├── pyrv32.py               Main emulator
├── memory.py               Memory map with I/O registers
├── uart.py                 UART and ConsoleUART with PTY
└── CLOCK.md                Clock register documentation
```

### Build & Run
```bash
# Build test
cd pyrv32/firmware
make libc_test      # or: tls_test, clock_test, printf_test

# Run test
cd ..
python3 pyrv32.py firmware/libc_test.bin
```

---

## Performance

- **Dhrystone**: 280 Dhrystones/second
- **Measured**: 100.8 KIPS (100,758 instructions/second)
- **libc_test**: 102 tests in 7.5 seconds
- **TLS_test**: 23 tests in 258 ms
- **Clock_test**: 15 tests in 5.5 seconds (includes timing measurements)

