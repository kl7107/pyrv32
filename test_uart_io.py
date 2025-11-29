#!/usr/bin/env python3
"""
Comprehensive UART I/O test suite.

Tests both debug UART (0x10000000) and console UART (0x10001000) functionality,
including interactive input/output through the console UART RX/TX channels.
"""

import sys
import time
sys.path.insert(0, '/home/dev/git/zesarux/pyrv32')

from pyrv32_system import RV32System


class UARTTestSuite:
    """Test suite for UART I/O functionality."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test(self, name, func):
        """Run a single test."""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print('='*60)
        self.tests_run += 1
        
        try:
            func()
            self.tests_passed += 1
            print(f"✓ PASSED")
            return True
        except AssertionError as e:
            self.tests_failed += 1
            print(f"✗ FAILED: {e}")
            return False
        except Exception as e:
            self.tests_failed += 1
            print(f"✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def assert_equal(self, actual, expected, msg=""):
        """Assert two values are equal."""
        if actual != expected:
            raise AssertionError(f"{msg}\nExpected: {repr(expected)}\nActual:   {repr(actual)}")
    
    def assert_contains(self, text, substring, msg=""):
        """Assert text contains substring."""
        if substring not in text:
            raise AssertionError(f"{msg}\nExpected substring: {repr(substring)}\nNot found in: {repr(text)}")
    
    def summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total:  {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✓")
        print(f"Failed: {self.tests_failed} ✗")
        print(f"{'='*60}\n")
        return self.tests_failed == 0


# Test 1: Debug UART basic output
def test_debug_uart_basic():
    """Test that debug UART captures printf-style output."""
    sys = RV32System()
    sys.load_binary('firmware/hello.bin')
    
    # Run the program
    result = sys.run(max_steps=10000)
    
    # Check it halted successfully
    assert result.status == 'halted', f"Expected halted, got {result.status}"
    
    # Read debug UART output
    output = sys.debug_uart_read_all()
    
    # Verify expected strings
    assert 'Hello, World from RV32IM!' in output, "Missing hello message"
    assert 'PyRV32' in output, "Missing PyRV32 reference"
    assert '42 + 13 = 55' in output, "Missing arithmetic test"
    assert '0xDEADBEEF' in output, "Missing hex value"
    
    print(f"Debug UART output ({len(output)} bytes):")
    print(output)


# Test 2: Echo program basic functionality
def test_echo_basic():
    """Test echo program receives and echoes back characters."""
    sys = RV32System()
    sys.load_binary('firmware/echo_test.bin')
    
    # Run until we get the prompt
    sys.run_until_output(max_steps=10000)
    
    # Read the prompt
    prompt = sys.console_uart_read()
    print(f"Prompt received: {repr(prompt)}")
    assert 'Echo test ready' in prompt, "Missing ready message"
    
    # Send a test character
    sys.console_uart_write('A')
    
    # Run until output
    sys.run_until_output(max_steps=10000)
    
    # Should echo back
    echo = sys.console_uart_read()
    print(f"Echo received: {repr(echo)}")
    assert 'A' in echo, "Character not echoed"
    
    # Send quit command
    sys.console_uart_write('Q')
    sys.run(max_steps=10000)
    
    # Check quit message
    output = sys.console_uart_read()
    print(f"Quit message: {repr(output)}")
    assert 'Quitting' in output, "Missing quit message"


# Test 3: Echo multiple characters
def test_echo_multiple():
    """Test echo program with multiple characters."""
    sys = RV32System()
    sys.load_binary('firmware/echo_test.bin')
    
    # Skip prompt
    sys.run_until_output(max_steps=10000)
    sys.console_uart_read()
    
    test_string = "Hello123"
    
    for char in test_string:
        sys.console_uart_write(char)
        sys.run_until_output(max_steps=1000)
        echo = sys.console_uart_read()
        assert char in echo, f"Character {repr(char)} not echoed"
        print(f"  '{char}' -> '{echo.strip()}'")
    
    # Quit
    sys.console_uart_write('Q')
    sys.run(max_steps=10000)


# Test 4: Interpreter - ADD command
def test_interpreter_add():
    """Test interpreter ADD command."""
    sys = RV32System()
    sys.load_binary('firmware/interpreter_test.bin')
    
    # Skip welcome message
    sys.run_until_output(max_steps=10000)
    welcome = sys.console_uart_read()
    print(f"Welcome message: {repr(welcome[:100])}...")
    assert 'Command Interpreter' in welcome, "Missing welcome"
    
    # Wait for prompt
    while '>' not in sys.console_uart_read():
        sys.run_until_output(max_steps=1000)
    
    # Send ADD command
    cmd = "ADD 42 13\r"
    for char in cmd:
        sys.console_uart_write(char)
    
    # Run and get result
    sys.run_until_output(max_steps=10000)
    output = sys.console_uart_read()
    print(f"ADD result: {repr(output)}")
    
    # Should echo command and show result
    assert '55' in output or '55' in sys.console_uart_read_all(), "Incorrect ADD result"


# Test 5: Interpreter - SUB command
def test_interpreter_sub():
    """Test interpreter SUB command."""
    sys = RV32System()
    sys.load_binary('firmware/interpreter_test.bin')
    
    # Skip to prompt
    sys.run_until_output(max_steps=10000)
    sys.console_uart_read()
    while '>' not in sys.console_uart_read():
        sys.run_until_output(max_steps=1000)
    
    # Send SUB command
    cmd = "SUB 100 37\r"
    for char in cmd:
        sys.console_uart_write(char)
    
    sys.run_until_output(max_steps=10000)
    output = sys.console_uart_read_all()
    print(f"SUB result: {repr(output[-50:])}")
    
    assert '63' in output, "Incorrect SUB result (100-37=63)"


# Test 6: Interpreter - MUL command
def test_interpreter_mul():
    """Test interpreter MUL command."""
    sys = RV32System()
    sys.load_binary('firmware/interpreter_test.bin')
    
    # Skip to prompt
    sys.run_until_output(max_steps=10000)
    sys.console_uart_read()
    while '>' not in sys.console_uart_read():
        sys.run_until_output(max_steps=1000)
    
    # Send MUL command
    cmd = "MUL 12 7\r"
    for char in cmd:
        sys.console_uart_write(char)
    
    sys.run_until_output(max_steps=10000)
    output = sys.console_uart_read_all()
    print(f"MUL result: {repr(output[-50:])}")
    
    assert '84' in output, "Incorrect MUL result (12*7=84)"


# Test 7: Interpreter - HEX command
def test_interpreter_hex():
    """Test interpreter HEX command."""
    sys = RV32System()
    sys.load_binary('firmware/interpreter_test.bin')
    
    # Skip to prompt
    sys.run_until_output(max_steps=10000)
    sys.console_uart_read()
    while '>' not in sys.console_uart_read():
        sys.run_until_output(max_steps=1000)
    
    # Send HEX command
    cmd = "HEX 255\r"
    for char in cmd:
        sys.console_uart_write(char)
    
    sys.run_until_output(max_steps=10000)
    output = sys.console_uart_read_all()
    print(f"HEX result: {repr(output[-50:])}")
    
    assert '0x000000FF' in output or 'FF' in output, "Incorrect HEX result"


# Test 8: Interpreter - ECHO command
def test_interpreter_echo():
    """Test interpreter ECHO command."""
    sys = RV32System()
    sys.load_binary('firmware/interpreter_test.bin')
    
    # Skip to prompt
    sys.run_until_output(max_steps=10000)
    sys.console_uart_read()
    while '>' not in sys.console_uart_read():
        sys.run_until_output(max_steps=1000)
    
    # Send ECHO command
    cmd = "ECHO Hello World\r"
    for char in cmd:
        sys.console_uart_write(char)
    
    sys.run_until_output(max_steps=10000)
    output = sys.console_uart_read_all()
    print(f"ECHO result: {repr(output[-100:])}")
    
    assert 'Hello World' in output, "ECHO didn't return text"


# Test 9: Interpreter - error handling
def test_interpreter_errors():
    """Test interpreter error handling."""
    sys = RV32System()
    sys.load_binary('firmware/interpreter_test.bin')
    
    # Skip to prompt
    sys.run_until_output(max_steps=10000)
    sys.console_uart_read()
    while '>' not in sys.console_uart_read():
        sys.run_until_output(max_steps=1000)
    
    # Send invalid command
    cmd = "INVALID\r"
    for char in cmd:
        sys.console_uart_write(char)
    
    sys.run_until_output(max_steps=10000)
    output = sys.console_uart_read_all()
    print(f"Error response: {repr(output[-100:])}")
    
    assert 'ERROR' in output or 'Unknown' in output, "Should report error for invalid command"


# Test 10: Dual UART separation
def test_dual_uart_separation():
    """Test that debug and console UARTs are separate."""
    sys = RV32System()
    
    # Manually write to debug UART
    sys.memory.uart.tx_byte(ord('D'))
    sys.memory.uart.tx_byte(ord('E'))
    sys.memory.uart.tx_byte(ord('B'))
    
    # Manually write to console UART
    sys.memory.console_uart.tx_byte(ord('C'))
    sys.memory.console_uart.tx_byte(ord('O'))
    sys.memory.console_uart.tx_byte(ord('N'))
    
    # Read from each
    debug_out = sys.debug_uart_read_all()
    console_out = sys.console_uart_read_all()
    
    print(f"Debug UART: {repr(debug_out)}")
    print(f"Console UART: {repr(console_out)}")
    
    assert debug_out == 'DEB', f"Debug UART mismatch: {repr(debug_out)}"
    assert console_out == 'CON', f"Console UART mismatch: {repr(console_out)}"


def main():
    """Run all tests."""
    suite = UARTTestSuite()
    
    print("\n" + "="*60)
    print("UART I/O Test Suite")
    print("="*60)
    
    # Basic tests
    suite.test("Debug UART basic output", test_debug_uart_basic)
    suite.test("Dual UART separation", test_dual_uart_separation)
    
    # Echo tests
    suite.test("Echo program basic", test_echo_basic)
    suite.test("Echo multiple characters", test_echo_multiple)
    
    # Interpreter tests
    suite.test("Interpreter ADD command", test_interpreter_add)
    suite.test("Interpreter SUB command", test_interpreter_sub)
    suite.test("Interpreter MUL command", test_interpreter_mul)
    suite.test("Interpreter HEX command", test_interpreter_hex)
    suite.test("Interpreter ECHO command", test_interpreter_echo)
    suite.test("Interpreter error handling", test_interpreter_errors)
    
    # Summary
    success = suite.summary()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
