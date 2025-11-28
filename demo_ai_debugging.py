#!/usr/bin/env python3
"""
Demo: AI-driven interactive simulator control.

This demonstrates what an AI assistant would do when connected via MCP,
but using the RV32System class directly instead of through MCP tools.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrv32_system import RV32System


def ai_debug_session():
    """Simulate an AI assistant debugging a program interactively."""
    
    print("=== AI Assistant Interactive Debugging Demo ===\n")
    
    # AI creates a simulator session
    print("AI: Creating simulator session...")
    sim = RV32System(start_addr=0x80000000, fs_root=".")
    print("AI: ✓ Session created\n")
    
    # AI creates a simple test program that prints and waits for input
    print("AI: I'll create a program that:")
    print("  1. Prints 'Hello' to UART")
    print("  2. Waits for input")
    print("  3. Echoes it back")
    print()
    
    # Simple echo program
    program = bytearray([
        # Print 'H' 'e' 'l' 'l' 'o' '\n'
        0x37, 0x05, 0x00, 0x10,  # lui a0, 0x10000  (UART base)
        0x13, 0x06, 0x80, 0x04,  # addi a2, zero, 'H'
        0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
        0x13, 0x06, 0x50, 0x06,  # addi a2, zero, 'e'
        0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
        0x13, 0x06, 0xc0, 0x06,  # addi a2, zero, 'l'
        0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
        0x13, 0x06, 0xc0, 0x06,  # addi a2, zero, 'l'
        0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
        0x13, 0x06, 0xf0, 0x06,  # addi a2, zero, 'o'
        0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
        0x13, 0x06, 0xa0, 0x00,  # addi a2, zero, '\n'
        0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
        # Read loop: wait for RX data
        0x83, 0x26, 0x45, 0x00,  # lw a3, 4(a0)     # Read RX status
        0xe3, 0x06, 0x06, 0xfe,  # beqz a3, -4      # Loop if no data
        # Echo back
        0x03, 0x07, 0x85, 0x00,  # lb a4, 8(a0)     # Read RX data
        0x23, 0x00, 0xe5, 0x00,  # sb a4, 0(a0)     # Write to TX
        # Halt
        0x73, 0x00, 0x10, 0x00,  # ebreak
    ])
    
    print("AI: Loading program into memory at 0x80000000...")
    sim.load_binary_data(bytes(program), 0x80000000)
    print("AI: ✓ Program loaded\n")
    
    # AI sets a breakpoint
    print("AI: Setting breakpoint at the input loop (0x80000030)...")
    sim.add_breakpoint(0x80000030)
    print("AI: ✓ Breakpoint set\n")
    
    # AI runs until output
    print("AI: Running until output is available...")
    result = sim.run_until_output(max_steps=10000)
    print(f"AI: ✓ Executed {result.instruction_count} instructions, status: {result.status}\n")
    
    # AI reads the output
    output = sim.uart_read()
    print(f"AI: Program says: {repr(output)}")
    print(f"AI: Great! The program printed its greeting.\n")
    
    # AI checks current state
    status = sim.get_status()
    print(f"AI: Current state:")
    print(f"  PC: 0x{status['pc']:08x}")
    print(f"  Instructions executed: {status['instruction_count']}")
    print(f"  Halted: {status['halted']}")
    print(f"  UART has data: {sim.uart_has_data()}\n")
    
    # AI examines registers
    print("AI: Let me check the registers...")
    a0 = sim.get_register('a0')
    a3 = sim.get_register('a3')
    print(f"  a0 (UART base): 0x{a0:08x}")
    print(f"  a3 (RX status): 0x{a3:08x}")
    print()
    
    # AI provides input
    print("AI: Now I'll send input 'X' to the program...")
    sim.uart_write('X')
    print("AI: ✓ Sent 'X' to UART RX\n")
    
    # AI steps through to see the read
    print("AI: Stepping through the input reading...")
    for i in range(5):
        result = sim.step(1)
        pc = result.pc - 4  # PC after instruction
        a3 = sim.get_register('a3')
        a4 = sim.get_register('a4')
        print(f"  Step {i+1}: PC=0x{pc:08x}, a3=0x{a3:08x}, a4=0x{a4:08x}")
    print()
    
    # AI runs to completion
    print("AI: Running to completion...")
    result = sim.run(max_steps=1000)
    print(f"AI: ✓ Status: {result.status}\n")
    
    # AI reads the echoed output
    if sim.uart_has_data():
        output = sim.uart_read()
        print(f"AI: Program echoed back: {repr(output)}")
    print()
    
    # AI summarizes
    print("AI: Summary of what happened:")
    print("  1. Program printed 'Hello\\n'")
    print("  2. Waited in loop reading RX status")
    print("  3. Received 'X' from me")
    print("  4. Echoed 'X' back to TX")
    print("  5. Halted with ebreak")
    print()
    print("AI: This demonstrates interactive debugging:")
    print("  - Run until output")
    print("  - Read and interpret UART data")
    print("  - Provide input in response")
    print("  - Step through execution")
    print("  - Inspect registers and state")
    print()
    print("=== This is what the MCP server enables AI assistants to do! ===")


if __name__ == "__main__":
    try:
        ai_debug_session()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
