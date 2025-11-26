#!/usr/bin/env python3
"""
Summary of s4 Investigation

FINDINGS:
=========

1. At breakpoint (vfprintf+0x96c, PC=0x80162c98):
   - Instruction: jalr ra, 0(s4)  [jump to function pointer in s4]
   - s4 = 0x80000000 (_start address)
   - This causes jump to _start instead of the intended function
   - Result: Program restarts infinitely

2. Trace Buffer Analysis:
   - Searched backwards through 78,620+ instructions
   - tsrneq s4 0x80000000 found NOTHING
   - This means s4 was 0x80000000 for THE ENTIRE EXECUTION
   - It was never properly initialized!

3. CPU Initialization:
   - All registers start at 0 (cpu.py __init__)
   - crt0.S only initializes: sp, tp, a0, a1, a2
   - s4 (x20) is NOT initialized by crt0.S
   - So s4 should be 0, not 0x80000000

CONCLUSION:
===========

There are two possibilities:

A) MEMORY CORRUPTION:
   - vfprintf reads s4 from a FILE structure in memory
   - That memory location contains 0x80000000
   - Need to find WHERE this value comes from
   - Check .data or .bss initialization

B) MISSING INITIALIZATION:
   - picolibc vfprintf expects __sinit() or similar to be called
   - This function should set up FILE structures with proper function pointers
   - We're not calling it in crt0.S
   - Need to add stdio initialization to crt0.S before main()

NEXT STEPS:
===========

1. Check picolibc source for stdio initialization requirements
2. Look for __sinit, __sfp_init, or similar functions
3. Add call to stdio init in crt0.S before calling main()
4. Check if FILE structures need to be set up
5. Verify that stdout/stderr are properly initialized

The value 0x80000000 is _start, which suggests it might be:
- A default/placeholder value in uninitialized memory
- The result of some pointer arithmetic gone wrong
- A sentinel value that should have been replaced during init

Most likely: vfprintf is reading from an uninitialized FILE structure
whose function pointer field happens to contain 0x80000000 from the
binary layout or linker script.
"""

print(__doc__)

print("\nRecommendation:")
print("=" * 70)
print("Check NetHack build for picolibc initialization.")
print("Look for missing __libc_init_array() or __sinit() calls.")
print("The crt0.S needs to initialize stdio before calling main().")
print("=" * 70)
