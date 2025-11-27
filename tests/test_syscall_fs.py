#!/usr/bin/env python3
"""
Test syscall handler - getcwd and chdir
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu import RV32CPU
from memory import Memory
from syscalls import SyscallHandler, SYS_GETCWD, SYS_CHDIR


def test_getcwd_initial(runner):
    """getcwd: initial cwd is /"""
    cpu = RV32CPU()
    mem = Memory()
    handler = SyscallHandler(fs_root=".")
    
    # Setup: a7=SYS_GETCWD, a0=buffer addr, a1=buffer size
    cpu.regs[17] = SYS_GETCWD
    cpu.regs[10] = 0x80001000  # Buffer address
    cpu.regs[11] = 100  # Buffer size
    
    handler.handle_syscall(cpu, mem)
    
    # Read result from buffer
    result = ""
    addr = 0x80001000
    for i in range(100):
        c = mem.read_byte(addr + i)
        if c == 0:
            break
        result += chr(c)
    
    if result != "/":
        runner.test_fail("getcwd initial", "/", result)


def test_getcwd_returns_length(runner):
    """getcwd: returns correct length"""
    cpu = RV32CPU()
    mem = Memory()
    handler = SyscallHandler(fs_root=".")
    
    cpu.regs[17] = SYS_GETCWD
    cpu.regs[10] = 0x80001000
    cpu.regs[11] = 100
    
    handler.handle_syscall(cpu, mem)
    
    # Return value should be 2 (1 for '/', 1 for null)
    ret = cpu.regs[10]
    if ret != 2:
        runner.test_fail("getcwd length", "2", str(ret))


def test_getcwd_buffer_too_small(runner):
    """getcwd: returns -ERANGE if buffer too small"""
    cpu = RV32CPU()
    mem = Memory()
    handler = SyscallHandler(fs_root=".")
    
    # Change to a longer path first
    cpu.regs[17] = SYS_CHDIR
    cpu.regs[10] = 0x80002000
    mem.write_byte(0x80002000, ord('/'))
    mem.write_byte(0x80002001, ord('a'))
    mem.write_byte(0x80002002, ord('b'))
    mem.write_byte(0x80002003, ord('c'))
    mem.write_byte(0x80002004, 0)
    
    handler.handle_syscall(cpu, mem)
    
    # Now try getcwd with buffer too small
    cpu.regs[17] = SYS_GETCWD
    cpu.regs[10] = 0x80001000
    cpu.regs[11] = 2  # Too small for "/abc\0" (5 bytes)
    
    handler.handle_syscall(cpu, mem)
    
    # Should return -ERANGE (34)
    ret = cpu.regs[10]
    import errno
    expected = (-errno.ERANGE) & 0xFFFFFFFF
    if ret != expected:
        runner.test_fail("getcwd ERANGE", f"0x{expected:08x}", f"0x{ret:08x}")


def test_chdir_absolute(runner):
    """chdir: can change to absolute path"""
    cpu = RV32CPU()
    mem = Memory()
    
    # Create temp directory for testing
    tmpdir = tempfile.mkdtemp(prefix="pyrv32_test_")
    try:
        handler = SyscallHandler(fs_root=tmpdir)
        
        # Create directory /test in fs_root
        os.makedirs(os.path.join(tmpdir, "test"), exist_ok=True)
        
        # chdir("/test")
        cpu.regs[17] = SYS_CHDIR
        cpu.regs[10] = 0x80001000
        path = "/test"
        for i, c in enumerate(path):
            mem.write_byte(0x80001000 + i, ord(c))
        mem.write_byte(0x80001000 + len(path), 0)
        
        handler.handle_syscall(cpu, mem)
        
        # Should return 0 (success)
        ret = cpu.regs[10]
        if ret != 0:
            runner.test_fail("chdir absolute", "0", str(ret))
        
        # Verify cwd changed
        if handler.cwd != "/test":
            runner.test_fail("chdir cwd", "/test", handler.cwd)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_chdir_creates_directory(runner):
    """chdir: creates directory if it doesn't exist"""
    cpu = RV32CPU()
    mem = Memory()
    
    tmpdir = tempfile.mkdtemp(prefix="pyrv32_test_")
    try:
        handler = SyscallHandler(fs_root=tmpdir)
        
        # chdir to non-existent directory
        cpu.regs[17] = SYS_CHDIR
        cpu.regs[10] = 0x80001000
        path = "/newdir"
        for i, c in enumerate(path):
            mem.write_byte(0x80001000 + i, ord(c))
        mem.write_byte(0x80001000 + len(path), 0)
        
        handler.handle_syscall(cpu, mem)
        
        # Should succeed and create directory
        ret = cpu.regs[10]
        if ret != 0:
            runner.test_fail("chdir creates dir", "0", str(ret))
        
        # Verify directory was created
        if not os.path.isdir(os.path.join(tmpdir, "newdir")):
            runner.test_fail("chdir creates dir", "directory exists", "directory not created")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_chdir_relative(runner):
    """chdir: can change to relative path"""
    cpu = RV32CPU()
    mem = Memory()
    
    tmpdir = tempfile.mkdtemp(prefix="pyrv32_test_")
    try:
        handler = SyscallHandler(fs_root=tmpdir)
        
        # First chdir to /parent
        os.makedirs(os.path.join(tmpdir, "parent", "child"), exist_ok=True)
        
        cpu.regs[17] = SYS_CHDIR
        cpu.regs[10] = 0x80001000
        path = "/parent"
        for i, c in enumerate(path):
            mem.write_byte(0x80001000 + i, ord(c))
        mem.write_byte(0x80001000 + len(path), 0)
        
        handler.handle_syscall(cpu, mem)
        
        # Now chdir to relative "child"
        cpu.regs[17] = SYS_CHDIR
        cpu.regs[10] = 0x80002000
        path = "child"
        for i, c in enumerate(path):
            mem.write_byte(0x80002000 + i, ord(c))
        mem.write_byte(0x80002000 + len(path), 0)
        
        handler.handle_syscall(cpu, mem)
        
        ret = cpu.regs[10]
        if ret != 0:
            runner.test_fail("chdir relative", "0", str(ret))
        
        # cwd should be /parent/child
        if handler.cwd != "/parent/child":
            runner.test_fail("chdir relative cwd", "/parent/child", handler.cwd)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_chdir_getcwd_integration(runner):
    """chdir+getcwd: getcwd returns path set by chdir"""
    cpu = RV32CPU()
    mem = Memory()
    
    tmpdir = tempfile.mkdtemp(prefix="pyrv32_test_")
    try:
        handler = SyscallHandler(fs_root=tmpdir)
        
        # chdir to /mypath
        os.makedirs(os.path.join(tmpdir, "mypath"), exist_ok=True)
        
        cpu.regs[17] = SYS_CHDIR
        cpu.regs[10] = 0x80001000
        path = "/mypath"
        for i, c in enumerate(path):
            mem.write_byte(0x80001000 + i, ord(c))
        mem.write_byte(0x80001000 + len(path), 0)
        
        handler.handle_syscall(cpu, mem)
        
        # Now getcwd
        cpu.regs[17] = SYS_GETCWD
        cpu.regs[10] = 0x80002000
        cpu.regs[11] = 100
        
        handler.handle_syscall(cpu, mem)
        
        # Read result
        result = ""
        for i in range(100):
            c = mem.read_byte(0x80002000 + i)
            if c == 0:
                break
            result += chr(c)
        
        if result != "/mypath":
            runner.test_fail("chdir+getcwd", "/mypath", result)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_chdir_rejects_file(runner):
    """chdir: returns -ENOTDIR when path is a file"""
    cpu = RV32CPU()
    mem = Memory()
    
    tmpdir = tempfile.mkdtemp(prefix="pyrv32_test_")
    try:
        handler = SyscallHandler(fs_root=tmpdir)
        
        # Create a file
        filepath = os.path.join(tmpdir, "somefile")
        with open(filepath, 'w') as f:
            f.write("test")
        
        # Try to chdir to it
        cpu.regs[17] = SYS_CHDIR
        cpu.regs[10] = 0x80001000
        path = "/somefile"
        for i, c in enumerate(path):
            mem.write_byte(0x80001000 + i, ord(c))
        mem.write_byte(0x80001000 + len(path), 0)
        
        handler.handle_syscall(cpu, mem)
        
        # Should return -ENOTDIR
        ret = cpu.regs[10]
        import errno
        expected = (-errno.ENOTDIR) & 0xFFFFFFFF
        if ret != expected:
            runner.test_fail("chdir file", f"0x{expected:08x} (-ENOTDIR)", f"0x{ret:08x}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_path_escape_prevention(runner):
    """chdir: prevents path escape with ../.."""
    cpu = RV32CPU()
    mem = Memory()
    
    tmpdir = tempfile.mkdtemp(prefix="pyrv32_test_")
    try:
        handler = SyscallHandler(fs_root=tmpdir)
        
        # Try to escape with ../../etc
        cpu.regs[17] = SYS_CHDIR
        cpu.regs[10] = 0x80001000
        path = "/../../etc"
        for i, c in enumerate(path):
            mem.write_byte(0x80001000 + i, ord(c))
        mem.write_byte(0x80001000 + len(path), 0)
        
        handler.handle_syscall(cpu, mem)
        
        # Should return -EACCES (permission denied)
        ret = cpu.regs[10]
        import errno
        expected = (-errno.EACCES) & 0xFFFFFFFF
        if ret != expected:
            runner.test_fail("path escape", f"0x{expected:08x} (-EACCES)", f"0x{ret:08x}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
