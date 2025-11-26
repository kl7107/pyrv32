# PyRV32 Runtime Architecture

## Master Runtime Files (firmware/)

All PyRV32 programs share a common runtime infrastructure located in `firmware/`:

```
firmware/
├── crt0.S          - Startup code (master version)
├── syscalls.c      - System call stubs (master version)
└── link.ld         - Linker script (master version)
```

### crt0.S - Startup Code
- Sets up global pointer (gp) for small data access
- Initializes stack pointer (sp) at end of RAM
- Clears .bss section (uninitialized data)
- Initializes Thread-Local Storage (.tdata, .tbss)
- Calls main()
- Halts on return

### syscalls.c - System Calls
- **I/O**: `_write()`, `_read()` → Console UART (0x10001000)
- **Memory**: `_sbrk()` → Heap management
- **Time**: `_gettimeofday()` → RTC (0x10000008)
- **Files**: Stubs returning ENOENT (no filesystem)
- **Process**: Stubs for fork/exec/wait (not supported)

### link.ld - Memory Layout
- **RAM**: 8MB at 0x80000000 - 0x807FFFFF
- **Text**: Code and read-only data
- **Data**: Initialized global variables
- **BSS**: Uninitialized globals (zeroed at startup)
- **TLS**: Thread-local storage for errno, etc.
- **Stack**: 1MB at end of RAM (grows down)
- **Heap**: Between BSS and stack (grows up)

## Program-Specific Files

Each program has its own directory with symlinks to the master runtime:

### Test Programs (firmware/)
```
firmware/
├── hello.c, fibonacci.c, printf_test.c, etc.
├── crt0.S          (master)
├── syscalls.c      (master)
├── link.ld         (master)
└── build.sh        → builds test programs
```

### NetHack (nethack-3.4.3/sys/pyrv32/)
```
sys/pyrv32/
├── crt0.S       → ../../../firmware/crt0.S    (symlink)
├── syscalls.c   → ../../../firmware/syscalls.c (symlink)
├── link.ld      → ../../../firmware/link.ld    (symlink)
├── pyrv32conf.h (NetHack configuration)
├── Makefile     (Build system)
└── README.md    (Documentation)
```

## Benefits of This Architecture

1. **Single Source of Truth**: Runtime bugs are fixed in one place
2. **Consistency**: All programs use identical startup/syscall behavior
3. **Easy Maintenance**: Update firmware/ and all programs benefit
4. **Clear Separation**: Runtime (firmware/) vs application logic (app-specific)
5. **Version Control**: Git tracks master files, symlinks are cheap

## Memory Map (All Programs)

```
0x80000000  ┌─────────────────┐
            │  .text          │ Code and constants
            ├─────────────────┤
            │  .data          │ Initialized globals
            ├─────────────────┤
            │  .bss           │ Uninitialized globals
            ├─────────────────┤
            │  .tdata/.tbss   │ Thread-local storage
            ├─────────────────┤
            │  Heap           │ ↓ grows down
            │  (via _sbrk)    │
            │                 │
            ╎                 ╎
            │                 │
            │  Stack          │ ↑ grows up (1MB)
0x807FFFFF  └─────────────────┘
```

## Hardware Interface (All Programs)

### Console UART (0x10001000)
- **TX** (0x10001000): Write character
- **RX** (0x10001004): Read character (if available)
- **Status** (0x10001008): Bit 0 = TX ready, Bit 1 = RX ready

### Debug UART (0x10000000)
- Same layout as Console UART
- Used for debug output (separate from game I/O)

### Real-Time Clock (0x10000008)
- **Seconds** (0x10000008): Unix timestamp
- **Nanoseconds** (0x1000000C): Sub-second precision

## Cross-Compilation

All programs are built with:
- **Compiler**: riscv64-unknown-elf-gcc
- **Arch**: -march=rv32im -mabi=ilp32
- **C Library**: picolibc (RISC-V variant)
- **Optimization**: -O2 (or -Os for size)
- **Debug**: -g (DWARF symbols in .elf)

## Build Workflow

```
Source Code (.c, .S)
         ↓
   Cross-compile (riscv64-unknown-elf-gcc)
         ↓
   Object Files (.o)
         ↓
   Link with crt0.o + syscalls.o + libc
         ↓
   ELF Binary (.elf) [with symbols]
         ↓
   objcopy -O binary
         ↓
   Raw Binary (.bin) [for emulator]
         ↓
   Load at 0x80000000 and execute
```

## Adding New Programs

To create a new PyRV32 program:

1. Create source files (*.c, *.S)
2. Create symlinks to runtime:
   ```bash
   ln -s ../../firmware/crt0.S .
   ln -s ../../firmware/syscalls.c .
   ln -s ../../firmware/link.ld .
   ```
3. Compile and link:
   ```bash
   riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 \
       -c crt0.S syscalls.c yourcode.c
   riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 \
       -Tlink.ld -o program.elf \
       crt0.o syscalls.o yourcode.o -lc -lgcc
   riscv64-unknown-elf-objcopy -O binary program.elf program.bin
   ```
4. Run: `python3 pyrv32.py program.bin`

## Future Enhancements

Potential improvements to the master runtime:

- **stdio buffering**: Improve printf performance
- **malloc**: Add heap allocator (currently just _sbrk)
- **File I/O**: Add ramdisk or flash filesystem
- **Interrupts**: Timer interrupts for preemptive scheduling
- **Exceptions**: Better handling of illegal instructions
- **Floating point**: Soft-float library (no RV32F hardware)

All programs would automatically benefit from these improvements!
