#!/usr/bin/env python3
"""
Memory Fault Tests - Verify memory access fault detection

Tests that the emulator correctly detects and reports invalid memory accesses.
All test functions receive a 'runner' object with log() and test_fail() methods.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory import Memory
from cpu import RV32CPU
from exceptions import MemoryAccessFault


def test_valid_ram_access(runner):
    """Test that valid RAM accesses work correctly"""
    mem = Memory()
    mem.current_pc = 0x80000000
    
    # Write to valid RAM addresses
    mem.write_byte(0x80000000, 0x42)
    mem.write_word(0x80000100, 0xDEADBEEF)
    mem.write_halfword(0x807FFF00, 0x1234)
    
    # Read back
    if mem.read_byte(0x80000000) != 0x42:
        runner.test_fail("test_valid_ram_access", 0x42, mem.read_byte(0x80000000))
    if mem.read_word(0x80000100) != 0xDEADBEEF:
        runner.test_fail("test_valid_ram_access", 0xDEADBEEF, mem.read_word(0x80000100))
    if mem.read_halfword(0x807FFF00) != 0x1234:
        runner.test_fail("test_valid_ram_access", 0x1234, mem.read_halfword(0x807FFF00))
    
    # Check end of RAM (last byte)
    mem.write_byte(0x807FFFFF, 0xFF)
    if mem.read_byte(0x807FFFFF) != 0xFF:
        runner.test_fail("test_valid_ram_access", 0xFF, mem.read_byte(0x807FFFFF))


def test_valid_uart_access(runner):
    """Test that UART TX address works correctly"""
    mem = Memory()
    mem.current_pc = 0x80000000
    
    # Write to UART
    mem.write_byte(0x10000000, 0x41)  # 'A'
    mem.write_byte(0x10000000, 0x42)  # 'B'
    
    # Read from UART (returns 0, no RX)
    if mem.read_byte(0x10000000) != 0:
        runner.test_fail("test_valid_uart_access", 0, mem.read_byte(0x10000000))
    
    # Check UART output
    output = mem.get_uart_output()
    if output != 'AB':
        runner.test_fail("test_valid_uart_access", 'AB', output)


def test_invalid_uart_offset(runner):
    """Test that UART+1 is invalid (only single address supported)"""
    mem = Memory()
    mem.current_pc = 0x80000000
    
    try:
        mem.write_byte(0x10000001, 0x42)
        runner.test_fail("test_invalid_uart_offset", "MemoryAccessFault", "no exception")
    except MemoryAccessFault as e:
        if e.address != 0x10000001:
            runner.test_fail("test_invalid_uart_offset", "0x10000001", f"0x{e.address:08x}")
        if e.access_type != 'store':
            runner.test_fail("test_invalid_uart_offset", "store", e.access_type)
        if e.pc != 0x80000000:
            runner.test_fail("test_invalid_uart_offset", "0x80000000", f"0x{e.pc:08x}")
    
    try:
        mem.read_byte(0x10000001)
        runner.test_fail("test_invalid_uart_offset", "MemoryAccessFault", "no exception")
    except MemoryAccessFault as e:
        if e.address != 0x10000001:
            runner.test_fail("test_invalid_uart_offset", "0x10000001", f"0x{e.address:08x}")
        if e.access_type != 'load':
            runner.test_fail("test_invalid_uart_offset", "load", e.access_type)


def test_read_below_ram(runner):
    """Test that reading below RAM base triggers fault"""
    mem = Memory()
    mem.current_pc = 0x80000100
    
    invalid_addresses = [
        0x00000000,  # Zero
        0x7FFFFFFF,  # Just below RAM
        0x00001000,  # Low memory
    ]
    
    for addr in invalid_addresses:
        try:
            mem.read_byte(addr)
            runner.test_fail("test_read_below_ram", "MemoryAccessFault", f"no exception at 0x{addr:08x}")
        except MemoryAccessFault as e:
            if e.address != addr:
                runner.test_fail("test_read_below_ram", f"0x{addr:08x}", f"0x{e.address:08x}")
            if e.access_type != 'load':
                runner.test_fail("test_read_below_ram", "load", e.access_type)
            if e.pc != 0x80000100:
                runner.test_fail("test_read_below_ram", "0x80000100", f"0x{e.pc:08x}")


def test_read_above_ram(runner):
    """Test that reading above RAM end triggers fault"""
    mem = Memory()
    mem.current_pc = 0x80000200
    
    invalid_addresses = [
        0x80800000,  # Just past end of 8MB RAM
        0x80800001,  # 
        0x90000000,  # Way above RAM
        0xFFFFFFFF,  # Top of address space
    ]
    
    for addr in invalid_addresses:
        try:
            mem.read_byte(addr)
            runner.test_fail("test_read_above_ram", "MemoryAccessFault", f"no exception at 0x{addr:08x}")
        except MemoryAccessFault as e:
            if e.address != addr:
                runner.test_fail("test_read_above_ram", f"0x{addr:08x}", f"0x{e.address:08x}")
            if e.access_type != 'load':
                runner.test_fail("test_read_above_ram", "load", e.access_type)
            if e.pc != 0x80000200:
                runner.test_fail("test_read_above_ram", "0x80000200", f"0x{e.pc:08x}")


def test_write_below_ram(runner):
    """Test that writing below RAM base triggers fault"""
    mem = Memory()
    mem.current_pc = 0x80000300
    
    invalid_addresses = [
        0x00000000,
        0x0FFFFFFF,  # End of reserved region
        0x50000000,  # Middle of unmapped space
    ]
    
    for addr in invalid_addresses:
        try:
            mem.write_byte(addr, 0x42)
            runner.test_fail("test_write_below_ram", "MemoryAccessFault", f"no exception at 0x{addr:08x}")
        except MemoryAccessFault as e:
            if e.address != addr:
                runner.test_fail("test_write_below_ram", f"0x{addr:08x}", f"0x{e.address:08x}")
            if e.access_type != 'store':
                runner.test_fail("test_write_below_ram", "store", e.access_type)
            if e.pc != 0x80000300:
                runner.test_fail("test_write_below_ram", "0x80000300", f"0x{e.pc:08x}")


def test_write_above_ram(runner):
    """Test that writing above RAM end triggers fault"""
    mem = Memory()
    mem.current_pc = 0x80000400
    
    invalid_addresses = [
        0x80800000,  # First byte past 8MB RAM
        0x81000000,
        0xA0000000,
        0xFFFFFFFF,
    ]
    
    for addr in invalid_addresses:
        try:
            mem.write_byte(addr, 0x42)
            runner.test_fail("test_write_above_ram", "MemoryAccessFault", f"no exception at 0x{addr:08x}")
        except MemoryAccessFault as e:
            if e.address != addr:
                runner.test_fail("test_write_above_ram", f"0x{addr:08x}", f"0x{e.address:08x}")
            if e.access_type != 'store':
                runner.test_fail("test_write_above_ram", "store", e.access_type)
            if e.pc != 0x80000400:
                runner.test_fail("test_write_above_ram", "0x80000400", f"0x{e.pc:08x}")


def test_word_access_spanning_boundary(runner):
    """Test word access at RAM boundary"""
    mem = Memory()
    mem.current_pc = 0x80000500
    
    # Valid: word access at end-3 (touches last 4 bytes of RAM)
    mem.write_word(0x807FFFFC, 0x12345678)
    if mem.read_word(0x807FFFFC) != 0x12345678:
        runner.test_fail("test_word_access_spanning_boundary", 0x12345678, mem.read_word(0x807FFFFC))
    
    # Invalid: word access at end (would extend past RAM)
    try:
        mem.write_word(0x807FFFFF, 0xDEADBEEF)
        # This writes 4 bytes: 0x807FFFFF, 0x80800000, 0x80800001, 0x80800002
        # The last 3 bytes are outside RAM
        runner.test_fail("test_word_access_spanning_boundary", "MemoryAccessFault", "no exception")
    except MemoryAccessFault as e:
        # Fault should occur on first invalid byte (0x80800000)
        if e.address != 0x80800000:
            runner.test_fail("test_word_access_spanning_boundary", "0x80800000", f"0x{e.address:08x}")
        if e.access_type != 'store':
            runner.test_fail("test_word_access_spanning_boundary", "store", e.access_type)


def test_halfword_access_spanning_boundary(runner):
    """Test halfword access at RAM boundary"""
    mem = Memory()
    mem.current_pc = 0x80000600
    
    # Valid: halfword at end-1 (last 2 bytes)
    mem.write_halfword(0x807FFFFE, 0xABCD)
    if mem.read_halfword(0x807FFFFE) != 0xABCD:
        runner.test_fail("test_halfword_access_spanning_boundary", 0xABCD, mem.read_halfword(0x807FFFFE))
    
    # Invalid: halfword at end (spans past RAM)
    try:
        mem.write_halfword(0x807FFFFF, 0x1234)
        runner.test_fail("test_halfword_access_spanning_boundary", "MemoryAccessFault", "no exception")
    except MemoryAccessFault as e:
        if e.address != 0x80800000:
            runner.test_fail("test_halfword_access_spanning_boundary", "0x80800000", f"0x{e.address:08x}")
        if e.access_type != 'store':
            runner.test_fail("test_halfword_access_spanning_boundary", "store", e.access_type)


def test_is_valid_address(runner):
    """Test the is_valid_address helper method"""
    mem = Memory()
    
    # Valid addresses
    if not mem.is_valid_address(0x80000000):
        runner.test_fail("test_is_valid_address", "True", "False for 0x80000000")
    if not mem.is_valid_address(0x80400000):
        runner.test_fail("test_is_valid_address", "True", "False for 0x80400000")
    if not mem.is_valid_address(0x807FFFFF):
        runner.test_fail("test_is_valid_address", "True", "False for 0x807FFFFF")
    if not mem.is_valid_address(0x10000000):
        runner.test_fail("test_is_valid_address", "True", "False for 0x10000000")
    
    # Invalid addresses
    if mem.is_valid_address(0x00000000):
        runner.test_fail("test_is_valid_address", "False", "True for 0x00000000")
    if mem.is_valid_address(0x7FFFFFFF):
        runner.test_fail("test_is_valid_address", "False", "True for 0x7FFFFFFF")
    if mem.is_valid_address(0x80800000):
        runner.test_fail("test_is_valid_address", "False", "True for 0x80800000")
    if mem.is_valid_address(0x10000001):
        runner.test_fail("test_is_valid_address", "False", "True for 0x10000001")
    if mem.is_valid_address(0x10000FFF):
        runner.test_fail("test_is_valid_address", "False", "True for 0x10000FFF")
    if mem.is_valid_address(0xFFFFFFFF):
        runner.test_fail("test_is_valid_address", "False", "True for 0xFFFFFFFF")
