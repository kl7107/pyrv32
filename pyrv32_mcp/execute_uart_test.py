#!/usr/bin/env python3
import sys
import os

# Change to the test directory
os.chdir('/home/dev/git/zesarux/pyrv32')
sys.path.insert(0, '.')

# Import after path is set
exec(open('/home/dev/git/zesarux/pyrv32/pyrv32_mcp/direct_uart_test.py').read())
