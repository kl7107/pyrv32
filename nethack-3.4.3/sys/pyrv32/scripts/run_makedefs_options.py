#!/usr/bin/env python3
"""Generate options file using makedefs -v with clean workflow."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nethack_util_runner import UtilityRunner

if __name__ == "__main__":
    # options has no input files - it's generated from compile-time config
    runner = UtilityRunner(
        name="options",
        input_files=[],  # No input files needed
        output_file="options",
        utility_flag="-v",
        binary_path="nethack-3.4.3/util/makedefs.bin",
        elf_path="nethack-3.4.3/util/makedefs.elf",
        max_steps=10_000_000
    )
    runner.run()
