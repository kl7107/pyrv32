#!/usr/bin/env python3
"""Test trace buffer functionality with NetHack"""
import subprocess

print("=" * 70)
print("Testing Trace Buffer with NetHack")
print("=" * 70)
print()
print("This test will:")
print("1. Set breakpoint at main() (0x801573cc)")
print("2. Continue to main")
print("3. Show last 10 trace entries (the instructions before main)")
print("4. Step 20 instructions into main")
print("5. Set breakpoint at main again")
print("6. Continue (to see if we loop back to main)")
print("7. If we hit main again, show trace to see how we got there")
print()

commands = """b 0x801573cc
c
t 10
s 20
b 0x801573cc
c
t 20
q
"""

print("Commands to send:")
for line in commands.strip().split('\n'):
    print(f"  {line}")
print()

proc = subprocess.Popen(
    ['timeout', '120', 'python3', 'pyrv32.py', '--step', '--trace-size', '1000',
     'firmware/nethack.bin'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/home/dev/git/zesarux/pyrv32'
)

try:
    stdout, _ = proc.communicate(input=commands, timeout=125)
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, _ = proc.communicate()
    print("TIMEOUT!")

# Show output
lines = stdout.splitlines()

# Find and show the trace dumps
print("=" * 70)
print("Output:")
print("=" * 70)

in_trace = False
trace_lines = []

for line in lines:
    # Detect trace buffer output
    if 'Trace buffer:' in line or in_trace:
        in_trace = True
        trace_lines.append(line)
        # End of trace when we see the prompt or breakpoint message
        if '(pyrv32-dbg)' in line or 'Breakpoint' in line:
            # Print this trace section
            for tline in trace_lines:
                print(tline)
            print()
            trace_lines = []
            in_trace = False
    
    # Also show important messages
    if any(keyword in line for keyword in ['Breakpoint', 'Step complete', 'Loading', 'Starting']):
        print(line)

print("\n" + "=" * 70)
print("Summary:")
print("=" * 70)

# Count how many times we hit breakpoints
bp_hits = [line for line in lines if 'Breakpoint' in line and 'hit at' in line]
print(f"Breakpoint hits: {len(bp_hits)}")
for hit in bp_hits:
    print(f"  {hit}")

# Check if trace buffer was shown
trace_shown = any('Trace buffer:' in line for line in lines)
if trace_shown:
    print("\n✅ Trace buffer was successfully displayed!")
else:
    print("\n❌ Trace buffer was NOT displayed")
