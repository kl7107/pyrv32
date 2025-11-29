"""
UART Module - Dual UART system with Debug and Console

Provides two independent UARTs:
1. Debug UART (0x10000000): TX only, writes to stdout/file for diagnostics
2. Console UART (0x10001000-0x10001008): TX/RX with PTY/terminal emulation
"""

import tempfile
import sys
import os
import pty
import select
import termios
import fcntl


# Debug UART (TX only, for diagnostics)
DEBUG_UART_TX_ADDR = 0x10000000

# Console UART (TX/RX for user interaction)
CONSOLE_UART_TX_ADDR = 0x10001000
CONSOLE_UART_RX_ADDR = 0x10001004
CONSOLE_UART_RX_STATUS_ADDR = 0x10001008

# Legacy alias
UART_TX_ADDR = DEBUG_UART_TX_ADDR


class UART:
    """
    Debug UART - Simple TX-only for diagnostics.
    
    Writes transmitted bytes to a binary file, preserving exact data.
    Also writes to stdout for immediate visibility.
    No RX implemented - reads return 0.
    """
    
    def __init__(self):
        # UART output file (binary mode for raw data)
        self.tx_file = tempfile.NamedTemporaryFile(
            mode='wb',
            delete=False,
            prefix='pyrv32_debug_uart_',
            suffix='.bin'
        )
        self.tx_path = self.tx_file.name
    
    def tx_byte(self, value):
        """
        Transmit a byte via Debug UART.
        
        Args:
            value: Byte value to transmit (0-255)
        """
        value = value & 0xFF
        byte_data = bytes([value])
        self.tx_file.write(byte_data)
        self.tx_file.flush()
        # Also write to stdout for immediate visibility
        sys.stdout.buffer.write(byte_data)
        sys.stdout.buffer.flush()
    
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
            prefix='pyrv32_debug_uart_',
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


class ConsoleUART:
    """
    Console UART - Full duplex TX/RX with PTY/terminal support.
    
    Provides:
    - TX: Write bytes to terminal (appears on terminal display)
    - RX: Read bytes from keyboard (buffered, infinite capacity)
    - RX Status: Check if input data is available
    
    Can operate in two modes:
    1. PTY mode: Creates a pseudo-terminal (use with screen/minicom/etc.)
    2. Direct mode: Uses stdin/stdout (for simple testing)
    """
    
    def __init__(self, use_pty=False, save_output=True, save_raw_output=None):
        """
        Initialize Console UART.
        
        Args:
            use_pty: If True, create a PTY. If False, use stdin/stdout.
            save_output: If True, buffer all TX output for display at end.
            save_raw_output: If provided, save all TX bytes to this file path.
        """
        self.use_pty = use_pty
        self.save_output = save_output
        self.rx_buffer = bytearray()
        self.tx_buffer = bytearray() if save_output else None
        self.save_raw_output = save_raw_output
        self.raw_output_file = None
        
        if save_raw_output:
            self.raw_output_file = open(save_raw_output, 'wb')
            print(f"[Console UART] Saving raw TX output to: {save_raw_output}", file=sys.stderr)
        
        if use_pty:
            # Create PTY for terminal emulation
            self.master_fd, self.slave_fd = pty.openpty()
            self.slave_name = os.ttyname(self.slave_fd)
            
            # Make master non-blocking for reads
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # Set raw mode on PTY
            attrs = termios.tcgetattr(self.master_fd)
            attrs[3] = attrs[3] & ~(termios.ECHO | termios.ICANON)
            termios.tcsetattr(self.master_fd, termios.TCSANOW, attrs)
            
            print(f"[Console UART] PTY created: {self.slave_name}", file=sys.stderr)
            print(f"[Console UART] Connect with: screen {self.slave_name}", file=sys.stderr)
        else:
            # Direct mode - only set up stdin if NOT in buffer-only mode
            if not save_output:
                # Use stdin (make non-blocking)
                self.master_fd = sys.stdin.fileno()
                flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
                fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                print("[Console UART] Direct mode (stdin/stdout)", file=sys.stderr)
            else:
                # Buffer-only mode - no stdin/stdout interaction
                self.master_fd = None
                print("[Console UART] Buffer-only mode (headless)", file=sys.stderr)
    
    def _poll_input(self):
        """Poll for new input and add to RX buffer."""
        if self.master_fd is None:
            # Buffer-only mode - no input polling
            return
            
        try:
            if self.use_pty:
                # Read from PTY
                data = os.read(self.master_fd, 1024)
                if data:
                    self.rx_buffer.extend(data)
            else:
                # Read from stdin
                data = os.read(self.master_fd, 1024)
                if data:
                    self.rx_buffer.extend(data)
        except (OSError, IOError):
            # No data available (EAGAIN/EWOULDBLOCK)
            pass
    
    def tx_byte(self, value):
        """
        Transmit a byte to console terminal.
        
        Args:
            value: Byte value to transmit (0-255)
        """
        value = value & 0xFF
        byte_data = bytes([value])
        
        # Save to buffer if enabled
        if self.save_output and self.tx_buffer is not None:
            self.tx_buffer.append(value)
        
        # Save raw output to file if enabled
        if self.raw_output_file:
            self.raw_output_file.write(byte_data)
            self.raw_output_file.flush()
        
        if self.use_pty:
            os.write(self.master_fd, byte_data)
        elif not self.save_output:
            # Only write to stdout if we're NOT saving to buffer
            # (if save_output=True, we're in headless/server mode)
            sys.stdout.buffer.write(byte_data)
            sys.stdout.buffer.flush()
    
    def rx_byte(self):
        """
        Receive a byte from console terminal.
        
        Returns:
            Byte value (0-255), or 0xFF if no data available
        """
        self._poll_input()
        
        if self.rx_buffer:
            return self.rx_buffer.pop(0)
        else:
            return 0xFF  # No data available
    
    def rx_status(self):
        """
        Check if RX data is available.
        
        Returns:
            0 if no data, 1 if data available
        """
        self._poll_input()
        return 1 if self.rx_buffer else 0
    
    def get_output(self):
        """
        Get all Console UART output as raw bytes.
        
        Returns:
            bytes object containing all transmitted data, or None if save_output=False
        """
        if self.tx_buffer is not None:
            return bytes(self.tx_buffer)
        return None
    
    def get_output_text(self, encoding='utf-8', errors='replace'):
        """
        Get Console UART output decoded as text.
        
        Args:
            encoding: Text encoding to use (default: utf-8)
            errors: How to handle decode errors (default: replace with �)
            
        Returns:
            Decoded text string, or None if save_output=False
        """
        output = self.get_output()
        if output is not None:
            return output.decode(encoding, errors=errors)
        return None
    
    def close(self):
        """
        Close Console UART resources.
        """
        if self.use_pty:
            os.close(self.master_fd)
            os.close(self.slave_fd)
