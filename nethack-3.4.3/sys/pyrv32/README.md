# PyRV32 Port Files

This directory contains the PyRV32-specific port of NetHack 3.4.3.

## Files

### Configuration
- **pyrv32conf.h** - Platform-specific configuration header
  - Defines UNIX, TTY_GRAPHICS, ANSI_DEFAULT
  - Disables file I/O features (INSURANCE, NEWS, MAIL, etc.)
  - Enables core gameplay features (AUTOPICKUP_EXCEPTIONS, GOLDOBJ)

### Build System
- **Makefile** - Top-level build orchestration
  - Builds host utilities (makedefs, lev_comp, dgn_comp)
  - Generates game data files
  - Cross-compiles for RV32IM
  - Links with picolibc

### Runtime Infrastructure (Symlinks)

These files are **symbolic links** to the master versions in `../../firmware/`:

- **crt0.S** → `../../../firmware/crt0.S`
  - Startup code with TLS initialization
  
- **syscalls.c** → `../../../firmware/syscalls.c`
  - System call stubs (_write, _read, _sbrk, etc.)
  - UART I/O implementation
  
- **link.ld** → `../../../firmware/link.ld`
  - Linker script for 8MB RAM layout

**Why symlinks?** This ensures a single source of truth for PyRV32 runtime code
that's shared across all programs (test suite, NetHack, future applications).
Changes to the runtime affect all programs consistently.

## Building

From the nethack-3.4.3 directory:

```bash
./build-pyrv32.sh
```

This will:
1. Build host utilities with native gcc
2. Generate game data files
3. Cross-compile game source for RV32IM
4. Link with picolibc
5. Create nethack.bin for the emulator

## Architecture

- **Target**: RV32IM (32-bit RISC-V with Integer + Multiply extensions)
- **RAM**: 8MB at 0x80000000
- **C Library**: Picolibc 1.8.6-2
- **Terminal**: ANSI_DEFAULT (hardcoded VT100 sequences, no termcap library)
- **Window System**: TTY only (text-based)

## Dependencies

- riscv64-unknown-elf-gcc (for RV32IM cross-compilation)
- picolibc (RISC-V variant)
- gcc (native, for host utilities)
- make

## Status

See BUILD_PROGRESS.md in parent directory for detailed build status.
