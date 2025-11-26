#!/usr/bin/env python3
"""Test register tracing with NetHack"""
import subprocess
import os

print("Testing register tracing with NetHack...")
print("Setting breakpoint at main (0x801573cc)")
print("Then stepping through with register tracing\n")

# Create test output file
trace_file = "/home/dev/git/zesarux/pyrv32/nethack_regtrace.log"

# Remove old trace file if it exists
if os.path.exists(trace_file):
    os.remove(trace_file)
    print(f"Removed old trace file: {trace_file}")

commands = """b 0x801573cc
c
s 100
q
"""

print("Commands to send:")
print(commands)

proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', '--reg-trace', '1', '--reg-file', trace_file,
     '--reg-nonzero', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

stdout, _ = proc.communicate(input=commands, timeout=30)

print("\nDebugger output (last 50 lines):")
lines = stdout.splitlines()
for line in lines[-50:]:
    print(line)

# Show trace file
print(f"\n\nRegister trace file: {trace_file}")
if os.path.exists(trace_file):
    with open(trace_file) as f:
        trace_lines = f.readlines()
    print(f"Trace file has {len(trace_lines)} lines")
    print("\nFirst 20 lines:")
    for line in trace_lines[:20]:
        print(line.rstrip())
    print("\nLast 20 lines:")
    for line in trace_lines[-20:]:
        print(line.rstrip())
else:
    print("ERROR: Trace file not created!")
