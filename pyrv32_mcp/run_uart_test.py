#!/usr/bin/env python3
import subprocess
import sys

result = subprocess.run([
    sys.executable,
    '/home/dev/git/zesarux/pyrv32/pyrv32_mcp/quick_interpreter_test.py'
])

sys.exit(result.returncode)
