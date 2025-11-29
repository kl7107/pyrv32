#!/bin/sh
# NetHack PyRV32 setup - Create symlinks for makefiles
# Based on sys/unix/setup.sh

# Were we started from the top level? Cope.
if [ -f sys/pyrv32/Makefile.top ]; then cd sys/pyrv32; fi

echo "Setting up NetHack 3.4.3 for PyRV32..."
echo ""
echo "Creating symlinks:"
echo "  Makefile -> sys/pyrv32/Makefile.top"
echo "  src/Makefile -> sys/pyrv32/Makefile.src"
echo "  util/Makefile -> sys/pyrv32/Makefile.utl"
echo ""

cd ../..

# Remove any existing makefiles
rm -f Makefile src/Makefile util/Makefile

# Create symlinks
ln -s sys/pyrv32/Makefile.top Makefile
ln -s ../sys/pyrv32/Makefile.src src/Makefile
ln -s ../sys/pyrv32/Makefile.utl util/Makefile

echo "Done! You can now:"
echo "  1. Run 'make' from the top-level directory to build"
echo "  2. Binary will be at: src/nethack.bin"
echo "  3. Run 'make clean' or 'make spotless' to clean"
echo ""
echo "Note: Runtime objects (crt0.o, syscalls.o) must exist in ../firmware/"
