#!/usr/bin/env python3
"""Rebuild NetHack and test with environ support"""
import subprocess
import os

print("=" * 70)
print("Rebuilding NetHack with environ support...")
print("=" * 70)

# Rebuild
result = subprocess.run(
    ['bash', '-c', 'cd nethack-3.4.3 && timeout 120 ./build-pyrv32.sh'],
    capture_output=True,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

# Show last part of build output
lines = result.stdout.splitlines()
print("\nBuild output (last 30 lines):")
for line in lines[-30:]:
    print(line)

if result.returncode != 0:
    print("\n\nBuild FAILED!")
    print("Error output:")
    print(result.stderr)
    exit(1)

# Check if binary was created
nethack_bin = '/home/dev/git/zesarux/pyrv32/firmware/nethack.bin'
if os.path.exists(nethack_bin):
    size = os.path.getsize(nethack_bin)
    print(f"\n✅ Build SUCCESS! Binary size: {size:,} bytes")
else:
    print("\n❌ Build FAILED! Binary not created")
    exit(1)

print("\n" + "=" * 70)
print("Testing NetHack (will run for 5 seconds)...")
print("=" * 70)

# Run NetHack without debugger, just PC trace
proc = subprocess.Popen(
    ['timeout', '5', 'python3', 'pyrv32.py', '--pc-trace', '100000', 'firmware/nethack.bin'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

try:
    stdout, _ = proc.communicate(timeout=10)
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, _ = proc.communicate()

print("\nNetHack output:")
print(stdout)

# Check if we got past getenv
if 'getenv' in stdout.lower() or any('0x801605' in line for line in stdout.splitlines()):
    print("\n⚠️  Still appears to be stuck around getenv area")
else:
    print("\n✅ Appears to have progressed past getenv!")
