#!/bin/bash
#
# Build script for C filesystem tests
#

set -e

CC=riscv64-unknown-elf-gcc
CFLAGS="-march=rv32im -mabi=ilp32 -O2 -g -Wall"
CFLAGS="$CFLAGS -isystem /usr/lib/picolibc/riscv64-unknown-elf/include"
CFLAGS="$CFLAGS -I../../firmware/include"
LDFLAGS="-march=rv32im -mabi=ilp32 -T../../firmware/link.ld"
LDFLAGS="$LDFLAGS -L/usr/lib/picolibc/riscv64-unknown-elf/lib/rv32im/ilp32"
LDFLAGS="$LDFLAGS -Wl,--gc-sections -nostartfiles -nodefaultlibs"

CRT0="../../firmware/crt0.o"
SYSCALLS="../../firmware/syscalls.o"
LIBS="-lc -lgcc"

echo "=== Building C Filesystem Tests ==="
echo

# Ensure firmware objects are built
if [ ! -f "$CRT0" ] || [ ! -f "$SYSCALLS" ]; then
    echo "Building firmware objects..."
    (cd ../../firmware && make)
fi

# Build each test
for src in test_*.c; do
    if [ ! -f "$src" ]; then
        echo "No test files found"
        exit 0
    fi
    
    base=$(basename "$src" .c)
    elf="${base}.elf"
    bin="${base}.bin"
    
    echo "Building $base..."
    
    # Compile
    $CC $CFLAGS -c "$src" -o "${base}.o"
    
    # Link
    $CC $LDFLAGS -o "$elf" "$CRT0" "$SYSCALLS" "${base}.o" $LIBS
    
    # Extract binary
    riscv64-unknown-elf-objcopy -O binary "$elf" "$bin"
    
    echo "  Created $bin"
done

echo
echo "=== Build Complete ==="
echo "Run tests with: ../../run_c_tests.py"
