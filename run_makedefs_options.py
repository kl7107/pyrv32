#!/usr/bin/env python3
"""Generate options file using makedefs -v with clean workflow."""

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
