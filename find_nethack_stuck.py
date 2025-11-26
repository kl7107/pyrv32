#!/usr/bin/env python3
"""Find where NetHack gets stuck using continuous execution with PC sampling"""
import subprocess
import collections
import time

print("Finding where NetHack gets stuck...")
print("Running continuously with PC tracing (will timeout after 10 seconds)\n")

# Run NetHack continuously with PC tracing
proc = subprocess.Popen(
    ['timeout', '10', 'python3', 'pyrv32.py', '--pc-trace', '50000', 'firmware/nethack.bin'],
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

# Extract PC values
pc_values = []
step_numbers = []
for line in stdout.splitlines():
    if '] PC=0x' in line:
        try:
            # Format: [  123456] PC=0x80001234
            parts = line.split(']')
            step = int(parts[0].strip()[1:])
            pc_str = parts[1].split('PC=0x')[1].strip()
            pc = int(pc_str, 16)
            pc_values.append(pc)
            step_numbers.append(step)
        except:
            pass

if not pc_values:
    print("ERROR: No PC values captured!")
    print("\nOutput:")
    print(stdout)
    exit(1)

print(f"Captured {len(pc_values)} PC samples")
print(f"Instruction range: {step_numbers[0]:,} to {step_numbers[-1]:,}")
print(f"Total instructions: {step_numbers[-1] - step_numbers[0]:,}\n")

# Group by regions
bss_clear = [pc for pc in pc_values if 0x80000000 <= pc < 0x80000100]
libc = [pc for pc in pc_values if 0x80000100 <= pc < 0x80100000]
nethack_main = [pc for pc in pc_values if 0x80100000 <= pc < 0x80180000]
late_code = [pc for pc in pc_values if 0x80180000 <= pc < 0x801a0000]

print(f"PC distribution by region:")
print(f"  BSS clear (0x80000000-0x80000100): {len(bss_clear)} samples")
print(f"  libc/runtime (0x80000100-0x80100000): {len(libc)} samples")
print(f"  NetHack main (0x80100000-0x80180000): {len(nethack_main)} samples")
print(f"  Late code (0x80180000-0x801a0000): {len(late_code)} samples")

# Find the most common PC in the last samples (where it's stuck)
print(f"\n\nWhere NetHack is stuck (last 50% of samples):")
last_half = pc_values[len(pc_values)//2:]
pc_counts = collections.Counter(last_half)

print(f"{'Address':>12s}  {'Count':>8s}  {'%':>6s}")
print("-" * 35)
total = len(last_half)
for pc, count in pc_counts.most_common(20):
    pct = (count / total * 100) if total > 0 else 0
    print(f"  0x{pc:08x}    {count:6d}   {pct:5.1f}%")

# Find where we transition from startup to main loop
print(f"\n\nTransition points:")
for i in range(min(20, len(pc_values)-1)):
    if pc_values[i] < 0x80100000 and pc_values[i+1] >= 0x80100000:
        print(f"  Step {step_numbers[i]:,}: Left startup area")
        print(f"    From: 0x{pc_values[i]:08x}")
        print(f"    To:   0x{pc_values[i+1]:08x}")

# Look at last 20 samples
print(f"\n\nLast 20 PC samples:")
for i in range(max(0, len(pc_values)-20), len(pc_values)):
    print(f"  [{step_numbers[i]:8d}] PC=0x{pc_values[i]:08x}")

print("\n\nDone!")
