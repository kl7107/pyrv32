#!/usr/bin/env python3
"""
Find the exact instruction that caused us to jump back to _start/clear_bss
"""
import subprocess

print("Searching for the transition point where we jump back to clear_bss...")
print()

proc = subprocess.Popen(
    ['python3', 'pyrv32.py', '--step', '--trace-size', '200000', 'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

# Get to second main() call and dump full trace
commands = """b 0x801573cc
c
s 1
c
t all
q
"""

stdout, _ = proc.communicate(input=commands, timeout=120)

# Parse trace to find when we jump TO clear_bss (0x80000020) or _start (0x80000000)
# We want to find the LAST time before the final main() call

lines = stdout.splitlines()

# Extract all trace entries
trace_entries = []
current_entry = None

for line in lines:
    # Detect start of trace entry: [  12345] PC=0x...
    if line.strip().startswith('[') and '] PC=0x' in line:
        if current_entry:
            trace_entries.append(current_entry)
        # Parse: [  12345] PC=0xDEADBEEF  insn=0x12345678
        parts = line.split(']', 1)
        step_str = parts[0].strip()[1:].strip()
        rest = parts[1].strip()
        pc_str = rest.split('PC=0x')[1].split()[0]
        
        current_entry = {
            'step': int(step_str),
            'pc': int(pc_str, 16),
            'raw': line
        }

if current_entry:
    trace_entries.append(current_entry)

print(f"Parsed {len(trace_entries)} trace entries")

# Find transitions to clear_bss or _start
print("\nLooking for jumps to _start (0x80000000) or clear_bss (0x80000020)...")

restart_points = []
for i in range(1, len(trace_entries)):
    prev_entry = trace_entries[i-1]
    curr_entry = trace_entries[i]
    
    # Check if we jumped to _start or clear_bss
    if curr_entry['pc'] == 0x80000000 or curr_entry['pc'] == 0x80000020:
        # Make sure previous PC was NOT in the startup area
        if prev_entry['pc'] >= 0x80000100:  # Outside crt0
            restart_points.append({
                'from_step': prev_entry['step'],
                'from_pc': prev_entry['pc'],
                'to_step': curr_entry['step'],
                'to_pc': curr_entry['pc']
            })

print(f"\nFound {len(restart_points)} restart transitions:")
for rp in restart_points:
    print(f"\n  Step {rp['from_step']:6d}: 0x{rp['from_pc']:08x}")
    print(f"    → Step {rp['to_step']:6d}: 0x{rp['to_pc']:08x}")
    
    # Show some context from the original output
    print(f"\n  Looking for these PCs in trace output...")

if restart_points:
    # Show details of the LAST restart (the one before second main)
    last_restart = restart_points[-1]
    print(f"\n\n{'='*70}")
    print(f"LAST RESTART (before second main() call):")
    print(f"{'='*70}")
    print(f"From step {last_restart['from_step']}: PC=0x{last_restart['from_pc']:08x}")
    print(f"To step {last_restart['to_step']}: PC=0x{last_restart['to_pc']:08x}")
    
    # Find this in the original trace output and show context
    print(f"\nSearching trace output for context around step {last_restart['from_step']}...")
    in_context = False
    context_lines = []
    for line in lines:
        if f"[{last_restart['from_step']:7d}]" in line or in_context:
            context_lines.append(line)
            in_context = True
            if len(context_lines) > 20:  # Show 20 lines of context
                break
    
    if context_lines:
        print("\nContext:")
        for line in context_lines[:15]:
            print(line)
else:
    print("\nNo restart transitions found - NetHack may not be looping after all!")
