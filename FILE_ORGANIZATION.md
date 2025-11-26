# PyRV32 File Organization

## Directory Structure with Symlinks

```
pyrv32/
│
├── firmware/                           ← Master runtime files
│   ├── crt0.S          (master)        ┐
│   ├── syscalls.c      (master)        │ Shared by all programs
│   ├── link.ld         (master)        ┘
│   ├── hello.c
│   ├── fibonacci.c
│   ├── printf_test.c
│   └── build.sh
│
├── nethack-3.4.3/
│   ├── sys/pyrv32/
│   │   ├── crt0.S      → ../../../firmware/crt0.S      (symlink)
│   │   ├── syscalls.c  → ../../../firmware/syscalls.c  (symlink)
│   │   ├── link.ld     → ../../../firmware/link.ld     (symlink)
│   │   ├── pyrv32conf.h   (NetHack-specific config)
│   │   ├── Makefile       (Build system)
│   │   └── README.md
│   ├── src/
│   │   ├── Makefile.pyrv32
│   │   └── *.c (game source)
│   ├── include/
│   │   └── *.h (headers)
│   └── build-pyrv32.sh
│
├── pyrv32.py                           (Emulator)
├── memory.py
├── RUNTIME_ARCHITECTURE.md
└── KLSIM_RV32_SUMMARY.md
```

## Symlink Benefits

✅ **Single source of truth**: Bug fixes in firmware/ automatically apply to NetHack
✅ **Easy updates**: Improve runtime and all programs benefit
✅ **Version control**: Git tracks master files, symlinks are metadata
✅ **Consistency**: All programs use identical memory layout and system calls
✅ **Modularity**: Runtime is independent of application code

## Build Flow

```
NetHack Source
      ↓
  (Makefile reads sys/pyrv32/)
      ↓
  Compile: crt0.S → crt0.o  ←──────── firmware/crt0.S (via symlink)
           syscalls.c → syscalls.o ←─ firmware/syscalls.c (via symlink)
           *.c → *.o
      ↓
  Link:    *.o + crt0.o + syscalls.o + libc
      ↓
           Using: link.ld ←─────────── firmware/link.ld (via symlink)
      ↓
  Output:  nethack.elf → nethack.bin
```

## Master File Changes Propagate Automatically

If you update `firmware/crt0.S`:
- Test programs in firmware/ use new version immediately
- NetHack build uses new version via symlink
- No duplication, no sync issues!

Example:
```bash
# Fix a bug in syscalls.c
vim firmware/syscalls.c

# Rebuild test program
cd firmware && ./build.sh hello

# Rebuild NetHack
cd ../nethack-3.4.3 && ./build-pyrv32.sh

# Both now use the fixed version!
```
