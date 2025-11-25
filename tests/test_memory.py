"""
Unit Tests for Memory Module

Tests memory operations and UART functionality.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import Memory, UART_TX_ADDR


def run_memory_tests():
    """Run all memory tests."""
    log_file = tempfile.NamedTemporaryFile(mode='w', delete=False,
                                           prefix='pyrv32_test_memory_', suffix='.log')
    log_path = log_file.name
    
    def log(msg):
        log_file.write(msg + '\n')
        log_file.flush()
    
    def test_fail(test_name, expected, actual, context=""):
        log(f"\n{'=' * 60}")
        log(f"TEST FAILED: {test_name}")
        log(f"Expected: {expected}")
        log(f"Actual:   {actual}")
        if context:
            log(f"Context:  {context}")
        log(f"Log file: {log_path}")
        log(f"{'=' * 60}\n")
        log_file.close()
        print(f"\n{'=' * 60}")
        print(f"TEST FAILED: {test_name}")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        if context:
            print(f"Context:  {context}")
        print(f"Log file: {log_path}")
        print(f"{'=' * 60}\n")
        sys.exit(1)
    
    log("=" * 60)
    log("Running Memory Unit Tests")
    log(f"Log file: {log_path}")
    log("=" * 60)
    
    mem = Memory()
    
    # Test 1: Read unwritten memory returns 0
    log("\nTest 1: Read unwritten memory returns 0")
    result = mem.read_byte(0x1000)
    log(f"  mem.read_byte(0x1000) = 0x{result:02x}")
    if result != 0:
        test_fail("Unwritten memory", "0x00", f"0x{result:02x}")
    log("  ✓ PASS")
    
    # Test 2: Write and read byte
    log("\nTest 2: Write and read byte")
    mem.write_byte(0x1000, 0x42)
    result = mem.read_byte(0x1000)
    log(f"  mem.write_byte(0x1000, 0x42)")
    log(f"  mem.read_byte(0x1000) = 0x{result:02x}")
    if result != 0x42:
        test_fail("Byte read/write", "0x42", f"0x{result:02x}")
    log("  ✓ PASS")
    
    # Test 3: Write and read halfword (little-endian)
    log("\nTest 3: Write and read halfword")
    mem.write_halfword(0x2000, 0x1234)
    result = mem.read_halfword(0x2000)
    b0 = mem.read_byte(0x2000)
    b1 = mem.read_byte(0x2001)
    log(f"  mem.write_halfword(0x2000, 0x1234)")
    log(f"  mem.read_halfword(0x2000) = 0x{result:04x}")
    log(f"  Byte 0: 0x{b0:02x}, Byte 1: 0x{b1:02x} (little-endian)")
    if result != 0x1234 or b0 != 0x34 or b1 != 0x12:
        test_fail("Halfword read/write", "0x1234", f"0x{result:04x}")
    log("  ✓ PASS")
    
    # Test 4: Write and read word (little-endian)
    log("\nTest 4: Write and read word")
    mem.write_word(0x3000, 0xDEADBEEF)
    result = mem.read_word(0x3000)
    b0 = mem.read_byte(0x3000)
    b1 = mem.read_byte(0x3001)
    b2 = mem.read_byte(0x3002)
    b3 = mem.read_byte(0x3003)
    log(f"  mem.write_word(0x3000, 0xDEADBEEF)")
    log(f"  mem.read_word(0x3000) = 0x{result:08x}")
    log(f"  Bytes: 0x{b0:02x} {b1:02x} {b2:02x} {b3:02x} (little-endian)")
    if result != 0xDEADBEEF or b0 != 0xEF or b1 != 0xBE or b2 != 0xAD or b3 != 0xDE:
        test_fail("Word read/write", "0xDEADBEEF", f"0x{result:08x}")
    log("  ✓ PASS")
    
    # Test 5: UART TX writes to file
    log("\nTest 5: UART TX writes to file")
    mem.write_byte(UART_TX_ADDR, ord('H'))
    mem.write_byte(UART_TX_ADDR, ord('i'))
    mem.write_byte(UART_TX_ADDR, ord('!'))
    uart_output = mem.get_uart_output()
    log(f"  Wrote 'H', 'i', '!' to UART")
    log(f"  UART output: '{uart_output}'")
    if uart_output != "Hi!":
        test_fail("UART output", "'Hi!'", f"'{uart_output}'")
    log("  ✓ PASS")
    
    # Test 6: UART read returns 0
    log("\nTest 6: UART read returns 0")
    result = mem.read_byte(UART_TX_ADDR)
    log(f"  mem.read_byte(UART_TX_ADDR) = 0x{result:02x}")
    if result != 0:
        test_fail("UART read", "0x00", f"0x{result:02x}")
    log("  ✓ PASS")
    
    # Test 7: Load program
    log("\nTest 7: Load program")
    program = [0x11, 0x22, 0x33, 0x44]
    mem.load_program(0x4000, program)
    for i, expected in enumerate(program):
        result = mem.read_byte(0x4000 + i)
        log(f"  mem[0x{0x4000+i:04x}] = 0x{result:02x} (expected 0x{expected:02x})")
        if result != expected:
            test_fail(f"Load program byte {i}", f"0x{expected:02x}", f"0x{result:02x}")
    log("  ✓ PASS")
    
    # Test 8: Memory is sparse (dict-based)
    log("\nTest 8: Memory sparseness")
    mem.write_byte(0x100000, 0xFF)
    mem.write_byte(0x200000, 0xAA)
    result1 = mem.read_byte(0x100000)
    result2 = mem.read_byte(0x200000)
    result3 = mem.read_byte(0x150000)  # Unwritten address in between
    log(f"  mem[0x100000] = 0x{result1:02x}")
    log(f"  mem[0x200000] = 0x{result2:02x}")
    log(f"  mem[0x150000] = 0x{result3:02x} (unwritten)")
    if result1 != 0xFF or result2 != 0xAA or result3 != 0:
        test_fail("Sparse memory", "0xFF, 0xAA, 0x00", f"0x{result1:02x}, 0x{result2:02x}, 0x{result3:02x}")
    log("  ✓ PASS")
    
    # Test 9: clear_uart() clears UART output
    log("\nTest 9: clear_uart() clears UART output")
    mem = Memory()  # Fresh instance for clean UART state
    mem.write_byte(UART_TX_ADDR, ord('T'))
    mem.write_byte(UART_TX_ADDR, ord('e'))
    mem.write_byte(UART_TX_ADDR, ord('s'))
    mem.write_byte(UART_TX_ADDR, ord('t'))
    uart_before = mem.get_uart_output()
    log(f"  UART before clear: '{uart_before}'")
    if uart_before != "Test":
        test_fail("UART before clear", "'Test'", f"'{uart_before}'")
    mem.clear_uart()
    uart_after = mem.get_uart_output()
    log(f"  UART after clear: '{uart_after}'")
    if uart_after != "":
        test_fail("UART after clear", "''", f"'{uart_after}'")
    log("  ✓ PASS")
    
    # Test 10: UART writes raw binary (newlines, tabs, etc.)
    # NOTE: UART now writes raw bytes, so \n is actual newline, \t is actual tab
    log("\nTest 10: UART writes raw binary characters")
    mem.clear_uart()
    mem.write_byte(UART_TX_ADDR, ord('A'))
    mem.write_byte(UART_TX_ADDR, 0x0A)  # newline - actual \n character
    mem.write_byte(UART_TX_ADDR, ord('B'))
    mem.write_byte(UART_TX_ADDR, 0x09)  # tab - actual \t character
    mem.write_byte(UART_TX_ADDR, ord('C'))
    uart_output = mem.get_uart_output()
    expected = "A\nB\tC"  # Actual newline and tab characters
    log(f"  UART output: {repr(uart_output)}")
    log(f"  Expected: {repr(expected)}")
    if uart_output != expected:
        test_fail("UART raw binary chars", expected, uart_output)
    log("  ✓ PASS")
    
    # Test 11: UART handles invalid UTF-8 with replacement characters
    log("\nTest 11: UART handles invalid UTF-8")
    mem.clear_uart()
    mem.write_byte(UART_TX_ADDR, 0xFF)  # Invalid UTF-8
    mem.write_byte(UART_TX_ADDR, 0x80)  # Invalid UTF-8
    mem.write_byte(UART_TX_ADDR, 0x00)  # Null byte
    uart_output = mem.get_uart_output()
    log(f"  UART output length: {len(uart_output)} chars")
    log(f"  UART output: {repr(uart_output)}")
    # UTF-8 decode with 'replace' should give 3 characters (replacement chars + null)
    if len(uart_output) != 3:
        test_fail("UART invalid UTF-8", "3 chars", f"{len(uart_output)} chars")
    log("  ✓ PASS")
    
    # Test 12: Memory address wraparound at 32-bit boundary
    log("\nTest 12: Memory address wraparound")
    # Write at max 32-bit address
    mem.write_byte(0xFFFFFFFF, 0x99)
    result = mem.read_byte(0xFFFFFFFF)
    log(f"  mem[0xFFFFFFFF] = 0x{result:02x}")
    if result != 0x99:
        test_fail("Max address write", "0x99", f"0x{result:02x}")
    log("  ✓ PASS")
    
    # Test 13: Misaligned halfword access
    log("\nTest 13: Misaligned halfword access")
    mem.write_halfword(0x5001, 0xABCD)  # Odd address
    result = mem.read_halfword(0x5001)
    b0 = mem.read_byte(0x5001)
    b1 = mem.read_byte(0x5002)
    log(f"  mem.write_halfword(0x5001, 0xABCD) [misaligned]")
    log(f"  mem.read_halfword(0x5001) = 0x{result:04x}")
    log(f"  Bytes: 0x{b0:02x} {b1:02x}")
    if result != 0xABCD or b0 != 0xCD or b1 != 0xAB:
        test_fail("Misaligned halfword", "0xABCD", f"0x{result:04x}")
    log("  ✓ PASS (implementation allows misaligned access)")
    
    # Test 14: Misaligned word access
    log("\nTest 14: Misaligned word access")
    mem.write_word(0x6001, 0x12345678)  # Misaligned by 1 byte
    result = mem.read_word(0x6001)
    log(f"  mem.write_word(0x6001, 0x12345678) [misaligned]")
    log(f"  mem.read_word(0x6001) = 0x{result:08x}")
    if result != 0x12345678:
        test_fail("Misaligned word", "0x12345678", f"0x{result:08x}")
    log("  ✓ PASS (implementation allows misaligned access)")
    
    # Test 15: reset() clears memory and UART
    log("\nTest 15: reset() clears memory and UART")
    mem.write_byte(0x7000, 0x55)
    mem.write_byte(UART_TX_ADDR, ord('X'))
    mem.reset()
    result_mem = mem.read_byte(0x7000)
    result_uart = mem.get_uart_output()
    log(f"  After reset: mem[0x7000] = 0x{result_mem:02x}")
    log(f"  After reset: UART = '{result_uart}'")
    if result_mem != 0:
        test_fail("Reset memory", "0x00", f"0x{result_mem:02x}")
    if result_uart != "":
        test_fail("Reset UART", "''", f"'{result_uart}'")
    log("  ✓ PASS")
    
    log("\n" + "=" * 60)
    log("ALL MEMORY TESTS PASSED ✓")
    log(f"Log file: {log_path}")
    log("=" * 60 + "\n")
    
    log_file.close()
    return log_path


if __name__ == "__main__":
    log_path = run_memory_tests()
    print(f"Memory tests PASSED ✓ (log: {log_path})")
