#!/usr/bin/env python3
"""Simple test of trace buffer with hello.c"""
import subprocess

print("Testing trace buffer with hello.bin (simpler program)...")

commands = """s 5
t 5
s 5
t 10
q
"""

print("Commands:")
print(commands)

proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', '--trace-size', '50', 'firmware/hello.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

stdout, _ = proc.communicate(input=commands, timeout=10)

print("\nFull output:")
print(stdout)
