"""
Unit Tests for Memory Module

Tests memory operations and UART functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import Memory
from uart import DEBUG_UART_TX_ADDR as UART_TX_ADDR


def test_read_unwritten_memory_returns_zero(runner):
    """Read unwritten memory returns 0"""
    mem = Memory()
    result = mem.read_byte(0x80001000)
    runner.log(f"  mem.read_byte(0x80001000) = 0x{result:02x}")
    if result != 0:
        runner.test_fail("Unwritten memory", "0x00", f"0x{result:02x}")


def test_write_and_read_byte(runner):
    """Write and read byte"""
    mem = Memory()
    mem.write_byte(0x80001000, 0x42)
    result = mem.read_byte(0x80001000)
    runner.log(f"  mem.write_byte(0x80001000, 0x42)")
    runner.log(f"  mem.read_byte(0x80001000) = 0x{result:02x}")
    if result != 0x42:
        runner.test_fail("Byte read/write", "0x42", f"0x{result:02x}")


def test_write_and_read_halfword(runner):
    """Write and read halfword (little-endian)"""
    mem = Memory()
    mem.write_halfword(0x80002000, 0x1234)
    result = mem.read_halfword(0x80002000)
    b0 = mem.read_byte(0x80002000)
    b1 = mem.read_byte(0x80002001)
    runner.log(f"  mem.write_halfword(0x80002000, 0x1234)")
    runner.log(f"  mem.read_halfword(0x80002000) = 0x{result:04x}")
    runner.log(f"  Byte 0: 0x{b0:02x}, Byte 1: 0x{b1:02x} (little-endian)")
    if result != 0x1234 or b0 != 0x34 or b1 != 0x12:
        runner.test_fail("Halfword read/write", "0x1234", f"0x{result:04x}")


def test_write_and_read_word(runner):
    """Write and read word (little-endian)"""
    mem = Memory()
    mem.write_word(0x80003000, 0xDEADBEEF)
    result = mem.read_word(0x80003000)
    b0 = mem.read_byte(0x80003000)
    b1 = mem.read_byte(0x80003001)
    b2 = mem.read_byte(0x80003002)
    b3 = mem.read_byte(0x80003003)
    runner.log(f"  mem.write_word(0x80003000, 0xDEADBEEF)")
    runner.log(f"  mem.read_word(0x80003000) = 0x{result:08x}")
    runner.log(f"  Bytes: 0x{b0:02x} {b1:02x} {b2:02x} {b3:02x} (little-endian)")
    if result != 0xDEADBEEF or b0 != 0xEF or b1 != 0xBE or b2 != 0xAD or b3 != 0xDE:
        runner.test_fail("Word read/write", "0xDEADBEEF", f"0x{result:08x}")


def test_uart_tx_writes(runner):
    """UART TX writes to file"""
    mem = Memory()
    mem.write_byte(UART_TX_ADDR, ord('H'))
    mem.write_byte(UART_TX_ADDR, ord('i'))
    mem.write_byte(UART_TX_ADDR, ord('!'))
    uart_output = mem.get_uart_output()
    runner.log(f"  Wrote 'H', 'i', '!' to UART")
    runner.log(f"  UART output: '{uart_output}'")
    if uart_output != "Hi!":
        runner.test_fail("UART output", "'Hi!'", f"'{uart_output}'")


def test_uart_read_returns_zero(runner):
    """UART read returns 0"""
    mem = Memory()
    result = mem.read_byte(UART_TX_ADDR)
    runner.log(f"  mem.read_byte(UART_TX_ADDR) = 0x{result:02x}")
    if result != 0:
        runner.test_fail("UART read", "0x00", f"0x{result:02x}")


def test_load_program(runner):
    """Load program"""
    mem = Memory()
    program = [0x11, 0x22, 0x33, 0x44]
    mem.load_program(0x80004000, program)
    for i, expected in enumerate(program):
        result = mem.read_byte(0x80004000 + i)
        runner.log(f"  mem[0x{0x80004000+i:04x}] = 0x{result:02x} (expected 0x{expected:02x})")
        if result != expected:
            runner.test_fail(f"Load program byte {i}", f"0x{expected:02x}", f"0x{result:02x}")


def test_memory_sparseness(runner):
    """Memory is sparse (dict-based)"""
    mem = Memory()
    # Test sparseness within valid 8MB RAM (0x80000000-0x807FFFFF)
    mem.write_byte(0x80000000, 0xFF)  # Start of RAM
    mem.write_byte(0x80400000, 0xAA)  # Middle of RAM (4MB offset)
    result1 = mem.read_byte(0x80000000)
    result2 = mem.read_byte(0x80400000)
    result3 = mem.read_byte(0x80200000)  # Unwritten address in between (2MB offset)
    runner.log(f"  mem[0x80000000] = 0x{result1:02x}")
    runner.log(f"  mem[0x80400000] = 0x{result2:02x}")
    runner.log(f"  mem[0x80200000] = 0x{result3:02x} (unwritten)")
    if result1 != 0xFF or result2 != 0xAA or result3 != 0:
        runner.test_fail("Sparse memory", "0xFF, 0xAA, 0x00", f"0x{result1:02x}, 0x{result2:02x}, 0x{result3:02x}")


def test_clear_uart(runner):
    """clear_uart() clears UART output"""
    mem = Memory()
    mem.write_byte(UART_TX_ADDR, ord('T'))
    mem.write_byte(UART_TX_ADDR, ord('e'))
    mem.write_byte(UART_TX_ADDR, ord('s'))
    mem.write_byte(UART_TX_ADDR, ord('t'))
    uart_before = mem.get_uart_output()
    runner.log(f"  UART before clear: '{uart_before}'")
    if uart_before != "Test":
        runner.test_fail("UART before clear", "'Test'", f"'{uart_before}'")
    mem.clear_uart()
    uart_after = mem.get_uart_output()
    runner.log(f"  UART after clear: '{uart_after}'")
    if uart_after != "":
        runner.test_fail("UART after clear", "''", f"'{uart_after}'")


def test_uart_raw_binary(runner):
    """UART writes raw binary (newlines, tabs, etc.)"""
    mem = Memory()
    mem.clear_uart()
    mem.write_byte(UART_TX_ADDR, ord('A'))
    mem.write_byte(UART_TX_ADDR, 0x0A)  # newline
    mem.write_byte(UART_TX_ADDR, ord('B'))
    mem.write_byte(UART_TX_ADDR, 0x09)  # tab
    mem.write_byte(UART_TX_ADDR, ord('C'))
    uart_output = mem.get_uart_output()
    expected = "A\nB\tC"
    runner.log(f"  UART output: {repr(uart_output)}")
    runner.log(f"  Expected: {repr(expected)}")
    if uart_output != expected:
        runner.test_fail("UART raw binary chars", expected, uart_output)


def test_uart_invalid_utf8(runner):
    """UART handles invalid UTF-8"""
    mem = Memory()
    mem.clear_uart()
    mem.write_byte(UART_TX_ADDR, 0xFF)  # Invalid UTF-8
    mem.write_byte(UART_TX_ADDR, 0x80)  # Invalid UTF-8
    mem.write_byte(UART_TX_ADDR, 0x00)  # Null byte
    uart_output = mem.get_uart_output()
    runner.log(f"  UART output length: {len(uart_output)} chars")
    runner.log(f"  UART output: {repr(uart_output)}")
    if len(uart_output) != 3:
        runner.test_fail("UART invalid UTF-8", "3 chars", f"{len(uart_output)} chars")


def test_memory_address_wraparound(runner):
    """Memory address access at upper end of valid RAM"""
    mem = Memory()
    # Test at the last valid address in 8MB RAM (0x80000000 + 8MB - 1)
    addr = 0x807FFFFF
    mem.write_byte(addr, 0x99)
    result = mem.read_byte(addr)
    runner.log(f"  mem[0x{addr:08x}] = 0x{result:02x}")
    if result != 0x99:
        runner.test_fail("Max valid RAM address write", "0x99", f"0x{result:02x}")


def test_misaligned_halfword(runner):
    """Misaligned halfword access"""
    mem = Memory()
    mem.write_halfword(0x80005001, 0xABCD)  # Odd address
    result = mem.read_halfword(0x80005001)
    b0 = mem.read_byte(0x80005001)
    b1 = mem.read_byte(0x80005002)
    runner.log(f"  mem.write_halfword(0x80005001, 0xABCD) [misaligned]")
    runner.log(f"  mem.read_halfword(0x80005001) = 0x{result:04x}")
    runner.log(f"  Bytes: 0x{b0:02x} {b1:02x}")
    if result != 0xABCD or b0 != 0xCD or b1 != 0xAB:
        runner.test_fail("Misaligned halfword", "0xABCD", f"0x{result:04x}")


def test_misaligned_word(runner):
    """Misaligned word access"""
    mem = Memory()
    mem.write_word(0x80006001, 0x12345678)  # Misaligned by 1 byte
    result = mem.read_word(0x80006001)
    runner.log(f"  mem.write_word(0x80006001, 0x12345678) [misaligned]")
    runner.log(f"  mem.read_word(0x80006001) = 0x{result:08x}")
    if result != 0x12345678:
        runner.test_fail("Misaligned word", "0x12345678", f"0x{result:08x}")


def test_reset_clears_memory_and_uart(runner):
    """reset() clears memory and UART"""
    mem = Memory()
    mem.write_byte(0x80007000, 0x55)
    mem.write_byte(UART_TX_ADDR, ord('X'))
    mem.reset()
    result_mem = mem.read_byte(0x80007000)
    result_uart = mem.get_uart_output()
    runner.log(f"  After reset: mem[0x80007000] = 0x{result_mem:02x}")
    runner.log(f"  After reset: UART = '{result_uart}'")
    if result_mem != 0:
        runner.test_fail("Reset memory", "0x00", f"0x{result_mem:02x}")
    if result_uart != "":
        runner.test_fail("Reset UART", "''", f"'{result_uart}'")
