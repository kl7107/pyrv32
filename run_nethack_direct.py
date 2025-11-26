#!/usr/bin/env python3
"""Run NetHack directly and capture any output"""
import subprocess
import time

print("Running NetHack directly (10 second timeout)...")
print("Looking for console output...\n")

proc = subprocess.Popen(
    ['timeout', '10', 'python3', 'pyrv32.py', '--no-test', 'firmware/nethack.bin'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

try:
    stdout, _ = proc.communicate(timeout=15)
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, _ = proc.communicate()

print("=" * 70)
print("NetHack Output:")
print("=" * 70)
print(stdout)
print("=" * 70)

# Check for specific patterns
if "Shall I pick a character" in stdout:
    print("\n✅ SUCCESS! NetHack reached character selection!")
elif "Welcome to NetHack" in stdout:
    print("\n✅ SUCCESS! NetHack started!")
elif any(c in stdout for c in ["@", "#", ".", "|", "-"]):  # Dungeon characters
    print("\n✅ SUCCESS! NetHack is displaying dungeon!")
elif len(stdout) > 500:
    print(f"\n✅ Got substantial output ({len(stdout)} bytes)")
else:
    print(f"\n⚠️  Limited output ({len(stdout)} bytes)")
