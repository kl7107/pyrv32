#!/usr/bin/env python3
"""Generate oracles file using makedefs -h with clean workflow."""

from nethack_util_runner import run_makedefs

if __name__ == "__main__":
    run_makedefs(
        name="oracles",
        input_files="oracles.txt",
        output_file="oracles",
        flag="-h"
    )
