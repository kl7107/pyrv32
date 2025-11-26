# NetHack Infinite Restart Bug - SOLVED

## Summary
NetHack was stuck in an infinite restart loop, executing approximately 78,620 instructions before calling `_start` again instead of continuing execution.

## Root Cause
**Misaligned Thread Pointer (tp) causing unaligned memory writes**

### The Bug Chain
1. **Linker Script Bug**: In `link.ld`, `__tdata_end` was not aligned
   - The `.tdata` section ended at an arbitrary address (0x801a3c1a)
   - This address was **not 4-byte aligned** (ends in 'a', not '0', '4', '8', or 'c')

2. **Startup Code**: `crt0.S` set `tp` to `__tdata_end`
   ```asm
   lui  tp, %hi(__tdata_end)
   addi tp, tp, %lo(__tdata_end)
   # Result: tp = 0x801a3c1a (misaligned!)
   ```

3. **Unaligned Write**: Code at PC=0x800005d0 calculated address as `tp + 0x10`
   ```asm
   add  a5, a5, tp     # a5 = 0x10 + 0x801a3c1a = 0x801a3c2a (misaligned!)
   sw   a4, 0(a5)      # Store word to misaligned address
   ```

4. **Memory Corruption**: The unaligned 32-bit write to 0x801a3c2a:
   - Wrote value 0x00000002 to bytes at 0x801a3c2a, 0x801a3c2b, 0x801a3c2c, 0x801a3c2d
   - This overwrote byte at 0x801a3c2c, changing memory there from 0x80000054 to 0x80000000

5. **s4 Corruption**: Later, code loaded s4 from corrupted memory:
   ```asm
   lw s4, 8(a0)        # Load from 0x801a3c2c
   # s4 = 0x80000000 (should have been 0x80000054 - a valid function pointer)
   ```

6. **Infinite Loop**: vfprintf called s4 as a function pointer:
   ```asm
   jalr ra, 0(s4)      # Jump to 0x80000000 = _start!
   ```
   This caused the program to restart from the beginning.

## The Fix
Modified `/home/dev/git/zesarux/pyrv32/nethack-3.4.3/sys/pyrv32/link.ld`:

```ld
  .tdata : {
    __tdata_start = .;
    *(.tdata .tdata.*)
    . = ALIGN(8);     /* ← ADDED: Align to 8 bytes */
    __tdata_end = .;
  } > RAM
```

## Results

### Before Fix:
- tp = 0x801a3c1a (misaligned)
- Program stuck in 78,620-instruction restart loop
- Never completed execution

### After Fix:
- tp = 0x801a3c20 (properly 8-byte aligned)
- Program executes 80,090 instructions
- **Terminates normally** with ebreak
- No more infinite restart loop!

## Debugging Tools Used
1. **Trace Buffer**: 200K-entry ring buffer to track execution history
2. **Conditional Breakpoints**: `bcond s4 0x80000000` to find where s4 got bad value
3. **Memory Watchpoints**: Tracked writes to 0x801a3c2c
4. **Automated Debugging**: Scripts to find exact corruption point

## Lessons Learned
- **Always align data structures** in linker scripts, especially TLS sections
- **Thread pointer must be properly aligned** for structure access
- **Unaligned memory accesses** can cause subtle corruption bugs
- **Automated debugging with conditional breakpoints** is extremely effective

## Timeline
- Instruction 78423: Unaligned write corrupts memory at 0x801a3c2c
- Instruction 78485: Load from corrupted memory sets s4=0x80000000  
- Instruction 78620: vfprintf calls s4 → jumps to _start → restart loop
- After fix: Clean execution, normal termination at 80,090 instructions

**Bug Status: FIXED ✓**
