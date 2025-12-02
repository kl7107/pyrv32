#!/usr/bin/env python3
"""
RV32System - Stateful RISC-V RV32IM Simulator

Encapsulates CPU, Memory, Syscalls, and Debugger into a controllable system.
Designed for programmatic control (MCP, testing, automation).
"""

from cpu import RV32CPU
from memory import Memory
from decoder import decode_instruction, get_instruction_name
from execute import execute_instruction
from exceptions import EBreakException, ECallException, MemoryAccessFault
from debugger import Debugger
from syscalls import SyscallHandler
from elf_loader import load_elf_image


class ExecutionResult:
    """Result of running the simulator"""
    def __init__(self, status, instruction_count=0, error=None, pc=None):
        self.status = status  # 'running', 'halted', 'breakpoint', 'error', 'max_steps'
        self.instruction_count = instruction_count
        self.error = error
        self.pc = pc
    
    def __repr__(self):
        return f"ExecutionResult(status={self.status}, instructions={self.instruction_count}, pc=0x{self.pc:08x if self.pc else 0:08x})"


class RV32System:
    """
    Stateful RV32IM simulator system.
    
    Provides programmatic control over CPU, memory, execution, and I/O.
    """
    
    def __init__(self, start_addr=0x80000000, fs_root="/home/dev/git/pyrv32/pyrv32_sim_fs", 
                 trace_buffer_size=10000):
        """
        Initialize the simulator system.
        
        Args:
            start_addr: Initial PC value (default 0x80000000)
            fs_root: Filesystem root for syscall handler
            trace_buffer_size: Size of execution trace buffer
        """
        self.cpu = RV32CPU()
        # Always use PTY for Console UART in headless/server mode
        self.memory = Memory(use_console_pty=False, save_console_output=True)
        self.syscall_handler = SyscallHandler(fs_root=fs_root)
        self.fs_root = fs_root  # Track filesystem root for coordination/cleanup
        self.debugger = Debugger(trace_buffer_size=trace_buffer_size)
        
        self.cpu.pc = start_addr
        self.start_addr = start_addr
        self.instruction_count = 0
        self.halted = False
        
        # Track UART output positions for incremental reads
        self._debug_uart_read_pos = 0
        self._console_uart_read_pos = 0
        
        # Symbol table for debugging
        self.symbols = {}  # name -> address
        self.reverse_symbols = {}  # address -> name
        self.elf_path = None  # Path to loaded ELF file
    
    def load_elf(self, elf_path):
        """
        Load an ELF file into memory.
        
        Parses the ELF file, loads all PT_LOAD segments into memory,
        and sets PC to the entry point.
        
        Args:
            elf_path: Path to ELF file
            
        Returns:
            Dictionary with:
                - bytes_loaded: Total bytes loaded
                - entry_point: ELF entry point address
                - segments: List of loaded segments (vaddr, size)
        """
        result = load_elf_image(self.memory, elf_path)
        self.symbols = result.symbols
        self.reverse_symbols = result.reverse_symbols
        self.elf_path = elf_path
        self.cpu.pc = result.entry_point

        segments = [{
            'vaddr': seg.vaddr,
            'memsz': seg.memsz,
            'filesz': seg.filesz,
            'flags': seg.flags
        } for seg in result.segments]

        return {
            'bytes_loaded': result.bytes_loaded,
            'entry_point': result.entry_point,
            'segments': segments,
            'symbols_loaded': len(self.symbols)
        }
    
    def lookup_symbol(self, name):
        """
        Look up symbol address by name.
        
        Args:
            name: Symbol name
            
        Returns:
            Address (int) or None if not found
        """
        return self.symbols.get(name)
    
    def reverse_lookup(self, address):
        """
        Look up symbol name by address.
        
        Args:
            address: Memory address
            
        Returns:
            Symbol name (str) or None if not found
        """
        return self.reverse_symbols.get(address)
    
    def get_symbol_info(self, address):
        """
        Get symbol information for an address.
        
        Returns the nearest symbol at or before the address.
        
        Args:
            address: Memory address
            
        Returns:
            Dictionary with 'name' and 'offset', or None
        """
        # Exact match
        if address in self.reverse_symbols:
            return {'name': self.reverse_symbols[address], 'offset': 0}
        
        # Find nearest symbol before this address
        candidates = [(addr, name) for addr, name in self.reverse_symbols.items() if addr < address]
        if candidates:
            nearest_addr, nearest_name = max(candidates, key=lambda x: x[0])
            return {'name': nearest_name, 'offset': address - nearest_addr}
        
        return None
    
    def disassemble(self, start_addr, end_addr):
        """
        Disassemble code with source interleaving using objdump.
        
        Args:
            start_addr: Start address (hex string or int)
            end_addr: End address (hex string or int)
            
        Returns:
            Disassembly output string
        """
        import subprocess
        
        if isinstance(start_addr, str):
            start_addr = int(start_addr, 16)
        if isinstance(end_addr, str):
            end_addr = int(end_addr, 16)
        
        if not self.elf_path:
            return "Error: No ELF file loaded"
        
        # Use objdump to disassemble with source
        cmd = [
            'riscv64-unknown-elf-objdump',
            '-d',
            '-S',
            '--start-address=' + hex(start_addr),
            '--stop-address=' + hex(end_addr),
            self.elf_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: objdump failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def reset(self):
        """Reset the system to initial state"""
        self.cpu = RV32CPU()
        self.memory = Memory()
        self.cpu.pc = self.start_addr
        self.instruction_count = 0
        self.halted = False
        self._debug_uart_read_pos = 0
        self._console_uart_read_pos = 0
        self.debugger.trace_buffer.clear()
    
    def step(self, count=1):
        """
        Execute N instructions.
        
        Args:
            count: Number of instructions to execute
            
        Returns:
            ExecutionResult with status and instruction count
        """
        # Clear halted flag to allow resuming after breakpoint/watchpoint
        self.halted = False
        
        executed = 0
        
        try:
            for i in range(count):
                # Fetch instruction
                insn = self.memory.read_word(self.cpu.pc)
                
                # Record in trace buffer
                self.debugger.trace_buffer.add(
                    self.instruction_count, 
                    self.cpu.pc, 
                    self.cpu.regs, 
                    insn
                )
                
                # Check for breakpoints
                should_break, break_msg = self.debugger.should_break(
                    self.cpu.pc, 
                    self.instruction_count, 
                    self.cpu.regs
                )
                if should_break:
                    # Auto-dump VT100 screen when hitting console RX status breakpoint (0x10001008)
                    if "0x10001008" in break_msg or "0x10001008" in str(self.cpu.pc):
                        self.dump_screen(show_cursor=True)
                    
                    return ExecutionResult(
                        'breakpoint', 
                        executed, 
                        error=break_msg,
                        pc=self.cpu.pc
                    )
                
                # Execute instruction
                try:
                    continue_exec = execute_instruction(self.cpu, self.memory, insn)
                    if not continue_exec:
                        self.halted = True
                        return ExecutionResult('halted', executed + 1, pc=self.cpu.pc)
                
                except ECallException:
                    # Handle syscall
                    self.syscall_handler.handle_syscall(self.cpu, self.memory)
                    self.cpu.pc += 4
                
                executed += 1
                self.instruction_count += 1
                
                # Check for watchpoints that were hit during instruction execution
                watchpoint_hits = self.memory.check_pending_watchpoints()
                if watchpoint_hits:
                    # Watchpoint was hit - halt after instruction completed
                    self.halted = True
                    wp_info = watchpoint_hits[0]  # Report first watchpoint
                    return ExecutionResult(
                        'halted',
                        executed,
                        error=f"{wp_info.access_type.capitalize()} watchpoint at {wp_info.address:#x}",
                        pc=self.cpu.pc
                    )
        
        except EBreakException as e:
            self.halted = True
            return ExecutionResult('halted', executed, pc=e.pc)
        
        except MemoryAccessFault as e:
            self.halted = True
            return ExecutionResult(
                'error', 
                executed,
                error=f"Memory fault: {e.access_type} at 0x{e.address:08x}",
                pc=e.pc
            )
        
        except Exception as e:
            self.halted = True
            return ExecutionResult(
                'error',
                executed,
                error=str(e),
                pc=self.cpu.pc
            )
        
        return ExecutionResult('running', executed, pc=self.cpu.pc)
    
    def run(self, max_steps=1000000):
        """
        Run until halted, breakpoint, or max_steps.
        
        Args:
            max_steps: Maximum instructions to execute
            
        Returns:
            ExecutionResult
        """
        # Clear halted flag to allow resuming after breakpoint/watchpoint
        self.halted = False
        
        executed = 0
        
        while executed < max_steps:
            result = self.step(1)
            executed += result.instruction_count
            
            if result.status != 'running':
                return ExecutionResult(
                    result.status,
                    executed,
                    result.error,
                    result.pc
                )
        
        return ExecutionResult('max_steps', executed, pc=self.cpu.pc)
    
    def run_until_output(self, max_steps=100000):
        """
        Run until console UART has new output or execution stops.
        
        Args:
            max_steps: Maximum instructions to execute
            
        Returns:
            ExecutionResult
        """
        # FIXED: Check console UART for output (NetHack writes to console, not debug)
        initial_output_len = len(self.memory.console_uart.get_output_text())
        
        for i in range(max_steps):
            result = self.step(1)
            
            # Check if we have new output on CONSOLE UART
            current_output_len = len(self.memory.console_uart.get_output_text())
            if current_output_len > initial_output_len:
                return ExecutionResult('running', result.instruction_count, pc=self.cpu.pc)
            
            # Check if execution stopped
            if result.status != 'running':
                return result
        
        return ExecutionResult('max_steps', max_steps, pc=self.cpu.pc)
    
    def run_until_console_status_read(self, max_steps=1000000):
        """
        Run until a read instruction accesses Console UART RX Status register (0x10001008).
        This is useful for detecting when a program is polling for input.
        
        Temporarily sets a read watchpoint at 0x10001008, runs until hit, then removes it.
        If a watchpoint already exists at that address, it will be left in place.
        
        Args:
            max_steps: Maximum instructions to execute
            
        Returns:
            ExecutionResult with status 'halted' if polling detected,
            or other status if execution stopped for another reason
        """
        CONSOLE_UART_RX_STATUS_ADDR = 0x10001008
        
        # Check if watchpoint already exists
        had_watchpoint = CONSOLE_UART_RX_STATUS_ADDR in self.memory.read_watchpoints
        if not had_watchpoint:
            self.add_read_watchpoint(CONSOLE_UART_RX_STATUS_ADDR)
        
        # Run normally - watchpoint will break execution
        result = self.run(max_steps)
        
        # Remove temporary watchpoint if we added it
        if not had_watchpoint:
            if CONSOLE_UART_RX_STATUS_ADDR in self.memory.read_watchpoints:
                self.remove_read_watchpoint(CONSOLE_UART_RX_STATUS_ADDR)
        
        return result
    
    # UART I/O methods
    
    # Debug UART (0x10000000) - TX only, typically used by printf/diagnostics
    
    def debug_uart_read(self):
        """
        Read any new debug UART TX output.
        
        Returns:
            String of new output since last read
        """
        full_output = self.memory.uart.get_output_text()
        new_output = full_output[self._debug_uart_read_pos:]
        self._debug_uart_read_pos = len(full_output)
        return new_output
    
    def debug_uart_read_all(self):
        """
        Read all debug UART TX output (including already-read data).
        
        Returns:
            Complete output string
        """
        return self.memory.uart.get_output_text()
    
    def debug_uart_has_data(self):
        """
        Check if debug UART has new output.
        
        Returns:
            True if there's unread output
        """
        full_output = self.memory.uart.get_output_text()
        return len(full_output) > self._debug_uart_read_pos
    
    # Console UART (0x10001000) - TX/RX for interactive I/O
    
    def console_uart_read(self):
        """
        Read any new console UART TX output.
        
        Returns:
            String of new output since last read
        """
        full_output = self.memory.console_uart.get_output_text()
        new_output = full_output[self._console_uart_read_pos:]
        self._console_uart_read_pos = len(full_output)
        return new_output
    
    def console_uart_read_all(self):
        """
        Read all console UART TX output (including already-read data).
        
        Returns:
            Complete output string
        """
        return self.memory.console_uart.get_output_text()
    
    def console_uart_write(self, data):
        """
        Write data to console UART RX (simulator stdin).
        
        Args:
            data: String or bytes to send to program
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        print(f"[CONSOLE_UART_WRITE] Writing {len(data)} bytes to RX buffer", flush=True)
        
        # Directly add to RX buffer for programmatic control
        for byte in data:
            self.memory.console_uart.rx_buffer.append(byte)
        
        print(f"[CONSOLE_UART_WRITE] RX buffer now has {len(self.memory.console_uart.rx_buffer)} bytes", flush=True)
    
    def console_uart_has_data(self):
        """
        Check if console UART has new output.
        
        Returns:
            True if there's unread output
        """
        full_output = self.memory.console_uart.get_output_text()
        return len(full_output) > self._console_uart_read_pos
    
    # Legacy/convenience methods - default to debug UART for backward compatibility
    
    def uart_read(self):
        """Read from debug UART (legacy method)."""
        return self.debug_uart_read()
    
    def uart_read_all(self):
        """Read all from debug UART (legacy method)."""
        return self.debug_uart_read_all()
    
    def uart_write(self, data):
        """Write to console UART RX (legacy method)."""
        return self.console_uart_write(data)
    
    def uart_has_data(self):
        """Check debug UART has data (legacy method)."""
        return self.debug_uart_has_data()
    
    # Register/Memory access
    
    def get_registers(self):
        """Get copy of all registers as dict"""
        return {
            'pc': self.cpu.pc,
            'x0': 0,  # Always zero
            **{f'x{i}': self.cpu.regs[i] for i in range(1, 32)}
        }
    
    def get_register(self, reg):
        """
        Get value of a register.
        
        Args:
            reg: Register number (0-31) or name ('x0', 'a0', 'sp', etc.)
            
        Returns:
            Register value
        """
        if isinstance(reg, str):
            # Convert name to number
            if reg == 'pc':
                return self.cpu.pc
            if reg.startswith('x'):
                reg = int(reg[1:])
            else:
                # ABI names
                abi_names = {
                    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
                    't0': 5, 't1': 6, 't2': 7,
                    's0': 8, 'fp': 8, 's1': 9,
                    'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
                    's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
                    't3': 28, 't4': 29, 't5': 30, 't6': 31
                }
                reg = abi_names.get(reg, 0)
        
        if reg == 0:
            return 0
        return self.cpu.regs[reg]
    
    def set_register(self, reg, value):
        """
        Set value of a register.
        
        Args:
            reg: Register number (0-31) or name
            value: Value to set
        """
        # Convert name to number first
        reg_num = reg
        if isinstance(reg, str):
            if reg == 'pc':
                self.cpu.pc = value & 0xFFFFFFFF
                return
            if reg.startswith('x'):
                reg_num = int(reg[1:])
            else:
                # ABI names
                abi_names = {
                    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
                    't0': 5, 't1': 6, 't2': 7,
                    's0': 8, 'fp': 8, 's1': 9,
                    'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
                    's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
                    't3': 28, 't4': 29, 't5': 30, 't6': 31
                }
                reg_num = abi_names.get(reg, 0)
        
        if reg_num == 0:
            return  # x0 is always zero
        
        self.cpu.regs[reg_num] = value & 0xFFFFFFFF
    
    def read_memory(self, address, length):
        """
        Read bytes from memory.
        
        Args:
            address: Memory address
            length: Number of bytes to read
            
        Returns:
            bytes object
        """
        data = bytearray()
        for i in range(length):
            data.append(self.memory.read_byte(address + i))
        return bytes(data)
    
    def write_memory(self, address, data):
        """
        Write bytes to memory.
        
        Args:
            address: Memory address
            data: bytes or bytearray to write
        """
        for i, byte in enumerate(data):
            self.memory.write_byte(address + i, byte)
    
    # Breakpoint management
    
    def add_breakpoint(self, address=None, reg_name=None, reg_value=None):
        """
        Add a breakpoint.
        
        Args:
            address: PC address (optional)
            reg_name: Register name for conditional (optional)
            reg_value: Register value for conditional (optional)
            
        Returns:
            Breakpoint ID
        """
        bp = self.debugger.bp_manager.add(
            address=address,
            reg_name=reg_name,
            reg_value=reg_value
        )
        return bp.id
    
    def remove_breakpoint(self, bp_id):
        """Remove breakpoint by ID"""
        return self.debugger.bp_manager.delete(bp_id)
    
    def list_breakpoints(self):
        """Get list of all breakpoints"""
        return self.debugger.bp_manager.list()
    
    def clear_breakpoints(self):
        """Remove all breakpoints"""
        return self.debugger.bp_manager.delete_all()
    
    # Watchpoint management
    
    def add_read_watchpoint(self, address):
        """Add read watchpoint at memory address"""
        self.memory.add_read_watchpoint(address)
    
    def remove_read_watchpoint(self, address):
        """Remove read watchpoint"""
        self.memory.remove_read_watchpoint(address)
    
    def add_write_watchpoint(self, address):
        """Add write watchpoint at memory address"""
        self.memory.add_write_watchpoint(address)
    
    def remove_write_watchpoint(self, address):
        """Remove write watchpoint"""
        self.memory.remove_write_watchpoint(address)
    
    def clear_write_watchpoints(self):
        """Clear all write watchpoints"""
        self.memory.clear_write_watchpoints()
    
    def list_read_watchpoints(self):
        """List all read watchpoints"""
        return sorted(list(self.memory.read_watchpoints))
    
    def list_write_watchpoints(self):
        """List all write watchpoints"""
        return sorted(list(self.memory.write_watchpoints))
    
    # Status queries
    
    def is_halted(self):
        """Check if system is halted"""
        return self.halted
    
    def get_pc(self):
        """Get current program counter"""
        return self.cpu.pc
    
    def get_instruction_count(self):
        """Get total instructions executed"""
        return self.instruction_count
    
    def get_status(self):
        """
        Get system status.
        
        Returns:
            Dict with status information
        """
        # FIXED: Correctly check console UART output
        return {
            'halted': self.halted,
            'pc': self.cpu.pc,
            'instruction_count': self.instruction_count,
            'console_has_output': len(self.memory.console_uart.get_output_text()) > 0,
            'breakpoint_count': len(self.debugger.bp_manager.list())
        }
    
    # VT100 Terminal screen commands
    
    def get_screen_display(self):
        """
        Get VT100 terminal screen as list of lines.
        
        Returns:
            List of 24 strings (80 chars each), or None if not available
        """
        return self.memory.console_uart.get_screen_display()
    
    def get_screen_text(self):
        """
        Get VT100 terminal screen as single string.
        
        Returns:
            String with newline-separated lines, or None if not available
        """
        return self.memory.console_uart.get_screen_text()
    
    def dump_screen(self, show_cursor=True):
        """
        Dump VT100 screen to log and return it.
        
        Args:
            show_cursor: Include cursor position in output
            
        Returns:
            Screen text, or None if not available
        """
        return self.memory.console_uart.dump_screen(show_cursor=show_cursor)
    
    def inject_console_input(self, data):
        """
        Inject input into console UART RX buffer.
        
        Args:
            data: String or bytes to inject
        """
        self.memory.console_uart.inject_input(data)
