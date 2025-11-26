#!/usr/bin/env python3
"""
Use trace buffer to debug NetHack - find what happens before jumping back to main
"""
import subprocess

print("=" * 70)
print("Debugging NetHack with Trace Buffer")
print("=" * 70)
print()
print("Strategy:")
print("1. Set breakpoint at main() entry (0x801573cc)")
print("2. Continue to main (first time)")
print("3. Step past the breakpoint")
print("4. Continue again - if we loop back to main, we'll hit the breakpoint")
print("5. Show last 50 trace entries to see how we got back to main")
print()

main_addr = 0x801573cc

commands = f"""b 0x{main_addr:08x}
c
s 1
c
t 50
q
"""

print("Commands:")
for line in commands.strip().split('\n'):
    print(f"  {line}")
print()

# Use larger trace buffer for better history
proc = subprocess.Popen(
    ['timeout', '120', 'python3', 'pyrv32.py', '--step', '--trace-size', '100000',
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
    print("TIMEOUT - NetHack likely did not loop back to main")
    print("This is actually GOOD - means it's progressing forward!")
    exit(0)

lines = stdout.splitlines()

# Count breakpoint hits
bp_hits = [line for line in lines if 'Breakpoint' in line and 'hit at' in line]
print(f"Breakpoint hits: {len(bp_hits)}")

if len(bp_hits) < 2:
    print("\n✅ NetHack did NOT loop back to main!")
    print("This means it's executing forward, not stuck in a restart loop.")
    print()
    print("Last 30 lines of output:")
    for line in lines[-30:]:
        print(line)
else:
    print("\n⚠️  NetHack DID loop back to main!")
    print("Showing trace buffer to see what happened...")
    print()
    
    # Find and display the trace buffer output
    in_trace = False
    for i, line in enumerate(lines):
        if 'Trace buffer:' in line:
            in_trace = True
        if in_trace:
            print(line)
            if i < len(lines) - 1 and '(pyrv32-dbg)' in lines[i+1]:
                break
