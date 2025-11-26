#!/usr/bin/env python3
"""Analyze NetHack execution to find hot spots and loops"""
import subprocess
import collections

print("Analyzing NetHack execution patterns...")
print("Running with PC tracing to find loops...\n")

# Run NetHack for a limited time with PC tracing
commands = """b 0x801573cc
c
s 10000
q
"""

proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', '--pc-trace', '100', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

stdout, _ = proc.communicate(input=commands, timeout=60)

# Extract PC values from trace
pc_values = []
for line in stdout.splitlines():
    if '] PC=0x' in line:
        try:
            pc_str = line.split('PC=0x')[1].split()[0]
            pc = int(pc_str, 16)
            pc_values.append(pc)
        except:
            pass

print(f"Captured {len(pc_values)} PC trace samples")

# Analyze PC distribution
pc_counts = collections.Counter(pc_values)
print(f"\nTop 30 most executed addresses:")
print(f"{'Address':>12s}  {'Count':>8s}  {'%':>6s}  {'Function Area':s}")
print("-" * 70)

total = len(pc_values)
for pc, count in pc_counts.most_common(30):
    pct = (count / total * 100) if total > 0 else 0
    
    # Try to identify function area
    if pc < 0x80000100:
        area = "startup/crt0"
    elif 0x80000100 <= pc < 0x80010000:
        area = "low code"
    elif 0x80010000 <= pc < 0x80100000:
        area = "libc/runtime"
    elif 0x80100000 <= pc < 0x80160000:
        area = "nethack code"
    elif 0x80160000 <= pc < 0x801a0000:
        area = "nethack late"
    else:
        area = "data/bss area"
    
    print(f"  0x{pc:08x}    {count:6d}   {pct:5.1f}%  {area}")

# Look for tight loops (consecutive same PC)
print(f"\n\nLooking for tight loops...")
i = 0
while i < len(pc_values) - 10:
    pc = pc_values[i]
    # Count how many consecutive times we see this PC
    count = 1
    while i + count < len(pc_values) and pc_values[i + count] == pc:
        count += 1
    
    if count >= 10:  # If we see same PC 10+ times in a row
        print(f"  Loop at 0x{pc:08x}: {count} consecutive occurrences at sample {i}")
        i += count
    else:
        i += 1

# Look for short loops (cycling between 2-4 addresses)
print(f"\n\nLooking for short loops (cycling patterns)...")
i = 0
while i < len(pc_values) - 20:
    # Check if we have a repeating pattern
    window = pc_values[i:i+8]
    if len(set(window)) <= 4:  # Only 4 or fewer distinct PCs
        # Check if this pattern repeats
        pattern_len = 2
        while pattern_len <= 4:
            pattern = window[:pattern_len]
            matches = 0
            for j in range(0, min(20, len(pc_values) - i), pattern_len):
                if pc_values[i+j:i+j+pattern_len] == pattern:
                    matches += 1
                else:
                    break
            
            if matches >= 5:  # Pattern repeats 5+ times
                print(f"  Cycle at sample {i}: {['0x%08x' % p for p in pattern]} repeats {matches} times")
                i += matches * pattern_len
                break
            pattern_len += 1
        else:
            i += 1
    else:
        i += 1

print("\n\nAnalysis complete!")
