"""
UART Module - Simple simulated UART TX

Provides a memory-mapped UART transmitter that writes raw binary data
to a file, exactly as transmitted by the RISC-V program.
"""

import tempfile


# UART TX address (memory-mapped I/O)
UART_TX_ADDR = 0x10000000


class UART:
    """
    Simple UART TX simulator.
    
    Writes transmitted bytes to a binary file, preserving exact data.
    No RX implemented - reads from UART address return 0.
    """
    
    def __init__(self):
        # UART output file (binary mode for raw data)
        self.tx_file = tempfile.NamedTemporaryFile(
            mode='wb',
            delete=False,
            prefix='pyrv32_uart_',
            suffix='.bin'
        )
        self.tx_path = self.tx_file.name
    
    def tx_byte(self, value):
        """
        Transmit a byte via UART.
        
        Args:
            value: Byte value to transmit (0-255)
        """
        value = value & 0xFF
        self.tx_file.write(bytes([value]))
        self.tx_file.flush()
    
    def rx_byte(self):
        """
        Receive a byte from UART.
        
        Returns:
            Always returns 0 (RX not implemented)
        """
        return 0
    
    def get_output(self):
        """
        Get all UART output as raw bytes.
        
        Returns:
            bytes object containing all transmitted data
        """
        self.tx_file.flush()
        with open(self.tx_path, 'rb') as f:
            return f.read()
    
    def get_output_text(self, encoding='utf-8', errors='replace'):
        """
        Get UART output decoded as text.
        
        Args:
            encoding: Text encoding to use (default: utf-8)
            errors: How to handle decode errors (default: replace with �)
            
        Returns:
            Decoded text string
        """
        return self.get_output().decode(encoding, errors=errors)
    
    def clear(self):
        """
        Clear UART output buffer.
        """
        self.tx_file.close()
        self.tx_file = tempfile.NamedTemporaryFile(
            mode='wb',
            delete=False,
            prefix='pyrv32_uart_',
            suffix='.bin'
        )
        self.tx_path = self.tx_file.name
    
    def reset(self):
        """
        Reset UART (same as clear).
        """
        self.clear()
    
    def close(self):
        """
        Close UART resources.
        """
        self.tx_file.close()
