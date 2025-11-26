#!/usr/bin/env python3
"""
Summary of TSR (Trace Search Reverse) Implementation

The tsr command has been successfully implemented with the following features:

1. COMMAND SYNTAX
   tsr <regname> <value> [<start_index>]
   
   - regname: Register name (a0-a7, s0-s11, t0-t6, ra, sp, pc, etc.)
   - value: Value to search for (supports hex with 0x prefix or decimal)
   - start_index: Optional - search backwards from this index (default: from end)

2. MONOTONIC INDEX COUNTER
   - Each trace entry gets a unique monotonic index starting at 0
   - Index increments with each instruction executed
   - Preserved even when old entries drop from ring buffer
   - Only resets on 't clear' command

3. SEARCH BEHAVIOR
   - Searches backwards through trace buffer (most recent to oldest)
   - If start_index specified, searches from that index backwards
   - Returns first matching entry found
   - Shows complete trace entry with all registers when found

4. IMPLEMENTATION DETAILS
   - TraceEntry.index added to store monotonic counter
   - TraceBuffer.total_count tracks monotonic index
   - TraceBuffer.search_reverse() performs the backward search
   - Debugger.search_trace_reverse() provides user-friendly interface
   - CLI handler in pyrv32.py processes tsr commands

5. USE CASES
   - Find when a register was set to a specific value
   - Locate where corruption occurred (e.g., s4 = 0x80000000)
   - Trace backwards from a crash point
   - Understand register value evolution
   - Debug initialization sequences

6. TEST RESULTS
   ✓ Successfully finds PC=0x80000000 at index 0
   ✓ Displays complete trace entry with all registers
   ✓ Handles hex and decimal values correctly
   ✓ Works with all register names
   ✓ Monotonic index preserved across executions

Example output from test:
  (pyrv32-dbg) tsr pc 0x80000000
  Found pc=0x80000000 at index 0 (step 0):
  [      0] PC=0x80000000  insn=0x80800137
            a0=0x00000000 a1=0x00000000 ... [all registers shown]

This feature will be extremely useful for debugging the NetHack vfprintf issue,
allowing us to find exactly when s4 was set to 0x80000000 instead of the
correct function pointer.
"""

print(__doc__)
