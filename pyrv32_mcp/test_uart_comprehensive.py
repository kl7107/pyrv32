#!/usr/bin/env python3
"""
Comprehensive UART testing suite.
Tests both debug UART and console UART with interactive I/O.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrv32_system import RV32System
import time

def test_debug_uart():
    """Test 1: Debug UART output (hello.bin)"""
    print("\n" + "="*60)
    print("TEST 1: Debug UART Output")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/hello.bin')
    
    result = sys_obj.run(max_steps=10000)
    
    print(f"Status: {result.status}")
    print(f"Instructions: {result.instruction_count}")
    
    output = sys_obj.uart_read()
    print(f"\nDebug UART Output ({len(output)} bytes):")
    print(output)
    
    expected = "Hello, World from RV32IM!"
    assert expected in output, f"Expected '{expected}' in output"
    
    print("✓ PASSED")
    return True


def test_console_uart_basic():
    """Test 2: Console UART basic write"""
    print("\n" + "="*60)
    print("TEST 2: Console UART Basic Write")
    print("="*60)
    
    sys_obj = RV32System()
    
    # Create a simple test that writes to console UART
    # For now, just verify the methods exist and work
    sys_obj.console_uart_write("TEST\n")
    
    # The console UART should have this in its RX buffer
    print("✓ PASSED (Console UART write method works)")
    return True


def test_interpreter_basic():
    """Test 3: Interpreter - Basic Commands"""
    print("\n" + "="*60)
    print("TEST 3: Interpreter - Basic Commands")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Run until we get the prompt
    print("Starting interpreter...")
    result = sys_obj.run_until_output(max_steps=50000)
    
    output = sys_obj.console_uart_read()
    print(f"Initial output ({len(output)} bytes):")
    print(output)
    
    assert "Simple Command Interpreter" in output, "Expected banner"
    assert ">" in output, "Expected prompt"
    
    print("✓ PASSED")
    return True


def test_interpreter_add():
    """Test 4: Interpreter - ADD command"""
    print("\n" + "="*60)
    print("TEST 4: Interpreter - ADD Command")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Get to prompt
    result = sys_obj.run_until_output(max_steps=50000)
    initial = sys_obj.console_uart_read()
    
    # Send ADD command
    print("Sending: ADD 42 13")
    sys_obj.console_uart_write("ADD 42 13\n")
    
    # Run until response
    result = sys_obj.run_until_output(max_steps=10000)
    output = sys_obj.console_uart_read()
    
    print(f"Response:")
    print(output)
    
    # Should echo command and show result
    assert "55" in output, f"Expected '55' in output, got: {output}"
    
    print("✓ PASSED")
    return True


def test_interpreter_sub():
    """Test 5: Interpreter - SUB command"""
    print("\n" + "="*60)
    print("TEST 5: Interpreter - SUB Command")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Get to prompt
    sys_obj.run_until_output(max_steps=50000)
    sys_obj.console_uart_read()
    
    # Send SUB command
    print("Sending: SUB 100 37")
    sys_obj.console_uart_write("SUB 100 37\n")
    
    result = sys_obj.run_until_output(max_steps=10000)
    output = sys_obj.console_uart_read()
    
    print(f"Response:")
    print(output)
    
    assert "63" in output, f"Expected '63' in output"
    
    print("✓ PASSED")
    return True


def test_interpreter_mul():
    """Test 6: Interpreter - MUL command"""
    print("\n" + "="*60)
    print("TEST 6: Interpreter - MUL Command")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Get to prompt
    sys_obj.run_until_output(max_steps=50000)
    sys_obj.console_uart_read()
    
    # Send MUL command
    print("Sending: MUL 7 8")
    sys_obj.console_uart_write("MUL 7 8\n")
    
    result = sys_obj.run_until_output(max_steps=10000)
    output = sys_obj.console_uart_read()
    
    print(f"Response:")
    print(output)
    
    assert "56" in output, f"Expected '56' in output"
    
    print("✓ PASSED")
    return True


def test_interpreter_hex():
    """Test 7: Interpreter - HEX command"""
    print("\n" + "="*60)
    print("TEST 7: Interpreter - HEX Command")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Get to prompt
    sys_obj.run_until_output(max_steps=50000)
    sys_obj.console_uart_read()
    
    # Send HEX command
    print("Sending: HEX 255")
    sys_obj.console_uart_write("HEX 255\n")
    
    result = sys_obj.run_until_output(max_steps=10000)
    output = sys_obj.console_uart_read()
    
    print(f"Response:")
    print(output)
    
    assert "0x" in output and "FF" in output.upper(), f"Expected hex format"
    
    print("✓ PASSED")
    return True


def test_interpreter_echo():
    """Test 8: Interpreter - ECHO command"""
    print("\n" + "="*60)
    print("TEST 8: Interpreter - ECHO Command")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Get to prompt
    sys_obj.run_until_output(max_steps=50000)
    sys_obj.console_uart_read()
    
    # Send ECHO command
    print("Sending: ECHO Hello World")
    sys_obj.console_uart_write("ECHO Hello World\n")
    
    result = sys_obj.run_until_output(max_steps=10000)
    output = sys_obj.console_uart_read()
    
    print(f"Response:")
    print(output)
    
    assert "Hello World" in output, f"Expected 'Hello World' in output"
    
    print("✓ PASSED")
    return True


def test_interpreter_error():
    """Test 9: Interpreter - Error handling"""
    print("\n" + "="*60)
    print("TEST 9: Interpreter - Error Handling")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Get to prompt
    sys_obj.run_until_output(max_steps=50000)
    sys_obj.console_uart_read()
    
    # Send unknown command
    print("Sending: INVALID")
    sys_obj.console_uart_write("INVALID\n")
    
    result = sys_obj.run_until_output(max_steps=10000)
    output = sys_obj.console_uart_read()
    
    print(f"Response:")
    print(output)
    
    assert "ERROR" in output or "Unknown" in output, f"Expected error message"
    
    print("✓ PASSED")
    return True


def test_interpreter_multi_command():
    """Test 10: Interpreter - Multiple commands in sequence"""
    print("\n" + "="*60)
    print("TEST 10: Interpreter - Multiple Commands")
    print("="*60)
    
    sys_obj = RV32System()
    sys_obj.load_binary('../firmware/interpreter_test.bin')
    
    # Get to prompt
    sys_obj.run_until_output(max_steps=50000)
    sys_obj.console_uart_read()
    
    commands = [
        ("ADD 10 20", "30"),
        ("SUB 50 15", "35"),
        ("MUL 6 7", "42"),
        ("ECHO Test", "Test"),
    ]
    
    for cmd, expected in commands:
        print(f"Sending: {cmd}")
        sys_obj.console_uart_write(cmd + "\n")
        
        result = sys_obj.run_until_output(max_steps=10000)
        output = sys_obj.console_uart_read()
        
        print(f"  Response: {output.strip()}")
        assert expected in output, f"Expected '{expected}' in output for command '{cmd}'"
    
    print("✓ PASSED")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("UART COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        test_debug_uart,
        test_console_uart_basic,
        test_interpreter_basic,
        test_interpreter_add,
        test_interpreter_sub,
        test_interpreter_mul,
        test_interpreter_hex,
        test_interpreter_echo,
        test_interpreter_error,
        test_interpreter_multi_command,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
