#!/bin/bash
#
# Build NetHack for PyRV32
#

set -e  # Exit on error

NETHACK_ROOT="/home/dev/git/zesarux/pyrv32/nethack-3.4.3"
cd "$NETHACK_ROOT"

echo "=== NetHack 3.4.3 for PyRV32 Build Script ==="
echo ""

# Step 1: Build host utilities
echo "[1/5] Building host utilities..."
cd util
if [ ! -f makedefs ]; then
    echo "  Building makedefs..."
    cd ../src
    gcc -O2 -I../include -c monst.c objects.c
    cd ../util
    gcc -O2 -I../include -o makedefs makedefs.c ../src/monst.o ../src/objects.o
fi
echo "  makedefs: OK"
cd "$NETHACK_ROOT"

# Step 2: Generate headers and source files
echo "[2/5] Generating headers and source files..."
cd include
if [ ! -f pm.h ]; then
    echo "  Generating pm.h..."
    ../util/makedefs -p
fi
if [ ! -f onames.h ]; then
    echo "  Generating onames.h..."
    ../util/makedefs -o
fi
if [ ! -f date.h ]; then
    echo "  Generating date.h..."
    ../util/makedefs -v
fi
cd ../src
if [ ! -f monstr.c ]; then
    echo "  Generating monstr.c..."
    ../util/makedefs -m
fi
if [ ! -f vis_tab.c ]; then
    echo "  Generating vis_tab.c..."
    ../util/makedefs -z
fi
cd "$NETHACK_ROOT"
echo "  Generated files: OK"

# Step 3: Build runtime objects
# Note: crt0.S, syscalls.c, and link.ld are symlinks to master versions in ../../../firmware/
echo "[3/5] Building runtime objects..."
cd sys/pyrv32

# Follow symlinks to check actual source file timestamps (not symlink timestamps)
CRT0_SRC=$(readlink -f crt0.S)
SYSCALLS_SRC=$(readlink -f syscalls.c)

# Always rebuild if source is newer than object (or object doesn't exist)
if [ ! -f ../../crt0.o ] || [ "$CRT0_SRC" -nt ../../crt0.o ]; then
    echo "  Building crt0.o (from master firmware/crt0.S)..."
    riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 -c -o ../../crt0.o crt0.S
fi

if [ ! -f ../../syscalls.o ] || [ "$SYSCALLS_SRC" -nt ../../syscalls.o ]; then
    echo "  Building syscalls.o (from master firmware/syscalls.c)..."
    riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 -O2 -g \
        -isystem /usr/lib/picolibc/riscv64-unknown-elf/include \
        -I../../include -I. -c -o ../../syscalls.o syscalls.c
fi
cd "$NETHACK_ROOT"
echo "  Runtime objects: OK"

# Step 4: Cross-compile game
echo "[4/5] Cross-compiling NetHack..."
cd src
make -f Makefile.pyrv32 clean
make -f Makefile.pyrv32
cd "$NETHACK_ROOT"
echo "  NetHack binary: OK"

# Step 5: Copy to firmware directory
echo "[5/5] Installing binary..."
if [ -f src/nethack.bin ]; then
    cp src/nethack.bin ../firmware/
    echo "  Installed to ../firmware/nethack.bin"
    SIZE=$(ls -lh src/nethack.bin | awk '{print $5}')
    echo "  Binary size: $SIZE"
else
    echo "  ERROR: nethack.bin not found!"
    exit 1
fi

echo ""
echo "=== Build Complete! ==="
echo ""
echo "To run:"
echo "  cd /home/dev/git/zesarux/pyrv32"
echo "  python3 pyrv32.py firmware/nethack.bin"
echo ""
