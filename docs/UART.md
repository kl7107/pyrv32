# UART Module

The pyrv32 simulator includes a memory-mapped UART transmitter for program output.

## Architecture

The UART is implemented as a separate module (`uart.py`) that the memory system delegates to. This provides clean separation of concerns and realistic hardware behavior.

### Memory-Mapped Address

- **UART TX Address**: `0x10000000`
- **Access**: Write-only (reads return 0)
- Writing a byte to this address transmits it via UART

## Implementation

### Module: `uart.py`

The UART module provides a simple transmit-only UART implementation:

```python
from uart import UART, UART_TX_ADDR

uart = UART()
```

**Key Features:**
- **Binary output**: Writes raw bytes to a temporary file (not text with escape sequences)
- **Two output modes**: Raw bytes or UTF-8 decoded text
- **Clean API**: Simple methods for transmit, receive, clear, and reset

### API Reference

#### `tx_byte(value)`
Transmit a single byte.

```python
uart.tx_byte(0x48)  # Send 'H'
uart.tx_byte(0x0A)  # Send newline
```

**Parameters:**
- `value` (int): Byte value (0-255), automatically masked to 8 bits

#### `rx_byte()`
Receive a byte (currently not implemented, returns 0).

```python
byte = uart.rx_byte()  # Returns 0 (no RX)
```

**Returns:** Always 0 (receive not implemented)

#### `get_output()`
Get transmitted data as raw bytes.

```python
raw = uart.get_output()
print(raw)  # b'Hello\n'
```

**Returns:** `bytes` object containing all transmitted data

#### `get_output_text()`
Get transmitted data as UTF-8 decoded text.

```python
text = uart.get_output_text()
print(text)  # "Hello\n"
```

**Returns:** String (UTF-8 decoded with replacement characters for invalid sequences)

**Error Handling:** Invalid UTF-8 bytes are replaced with � (U+FFFD)

#### `clear()`
Clear the UART buffer.

```python
uart.clear()  # Discard all transmitted data
```

#### `reset()`
Reset the UART (same as clear).

```python
uart.reset()  # Clear buffer and reset state
```

## Usage from Memory

The Memory class automatically handles UART through memory-mapped I/O:

```python
from memory import Memory, UART_TX_ADDR

mem = Memory()

# Write to UART via memory
mem.write_byte(UART_TX_ADDR, ord('H'))
mem.write_byte(UART_TX_ADDR, ord('i'))
mem.write_byte(UART_TX_ADDR, 0x0A)  # newline

# Get output as text
text = mem.get_uart_output()
print(text)  # "Hi\n"

# Get output as raw bytes
raw = mem.get_uart_output_raw()
print(raw)  # b'Hi\n'

# Clear UART buffer
mem.clear_uart()
```

## Binary vs Text Output

The UART writes **raw binary data**, not text with escape sequences:

```python
mem.write_byte(UART_TX_ADDR, 0x48)  # 'H'
mem.write_byte(UART_TX_ADDR, 0x0A)  # Actual newline char, not "\x0a" string
mem.write_byte(UART_TX_ADDR, 0x09)  # Actual tab char, not "\x09" string

text = mem.get_uart_output()
# text == "H\n\t" (actual whitespace chars)
```

This matches real hardware behavior where the UART transmits exact byte values.

## Example: Hello World

```python
from memory import Memory, UART_TX_ADDR

mem = Memory()
uart_addr = UART_TX_ADDR

# Transmit "Hello\n"
for char in b'Hello\n':
    mem.write_byte(uart_addr, char)

# Get output
output = mem.get_uart_output()
print(output)  # "Hello\n"
```

## Assembly Example

```assembly
# Load UART address
lui  x10, 0x10000        # x10 = 0x10000000

# Output 'H' (ASCII 72)
addi x11, x0, 72         # x11 = 72
sb   x11, 0(x10)         # Write to UART

# Output newline (ASCII 10)
addi x11, x0, 10         # x11 = 10
sb   x11, 0(x10)         # Write to UART
```

## Implementation Details

### Temporary File

The UART uses a temporary file for output storage:
- **Mode**: Binary (`'wb'`)
- **Location**: System temp directory (`/tmp/pyrv32_uart_*.bin`)
- **Lifecycle**: Created on UART initialization, persists until cleared/reset
- **Access**: Seekable for re-reading output

### UTF-8 Decoding

When reading as text via `get_output_text()`:
- Decodes as UTF-8
- Invalid sequences replaced with � (U+FFFD)
- Preserves all valid characters including whitespace

Example:
```python
mem.write_byte(UART_TX_ADDR, 0xFF)  # Invalid UTF-8
text = mem.get_uart_output()
# text == "�" (replacement character)

raw = mem.get_uart_output_raw()
# raw == b'\xff' (exact byte)
```

## Testing

The UART module is fully tested in `tests/test_memory.py`:
- Binary character output (newlines, tabs, control chars)
- Invalid UTF-8 handling
- Clear/reset functionality
- Memory-mapped I/O integration

See `docs/TESTING.md` for complete test coverage details.
