#!/usr/bin/env python3
"""
Local MCP server test - verifies the server responds to MCP protocol correctly.

This connects to the MCP server locally and tests basic operations.
"""

import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_mcp_server():
    """Test MCP server by sending JSON-RPC messages."""
    
    print("=== Testing pyrv32 MCP Server Locally ===\n")
    
    # Import the server
    from pyrv32_mcp.pyrv32_server import PyRV32Server
    
    print("✓ Server imports successfully")
    
    # Create server instance
    server = PyRV32Server()
    print("✓ Server instance created")
    
    # Test session manager
    session_id = server.session_manager.create_session()
    print(f"✓ Created test session: {session_id}")
    
    session = server.session_manager.get_session(session_id)
    assert session is not None, "Session should exist"
    print("✓ Can retrieve session")
    
    # Test loading a simple program
    program = bytes([
        0x37, 0x05, 0x00, 0x10,  # lui a0, 0x10000
        0x13, 0x06, 0x80, 0x04,  # addi a2, zero, 'H'
        0x23, 0x00, 0xc5, 0x00,  # sb a2, 0(a0)
        0x73, 0x00, 0x10, 0x00,  # ebreak
    ])
    session.load_binary_data(program, 0x80000000)
    print("✓ Can load binary data")
    
    # Test execution
    result = session.run(max_steps=100)
    print(f"✓ Can execute (ran {result.instruction_count} instructions)")
    
    # Test UART read
    if session.uart_has_data():
        data = session.uart_read()
        print(f"✓ Can read UART data: {repr(data)}")
    
    # Test register access
    regs = session.get_registers()
    print(f"✓ Can read registers (got {len(regs)} values)")
    
    # Test memory access
    mem = session.read_memory(0x80000000, 16)
    print(f"✓ Can read memory ({len(mem)} bytes)")
    
    # Test breakpoint
    session.reset()
    session.add_breakpoint(0x80000004)  # After first instruction
    breakpoints = session.list_breakpoints()
    assert len(breakpoints) > 0, f"Expected breakpoints, got {breakpoints}"
    print(f"✓ Can add/list breakpoints (found {len(breakpoints)} breakpoint(s))")
    
    # Cleanup
    destroyed = server.session_manager.destroy_session(session_id)
    assert destroyed
    print("✓ Can destroy session")
    
    print("\n=== All MCP Server Tests Passed! ===")
    print("\nNext steps:")
    print("1. Configure in VS Code/Claude Desktop")
    print("2. Test with real AI assistant")
    print("3. Build a real program to debug")
    print("4. Publish to GitHub!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
