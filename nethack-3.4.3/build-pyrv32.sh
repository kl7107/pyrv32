#!/bin/bash
#
# Build NetHack for PyRV32
#

set -e  # Exit on error

NETHACK_ROOT="/home/dev/git/zesarux/pyrv32/nethack-3.4.3"
cd "$NETHACK_ROOT"

echo "=== NetHack 3.4.3 for PyRV32 Build Script ==="
echo ""

# Step 1: Build host utilities and generate files
echo "[1/3] Building host utilities and generating files..."
make -C util generated-files

# Step 2: Cross-compile game
echo "[2/3] Cross-compiling NetHack..."
make -C src -f Makefile.pyrv32

# Step 3: Copy to firmware directory
echo "[3/3] Installing binary..."
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
