#!/usr/bin/env python3
"""
Simple interactive version - just start in step mode
"""

import subprocess

subprocess.run([
    'python3', 'pyrv32.py',
    '--trace-size', '200000',
    '--step',
    'nethack-3.4.3/src/nethack.bin'
])
