#!/usr/bin/env python3
"""
DEMONSTRATION: How to find when s4 becomes 0x80000000

This shows the complete workflow using the new conditional breakpoint feature.
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  Finding When s4 Becomes 0x80000000 - Complete Workflow              ║
╚══════════════════════════════════════════════════════════════════════╝

STEP 1: Start NetHack in step mode
────────────────────────────────────────────────────────────────────────
Run:
  python3 pyrv32.py --trace-size 200000 --step nethack-3.4.3/src/nethack.bin

You will see:
  0x80000000: LUI        (0x80800137)
  PC=0x80000000  ra=0x00000000 sp=0x00000000 ...
  (pyrv32-dbg) 

Notice: 
  ✓ NO instructions executed yet (step mode starts BEFORE first instruction)
  ✓ All registers are 0, including s4=0x00000000
  ✓ PC is at _start (0x80000000)


STEP 2: Set conditional breakpoint for s4
────────────────────────────────────────────────────────────────────────
At the (pyrv32-dbg) prompt, type:

  bcond s4 0x80000000

You will see:
  Breakpoint 1 set when s4=0x80000000


STEP 3: Continue execution
────────────────────────────────────────────────────────────────────────
Type:

  c

The program will run at full speed until s4 becomes 0x80000000!


STEP 4: When breakpoint hits
────────────────────────────────────────────────────────────────────────
You will see something like:

  Breakpoint 1 hit: s4=0x80000000
  0x8xxxxxxx: ADDI       (0xXXXXXXXX)
  PC=0x8xxxxxxx  ra=0x... sp=0x... s4=0x80000000 ...
  (pyrv32-dbg)

This shows:
  • The EXACT PC where s4 was set to 0x80000000
  • The instruction that did it
  • All register values at that moment


STEP 5: Examine the context
────────────────────────────────────────────────────────────────────────
Type these commands to understand what happened:

  x             Show current instruction disassembly
  r             Show all registers
  t 10          Show last 10 trace entries (leading up to this point)
  t info        Show trace buffer statistics


EXAMPLE: Other Conditional Breakpoints
────────────────────────────────────────────────────────────────────────
You can set conditional breakpoints for any register:

  bcond a0 0x1234           Break when a0 equals 0x1234
  bcond sp 0x807ffff0       Break when stack pointer set
  bcond ra 0                Break when return address is 0
  b 0x80001000 s4 0x80000000  Break at address only if s4=0x80000000


SEARCH COMMANDS (for trace buffer analysis)
────────────────────────────────────────────────────────────────────────
  tsr s4 0x80000000         Search backwards for when s4 WAS 0x80000000
  tsrneq s4 0x80000000      Search backwards for when s4 was NOT 0x80000000


WHY THIS IS POWERFUL
────────────────────────────────────────────────────────────────────────
Old way:
  - Set breakpoint at specific address
  - Step through code manually
  - Check registers after each step
  - Takes forever!

New way:
  - Set bcond for register value
  - Run at full speed
  - Stops INSTANTLY when condition met
  - See exact instruction that caused it

With 200K trace buffer, you have complete history of what led to the bug!


READY TO TRY IT?
────────────────────────────────────────────────────────────────────────
Run this script:
  python3 simple_step.py

Then type:
  bcond s4 0x80000000
  c

Watch it find the bug automatically!

╚══════════════════════════════════════════════════════════════════════╝
""")
