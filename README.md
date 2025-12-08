# pyrv32 - RISC-V RV32IM Simulator

A Python RISC-V RV32IM instruction simulator with Linux syscall emulation and MCP server interface for AI agent control. Runs NetHack 3.4.3 and other programs.

## Quick Start

```bash
# Run unit tests
python3 -m pytest tests/

# Run a program
python3 pyrv32.py firmware/hello.elf

# Start MCP server (for AI agent control)
cd pyrv32_mcp && python3 sim_server_mcp_v2.py &

# Build and run NetHack
cd nethack-3.4.3/sys/pyrv32 && ./setup.sh
cd nethack-3.4.3 && make -j4
# Then load nethack-3.4.3/src/nethack.elf via MCP
```

## Features

- **RV32IM ISA**: Full base integer + multiply/divide instructions
- **Linux Syscalls**: read, write, open, close, stat, brk, exit, etc.
- **VT100 Terminal**: Full terminal emulation for curses programs
- **MCP Server**: AI agent control via Model Context Protocol
- **Symbolic Debugging**: Symbol lookup, source-level disassembly, breakpoints
- **ELF Loading**: Direct loading of cross-compiled ELF binaries

## Project Structure

```
pyrv32/
├── cpu.py, memory.py, decoder.py, execute.py  # Core simulator
├── syscalls.py          # Linux syscall emulation
├── pyrv32_system.py     # High-level simulator API
├── uart.py              # UART + VT100 terminal
├── firmware/            # Runtime library + test programs
├── tests/               # Python unit tests
├── asm_tests/           # Assembly instruction tests
├── pyrv32_mcp/          # MCP server for AI control
├── nethack-3.4.3/       # NetHack 3.4.3 source
└── pyrv32_sim_fs/       # Virtual filesystem root
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Memory map, syscalls, MCP tools
- [MEMORY_MAP.md](MEMORY_MAP.md) - Detailed memory layout
- [firmware/README.md](firmware/README.md) - Runtime library
- [pyrv32_mcp/README.md](pyrv32_mcp/README.md) - MCP server usage

## Building Programs

Cross-compile with the RISC-V toolchain:

```bash
riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 \
    -Tfirmware/link.ld -o program.elf \
    firmware/crt0.S firmware/syscalls.c your_program.c -lc -lgcc
```

## License

MIT License. NetHack has its own license (see nethack-3.4.3/dat/license).
