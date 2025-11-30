#!/usr/bin/env python3
"""Generate quest.dat file using makedefs -q with clean workflow."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nethack_util_runner import run_makedefs

if __name__ == "__main__":
    run_makedefs(
        name="quest.dat",
        input_files="quest.txt",
        output_file="quest.dat",
        flag="-q",
        max_steps=50_000_000  # quest.txt is large (99KB)
    )
