#!/usr/bin/env python3
import subprocess
import sys
result = subprocess.run([sys.executable, 'run_all_uart_tests.py'], cwd='/home/dev/git/zesarux/pyrv32/pyrv32_mcp')
sys.exit(result.returncode)
