# NetHack Debugging Session Summary

## Date: 2024-11-26

### BREAKTHROUGH! 🎉

**Found the root cause using the trace buffer!**

NetHack is stuck in an infinite restart loop because:
1. vfprintf() is called to output text
2. s4 register contains 0x80000000 (_start address) instead of a function pointer
3. vfprintf executes `jalr s4` at PC=0x80162c98
4. This jumps to _start, restarting the entire program
5. Loop repeats forever (~78,547 instructions per iteration)

**The bug**: s4 should contain a pointer to a character output function (putc/write),  
but instead contains the program start address.

**How we found it**: Trace buffer showed the exact instruction (step 78620) that jumped from vfprintf to _start.

### Accomplishments ✅

1. **Implemented Complete Debugger System**
   - ✅ Breakpoint manager with add/delete/list/enable/disable
   - ✅ Interactive CLI with command history
   - ✅ Single stepping (s, s N, c commands)
   - ✅ Compact register dumps
   - ✅ Register tracing to file with --reg-trace option
   - ✅ Non-zero register filtering with --reg-nonzero
   - ✅ PC tracing with --pc-trace option
   - ✅ **TRACE BUFFER!** Ring buffer storing full execution history
   - ✅ Trace commands: t N, t M N, t all, t clear, t info

2. **Fixed environ Support**
   - ✅ Added `environ` global variable to crt0.S
   - ✅ Set up empty environment array (envp[0] = NULL)
   - ✅ Pass envp to main() as third argument  
   - ✅ Initialize global environ pointer in BSS

3. **Debugging Progress**
   - ✅ Confirmed NetHack builds successfully (1.7MB binary)
   - ✅ Confirmed BSS clearing works (78K instructions)
   - ✅ Confirmed main() is called at 0x801573cc
   - ✅ Discovered NetHack calls getenv() early in initialization
   - ✅ Fixed getenv() support with environ variable
   - ✅ NetHack now progresses past getenv() calls
   - ✅ **Found the restart loop bug in vfprintf!**

### Current Status

**NetHack executes but produces no console output.**

After 156K+ instructions:
- Main() has been called
- getenv() has been called (and returns NULL correctly)
- Code is executing deep into NetHack initialization
- No write() syscall has been called yet
- No output to console UART

### Investigation Findings

1. **Function Calls Observed:**
   - getenv() at 0x801605f0 ✅
   - getpid() called from main
   - umask() called from main
   - choose_windows() called

2. **Code Flow:**
   - BSS clear: instructions 0-78,141
   - main() entry: instruction 78,141
   - After 500 steps in main: PC=0x80157334, a0=-1 (error return)

3. **Missing:**
   - No write() calls detected
   - No console output
   - Likely stuck in error handling or waiting for files

### Next Steps

1. **Find where NetHack tries to open files**
   - Set breakpoint on open() syscall
   - See what files it's looking for
   - Check what errors it's getting

2. **Find where NetHack expects to write output**
   - Set breakpoint on write(), puts(), printf()
   - See if it ever reaches output code
   - Check if it's stuck before output

3. **Implement ELF Support (Priority 4 from plan)**
   - Load .elf files
   - Run objdump for source/asm mixed view
   - Map PC to source lines
   - Show C source during debugging

4. **Debug with source visibility**
   - Step through NetHack with C source visible
   - See exactly what code is executing
   - Find the bottleneck

### Files Modified This Session

- `pyrv32.py`: Added --reg-trace, --reg-file, --reg-nonzero options
- `debugger.py`: Added register tracing methods
- `firmware/crt0.S`: Added environ support
- Created test scripts:
  - `test_debugger_integration.py`
  - `find_nethack.py`
  - `test_nethack_debug.py`
  - `step_nethack_main.py`
  - `test_nethack_regtrace.py`
  - `analyze_nethack.py`
  - `find_nethack_stuck.py`
  - `disasm_stuck_addresses.py`
  - `find_output_calls.py`
  - `check_main_jumps.py`
  - `test_write_breakpoint.py`
  - And more...

### Performance Metrics

- Simulator speed: ~100-110 KIPS
- BSS clear time: <1 second (78K instructions)
- NetHack initialization: 156K+ instructions (no output yet)
- Register trace file: 156,243 lines for 78K instructions

### Test Results

- ✅ All debugger unit tests pass
- ✅ Breakpoints work correctly
- ✅ Single stepping works
- ✅ Register tracing works
- ✅ PC tracing works
- ✅ NetHack builds cleanly
- ✅ NetHack loads and executes
- ❌ NetHack produces no output
- ❌ NetHack appears stuck in initialization

### Hypothesis

NetHack is likely:
1. Trying to access configuration files (not present)
2. Returning errors from file access attempts
3. Either looping in retry logic OR
4. Proceeding with defaults but not reaching output yet

Need to instrument file I/O syscalls to see what's being attempted.
