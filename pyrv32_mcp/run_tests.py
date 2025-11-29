#!/usr/bin/env python3
"""Run compilation and tests."""

import subprocess
import sys

print("="*60)
print("Step 1: Compiling interpreter_test.c")
print("="*60)

result = subprocess.run([sys.executable, 'compile_interpreter.py'], cwd='/home/dev/git/zesarux/pyrv32/pyrv32_mcp')
if result.returncode != 0:
    print("Compilation failed!")
    sys.exit(1)

print("\n" + "="*60)
print("Step 2: Running comprehensive UART tests")
print("="*60)

result = subprocess.run([sys.executable, 'test_uart_comprehensive.py'], cwd='/home/dev/git/zesarux/pyrv32/pyrv32_mcp')
sys.exit(result.returncode)
