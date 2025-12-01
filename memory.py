"""
Memory Module - Byte-addressable memory with dual UART system

Features:
- Byte-addressable memory (sparse dict-based)
- Debug UART at 0x10000000 (TX only, for diagnostics)
- Console UART at 0x10001000-0x10001008 (TX/RX for user I/O)
- Memory-mapped millisecond timer at 0x10000004
- Little-endian byte ordering
- Memory access fault detection
"""

import time
from uart import (
    UART, ConsoleUART,
    DEBUG_UART_TX_ADDR,
    CONSOLE_UART_TX_ADDR, CONSOLE_UART_RX_ADDR, CONSOLE_UART_RX_STATUS_ADDR
)
from exceptions import MemoryAccessFault


class WatchpointHit:
    """Marker for when a watchpoint is hit during memory access"""
    def __init__(self, address, access_type):
        self.address = address
        self.access_type = access_type  # 'read' or 'write'

class Memory:
    """
    Byte-addressable memory with dual UART system.
    
    Uses a dictionary for sparse memory (only stores written addresses).
    
    Memory Map:
    - 0x80000000 - 0x807FFFFF: RAM (8MB)
    - 0x10000000: Debug UART TX (write-only)
    - 0x10000004: Millisecond timer (read-only, 32-bit)
    - 0x10000008: Unix time - seconds since epoch (read-only, 32-bit)
    - 0x1000000C: Nanoseconds within current second (read-only, 32-bit, 0-999999999)
    - 0x10001000: Console UART TX (write-only)
    - 0x10001004: Console UART RX (read-only, 0xFF if no data)
    - 0x10001008: Console UART RX Status (read-only, 0=no data, 1=data available)
    """
    
    # Memory map constants
    RAM_BASE = 0x80000000
    RAM_SIZE = 8 * 1024 * 1024  # 8MB
    RAM_END = RAM_BASE + RAM_SIZE - 1
    
    # Debug UART
    DEBUG_UART_TX = DEBUG_UART_TX_ADDR
    
    # Timer and clock
    TIMER_ADDR = 0x10000004          # Millisecond timer
    CLOCK_TIME_ADDR = 0x10000008     # Unix time (seconds)
    CLOCK_NSEC_ADDR = 0x1000000C     # Nanoseconds within second
    
    # Console UART
    CONSOLE_UART_TX = CONSOLE_UART_TX_ADDR
    CONSOLE_UART_RX = CONSOLE_UART_RX_ADDR
    CONSOLE_UART_RX_STATUS = CONSOLE_UART_RX_STATUS_ADDR
    
    def __init__(self, use_console_pty=False, save_console_output=True, save_console_raw=None):
        """
        Initialize memory system.
        
        Args:
            use_console_pty: If True, create PTY for Console UART. 
                           If False, use stdin/stdout (simpler for testing).
            save_console_output: If True, buffer Console UART output for display at end.
            save_console_raw: If provided, save raw console TX bytes to this file path.
        """
        # Sparse memory - dict mapping address to byte value
        self.mem = {}
        
        # Watchpoint hits for current instruction (cleared after each instruction)
        self.pending_watchpoints = []
        
        # Debug UART (TX only, for printf debugging)
        self.uart = UART()
        
        # Console UART (TX/RX for user interaction)
        self.console_uart = ConsoleUART(use_pty=use_console_pty, save_output=save_console_output,
                                        save_raw_output=save_console_raw)
        
        # Memory watchpoints for debugging
        self.read_watchpoints = set()   # Addresses to watch for reads
        self.write_watchpoints = set()  # Addresses to watch for writes
        
        # Timer - records start time when first instruction executes
        self.timer_start = None
        
        # Current PC for fault reporting (set by CPU before each access)
        self.current_pc = 0
    
    def is_valid_address(self, address):
        """Check if address is in a valid memory region."""
        address = address & 0xFFFFFFFF
        
        # Check RAM range
        if self.RAM_BASE <= address <= self.RAM_END:
            return True
        
        # Debug UART TX
        if address == self.DEBUG_UART_TX:
            return True
        
        # Timer (4 bytes: 0x10000004 - 0x10000007)
        if 0x10000004 <= address <= 0x10000007:
            return True
        
        # Unix time clock (4 bytes: 0x10000008 - 0x1000000B)
        if 0x10000008 <= address <= 0x1000000B:
            return True
        
        # Nanosecond clock (4 bytes: 0x1000000C - 0x1000000F)
        if 0x1000000C <= address <= 0x1000000F:
            return True
        
        # Console UART (TX, RX, RX Status)
        if address in (self.CONSOLE_UART_TX, self.CONSOLE_UART_RX, self.CONSOLE_UART_RX_STATUS):
            return True
        
        return False
    
    def read_byte(self, address):
        """
        Read a byte from memory.
        
        Args:
            address: 32-bit memory address
            
        Returns:
            Byte value (0-255), or 0 if never written (within valid range)
            
        Raises:
            MemoryAccessFault: If address is outside valid memory regions
        """
        address = address & 0xFFFFFFFF
        
        # Check if address is valid
        if not self.is_valid_address(address):
            raise MemoryAccessFault(address, 'load', self.current_pc)
        
        # Check read watchpoints - record hit but don't break yet
        if address in self.read_watchpoints:
            wp_hit = WatchpointHit(address, 'read')
            self.pending_watchpoints.append(wp_hit)
            print(f"\n[READ WATCHPOINT] Read from {address:#x} (PC={self.current_pc:#x})")
            
            # Auto-dump VT100 screen when reading console RX status (0x10001008)
            if address == 0x10001008 and hasattr(self, 'console_uart'):
                screen_text = self.console_uart.dump_screen(show_cursor=True)
                if screen_text:
                    print(f"[SCREEN DUMP] Captured screen at RX status read")
        
        # Initialize timer on first access
        if self.timer_start is None:
            self.timer_start = time.time()
        
        # Debug UART read returns 0 (no RX)
        if address == self.DEBUG_UART_TX:
            return 0
        
        # Timer read (0x10000004-0x10000007) - milliseconds since start
        if 0x10000004 <= address <= 0x10000007:
            elapsed_ms = int((time.time() - self.timer_start) * 1000)
            elapsed_ms = elapsed_ms & 0xFFFFFFFF  # Keep as 32-bit
            # Return appropriate byte (little-endian)
            byte_offset = address - 0x10000004
            return (elapsed_ms >> (byte_offset * 8)) & 0xFF
        
        # Unix time read (0x10000008-0x1000000B) - seconds since epoch
        if 0x10000008 <= address <= 0x1000000B:
            unix_time = int(time.time())
            unix_time = unix_time & 0xFFFFFFFF  # Keep as 32-bit
            # Return appropriate byte (little-endian)
            byte_offset = address - 0x10000008
            return (unix_time >> (byte_offset * 8)) & 0xFF
        
        # Nanosecond read (0x1000000C-0x1000000F) - nanoseconds within current second
        if 0x1000000C <= address <= 0x1000000F:
            current_time = time.time()
            nanoseconds = int((current_time - int(current_time)) * 1_000_000_000)
            nanoseconds = nanoseconds & 0xFFFFFFFF  # Keep as 32-bit
            # Return appropriate byte (little-endian)
            byte_offset = address - 0x1000000C
            return (nanoseconds >> (byte_offset * 8)) & 0xFF
        
        # Console UART TX read returns 0 (write-only)
        if address == self.CONSOLE_UART_TX:
            return 0
        
        # Console UART RX - read byte (0xFF if no data)
        if address == self.CONSOLE_UART_RX:
            return self.console_uart.rx_byte()
        
        # Console UART RX Status - check for data
        if address == self.CONSOLE_UART_RX_STATUS:
            return self.console_uart.rx_status()
        
        # Normal memory read
        return self.mem.get(address, 0)
    
    def write_byte(self, address, value):
        """
        Write a byte to memory.
        
        Args:
            address: 32-bit memory address
            value: Byte value to write (0-255)
            
        Raises:
            MemoryAccessFault: If address is outside valid memory regions
        """
        address = address & 0xFFFFFFFF
        value = value & 0xFF
        
        # Check if address is valid
        if not self.is_valid_address(address):
            raise MemoryAccessFault(address, 'store', self.current_pc)
        
        # Check write watchpoints - record hit but don't break yet
        if address in self.write_watchpoints:
            wp_hit = WatchpointHit(address, 'write')
            self.pending_watchpoints.append(wp_hit)
            print(f"\n[WRITE WATCHPOINT] Write to {address:#x} = {value:#04x} (PC={self.current_pc:#x})")
        
        # Initialize timer on first access
        if self.timer_start is None:
            self.timer_start = time.time()
        
        # Debug UART TX - transmit byte
        if address == self.DEBUG_UART_TX:
            self.uart.tx_byte(value)
            return
        
        # Timer is read-only, writes are ignored
        if 0x10000004 <= address <= 0x10000007:
            return
        
        # Unix time is read-only, writes are ignored
        if 0x10000008 <= address <= 0x1000000B:
            return
        
        # Nanoseconds is read-only, writes are ignored
        if 0x1000000C <= address <= 0x1000000F:
            return
        
        # Console UART TX - transmit byte
        if address == self.CONSOLE_UART_TX:
            self.console_uart.tx_byte(value)
            return
        
        # Console UART RX is read-only, writes ignored
        if address == self.CONSOLE_UART_RX:
            return
        
        # Console UART RX Status is read-only, writes ignored
        if address == 0x10001008:
            return
        
        # Normal memory write
        self.mem[address] = value
    
    def read_halfword(self, address):
        """
        Read a 16-bit halfword (little-endian).
        
        Args:
            address: Memory address (should be 2-byte aligned)
            
        Returns:
            16-bit value
        """
        b0 = self.read_byte(address)
        b1 = self.read_byte(address + 1)
        return b0 | (b1 << 8)
    
    def write_halfword(self, address, value):
        """
        Write a 16-bit halfword (little-endian).
        
        Args:
            address: Memory address (should be 2-byte aligned)
            value: 16-bit value to write
        """
        value = value & 0xFFFF
        self.write_byte(address, value & 0xFF)
        self.write_byte(address + 1, (value >> 8) & 0xFF)
    
    def read_word(self, address):
        """
        Read a 32-bit word (little-endian).
        
        Args:
            address: Memory address (should be 4-byte aligned)
            
        Returns:
            32-bit value
        """
        b0 = self.read_byte(address)
        b1 = self.read_byte(address + 1)
        b2 = self.read_byte(address + 2)
        b3 = self.read_byte(address + 3)
        return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
    
    def write_word(self, address, value):
        """
        Write a 32-bit word (little-endian).
        
        Args:
            address: Memory address (should be 4-byte aligned)
            value: 32-bit value to write
        """
        value = value & 0xFFFFFFFF
        self.write_byte(address, value & 0xFF)
        self.write_byte(address + 1, (value >> 8) & 0xFF)
        self.write_byte(address + 2, (value >> 16) & 0xFF)
        self.write_byte(address + 3, (value >> 24) & 0xFF)
    
    def load_program(self, address, data):
        """
        Load program data into memory.
        
        Args:
            address: Starting address
            data: Bytes or list of bytes to load
        """
        for i, byte in enumerate(data):
            self.write_byte(address + i, byte)
    
    def get_uart_output(self):
        """
        Get the current UART output as text.
        
        Returns:
            String of all UART output (UTF-8 decoded, errors replaced)
        """
        return self.uart.get_output_text()
    
    def get_uart_output_raw(self):
        """
        Get the current UART output as raw bytes.
        
        Returns:
            bytes object containing all transmitted data
        """
        return self.uart.get_output()
    
    def clear_uart(self):
        """
        Clear UART output.
        """
        self.uart.clear()
    
    def reset(self):
        """
        Reset memory (clear all).
        """
        self.mem.clear()
        self.uart.reset()
        # Note: Don't reset console_uart - it maintains its PTY connection
    
    def add_read_watchpoint(self, address):
        """Add a read watchpoint at the specified address."""
        self.read_watchpoints.add(address & 0xFFFFFFFF)
    
    def add_write_watchpoint(self, address):
        """Add a write watchpoint at the specified address."""
        self.write_watchpoints.add(address & 0xFFFFFFFF)
    
    def remove_read_watchpoint(self, address):
        """Remove a read watchpoint."""
        self.read_watchpoints.discard(address & 0xFFFFFFFF)
    
    def remove_write_watchpoint(self, address):
        """Remove a write watchpoint."""
        self.write_watchpoints.discard(address & 0xFFFFFFFF)
    
    def clear_watchpoints(self):
        """Clear all watchpoints."""
        self.read_watchpoints.clear()
        self.write_watchpoints.clear()
    
    def check_pending_watchpoints(self):
        """
        Check if any watchpoints were hit during the last instruction.
        Returns the list of watchpoint hits and clears the pending list.
        """
        hits = self.pending_watchpoints[:]
        self.pending_watchpoints.clear()
        return hits