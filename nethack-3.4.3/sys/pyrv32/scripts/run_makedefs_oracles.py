#!/usr/bin/env python3
"""Generate oracles file using makedefs -h with clean workflow."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nethack_util_runner import run_makedefs

if __name__ == "__main__":
    run_makedefs(
        name="oracles",
        input_files="oracles.txt",
        output_file="oracles",
        flag="-h"
    )
