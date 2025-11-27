# Filesystem Syscall Implementation Plan

## Required Syscalls (from NetHack's syscalls.c)

| Function | Linux Syscall # | Priority | Status |
|----------|----------------|----------|--------|
| getcwd   | SYS_getcwd (17) | HIGH | TODO |
| chdir    | SYS_chdir (49) | HIGH | TODO |
| open     | SYS_openat (56) | HIGH | TODO |
| close    | SYS_close (57) | HIGH | TODO |
| read     | SYS_read (63) | HIGH | TODO |
| write    | SYS_write (64) | HIGH | TODO |
| lseek    | SYS_lseek (62) | MEDIUM | TODO |
| fstat    | SYS_fstat (80) | MEDIUM | TODO |
| stat     | SYS_fstatat (79) | MEDIUM | TODO |
| access   | SYS_faccessat (48) | MEDIUM | TODO |
| unlink   | SYS_unlinkat (35) | LOW | TODO |
| rename   | SYS_renameat (38) | LOW | TODO |
| isatty   | (uses fstat) | MEDIUM | TODO |

## Implementation Layers

### Layer 1: C Syscall Wrappers (syscalls.c)
- Inline assembly to issue ECALL
- Marshal arguments into a0-a7 registers
- Handle return value in a0

### Layer 2: Python Syscall Handler (syscalls.py)
- Intercept ECALL in execute.py
- Read syscall # from a7
- Read arguments from a0-a6
- Call host Python os.* functions
- Write return value to a0
- Map paths: simulated → host temp directory

### Layer 3: Tests
- Python unit tests for syscalls.py (tests/test_syscalls.py) ✓
- C integration tests (tests/c/test_fs_*.c)
- NetHack integration test

## Test Strategy

### Python Tests (tests/test_syscalls.py)
- Test each syscall handler in isolation
- Use temporary directories
- Verify error handling
- Already implemented ✓

### C Tests (new: tests/c/)
Small standalone C programs that:
1. Test single syscall (e.g., test_chdir.c)
2. Test syscall sequences (e.g., test_open_read_close.c)
3. Easy to compile and debug
4. Use /tmp/pyrv32-test-XXXXXX for all tests

### Integration Test
- Run NetHack
- Verify it gets past chdir

## Path Mapping

Simulated path → Host path:
- `/nethack` → `{temp_dir}/nethack`
- `/nethack/save` → `{temp_dir}/nethack/save`
- etc.

Jail to temp_dir - no `../` escapes allowed.

## Next Steps

1. ✓ Create Python syscall handlers (syscalls.py) 
2. ✓ Add ECALL interception in execute.py
3. ✓ Write Python unit tests
4. TODO: Create C test harness
5. TODO: Write C syscall tests
6. TODO: Update syscalls.c with ECALL wrappers
7. TODO: Test with NetHack
