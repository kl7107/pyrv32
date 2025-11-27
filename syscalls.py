"""
Linux RISC-V 32-bit Syscall Handler

Implements syscall emulation by intercepting ECALL instructions and
translating simulated syscalls to host Python OS operations.

Syscall ABI (Linux RV32):
- a7 (x17): syscall number
- a0-a5 (x10-x15): arguments
- a0 (x10): return value (or -errno on error)
"""

import os
import errno
import struct


# Linux RV32 syscall numbers (from Linux kernel arch/riscv/include/uapi/asm/unistd.h)
SYS_GETCWD = 17
SYS_UNLINKAT = 35
SYS_RENAMEAT = 38
SYS_FACCESSAT = 48
SYS_CHDIR = 49
SYS_OPENAT = 56
SYS_CLOSE = 57
SYS_LSEEK = 62
SYS_READ = 63
SYS_WRITE = 64
SYS_FSTATAT = 79
SYS_FSTAT = 80
SYS_EXIT = 93
SYS_EXIT_GROUP = 94


class SyscallHandler:
    """
    Handles Linux RISC-V syscalls by intercepting ECALL instructions.
    
    Maps simulated filesystem to host filesystem with optional root prefix.
    """
    
    def __init__(self, fs_root="."):
        """
        Initialize syscall handler.
        
        Args:
            fs_root: Host directory to use as simulated filesystem root
                    (e.g., "./pyrv32-fs" maps simulated "/" to "./pyrv32-fs/")
        """
        self.fs_root = os.path.abspath(fs_root)
        self.cwd = "/"  # Simulated current working directory
        self.fd_map = {}  # Map simulated fd -> host file object
        self.next_fd = 3  # Start after stdin/stdout/stderr
        
        # Map stdin/stdout/stderr to Python equivalents
        # Note: We don't actually use these since UART handles I/O,
        # but they're here for completeness
        self.fd_map[0] = None  # stdin
        self.fd_map[1] = None  # stdout  
        self.fd_map[2] = None  # stderr
    
    def handle_syscall(self, cpu, memory):
        """
        Handle ECALL syscall.
        
        Args:
            cpu: RV32CPU instance with registers containing syscall args
            memory: Memory instance for reading/writing strings and buffers
            
        Returns:
            None (modifies cpu.regs[10] with return value)
        """
        syscall_num = cpu.regs[17]  # a7
        
        # Dispatch to handler
        handlers = {
            SYS_GETCWD: self._sys_getcwd,
            SYS_CHDIR: self._sys_chdir,
            SYS_OPENAT: self._sys_openat,
            SYS_CLOSE: self._sys_close,
            SYS_LSEEK: self._sys_lseek,
            SYS_READ: self._sys_read,
            SYS_WRITE: self._sys_write,
            SYS_FSTATAT: self._sys_fstatat,
            SYS_FSTAT: self._sys_fstat,
            SYS_FACCESSAT: self._sys_faccessat,
            SYS_UNLINKAT: self._sys_unlinkat,
            SYS_RENAMEAT: self._sys_renameat,
            SYS_EXIT: self._sys_exit,
            SYS_EXIT_GROUP: self._sys_exit_group,
        }
        
        handler = handlers.get(syscall_num)
        if handler:
            result = handler(cpu, memory)
            cpu.regs[10] = result & 0xFFFFFFFF  # a0 = return value
        else:
            # Unsupported syscall - return -ENOSYS
            cpu.regs[10] = self._neg_errno(errno.ENOSYS)
    
    # Helper methods
    
    def _neg_errno(self, err):
        """Convert errno to negative value (Linux syscall convention)"""
        return (-err) & 0xFFFFFFFF
    
    def _read_string(self, memory, addr, max_len=4096):
        """Read null-terminated string from simulated memory"""
        chars = []
        for i in range(max_len):
            try:
                c = memory.read_byte(addr + i)
                if c == 0:
                    break
                chars.append(chr(c))
            except:
                break
        return ''.join(chars)
    
    def _write_string(self, memory, addr, s, max_len):
        """Write null-terminated string to simulated memory"""
        bytes_written = 0
        for i, c in enumerate(s):
            if i >= max_len - 1:  # Leave room for null terminator
                break
            try:
                memory.write_byte(addr + i, ord(c))
                bytes_written += 1
            except:
                break
        # Null terminator
        if bytes_written < max_len:
            try:
                memory.write_byte(addr + bytes_written, 0)
            except:
                pass
        return bytes_written
    
    def _write_u32(self, memory, addr, value):
        """Write 32-bit unsigned value to memory (little-endian)"""
        value = value & 0xFFFFFFFF
        memory.write_byte(addr + 0, (value >> 0) & 0xFF)
        memory.write_byte(addr + 1, (value >> 8) & 0xFF)
        memory.write_byte(addr + 2, (value >> 16) & 0xFF)
        memory.write_byte(addr + 3, (value >> 24) & 0xFF)
    
    def _write_u16(self, memory, addr, value):
        """Write 16-bit unsigned value to memory (little-endian)"""
        value = value & 0xFFFF
        memory.write_byte(addr + 0, (value >> 0) & 0xFF)
        memory.write_byte(addr + 1, (value >> 8) & 0xFF)
    
    def _write_u64(self, memory, addr, value):
        """Write 64-bit unsigned value to memory (little-endian)"""
        value = value & 0xFFFFFFFFFFFFFFFF
        for i in range(8):
            memory.write_byte(addr + i, (value >> (i * 8)) & 0xFF)
    
    def _to_signed(self, value):
        """Convert unsigned 32-bit to signed"""
        if value & 0x80000000:
            return value - 0x100000000
        return value
    
    def _alloc_fd(self):
        """Allocate a new file descriptor"""
        fd = self.next_fd
        self.next_fd += 1
        return fd
    
    def _sim_to_host_path(self, sim_path):
        """
        Convert simulated absolute path to host path.
        
        Args:
            sim_path: Simulated path (e.g., "/nethack/save")
            
        Returns:
            Host path (e.g., "./pyrv32-fs/nethack/save")
        """
        # Remove leading slash
        if sim_path.startswith('/'):
            sim_path = sim_path[1:]
        
        # Join with fs_root
        host_path = os.path.join(self.fs_root, sim_path)
        
        # Ensure path stays within fs_root (prevent escapes)
        host_path = os.path.abspath(host_path)
        if not host_path.startswith(self.fs_root):
            # Path escape attempt - treat as EACCES
            return None
        
        return host_path
    
    # Syscall implementations
    
    def _sys_getcwd(self, cpu, memory):
        """
        getcwd(buf, size) - Get current working directory
        
        Args:
            a0: buffer address
            a1: buffer size
            
        Returns:
            Number of bytes written (including null), or -errno
        """
        buf_addr = cpu.regs[10]  # a0
        buf_size = cpu.regs[11]  # a1
        
        cwd = self.cwd
        if len(cwd) + 1 > buf_size:
            return self._neg_errno(errno.ERANGE)
        
        bytes_written = self._write_string(memory, buf_addr, cwd, buf_size)
        return bytes_written + 1  # Include null terminator
    
    def _sys_chdir(self, cpu, memory):
        """
        chdir(path) - Change current directory
        
        Args:
            a0: path string address
            
        Returns:
            0 on success, -errno on error
        """
        path_addr = cpu.regs[10]  # a0
        path = self._read_string(memory, path_addr)
        
        # Convert to absolute path if relative
        if not path.startswith('/'):
            if self.cwd == '/':
                path = '/' + path
            else:
                path = self.cwd + '/' + path
        
        # Check if directory exists on host
        host_path = self._sim_to_host_path(path)
        if host_path is None:
            return self._neg_errno(errno.EACCES)
        
        # For now, accept any path within fs_root
        # Real implementation would check os.path.isdir(host_path)
        # but we'll be lenient and create directories on demand
        if not os.path.exists(host_path):
            try:
                os.makedirs(host_path, exist_ok=True)
            except:
                return self._neg_errno(errno.ENOENT)
        
        if not os.path.isdir(host_path):
            return self._neg_errno(errno.ENOTDIR)
        
        self.cwd = path
        return 0
    
    def _sys_openat(self, cpu, memory):
        """
        openat(dirfd, pathname, flags, mode) - Open file
        
        Args:
            a0: dirfd (ignored for absolute paths, -100=AT_FDCWD for relative)
            a1: pathname address
            a2: flags
            a3: mode
            
        Returns:
            fd on success, -errno on error
        """
        dirfd = self._to_signed(cpu.regs[10])  # a0
        pathname_addr = cpu.regs[11]  # a1
        flags = cpu.regs[12]  # a2
        mode = cpu.regs[13]  # a3
        
        # Read pathname from memory
        pathname = self._read_string(memory, pathname_addr)
        if pathname is None:
            return self._neg_errno(errno.EFAULT)
        
        # Convert to host path
        host_path = self._sim_to_host_path(pathname)
        if host_path is None:
            return self._neg_errno(errno.ENOENT)
        
        try:
            # Open file on host
            host_fd = os.open(host_path, flags, mode)
            
            # Allocate simulator fd
            sim_fd = self._alloc_fd()
            self.fd_map[sim_fd] = host_fd
            
            return sim_fd
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_close(self, cpu, memory):
        """
        close(fd) - Close file descriptor
        
        Args:
            a0: fd
            
        Returns:
            0 on success, -errno on error
        """
        fd = cpu.regs[10] & 0xFFFFFFFF  # a0
        
        if fd not in self.fd_map:
            return self._neg_errno(errno.EBADF)
        
        file_obj = self.fd_map[fd]
        if file_obj is not None:
            try:
                file_obj.close()
            except:
                pass
        
        del self.fd_map[fd]
        return 0
    
    def _sys_read(self, cpu, memory):
        """
        read(fd, buf, count) - Read from file
        
        Args:
            a0: fd
            a1: buffer address
            a2: count
            
        Returns:
            bytes read on success, -errno on error
        """
        fd = cpu.regs[10]  # a0
        buf_addr = cpu.regs[11]  # a1
        count = cpu.regs[12]  # a2
        
        if fd not in self.fd_map:
            return self._neg_errno(errno.EBADF)
        
        host_fd = self.fd_map[fd]
        
        try:
            # Read from host file
            data = os.read(host_fd, count)
            
            # Write to simulator memory
            for i, byte in enumerate(data):
                memory.write_byte(buf_addr + i, byte)
            
            return len(data)
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_write(self, cpu, memory):
        """
        write(fd, buf, count) - Write to file
        
        Args:
            a0: fd
            a1: buffer address
            a2: count
            
        Returns:
            bytes written on success, -errno on error
        """
        fd = cpu.regs[10]  # a0
        buf_addr = cpu.regs[11]  # a1
        count = cpu.regs[12]  # a2
        
        if fd not in self.fd_map:
            return self._neg_errno(errno.EBADF)
        
        host_fd = self.fd_map[fd]
        
        try:
            # Read from simulator memory
            data = bytes([memory.read_byte(buf_addr + i) for i in range(count)])
            
            # Write to host file
            written = os.write(host_fd, data)
            
            return written
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_lseek(self, cpu, memory):
        """
        lseek(fd, offset, whence) - Reposition file offset
        
        Args:
            a0: fd
            a1: offset (low 32 bits)
            a2: whence (SEEK_SET=0, SEEK_CUR=1, SEEK_END=2)
            
        Returns:
            new offset on success, -errno on error
        """
        fd = cpu.regs[10]  # a0
        offset = self._to_signed(cpu.regs[11])  # a1 (signed offset)
        whence = cpu.regs[12]  # a2
        
        if fd not in self.fd_map:
            return self._neg_errno(errno.EBADF)
        
        host_fd = self.fd_map[fd]
        
        try:
            # Seek in host file
            new_offset = os.lseek(host_fd, offset, whence)
            return new_offset
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_fstat(self, cpu, memory):
        """
        fstat(fd, statbuf) - Get file status
        
        Args:
            a0: fd
            a1: stat buffer address
            
        Returns:
            0 on success, -errno on error
        """
        fd = cpu.regs[10]  # a0
        statbuf_addr = cpu.regs[11]  # a1
        
        if fd not in self.fd_map:
            return self._neg_errno(errno.EBADF)
        
        host_fd = self.fd_map[fd]
        
        try:
            # Get file status from host
            st = os.fstat(host_fd)
            
            # Write stat structure to memory
            # Actual newlib/picolibc stat structure layout for RISC-V 32-bit
            # (determined by running test_stat_layout.c):
            # struct stat {
            #   dev_t st_dev;        // 2 bytes (offset 0)
            #   ino_t st_ino;        // 2 bytes (offset 2)
            #   mode_t st_mode;      // 4 bytes (offset 4)
            #   nlink_t st_nlink;    // 2 bytes (offset 8)
            #   uid_t st_uid;        // 2 bytes (offset 10)
            #   gid_t st_gid;        // 2 bytes (offset 12)
            #   dev_t st_rdev;       // 2 bytes (offset 14)
            #   off_t st_size;       // 8 bytes (offset 16)
            #   ... (other fields)
            # }
            
            self._write_u16(memory, statbuf_addr + 0, st.st_dev & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 2, st.st_ino & 0xFFFF)
            self._write_u32(memory, statbuf_addr + 4, st.st_mode)
            self._write_u16(memory, statbuf_addr + 8, st.st_nlink & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 10, st.st_uid & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 12, st.st_gid & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 14, st.st_rdev & 0xFFFF)
            self._write_u64(memory, statbuf_addr + 16, st.st_size)
            
            return 0
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_fstatat(self, cpu, memory):
        """
        fstatat(dirfd, pathname, statbuf, flags) - Get file status by path
        
        Args:
            a0: dirfd
            a1: pathname address
            a2: stat buffer address
            a3: flags
            
        Returns:
            0 on success, -errno on error
        """
        dirfd = self._to_signed(cpu.regs[10])  # a0
        pathname_addr = cpu.regs[11]  # a1
        statbuf_addr = cpu.regs[12]  # a2
        flags = cpu.regs[13]  # a3
        
        # Read pathname
        pathname = self._read_string(memory, pathname_addr)
        if pathname is None:
            return self._neg_errno(errno.EFAULT)
        
        # Convert to host path
        host_path = self._sim_to_host_path(pathname)
        if host_path is None:
            return self._neg_errno(errno.ENOENT)
        
        try:
            # Get file status from host
            st = os.stat(host_path)
            
            # Write stat structure to memory (same layout as fstat)
            self._write_u16(memory, statbuf_addr + 0, st.st_dev & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 2, st.st_ino & 0xFFFF)
            self._write_u32(memory, statbuf_addr + 4, st.st_mode)
            self._write_u16(memory, statbuf_addr + 8, st.st_nlink & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 10, st.st_uid & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 12, st.st_gid & 0xFFFF)
            self._write_u16(memory, statbuf_addr + 14, st.st_rdev & 0xFFFF)
            self._write_u64(memory, statbuf_addr + 16, st.st_size)
            
            return 0
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_faccessat(self, cpu, memory):
        """
        faccessat(dirfd, pathname, mode, flags) - Check file accessibility
        
        Args:
            a0: dirfd
            a1: pathname address
            a2: mode (F_OK=0, R_OK=4, W_OK=2, X_OK=1)
            a3: flags
            
        Returns:
            0 if accessible, -errno on error
        """
        dirfd = self._to_signed(cpu.regs[10])  # a0
        pathname_addr = cpu.regs[11]  # a1
        mode = cpu.regs[12]  # a2
        flags = cpu.regs[13]  # a3
        
        # Read pathname
        pathname = self._read_string(memory, pathname_addr)
        if pathname is None:
            return self._neg_errno(errno.EFAULT)
        
        # Convert to host path
        host_path = self._sim_to_host_path(pathname)
        if host_path is None:
            return self._neg_errno(errno.ENOENT)
        
        try:
            # Check accessibility on host
            if os.access(host_path, mode):
                return 0
            else:
                return self._neg_errno(errno.EACCES)
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_unlinkat(self, cpu, memory):
        """
        unlinkat(dirfd, pathname, flags) - Delete a file
        
        Args:
            a0: dirfd
            a1: pathname address
            a2: flags (AT_REMOVEDIR=0x200 for directories)
            
        Returns:
            0 on success, -errno on error
        """
        dirfd = self._to_signed(cpu.regs[10])  # a0
        pathname_addr = cpu.regs[11]  # a1
        flags = cpu.regs[12]  # a2
        
        # Read pathname
        pathname = self._read_string(memory, pathname_addr)
        if pathname is None:
            return self._neg_errno(errno.EFAULT)
        
        # Convert to host path
        host_path = self._sim_to_host_path(pathname)
        if host_path is None:
            return self._neg_errno(errno.ENOENT)
        
        try:
            # Check if removing directory
            if flags & 0x200:  # AT_REMOVEDIR
                os.rmdir(host_path)
            else:
                os.unlink(host_path)
            return 0
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_renameat(self, cpu, memory):
        """
        renameat(olddirfd, oldpath, newdirfd, newpath) - Rename a file
        
        Args:
            a0: olddirfd
            a1: oldpath address
            a2: newdirfd
            a3: newpath address
            
        Returns:
            0 on success, -errno on error
        """
        olddirfd = self._to_signed(cpu.regs[10])  # a0
        oldpath_addr = cpu.regs[11]  # a1
        newdirfd = self._to_signed(cpu.regs[12])  # a2
        newpath_addr = cpu.regs[13]  # a3
        
        # Read paths
        oldpath = self._read_string(memory, oldpath_addr)
        newpath = self._read_string(memory, newpath_addr)
        if oldpath is None or newpath is None:
            return self._neg_errno(errno.EFAULT)
        
        # Convert to host paths
        old_host_path = self._sim_to_host_path(oldpath)
        new_host_path = self._sim_to_host_path(newpath)
        if old_host_path is None or new_host_path is None:
            return self._neg_errno(errno.ENOENT)
        
        try:
            os.rename(old_host_path, new_host_path)
            return 0
        except OSError as e:
            return self._neg_errno(e.errno)
    
    def _sys_exit(self, cpu, memory):
        """
        exit(status) - Terminate process
        
        Args:
            a0: exit status
            
        Returns:
            Does not return (raises exception)
        """
        from exceptions import EBreakException
        # Treat as EBREAK for clean termination
        raise EBreakException(cpu.pc)
    
    def _sys_exit_group(self, cpu, memory):
        """
        exit_group(status) - Terminate all threads (same as exit for single-threaded)
        
        Args:
            a0: exit status
            
        Returns:
            Does not return (raises exception)
        """
        return self._sys_exit(cpu, memory)
