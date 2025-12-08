# PyRV32 Architecture

A Python RISC-V RV32IM instruction simulator with syscall emulation and MCP server interface.

## Memory Map

```
0x00000000 - 0x0FFFFFFF  Reserved
0x10000000 - 0x10000007  Debug UART (TX/RX/Status)
0x10000008 - 0x1000000F  Real-Time Clock (seconds + nanoseconds)
0x10001000 - 0x10001007  Console UART (TX/RX/Status)
0x80000000 - 0x807FFFFF  RAM (8 MB, code + data + stack)
```

### Key Addresses
| Address      | Purpose                     |
|--------------|-----------------------------|
| `0x80000000` | Reset Vector / RAM base     |
| `0x80700000` | Heap end (grows up)         |
| `0x80800000` | Stack top (grows down)      |
| `0x10000000` | Debug UART TX register      |
| `0x10001000` | Console UART TX register    |
| `0x10000008` | RTC seconds (read-only)     |

## UART Registers

### Console UART (0x10001000) - Primary I/O
| Offset | Register   | Description |
|--------|------------|-------------|
| +0x00  | TX Data    | Write: send byte |
| +0x04  | RX Data    | Read: receive byte |
| +0x08  | RX Status  | Bit 0: data available |

### Debug UART (0x10000000) - Debug Output
Same register layout as Console UART.

## Runtime Architecture

### Startup (firmware/crt0.S)
1. Initialize `gp` (global pointer) for small data access
2. Set `sp` (stack pointer) to end of RAM
3. Clear `.bss` section
4. Initialize Thread-Local Storage (`.tdata`, `.tbss`)
5. Set up `argv`/`envp` on stack
6. Call `main(argc, argv, envp)`
7. Call `exit()` with return value

### System Calls (firmware/syscalls.c)
Implemented via `ecall` instruction with syscall number in `a7`:

| Syscall | Number | Description |
|---------|--------|-------------|
| read    | 63     | Read from fd |
| write   | 64     | Write to fd |
| openat  | 56     | Open file |
| close   | 57     | Close fd |
| fstat   | 80     | File status |
| brk     | 214    | Heap management |
| exit    | 93     | Exit program |
| gettimeofday | 169 | Get time |
| getcwd  | 17     | Get working directory |
| chdir   | 49     | Change directory |
| getuid  | 174    | Returns 1000 |
| getpid  | 172    | Returns 1 |

### Memory Layout
```
0x80000000  ┌─────────────────┐
            │  .text          │ Code
            ├─────────────────┤
            │  .rodata        │ Constants
            ├─────────────────┤
            │  .data          │ Initialized globals
            ├─────────────────┤
            │  .bss           │ Uninitialized (zeroed)
            ├─────────────────┤
            │  .tdata/.tbss   │ Thread-local storage
            ├─────────────────┤
            │  Heap ↓         │ grows toward stack
            ╎                 ╎
            │  Stack ↑        │ grows toward heap
0x80800000  └─────────────────┘
```

## MCP Server Interface

The simulator exposes an MCP (Model Context Protocol) server on port 5555 for AI agent control.

### Key MCP Tools
| Tool | Description |
|------|-------------|
| `sim_create` | Create new simulator session |
| `sim_load_elf` | Load ELF binary into memory |
| `sim_run` | Execute until halt/breakpoint |
| `sim_step` | Execute N instructions |
| `sim_send_input_and_run` | Write input + run until idle |
| `sim_get_screen` | Get VT100 terminal screen |
| `sim_get_registers` | Read all registers |
| `sim_read_memory` | Read memory bytes |
| `sim_add_breakpoint` | Set PC breakpoint |
| `sim_lookup_symbol` | Find symbol address by name |
| `sim_disassemble` | Disassemble with source |

### Starting MCP Server
```bash
cd pyrv32_mcp && python3 sim_server_mcp_v2.py &
```

## Building Programs

### Cross-Compilation
```bash
riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 \
    -Tfirmware/link.ld -o program.elf \
    firmware/crt0.S firmware/syscalls.c program.c \
    -lc -lgcc
```

### Test Programs
```bash
cd firmware && make          # Build all test programs
python3 run_c_tests.py       # Run C test suite
```

### NetHack
```bash
cd nethack-3.4.3/sys/pyrv32 && ./setup.sh
cd nethack-3.4.3 && make -j4
# Output: nethack-3.4.3/src/nethack.elf
```

## Project Structure

```
pyrv32/
├── cpu.py              # CPU state (registers, PC, CSRs)
├── memory.py           # Memory subsystem with UART
├── decoder.py          # Instruction decoder
├── execute.py          # Instruction execution
├── syscalls.py         # Linux syscall emulation
├── pyrv32_system.py    # High-level simulator API
├── elf_loader.py       # ELF file parser
├── uart.py             # UART + VT100 terminal emulation
├── debugger.py         # Interactive debugger
│
├── firmware/           # Runtime library
│   ├── crt0.S          # Startup code
│   ├── syscalls.c      # C syscall stubs
│   ├── link.ld         # Linker script
│   └── *.c             # Test programs
│
├── tests/              # Python unit tests
│   ├── test_*.py       # Per-instruction tests
│   └── c/              # C test programs
│
├── asm_tests/          # Assembly test suite
│   ├── basic/          # RV32I instruction tests
│   └── m_ext/          # M extension tests
│
├── pyrv32_mcp/         # MCP server
│   ├── sim_server_mcp_v2.py  # Main MCP server
│   └── session_manager.py    # Multi-session support
│
├── nethack-3.4.3/      # NetHack 3.4.3 source
│   └── sys/pyrv32/     # PyRV32-specific port
│
└── pyrv32_sim_fs/      # Virtual filesystem root
    ├── dat/            # NetHack data files
    └── var/            # Runtime state
```

## Instruction Set

Supports RV32IM (Base Integer + Multiply/Divide):
- **RV32I**: 37 base instructions (load/store, arithmetic, branch, jump)
- **M Extension**: 8 multiply/divide instructions (mul, mulh, div, rem, etc.)

## References
- [RISC-V Spec](https://riscv.org/specifications/)
- [picolibc](https://github.com/picolibc/picolibc) - C library for embedded
