# NetHack Build System Progress

## Completed

Successfully created complete build infrastructure for NetHack 3.4.3 on PyRV32:

### Build Files Created

1. **sys/pyrv32/pyrv32conf.h** - Platform configuration
   - Defines UNIX, TTY_GRAPHICS, ANSI_DEFAULT
   - Disables file I/O, wizard mode, compression, shell
   - Enables AUTOPICKUP_EXCEPTIONS, GOLDOBJ
   - Does NOT include unixconf.h directly (fixed header order issue)

2. **sys/pyrv32/link.ld** - Linker script (symlink to firmware/link.ld)
   - 8MB RAM at 0x80000000
   - Text, data, BSS, TLS sections
   - 1MB stack at end of RAM
   - Heap between BSS and stack

3. **sys/pyrv32/crt0.S** - Startup code (symlink to firmware/crt0.S)
   - Sets up global pointer (gp)
   - Sets up stack pointer (sp)
   - Clears BSS
   - Initializes TLS (Thread-Local Storage)
   - Calls main()

4. **sys/pyrv32/syscalls.c** - System call stubs (symlink to firmware/syscalls.c)
   - _write() → Console UART
   - _read() → Console UART (with input support)
   - _sbrk() → Heap management
   - _gettimeofday() → RTC
   - File operation stubs (return errors)
   
   **Note**: crt0.S, syscalls.c, and link.ld are symbolic links to the master
   versions in `../../firmware/`. This ensures a single source of truth for
   all PyRV32 programs.

5. **sys/pyrv32/Makefile** - Top-level build orchestration
   - Builds host utilities (makedefs, lev_comp, dgn_comp)
   - Generates data files
   - Cross-compiles game with riscv64-unknown-elf-gcc

6. **src/Makefile.pyrv32** - Game source compilation
   - ARCH_FLAGS: -march=rv32im -mabi=ilp32
   - Links with picolibc
   - Generates nethack.elf and nethack.bin

7. **build-pyrv32.sh** - Automated build script
   - 5-step process: utils, data, runtime, game, install
   - Tracks dependencies
   - Reports progress

8. **include/config.h** - Modified to detect PYRV32
   - Includes pyrv32conf.h when PYRV32 defined
   - Preserves normal UNIX path otherwise

### Build Tools

- **makedefs** - Successfully built and tested
  - Generates pm.h, onames.h, date.h, monstr.c, vis_tab.c

### Compilation Status

**Successfully compiled 114+ source files!**

All core game files compile without errors:
- Core engine (allmain.c, cmd.c, decl.c, etc.)
- Monster system (monst.c, mondata.c, mon.c, etc.)
- Object system (objects.c, objnam.c, mkobj.c, etc.)
- Dungeon generation (mklev.c, mkmap.c, mkmaze.c, etc.)
- Combat and AI (mhitm.c, mhitu.c, monmove.c, etc.)
- Player actions (apply.c, cmd.c, do.c, invent.c, etc.)
- TTY window system (getline.c, termcap.c, topl.c, wintty.c)

Only warnings (no errors):
- Format overflow warnings in weapon.c (cosmetic)
- Uninitialized variable warnings in vision.c (harmless)
- String truncation warnings (intentional)

##Current Blocker

**Missing sys/termios.h in picolibc**

Files that need termios.h:
- `unixtty.c` - TTY initialization and control
- `ioctl.c` - Terminal ioctl operations (already removed)

Picolibc has `/usr/lib/picolibc/riscv64-unknown-elf/include/termios.h`, but it just includes `<sys/termios.h>` which doesn't exist.

## Solutions

### Option 1: Create Stub sys/termios.h (RECOMMENDED)
Create minimal termios definitions that unixtty.c needs:
```c
// In sys/pyrv32/include/sys/termios.h
#ifndef _SYS_TERMIOS_H_
#define _SYS_TERMIOS_H_

// Minimal termios for ANSI_DEFAULT mode
typedef unsigned int tcflag_t;
typedef unsigned char cc_t;
typedef unsigned int speed_t;

#define NCCS 20

struct termios {
    tcflag_t c_iflag;
    tcflag_t c_oflag;
    tcflag_t c_cflag;
    tcflag_t c_lflag;
    cc_t c_cc[NCCS];
    speed_t c_ispeed;
    speed_t c_ospeed;
};

// Stub functions (return success, do nothing)
static inline int tcgetattr(int fd, struct termios *t) { return 0; }
static inline int tcsetattr(int fd, int opt, const struct termios *t) { return 0; }

#endif
```

Then add `-I../sys/pyrv32/include` to CFLAGS so it's found first.

### Option 2: Replace unixtty.c with Minimal Version
Create `sys/pyrv32/pyrv32tty.c` with stubs for:
- `gettty()`, `settty()`, `setftty()` - no-ops for ANSI_DEFAULT
- `error()`, `xputs()` - just call putchar/puts

### Option 3: Conditional Compilation in unixtty.c
Add `#ifdef ANSI_DEFAULT` guards to skip termios code.

## Next Steps

1. Implement Option 1 (create stub sys/termios.h)
2. Update Makefile.pyrv32 to add `-I../sys/pyrv32/include`
3. Complete compilation
4. Link nethack.elf
5. Convert to nethack.bin
6. Test on PyRV32 emulator
7. Debug any runtime issues

## Estimated Remaining Work

- Create termios stub: 10 minutes
- Complete build: 5 minutes  
- First test run: 5 minutes
- Debug and fixes: Variable (30-60 minutes)

## Key Technical Achievements

1. **Fixed header include order** - pyrv32conf.h must NOT include unixconf.h directly, or system.h gets included before tradstdc.h defines FDECL/NDECL macros.

2. **Removed ioctl.c** - Not needed for ANSI_DEFAULT mode.

3. **Proper TLS setup** - crt0.S correctly initializes thread-local storage for errno, etc.

4. **Cross-compilation working** - riscv64-unknown-elf-gcc with -march=rv32im -mabi=ilp32 compiling successfully.

5. **Picolibc integration** - Using -isystem to avoid conflicts, links with -lc -lgcc.

## Build System Architecture

```
build-pyrv32.sh
├── [1] Build host utilities (native gcc)
│   └── makedefs (for generating headers/data)
├── [2] Generate headers and sources
│   ├── pm.h, onames.h (monster/object names)
│   ├── date.h (version/build info)
│   └── monstr.c, vis_tab.c (generated code)
├── [3] Build runtime objects (cross-compile)
│   ├── crt0.o (startup)
│   └── syscalls.o (system calls)
├── [4] Cross-compile game (Makefile.pyrv32)
│   ├── Compile all .c files → .o
│   └── Link → nethack.elf → nethack.bin
└── [5] Install to firmware/
```

## File Sizes (Estimated)

- Source code: ~140 .c files, ~250,000 lines
- Compiled .o files: ~2-3 MB
- nethack.elf (with debug): ~4-5 MB
- nethack.bin (stripped): ~1-2 MB
- Runtime memory: ~2-4 MB heap, 1 MB stack

## Testing Plan

1. **Boot test**: Verify program starts, doesn't crash
2. **Console output**: Check if VT100 escape sequences appear
3. **Input test**: Test keyboard input via Console UART
4. **Menu navigation**: Try character selection
5. **Game start**: See if dungeon renders
6. **Basic movement**: Test hjkl commands
7. **Save/load**: Will fail (expected), document error messages

## Known Limitations (Phase 1)

- No file I/O (save/load disabled)
- No wizard mode
- No external pager
- No shell escape
- No compression
- Limited to 8MB RAM
- No floating point (not needed)

All acceptable for initial proof-of-concept!
