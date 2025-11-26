"""
Memory Module - Simple byte-addressable memory with memory-mapped UART

Features:
- Byte-addressable memory (simple dict-based, sparse)
- Memory-mapped UART TX at 0x10000000
- Memory-mapped millisecond timer at 0x10000004
- Little-endian byte ordering
- Memory access fault detection for invalid addresses
"""

import time
from uart import UART, UART_TX_ADDR
from exceptions import MemoryAccessFault


class Memory:
    """
    Simple byte-addressable memory.
    
    Uses a dictionary for sparse memory (only stores written addresses).
    Handles UART as memory-mapped I/O at address 0x10000000.
    Handles millisecond timer at address 0x10000004.
    
    Valid address ranges:
    - 0x80000000 - 0x807FFFFF: RAM (8MB)
    - 0x10000000: UART TX register
    - 0x10000004: Millisecond timer (read-only, uint32)
    """
    
    # Memory map constants
    RAM_BASE = 0x80000000
    RAM_SIZE = 8 * 1024 * 1024  # 8MB
    RAM_END = RAM_BASE + RAM_SIZE - 1
    
    UART_BASE = 0x10000000
    UART_END = 0x10000000  # Only single address supported (TX register)
    
    TIMER_ADDR = 0x10000004  # Millisecond timer (32-bit read-only)
    
    def __init__(self):
        # Sparse memory - dict mapping address to byte value
        self.mem = {}
        
        # UART peripheral
        self.uart = UART()
        
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
        
        # Check UART (single address only)
        if address == UART_TX_ADDR:
            return True
        
        # Check timer (4 bytes: 0x10000004 - 0x10000007)
        if 0x10000004 <= address <= 0x10000007:
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
        
        # Initialize timer on first access
        if self.timer_start is None:
            self.timer_start = time.time()
        
        # Reading from UART address returns 0 (no RX implemented)
        if address == UART_TX_ADDR:
            return self.uart.rx_byte()
        
        # Reading from timer (0x10000004-0x10000007)
        if 0x10000004 <= address <= 0x10000007:
            elapsed_ms = int((time.time() - self.timer_start) * 1000)
            elapsed_ms = elapsed_ms & 0xFFFFFFFF  # Keep as 32-bit
            # Return appropriate byte (little-endian)
            byte_offset = address - 0x10000004
            return (elapsed_ms >> (byte_offset * 8)) & 0xFF
        
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
        
        # Initialize timer on first access
        if self.timer_start is None:
            self.timer_start = time.time()
        
        # UART TX - transmit byte
        if address == UART_TX_ADDR:
            self.uart.tx_byte(value)
            return
        
        # Timer is read-only, writes are ignored
        if 0x10000004 <= address <= 0x10000007:
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
