#!/usr/bin/env python3
"""
Find what happens between the two main() calls using trace buffer
"""
import subprocess
import sys

print("Finding the gap between first main() call and second main() call...")
print()

# Run with very large trace buffer
proc = subprocess.Popen(
    ['timeout', '60', 'python3', 'pyrv32.py', '--step', '--trace-size', '200000',
     'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

# Just continue to see if it hits any issues
commands = """b 0x801573cc
c
s 1
c
q
"""

try:
    stdout, _ = proc.communicate(input=commands, timeout=65)
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, _ = proc.communicate()
    print("Timeout - NetHack never returned to main")
    sys.exit(0)

# Parse the output to analyze the trace
lines = stdout.splitlines()

# Find if we hit main twice
bp_hits = [line for line in lines if 'Breakpoint' in line and 'hit at 0x801573cc' in line]
print(f"Number of times we hit main: {len(bp_hits)}")

if len(bp_hits) >= 2:
    print("\n✅ Confirmed: NetHack loops back to main!")
    print("\nNow let's analyze the execution trace...")
    
    # Extract instruction count from statistics
    for line in lines:
        if 'Instructions executed:' in line:
            print(f"\n{line}")
            parts = line.split(':')
            if len(parts) >= 2:
                count_str = parts[1].strip().split()[0].replace(',', '')
                total_insns = int(count_str)
                print(f"Total instructions: {total_insns:,}")
                
                # We know first main is around step 78K
                # Second main should be near the end
                # So the "return and restart" happens somewhere between
                print(f"\nFirst main() call: ~step 78,000")
                print(f"Second main() call: ~step {total_insns}")
                print(f"Gap: ~{total_insns - 78000:,} instructions")
else:
    print("\nNetHack did not loop back to main within timeout")
