# NetHack 3.4.3 - Technical Information

**INSTRUCTIONS:** Keep this document concise and factual. Focus on technical details, API requirements, and architectural insights discovered during analysis. Remove outdated information as we learn more.

---

## Source Code Structure

- **Total Size:** 255,353 lines (265 .c files, 159 .h files)
- **Core Game:** 106 C files in `src/`
- **TTY Window System:** 4 files, 4,548 lines in `win/tty/`
  - `getline.c` (284 lines) - Input handling
  - `termcap.c` (1,185 lines) - Terminal control
  - `topl.c` (467 lines) - Top line messages
  - `wintty.c` (2,612 lines) - Main TTY windowing
- **Build System:** Traditional Unix Makefiles in `sys/unix/`
- **Data Files:** `dat/` directory compiled into `nhdat` binary

## Binary Size Estimates

- **Compiled binary:** 300-500KB
- **Runtime data:** ~2MB
- **Heap requirements:** ~4MB
- **Stack:** ~1MB
- **Total memory:** ~7.4MB (fits in 8MB)

## Dependencies

### Standard C Library (libc) ✅ Have Picolibc

**Memory:**
- `malloc()`, `free()`, `calloc()`, `realloc()` ✅ Working (7MB heap)

**String Operations:**
- `strlen()`, `strcpy()`, `strcmp()`, `strncpy()`, `strncmp()` ✅
- `strcat()`, `strncat()`, `strchr()`, `strrchr()`, `strstr()` ✅
- `memcpy()`, `memset()`, `memmove()`, `memcmp()`, `memchr()` ✅

**String Formatting:**
- `sprintf()`, `snprintf()` ✅ (102 tests passing)
- `printf()`, `fprintf()` ✅ (FILE* with function pointers)

**Conversion:**
- `atoi()`, `atol()`, `strtol()`, `strtoul()` ✅

**Character Classification:**
- `isalpha()`, `isdigit()`, `isspace()`, `toupper()`, `tolower()` ✅

**Time:**
- `time()`, `gettimeofday()` ✅ (Unix time + nanoseconds)
- `localtime()`, `gmtime()` - Available in picolibc

**Random Numbers:**
- `rand()`, `srand()` ✅ (TLS-based, working)

**Sorting/Searching:**
- `qsort()`, `bsearch()` ✅ (tested)

**Environment:**
- `getenv()` - Stub or implement (not critical)

**Miscellaneous:**
- `abs()`, `labs()`, `div()` ✅
- `strtok()` ✅ (TLS-based)

**Status:** All NetHack libc requirements met by picolibc 1.8.6-2

### File I/O System
**Stream I/O:**
- `fopen()`, `fclose()`, `fread()`, `fwrite()`, `fseek()`, `ftell()`

**Character I/O:**
- `fgets()`, `fputs()`, `fgetc()`, `fputc()`

**Low-level I/O:**
- `open()`, `close()`, `read()`, `write()`

**File Operations:**
- `stat()`, `access()`, `unlink()`, `rename()`

**Porting Options:**
1. **Phase 1 (Recommended):** Stub out (disable save/load, play-only)
2. **Phase 2:** Implement in-memory filesystem (saves within session)
3. **Phase 3:** Add filesystem support to emulator (persistent saves)

**For PyRV32 Phase 1:**
- All file operations return -1/NULL
- errno set to ENOENT/ENOSYS
- NetHack will detect and disable save/load features
- Game remains fully playable without persistence

### Terminal/Display System

**NetHack supports 3 terminal modes for TTY:**

1. **TERMLIB** - Uses termcap/terminfo library (complex, requires database files)
2. **ANSI_DEFAULT** - Hardcoded VT100 escape sequences (⭐ **CHOSEN FOR PYRV32**)
3. **NO_TERMS** - Minimal scrolling text (poor UX)

**ANSI_DEFAULT Details:**
- No termcap/terminfo library needed
- No database files required
- Hardcoded VT100/ANSI escape sequences in `termcap.c`
- Perfect for embedded systems with VT100-compatible terminals
- Code size: ~800 lines (vs 1,185 for full TERMLIB)

**Configuration:**
```c
#define TTY_GRAPHICS    // Text terminal mode
#define ANSI_DEFAULT    // Hardcoded VT100 sequences
#undef TERMLIB          // Disable termcap library
#define TEXTCOLOR       // Optional: enable colors
```

**VT100 Capabilities Used:**
- Cursor movement (CM), screen clear (CL/CE/CD)
- Reverse video (SO/SE), bold (MD/ME), underline (US/UE)
- Terminal size (LI, CO) - hardcoded to 24x80 or configurable

**For PyRV32:**
- Console UART outputs VT100 escape sequences
- Terminal emulator (xterm/PTY) interprets them
- No special porting needed - use ANSI_DEFAULT as-is

See `TERMINAL_OPTIONS.md` for complete analysis.

## Build Process

1. Build host utilities: `makedefs`, `lev_comp`, `dgn_comp`
2. Generate source files from data files
3. Compile data files into `nhdat`
4. Compile game source
5. Link everything together

**For cross-compilation:**
- Need separate host and target builds
- Utilities run on host to generate data
- Game compiled for RV32IM target

## Configuration Options

Key defines in `config.h`:
- Window system selection (TTY, X11, etc.)
- Feature enables/disables
- Memory limits
- Platform-specific behavior

## Key Insights

- **Terminal mode decided:** ANSI_DEFAULT with hardcoded VT100 sequences
- **No termcap library needed:** NetHack's termcap.c supports ANSI_DEFAULT natively
- **Libc complete:** Picolibc 1.8.6-2 provides all required functions (186+ tests passing)
- **TLS working:** errno, rand/srand, strtok all use thread-local storage correctly
- **Data files:** Compiled into binary at build time (not runtime files)
- **Save files:** Will stub out for Phase 1 (disable save/load)
- **Memory usage:** Well within 8MB limit with careful configuration
- **No floating point:** Uses integer math throughout (RV32IM perfect)
- **Real-time clock:** Unix time + nanoseconds available for timestamps/seeding
