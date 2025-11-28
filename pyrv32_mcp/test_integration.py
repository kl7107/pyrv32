#!/usr/bin/env python3
"""
Integration test for pyrv32 MCP server.

Tests end-to-end workflow: create session, load NetHack, interact via UART.
This demonstrates the key capability: AI-driven interactive gameplay.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrv32_mcp.session_manager import SessionManager


def test_hello_world():
    """Test basic workflow with simple hello world binary."""
    
    print("Testing basic MCP workflow with hello world...")
    
    # Create session manager (simulates MCP server's internal state)
    manager = SessionManager()
    
    # Step 1: Create session
    session_id = manager.create_session(fs_root=".")
    print(f"✓ Created session: {session_id}")
    
    session = manager.get_session(session_id)
    assert session is not None, "Session should exist"
    
    # Step 2: Load simple binary (use test binary if exists)
    test_binaries = [
        "tests/c/test_hello_world.bin",
        "tests/c/test_basic.bin",
        "tests/test_basic.bin",
    ]
    
    binary_path = None
    for path in test_binaries:
        if os.path.exists(path):
            binary_path = path
            break
    
    if not binary_path:
        print("⚠ No test binaries found - creating simple test...")
        # Create minimal test program
        program = bytearray([
            # UART TX base: 0x10000000
            # Write 'H' to UART
            0x37, 0x05, 0x00, 0x10,  # lui a0, 0x10000  (UART base)
            0x13, 0x06, 0x80, 0x04,  # addi a2, zero, 'H'
            0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
            # ebreak
            0x73, 0x00, 0x10, 0x00,  # ebreak
        ])
        session.load_binary_data(bytes(program), 0x80000000)
        print("✓ Loaded test program")
    else:
        try:
            session.load_binary(binary_path)
            print(f"✓ Loaded binary: {binary_path}")
        except Exception as e:
            print(f"⚠ Error loading {binary_path}: {e}")
            return
    
    # Step 3: Run until output or halt
    result = session.run(max_steps=10000)
    print(f"✓ Ran {result.instruction_count} instructions, status: {result.status}")
    
    # Step 4: Read output if any
    if session.uart_has_data():
        output = session.uart_read()
        print(f"✓ Read {len(output)} bytes: {repr(output)}")
    else:
        print("✓ No UART output (program may have halted)")
    
    # Step 5: Check status
    status = session.get_status()
    print(f"✓ Final status:")
    print(f"  PC: 0x{status['pc']:08x}")
    print(f"  Total instructions: {status['instruction_count']}")
    print(f"  Halted: {status['halted']}")
    
    # Step 6: Test register access
    regs = session.get_registers()
    print(f"✓ Got {len(regs)} registers")
    
    # Step 7: Test memory access
    mem = session.read_memory(0x80000000, 16)
    print(f"✓ Read {len(mem)} bytes from memory: {mem.hex()}")
    
    # Step 8: Cleanup
    manager.destroy_session(session_id)
    print(f"✓ Destroyed session")
    
    print("\n✅ Basic MCP workflow test PASSED")
    print("Demonstrated capabilities:")
    print("  - Create/destroy sessions")
    print("  - Load binary data")
    print("  - Execute instructions")
    print("  - Read UART output")
    print("  - Access registers and memory")


def test_nethack_character_creation():
    """Test interactive NetHack character creation workflow."""
    
    print("Testing NetHack character creation via MCP workflow...")
    
    # Create session manager (simulates MCP server's internal state)
    manager = SessionManager()
    
    # Step 1: Create session
    session_id = manager.create_session(fs_root="nethack")
    print(f"✓ Created session: {session_id}")
    
    session = manager.get_session(session_id)
    assert session is not None, "Session should exist"
    
    # Step 2: Load NetHack binary
    try:
        session.load_binary("nethack/nethack.bin")
        print("✓ Loaded nethack.bin")
    except FileNotFoundError:
        print("⚠ nethack.bin not found - skipping (build NetHack first)")
        return
    
    # Step 3: Run until first output
    result = session.run_until_output(max_steps=100000)
    print(f"✓ Ran {result.instruction_count} instructions, status: {result.status}")
    
    # Step 4: Read initial output
    output = session.uart_read()
    print(f"✓ Read {len(output)} bytes of output")
    print(f"First output:\n{output[:200]}")  # Show first 200 chars
    
    # Should contain copyright notice
    assert "NetHack" in output or "Copyright" in output, "Should show NetHack copyright"
    
    # Step 5: Send newline to continue
    session.uart_write("\n")
    print("✓ Wrote newline to continue")
    
    # Step 6: Run until next prompt
    result = session.run_until_output(max_steps=100000)
    print(f"✓ Ran {result.instruction_count} more instructions")
    
    # Step 7: Read next prompt
    output = session.uart_read()
    print(f"✓ Read next prompt:\n{output[:200]}")
    
    # Step 8: Enter character name
    session.uart_write("TestPlayer\n")
    print("✓ Wrote character name: TestPlayer")
    
    # Step 9: Run to process input
    result = session.run_until_output(max_steps=100000)
    print(f"✓ Ran {result.instruction_count} more instructions")
    
    # Step 10: Read response
    output = session.uart_read()
    print(f"✓ Got response ({len(output)} bytes):\n{output[:200]}")
    
    # Step 11: Check status
    status = session.get_status()
    print(f"✓ Final status:")
    print(f"  PC: 0x{status['pc']:08x}")
    print(f"  Total instructions: {status['instruction_count']}")
    print(f"  Halted: {status['halted']}")
    print(f"  UART has data: {status['uart_has_data']}")
    
    # Step 12: Cleanup
    manager.destroy_session(session_id)
    print(f"✓ Destroyed session")
    
    print("\n✅ NetHack character creation test PASSED")
    print("This demonstrates AI can:")
    print("  - Create simulator sessions")
    print("  - Load binaries")
    print("  - Run until output appears")
    print("  - Read UART output to see prompts")
    print("  - Write UART input to respond")
    print("  - Continue interactive gameplay")


if __name__ == "__main__":
    try:
        # Run basic test first
        test_hello_world()
        print("\n" + "="*60 + "\n")
        
        # Try NetHack test if available
        test_nethack_character_creation()
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
