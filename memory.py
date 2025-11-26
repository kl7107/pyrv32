"""
Memory Module - Simple byte-addressable memory with memory-mapped UART

Features:
- Byte-addressable memory (simple dict-based, sparse)
- Memory-mapped UART TX at 0x10000000
- Little-endian byte ordering
- Memory access fault detection for invalid addresses
"""

from uart import UART, UART_TX_ADDR
from exceptions import MemoryAccessFault


class Memory:
    """
    Simple byte-addressable memory.
    
    Uses a dictionary for sparse memory (only stores written addresses).
    Handles UART as memory-mapped I/O at address 0x10000000.
    
    Valid address ranges:
    - 0x80000000 - 0x807FFFFF: RAM (8MB)
    - 0x10000000 - 0x10000FFF: UART (4KB peripheral region)
    """
    
    # Memory map constants
    RAM_BASE = 0x80000000
    RAM_SIZE = 8 * 1024 * 1024  # 8MB
    RAM_END = RAM_BASE + RAM_SIZE - 1
    
    UART_BASE = 0x10000000
    UART_END = 0x10000000  # Only single address supported (TX register)
    
    def __init__(self):
        # Sparse memory - dict mapping address to byte value
        self.mem = {}
        
        # UART peripheral
        self.uart = UART()
        
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
        
        # Reading from UART address returns 0 (no RX implemented)
        if address == UART_TX_ADDR:
            return self.uart.rx_byte()
        
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
        
        # UART TX - transmit byte
        if address == UART_TX_ADDR:
            self.uart.tx_byte(value)
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
