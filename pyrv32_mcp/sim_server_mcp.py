#!/usr/bin/env python3
"""
Persistent TCP-based simulator server using MCP protocol.

This server runs continuously, speaks MCP protocol over TCP,
and manages RV32System sessions that persist across client disconnections.

Run with: python3 sim_server_mcp.py
"""

import sys
import os
import asyncio
from typing import Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.types import Tool, TextContent
from session_manager import SessionManager


class SimulatorMCPServer:
    """MCP server for simulator with TCP transport."""
    
    def __init__(self):
        self.app = Server("pyrv32-simulator")
        self.session_manager = SessionManager()
        self._register_tools()
        print(f"Session manager initialized: {id(self.session_manager)}")
    
    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.app.list_tools()
        async def list_tools() -> list[Tool]:
            """List available simulator tools."""
            return [
                Tool(
                    name="sim_create",
                    description="Create a new simulator session. Returns session_id for use with other tools.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_addr": {
                                "type": "string",
                                "description": "Initial PC value in hex (default: 0x80000000)",
                                "default": "0x80000000"
                            },
                            "fs_root": {
                                "type": "string",
                                "description": "Root directory for filesystem syscalls (default: '.')",
                                "default": "."
                            }
                        }
                    }
                ),
                Tool(
                    name="sim_load",
                    description="Load a RISC-V binary into simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "binary_path": {"type": "string", "description": "Path to RISC-V binary file"}
                        },
                        "required": ["session_id", "binary_path"]
                    }
                ),
                Tool(
                    name="sim_reset",
                    description="Reset simulator session to initial state.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_destroy",
                    description="Destroy a simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_step",
                    description="Execute one or more instructions.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "count": {"type": "integer", "description": "Number of instructions (default: 1)", "default": 1}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_run",
                    description="Run until halt, breakpoint, or max steps.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_run_until_output",
                    description="Run until UART output is available or halt.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_get_status",
                    description="Get current status of simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_uart_read",
                    description="Read available UART output from simulator.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_uart_write",
                    description="Write data to UART input.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "data": {"type": "string", "description": "Data to write"}
                        },
                        "required": ["session_id", "data"]
                    }
                ),
                Tool(
                    name="sim_uart_has_data",
                    description="Check if UART has output data available.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_get_registers",
                    description="Get all register values.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_get_register",
                    description="Get single register value by number or name.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "register": {"type": "string", "description": "Register number (0-31) or name (x0-x31, zero, ra, sp, etc.)"}
                        },
                        "required": ["session_id", "register"]
                    }
                ),
                Tool(
                    name="sim_set_register",
                    description="Set register value by number or name.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "register": {"type": "string", "description": "Register number or name"},
                            "value": {"type": "string", "description": "Value to set (hex string like '0x12345678')"}
                        },
                        "required": ["session_id", "register", "value"]
                    }
                ),
                Tool(
                    name="sim_read_memory",
                    description="Read memory from simulator.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "address": {"type": "string", "description": "Memory address in hex (like '0x80000000')"},
                            "length": {"type": "integer", "description": "Number of bytes to read"}
                        },
                        "required": ["session_id", "address", "length"]
                    }
                ),
                Tool(
                    name="sim_write_memory",
                    description="Write memory to simulator.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "address": {"type": "string", "description": "Memory address in hex"},
                            "data": {"type": "string", "description": "Hex string of bytes to write (like 'deadbeef')"}
                        },
                        "required": ["session_id", "address", "data"]
                    }
                ),
                Tool(
                    name="sim_add_breakpoint",
                    description="Add breakpoint at address.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "address": {"type": "string", "description": "Breakpoint address in hex"}
                        },
                        "required": ["session_id", "address"]
                    }
                ),
                Tool(
                    name="sim_remove_breakpoint",
                    description="Remove breakpoint at address.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "address": {"type": "string", "description": "Breakpoint address in hex"}
                        },
                        "required": ["session_id", "address"]
                    }
                ),
                Tool(
                    name="sim_list_breakpoints",
                    description="List all breakpoints.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
            ]
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            
            try:
                # Session management
                if name == "sim_create":
                    start_addr = int(arguments.get("start_addr", "0x80000000"), 16)
                    fs_root = arguments.get("fs_root", ".")
                    session_id = self.session_manager.create_session(start_addr, fs_root)
                    return [TextContent(type="text", text=f"Created session: {session_id}")]
                
                elif name == "sim_destroy":
                    success = self.session_manager.destroy_session(arguments["session_id"])
                    msg = f"Destroyed session: {arguments['session_id']}" if success else f"Error: Session not found"
                    return [TextContent(type="text", text=msg)]
                
                # Get session for all other operations
                session_id = arguments.get("session_id")
                if not session_id:
                    return [TextContent(type="text", text="Error: session_id required")]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(type="text", text=f"Error: Session {session_id} not found")]
                
                # Binary operations
                if name == "sim_load":
                    session.load_binary(arguments["binary_path"])
                    return [TextContent(type="text", text=f"Loaded binary: {arguments['binary_path']}")]
                
                elif name == "sim_reset":
                    session.reset()
                    return [TextContent(type="text", text=f"Reset session: {session_id}")]
                
                # Execution
                elif name == "sim_step":
                    result = session.step(arguments.get("count", 1))
                    text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                    if result.error:
                        text += f"\nError: {result.error}"
                    return [TextContent(type="text", text=text)]
                
                elif name == "sim_run":
                    result = session.run(arguments.get("max_steps", 1000000))
                    text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                    if result.error:
                        text += f"\nError: {result.error}"
                    return [TextContent(type="text", text=text)]
                
                elif name == "sim_run_until_output":
                    result = session.run_until_output(arguments.get("max_steps", 1000000))
                    text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                    if result.error:
                        text += f"\nError: {result.error}"
                    return [TextContent(type="text", text=text)]
                
                elif name == "sim_get_status":
                    status = session.get_status()
                    text = f"PC: 0x{status['pc']:08x}\nInstructions: {status['instruction_count']}\nHalted: {status['halted']}\nUART has data: {status['uart_has_data']}"
                    return [TextContent(type="text", text=text)]
                
                # UART
                elif name == "sim_uart_read":
                    data = session.uart_read()
                    return [TextContent(type="text", text=data)]
                
                elif name == "sim_uart_write":
                    session.uart_write(arguments["data"])
                    return [TextContent(type="text", text="Data written to UART")]
                
                elif name == "sim_uart_has_data":
                    has_data = session.uart_has_data()
                    return [TextContent(type="text", text=str(has_data))]
                
                # Registers
                elif name == "sim_get_registers":
                    regs = session.get_registers()
                    text = "\n".join([f"{k}: 0x{v:08x}" for k, v in sorted(regs.items())])
                    return [TextContent(type="text", text=text)]
                
                elif name == "sim_get_register":
                    value = session.get_register(arguments["register"])
                    return [TextContent(type="text", text=f"0x{value:08x}")]
                
                elif name == "sim_set_register":
                    value = int(arguments["value"], 16) if isinstance(arguments["value"], str) else arguments["value"]
                    session.set_register(arguments["register"], value)
                    return [TextContent(type="text", text=f"Set {arguments['register']} = {arguments['value']}")]
                
                # Memory
                elif name == "sim_read_memory":
                    address = int(arguments["address"], 16)
                    data = session.read_memory(address, arguments["length"])
                    return [TextContent(type="text", text=data.hex())]
                
                elif name == "sim_write_memory":
                    address = int(arguments["address"], 16)
                    data = bytes.fromhex(arguments["data"])
                    session.write_memory(address, data)
                    return [TextContent(type="text", text="Memory written")]
                
                # Breakpoints
                elif name == "sim_add_breakpoint":
                    address = int(arguments["address"], 16)
                    session.add_breakpoint(address)
                    return [TextContent(type="text", text=f"Added breakpoint at {arguments['address']}")]
                
                elif name == "sim_remove_breakpoint":
                    address = int(arguments["address"], 16)
                    session.remove_breakpoint(address)
                    return [TextContent(type="text", text=f"Removed breakpoint at {arguments['address']}")]
                
                elif name == "sim_list_breakpoints":
                    breakpoints = session.list_breakpoints()
                    text = "\n".join([hex(bp) for bp in breakpoints]) if breakpoints else "No breakpoints"
                    return [TextContent(type="text", text=text)]
                
                else:
                    return [TextContent(type="text", text=f"Error: Unknown tool {name}")]
            
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a single client connection."""
        addr = writer.get_extra_info('peername')
        print(f"Client connected: {addr}")
        
        try:
            await self.app.run(
                reader,
                writer,
                self.app.create_initialization_options()
            )
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            print(f"Client disconnected: {addr}")
            writer.close()
            await writer.wait_closed()
    
    async def run(self, host="127.0.0.1", port=5555):
        """Run the TCP server."""
        server = await asyncio.start_server(
            self.handle_client,
            host,
            port
        )
        
        addr = server.sockets[0].getsockname()
        print(f"pyrv32 MCP Simulator Server")
        print(f"Listening on {addr[0]}:{addr[1]}")
        print(f"Press Ctrl+C to stop")
        
        async with server:
            await server.serve_forever()


async def main():
    """Main entry point."""
    server = SimulatorMCPServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    asyncio.run(main())
