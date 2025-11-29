#!/bin/bash
#
# Build NetHack for PyRV32
# Uses the top-level Makefile.top structure
#

set -e  # Exit on error

NETHACK_ROOT="/home/dev/git/zesarux/pyrv32/nethack-3.4.3"
cd "$NETHACK_ROOT"

# Use the top-level makefile (delegates to util, sys/pyrv32, and src)
make -f sys/pyrv32/Makefile.top "$@"
