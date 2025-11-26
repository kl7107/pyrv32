#!/bin/bash
# Build script for RV32IM firmware

set -e  # Exit on error

# Toolchain prefix (adjust if your toolchain has a different prefix)
PREFIX=riscv64-unknown-elf
# Alternative common prefixes:
# PREFIX=riscv32-unknown-elf
# PREFIX=riscv-none-elf

CC=${PREFIX}-gcc
OBJCOPY=${PREFIX}-objcopy
OBJDUMP=${PREFIX}-objdump
SIZE=${PREFIX}-size

# Compiler flags
CFLAGS="-march=rv32im -mabi=ilp32 -O2 -g -Wall -Wextra"
CFLAGS="$CFLAGS -nostdlib -nostartfiles -ffreestanding"
CFLAGS="$CFLAGS -fno-builtin -fno-stack-protector"

# Linker flags
LDFLAGS="-T link.ld -nostdlib -nostartfiles"
LDFLAGS="$LDFLAGS -Wl,--gc-sections"  # Remove unused sections

# Source files
SOURCES="crt0.S runtime.c hello.c"

# Output files
ELF_OUT="hello.elf"
BIN_OUT="hello.bin"
LST_OUT="hello.lst"

echo "=== Building RV32IM Hello World ==="
echo "Toolchain: $PREFIX"
echo "Sources: $SOURCES"
echo ""

# Compile and link
echo "Compiling..."
$CC $CFLAGS $LDFLAGS $SOURCES -o $ELF_OUT

# Show size
echo ""
echo "Size information:"
$SIZE $ELF_OUT

# Generate binary
echo ""
echo "Generating binary..."
$OBJCOPY -O binary $ELF_OUT $BIN_OUT

# Generate disassembly
echo "Generating disassembly..."
$OBJDUMP -d -S $ELF_OUT > $LST_OUT

# Show binary size
BIN_SIZE=$(stat -f%z "$BIN_OUT" 2>/dev/null || stat -c%s "$BIN_OUT" 2>/dev/null)
echo ""
echo "✓ Build complete!"
echo "  ELF:    $ELF_OUT"
echo "  Binary: $BIN_OUT ($BIN_SIZE bytes)"
echo "  Listing: $LST_OUT"
echo ""
echo "Run with: ../pyrv32.py $BIN_OUT"
