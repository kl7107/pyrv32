# NetHack 3.4.3 for PyRV32 - Build System

This document describes the build system for NetHack on the PyRV32 bare-metal RISC-V simulator.

## Build System Organization

The build system follows standard NetHack conventions with PyRV32-specific adaptations:

### Makefile Structure

```
nethack-3.4.3/
├── sys/pyrv32/
│   ├── Makefile.top        # Top-level makefile (entry point)
│   ├── Makefile            # Runtime objects (crt0.o, syscalls.o)
│   ├── crt0.S              # Startup code (symlink to firmware/crt0.S)
│   └── syscalls.c          # System calls (symlink to firmware/syscalls.c)
├── src/
│   └── Makefile.pyrv32     # Game binary build
├── util/
│   └── Makefile            # Host tools (makedefs, lev_comp, etc.)
└── build-pyrv32.sh         # Convenience wrapper script
```

### Build Flow

1. **Host Utilities** (`util/`) - Built first
   - `makedefs` - Generates headers (pm.h, onames.h, date.h, etc.)
   - `lev_comp` - Level compiler
   - `dgn_comp` - Dungeon compiler
   - Target: `make generated-files`

2. **Runtime Objects** (`sys/pyrv32/`) - Built second
   - `crt0.o` - Startup code (sets up stack, calls main)
   - `syscalls.o` - System call implementations (picolibc interface)
   - Target: `make runtime`

3. **Game Binary** (`src/`) - Built last
   - Links all game objects with runtime objects
   - Produces `nethack.elf` (with debug symbols) and `nethack.bin` (raw binary)
   - Target: `make -f Makefile.pyrv32`

## Building

### Quick Build

Use the convenience script:
```bash
./build-pyrv32.sh
```

### Manual Build

Use the top-level makefile:
```bash
make -f sys/pyrv32/Makefile.top
```

### Build Targets

- `make -f sys/pyrv32/Makefile.top` or `make -f sys/pyrv32/Makefile.top all` - Build everything
- `make -f sys/pyrv32/Makefile.top game` - Build game only (same as `all`)
- `make -f sys/pyrv32/Makefile.top install` - Build and copy to `../firmware/nethack.bin`
- `make -f sys/pyrv32/Makefile.top clean` - Remove build artifacts
- `make -f sys/pyrv32/Makefile.top spotless` - Deep clean (also removes generated files)

### Build Output

- `src/nethack.elf` - ELF binary with debug symbols (for debugging)
- `src/nethack.bin` - Raw binary for PyRV32 simulator
- `src/nethack.map` - Linker map file

## Running

After building:
```bash
cd /home/dev/git/zesarux/pyrv32
python3 pyrv32.py firmware/nethack.bin
```

Or use the MCP server (recommended for debugging):
```bash
cd pyrv32_mcp
python3 sim_server_mcp_v2.py
```

## Cross-Compilation Setup

### Toolchain

- **Target**: RISC-V RV32IM (32-bit with multiply/divide)
- **Compiler**: `riscv64-unknown-elf-gcc`
- **C Library**: picolibc (lightweight embedded C library)
- **ABI**: ilp32 (integer-long-pointer 32-bit)

### Compiler Flags

```make
ARCH_FLAGS = -march=rv32im -mabi=ilp32
CFLAGS = $(ARCH_FLAGS) -O2 -g -Wall \
    -I../../firmware/include \
    -isystem /usr/lib/picolibc/riscv64-unknown-elf/include \
    -I../sys/pyrv32/include -I../include -I../sys/pyrv32 \
    -ffunction-sections -fdata-sections \
    -DPYRV32 -DANSI_DEFAULT
```

### Linker Configuration

- **Linker Script**: `sys/pyrv32/link.ld`
- **Entry Point**: `0x80000000` (standard RISC-V DRAM base)
- **Garbage Collection**: `--gc-sections` (remove unused code/data)
- **No Standard Library**: `-nostartfiles -nodefaultlibs`
- **Libraries**: `-lc -lgcc` (picolibc + compiler runtime)

## Platform Headers

Platform-specific headers are in `../firmware/include/`:

- `sys/ioctl.h` - Terminal I/O control (TIOCGWINSZ, struct winsize)
- `sys/termios.h` - Terminal attributes (POSIX termios interface)

These headers define OS-level syscalls implemented in `firmware/syscalls.c`.

## Configuration

NetHack is configured as minimal UNIX:

- `UNIX` - Base Unix compatibility
- `POSIX_TYPES` - Use POSIX type definitions
- `ANSI_DEFAULT` - ANSI terminal mode (no ncurses)
- **NOT** `LINUX` - Avoids Linux-specific dependencies

Platform-specific configuration is in `include/config.h` and `include/unixconf.h` using `#ifdef PYRV32` guards.

## Troubleshooting

### Clean Build Issues

If you encounter strange build errors:
```bash
make -f sys/pyrv32/Makefile.top spotless
make -f sys/pyrv32/Makefile.top
```

### Runtime Object Location

Runtime objects (`crt0.o`, `syscalls.o`) are built in `sys/pyrv32/`, not at the top level. The source files are symlinks to `../firmware/`.

### Dependency Tracking

The build system uses automatic dependency tracking (`.d` files). If you modify headers, dependencies are automatically updated.

### ANSI_DEFAULT Warning

You may see warnings about `ANSI_DEFAULT` being redefined. This is harmless - it's defined both in `include/config.h` and on the command line for safety.

## Development Notes

### Modifying the Build System

- **Adding Source Files**: Edit `src/Makefile.pyrv32` (`HACKCSRC`, `SYSSRC`, or `WINSRC` variables)
- **Changing Compiler Flags**: Edit `CFLAGS` in `src/Makefile.pyrv32`
- **Adding Build Steps**: Edit `sys/pyrv32/Makefile.top`

### Debugging

Use the `.elf` file for debugging with gdb:
```bash
riscv64-unknown-elf-gdb src/nethack.elf
```

Or use the PyRV32 MCP debugger for interactive debugging in the simulator.

## Comparison to Standard NetHack

Standard Unix NetHack uses `sys/unix/setup.sh` to copy/symlink makefiles into place, then runs `make` at the top level. Our build system:

1. Uses `sys/pyrv32/Makefile.top` instead of top-level `Makefile`
2. Explicitly delegates to subdirectories (no symlinks needed)
3. Builds runtime objects in `sys/pyrv32/` (not standard NetHack practice)
4. Uses cross-compilation toolchain instead of host compiler

This keeps the PyRV32 build isolated from standard Unix builds.
