#!/usr/bin/env python3
"""Generate data file using makedefs -d with clean workflow."""

from nethack_util_runner import run_makedefs

if __name__ == "__main__":
    run_makedefs(
        name="data",
        input_files="data.base",
        output_file="data",
        flag="-d",
        max_steps=100_000_000  # data takes longer
    )
