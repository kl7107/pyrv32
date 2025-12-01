"""
UART Module - Dual UART system with Debug and Console

Provides two independent UARTs:
1. Debug UART (0x10000000): TX only, writes to stdout/file for diagnostics
2. Console UART (0x10001000-0x10001008): TX/RX with PTY/terminal emulation + VT100 screen

Console UART now includes pyte virtual terminal for 80x24 VT100 emulation.
"""

import tempfile
import sys
import os
import pty
import select
import termios
import fcntl

try:
    import pyte
    PYTE_AVAILABLE = True
except ImportError:
    PYTE_AVAILABLE = False
    print("[Warning] pyte library not available - VT100 terminal emulation disabled", file=sys.stderr)


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
    Console UART - Full duplex TX/RX with PTY/terminal support + VT100 emulation.
    
    Provides:
    - TX: Write bytes to terminal (appears on terminal display)
    - RX: Read bytes from keyboard (buffered, infinite capacity)
    - RX Status: Check if input data is available
    - VT100 Emulation: 80x24 virtual screen using pyte library
    - Logging: Console TX/RX and screen dumps to /tmp
    
    Can operate in two modes:
    1. PTY mode: Creates a pseudo-terminal (use with screen/minicom/etc.)
    2. Direct mode: Uses stdin/stdout (for simple testing)
    """
    
    def __init__(self, use_pty=False, save_output=True, save_raw_output=None):
        """
        Initialize Console UART with VT100 terminal emulation.
        
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
        
        # VT100 terminal emulation with pyte
        if PYTE_AVAILABLE:
            self.screen = pyte.Screen(80, 24)
            self.stream = pyte.Stream(self.screen)
            self.vt100_enabled = True
            print("[Console UART] VT100 terminal emulation enabled (80x24)", file=sys.stderr)
        else:
            self.screen = None
            self.stream = None
            self.vt100_enabled = False
        
        # Logging files in /tmp
        self.tx_log = open('/tmp/console_tx.log', 'w')
        self.rx_log = open('/tmp/console_rx.log', 'w')
        self.screen_log = open('/tmp/screen_dump.log', 'w')
        self.last_screen_dump_time = 0  # Rate limit screen dumps
        self.last_screen_content = None  # Track screen changes
        print("[Console UART] Logging to /tmp/console_tx.log, /tmp/console_rx.log, /tmp/screen_dump.log", file=sys.stderr)
        
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
        char = chr(value)
        
        # Log TX to file
        if value >= 32 and value < 127:
            self.tx_log.write(char)
        else:
            self.tx_log.write(f'<0x{value:02x}>')
        self.tx_log.flush()
        
        # Feed to VT100 terminal emulator
        if self.vt100_enabled:
            self.stream.feed(char)
        
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
            byte_val = self.rx_buffer.pop(0)
            # Log RX to file
            if byte_val >= 32 and byte_val < 127:
                self.rx_log.write(chr(byte_val))
            else:
                self.rx_log.write(f'<0x{byte_val:02x}>')
            self.rx_log.flush()
            return byte_val
        else:
            return 0xFF  # No data available
    
    def rx_status(self):
        """
        Check if RX data is available.
        
        Returns:
            0 if no data, 1 if data available
        """
        self._poll_input()
        status = 1 if self.rx_buffer else 0
        # Debug logging
        if len(self.rx_buffer) > 0:
            print(f"[UART RX STATUS] Buffer has {len(self.rx_buffer)} bytes, returning status=1", flush=True)
        
        # Auto-dump screen when checking RX status and no data available (waiting for input)
        # Rate limit: only dump if screen changed or 1 second elapsed
        if status == 0 and PYTE_AVAILABLE and hasattr(self, 'screen'):
            import time
            current_time = time.time()
            current_screen = '\n'.join(self.screen.display)
            
            if (current_screen != self.last_screen_content or 
                current_time - self.last_screen_dump_time >= 1.0):
                self.dump_screen(show_cursor=True)
                self.last_screen_dump_time = current_time
                self.last_screen_content = current_screen
        
        return status
    
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
    
    def get_screen_display(self):
        """
        Get the current VT100 terminal screen as a list of lines.
        
        Returns:
            List of 24 strings (80 chars each), or None if VT100 disabled
        """
        if not self.vt100_enabled:
            return None
        return self.screen.display
    
    def get_screen_text(self):
        """
        Get the current VT100 terminal screen as a single string.
        
        Returns:
            String with lines separated by newlines, or None if VT100 disabled
        """
        if not self.vt100_enabled:
            return None
        return '\n'.join(self.screen.display)
    
    def dump_screen(self, show_cursor=True):
        """
        Dump the current VT100 screen to screen_dump.log and return it.
        
        Args:
            show_cursor: If True, show cursor position in output
            
        Returns:
            Screen text, or None if VT100 disabled
        """
        if not self.vt100_enabled:
            return None
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.screen_log.write(f"\n{'='*80}\n")
        self.screen_log.write(f"Screen dump at {timestamp}\n")
        if show_cursor:
            self.screen_log.write(f"Cursor: row={self.screen.cursor.y}, col={self.screen.cursor.x}\n")
        self.screen_log.write(f"{'='*80}\n")
        
        for i, line in enumerate(self.screen.display):
            self.screen_log.write(f"{i+1:2d} |{line}|\n")
        
        self.screen_log.write(f"{'='*80}\n")
        self.screen_log.flush()
        
        return self.get_screen_text()
    
    def inject_input(self, data):
        """
        Inject input data into the RX buffer (simulate keyboard input).
        
        Args:
            data: String or bytes to inject
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.rx_buffer.extend(data)
        
        # Log injected input
        for byte in data:
            if byte >= 32 and byte < 127:
                self.rx_log.write(chr(byte))
            else:
                self.rx_log.write(f'<0x{byte:02x}>')
        self.rx_log.flush()
    
    def close(self):
        """
        Close Console UART resources.
        """
        # Close log files
        self.tx_log.close()
        self.rx_log.close()
        self.screen_log.close()
        
        if self.use_pty:
            os.close(self.master_fd)
            os.close(self.slave_fd)
    
    def get_tx_data(self):
        """
        Get transmitted data (compatibility with old interface).
        
        Returns:
            bytes object of TX data
        """
        return self.get_output() or b''
