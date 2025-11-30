#!/usr/bin/env python3
"""Generate rumors file using makedefs -r with clean workflow."""

from nethack_util_runner import run_makedefs

if __name__ == "__main__":
    run_makedefs(
        name="rumors",
        input_files=["rumors.tru", "rumors.fal"],
        output_file="rumors",
        flag="-r"
    )
