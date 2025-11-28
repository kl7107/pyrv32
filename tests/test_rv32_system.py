#!/usr/bin/env python3
"""
Unit tests for RV32System class
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyrv32_system import RV32System, ExecutionResult


def test_system_create(runner):
    """RV32System: can create instance"""
    sys = RV32System()
    if sys is None:
        runner.test_fail("create system", "instance", "None")
    
    if sys.cpu is None:
        runner.test_fail("create system", "cpu exists", "cpu is None")
    
    if sys.memory is None:
        runner.test_fail("create system", "memory exists", "memory is None")


def test_system_initial_state(runner):
    """RV32System: initial state is correct"""
    sys = RV32System(start_addr=0x80000000)
    
    if sys.cpu.pc != 0x80000000:
        runner.test_fail("initial state", "PC=0x80000000", f"PC=0x{sys.cpu.pc:08x}")
    
    if sys.instruction_count != 0:
        runner.test_fail("initial state", "instruction_count=0", f"instruction_count={sys.instruction_count}")
    
    if sys.halted:
        runner.test_fail("initial state", "not halted", "halted=True")


def test_load_binary_data(runner):
    """RV32System: can load binary data"""
    sys = RV32System()
    
    # Simple program: addi x1, x0, 42; ebreak
    # addi x1, x0, 42 = 0x02a00093
    # ebreak = 0x00100073
    program = bytes([
        0x93, 0x00, 0xa0, 0x02,  # addi x1, x0, 42
        0x73, 0x00, 0x10, 0x00,  # ebreak
    ])
    
    size = sys.load_binary_data(program)
    
    if size != 8:
        runner.test_fail("load binary", "8 bytes", f"{size} bytes")
    
    # Verify loaded correctly
    word1 = sys.memory.read_word(0x80000000)
    if word1 != 0x02a00093:
        runner.test_fail("load binary", "0x02a00093", f"0x{word1:08x}")


def test_step_one_instruction(runner):
    """RV32System: can execute one instruction"""
    sys = RV32System()
    
    # addi x1, x0, 42
    program = bytes([0x93, 0x00, 0xa0, 0x02])
    sys.load_binary_data(program)
    
    result = sys.step(1)
    
    if result.status != 'running':
        runner.test_fail("step execution", "running", result.status)
    
    if result.instruction_count != 1:
        runner.test_fail("step execution", "1 instruction", f"{result.instruction_count} instructions")
    
    if sys.cpu.regs[1] != 42:
        runner.test_fail("step execution", "x1=42", f"x1={sys.cpu.regs[1]}")


def test_step_until_halt(runner):
    """RV32System: execution halts on ebreak"""
    sys = RV32System()
    
    # addi x1, x0, 42; ebreak
    program = bytes([
        0x93, 0x00, 0xa0, 0x02,  # addi x1, x0, 42
        0x73, 0x00, 0x10, 0x00,  # ebreak
    ])
    sys.load_binary_data(program)
    
    # Step 1: addi
    result1 = sys.step(1)
    if result1.status != 'running':
        runner.test_fail("step to ebreak", "running", result1.status)
    
    # Step 2: ebreak
    result2 = sys.step(1)
    if result2.status != 'halted':
        runner.test_fail("step to ebreak", "halted", result2.status)
    
    if not sys.halted:
        runner.test_fail("step to ebreak", "sys.halted=True", "sys.halted=False")


def test_run_until_halt(runner):
    """RV32System: run() executes until halt"""
    sys = RV32System()
    
    # addi x1, x0, 1; addi x1, x1, 1; addi x1, x1, 1; ebreak
    program = bytes([
        0x93, 0x00, 0x10, 0x00,  # addi x1, x0, 1
        0x93, 0x80, 0x10, 0x00,  # addi x1, x1, 1
        0x93, 0x80, 0x10, 0x00,  # addi x1, x1, 1
        0x73, 0x00, 0x10, 0x00,  # ebreak
    ])
    sys.load_binary_data(program)
    
    result = sys.run(max_steps=100)
    
    if result.status != 'halted':
        runner.test_fail("run until halt", "halted", result.status)
    
    # 3 addi instructions execute, ebreak halts before completing
    if result.instruction_count != 3:
        runner.test_fail("run until halt", "3 instructions", f"{result.instruction_count} instructions")
    
    if sys.cpu.regs[1] != 3:
        runner.test_fail("run until halt", "x1=3", f"x1={sys.cpu.regs[1]}")


def test_uart_write_and_read(runner):
    """RV32System: can write to UART RX and read from UART TX"""
    sys = RV32System()
    
    # Write data to UART RX
    sys.uart_write("Hello")
    
    # Check that data is queued in rx_buffer
    if len(sys.memory.console_uart.rx_buffer) == 0:
        runner.test_fail("uart write", "has RX data", "no RX data")
    
    # For reading TX: need a program that writes to UART
    # For now, just test the read mechanism
    initial_output = sys.uart_read()
    if initial_output != "":
        runner.test_fail("uart read initial", "empty", f"'{initial_output}'")
    
    # Manually write to console UART TX
    test_msg = "Test output"
    for char in test_msg:
        sys.memory.console_uart.tx_byte(ord(char))
    
    # Read should get new output
    output = sys.uart_read()
    if output != test_msg:
        runner.test_fail("uart read", f"'{test_msg}'", f"'{output}'")
    
    # Second read should be empty (already read)
    output2 = sys.uart_read()
    if output2 != "":
        runner.test_fail("uart read twice", "empty", f"'{output2}'")


def test_uart_read_all(runner):
    """RV32System: uart_read_all() returns complete output"""
    sys = RV32System()
    
    # Write some output
    for char in "ABC":
        sys.memory.console_uart.tx_byte(ord(char))
    
    # Incremental read
    partial = sys.uart_read()
    if partial != "ABC":
        runner.test_fail("uart read all", "'ABC' from first read", f"'{partial}'")
    
    # Write more
    for char in "DEF":
        sys.memory.console_uart.tx_byte(ord(char))
    
    # read_all should include both
    all_output = sys.uart_read_all()
    if all_output != "ABCDEF":
        runner.test_fail("uart read all", "'ABCDEF'", f"'{all_output}'")


def test_reset(runner):
    """RV32System: reset() restores initial state"""
    sys = RV32System()
    
    # Load and run program
    program = bytes([0x93, 0x00, 0xa0, 0x02, 0x73, 0x00, 0x10, 0x00])
    sys.load_binary_data(program)
    sys.run()
    
    # Verify state changed
    if sys.cpu.regs[1] != 42:
        runner.test_fail("reset", "x1=42 before reset", f"x1={sys.cpu.regs[1]}")
    
    if not sys.halted:
        runner.test_fail("reset", "halted before reset", "not halted")
    
    # Reset
    sys.reset()
    
    # Verify reset state
    if sys.cpu.pc != 0x80000000:
        runner.test_fail("reset", "PC=0x80000000", f"PC=0x{sys.cpu.pc:08x}")
    
    if sys.instruction_count != 0:
        runner.test_fail("reset", "instruction_count=0", f"count={sys.instruction_count}")
    
    if sys.halted:
        runner.test_fail("reset", "not halted", "halted=True")
    
    if sys.cpu.regs[1] != 0:
        runner.test_fail("reset", "x1=0", f"x1={sys.cpu.regs[1]}")


def test_get_set_registers(runner):
    """RV32System: can get and set registers"""
    sys = RV32System()
    
    # Set register by number
    sys.set_register(5, 0x12345678)
    val = sys.get_register(5)
    if val != 0x12345678:
        runner.test_fail("get/set register", "0x12345678", f"0x{val:08x}")
    
    # Set register by name
    sys.set_register('a0', 0xabcdef00)
    val = sys.get_register('a0')
    if val != 0xabcdef00:
        runner.test_fail("get/set register name", "0xabcdef00", f"0x{val:08x}")
    
    # Get PC
    pc = sys.get_register('pc')
    if pc != sys.cpu.pc:
        runner.test_fail("get PC", f"0x{sys.cpu.pc:08x}", f"0x{pc:08x}")
    
    # x0 should always be 0
    sys.set_register(0, 0x12345678)
    val = sys.get_register(0)
    if val != 0:
        runner.test_fail("x0 always zero", "0", f"{val}")


def test_get_all_registers(runner):
    """RV32System: get_registers() returns dict"""
    sys = RV32System()
    
    sys.cpu.regs[10] = 0x42
    sys.cpu.pc = 0x80001234
    
    regs = sys.get_registers()
    
    if not isinstance(regs, dict):
        runner.test_fail("get_registers", "dict", type(regs).__name__)
    
    if regs['x10'] != 0x42:
        runner.test_fail("get_registers", "x10=0x42", f"x10=0x{regs['x10']:08x}")
    
    if regs['pc'] != 0x80001234:
        runner.test_fail("get_registers", "PC=0x80001234", f"PC=0x{regs['pc']:08x}")


def test_read_write_memory(runner):
    """RV32System: can read and write memory"""
    sys = RV32System()
    
    # Write bytes
    data = bytes([0x11, 0x22, 0x33, 0x44])
    sys.write_memory(0x80001000, data)
    
    # Read back
    read_data = sys.read_memory(0x80001000, 4)
    
    if read_data != data:
        runner.test_fail("read/write memory", 
                        f"{data.hex()}", 
                        f"{read_data.hex()}")


def test_breakpoint_management(runner):
    """RV32System: can add/remove/list breakpoints"""
    sys = RV32System()
    
    # Add breakpoint
    bp_id = sys.add_breakpoint(address=0x80001000)
    
    if bp_id is None:
        runner.test_fail("add breakpoint", "valid ID", "None")
    
    # List breakpoints
    bps = sys.list_breakpoints()
    if len(bps) != 1:
        runner.test_fail("list breakpoints", "1 breakpoint", f"{len(bps)} breakpoints")
    
    # Remove breakpoint
    removed = sys.remove_breakpoint(bp_id)
    if not removed:
        runner.test_fail("remove breakpoint", "True", "False")
    
    # List should be empty
    bps = sys.list_breakpoints()
    if len(bps) != 0:
        runner.test_fail("list after remove", "0 breakpoints", f"{len(bps)} breakpoints")


def test_breakpoint_hit(runner):
    """RV32System: execution stops at breakpoint"""
    sys = RV32System()
    
    # Load program: 3 addi instructions
    program = bytes([
        0x93, 0x00, 0x10, 0x00,  # addi x1, x0, 1  @ 0x80000000
        0x93, 0x80, 0x10, 0x00,  # addi x1, x1, 1  @ 0x80000004
        0x93, 0x80, 0x10, 0x00,  # addi x1, x1, 1  @ 0x80000008
    ])
    sys.load_binary_data(program)
    
    # Set breakpoint at second instruction
    sys.add_breakpoint(address=0x80000004)
    
    # Run
    result = sys.run(max_steps=100)
    
    if result.status != 'breakpoint':
        runner.test_fail("breakpoint hit", "breakpoint", result.status)
    
    # Should have executed 1 instruction (stopped before 2nd)
    if result.instruction_count != 1:
        runner.test_fail("breakpoint hit", "1 instruction", f"{result.instruction_count} instructions")
    
    # PC should be at breakpoint
    if sys.cpu.pc != 0x80000004:
        runner.test_fail("breakpoint hit", "PC=0x80000004", f"PC=0x{sys.cpu.pc:08x}")


def test_get_status(runner):
    """RV32System: get_status() returns dict"""
    sys = RV32System()
    
    status = sys.get_status()
    
    if not isinstance(status, dict):
        runner.test_fail("get_status", "dict", type(status).__name__)
    
    if 'halted' not in status:
        runner.test_fail("get_status", "has 'halted' key", "missing 'halted'")
    
    if 'pc' not in status:
        runner.test_fail("get_status", "has 'pc' key", "missing 'pc'")
    
    if 'instruction_count' not in status:
        runner.test_fail("get_status", "has 'instruction_count' key", "missing")
