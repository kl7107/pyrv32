"""
MCP server for pyrv32 RISC-V simulator.

Exposes simulator capabilities as MCP tools using stdio transport.
This is a thin proxy that forwards requests to the persistent TCP server.
"""

import sys
import asyncio
from typing import Any

# Import from the MCP library (not our local package)
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .sim_client import SimulatorClient


class PyRV32Server:
    """MCP server for pyrv32 simulator (thin proxy)."""
    
    def __init__(self):
        self.app = Server("pyrv32-simulator")
        self.client = SimulatorClient()  # Connect to TCP server
        
        # Register tools
        self._register_tools()
    
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
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier from sim_create"
                            },
                            "binary_path": {
                                "type": "string",
                                "description": "Path to RISC-V ELF binary file"
                            }
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
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_destroy",
                    description="Destroy a simulator session and free resources.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_step",
                    description="Execute one or more instructions in simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of instructions to execute (default: 1)",
                                "default": 1
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_run",
                    description="Run simulator session until halt, breakpoint, or max steps.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "max_steps": {
                                "type": "integer",
                                "description": "Maximum instructions to execute (default: 1000000)",
                                "default": 1000000
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_run_until_output",
                    description="Run simulator until UART output is available or halt.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "max_steps": {
                                "type": "integer",
                                "description": "Maximum instructions to execute (default: 1000000)",
                                "default": 1000000
                            }
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
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_uart_read",
                    description="Read available UART output from simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_uart_write",
                    description="Write data to UART input of simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "data": {
                                "type": "string",
                                "description": "Data to write to UART input"
                            }
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
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="sim_get_registers",
                    description="Get all register values from simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            }
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
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "register": {
                                "type": "string",
                                "description": "Register number (0-31) or name (x0-x31, zero, ra, sp, etc.)"
                            }
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
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "register": {
                                "type": "string",
                                "description": "Register number (0-31) or name (x0-x31, zero, ra, sp, etc.)"
                            },
                            "value": {
                                "type": "string",
                                "description": "Value to set (hex string like '0x12345678')"
                            }
                        },
                        "required": ["session_id", "register", "value"]
                    }
                ),
                Tool(
                    name="sim_read_memory",
                    description="Read memory from simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "address": {
                                "type": "string",
                                "description": "Memory address in hex (like '0x80000000')"
                            },
                            "length": {
                                "type": "integer",
                                "description": "Number of bytes to read"
                            }
                        },
                        "required": ["session_id", "address", "length"]
                    }
                ),
                Tool(
                    name="sim_write_memory",
                    description="Write memory to simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "address": {
                                "type": "string",
                                "description": "Memory address in hex (like '0x80000000')"
                            },
                            "data": {
                                "type": "string",
                                "description": "Hex string of bytes to write (like 'deadbeef')"
                            }
                        },
                        "required": ["session_id", "address", "data"]
                    }
                ),
                Tool(
                    name="sim_add_breakpoint",
                    description="Add breakpoint at address in simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "address": {
                                "type": "string",
                                "description": "Breakpoint address in hex (like '0x80000000')"
                            }
                        },
                        "required": ["session_id", "address"]
                    }
                ),
                Tool(
                    name="sim_remove_breakpoint",
                    description="Remove breakpoint at address in simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "address": {
                                "type": "string",
                                "description": "Breakpoint address in hex (like '0x80000000')"
                            }
                        },
                        "required": ["session_id", "address"]
                    }
                ),
                Tool(
                    name="sim_list_breakpoints",
                    description="List all breakpoints in simulator session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            }
                        },
                        "required": ["session_id"]
                    }
                )
            ]
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            
            if name == "sim_create":
                start_addr = int(arguments.get("start_addr", "0x80000000"), 16)
                fs_root = arguments.get("fs_root", ".")
                session_id = self.session_manager.create_session(
                    start_addr=start_addr,
                    fs_root=fs_root
                )
                return [TextContent(
                    type="text",
                    text=f"Created session: {session_id}"
                )]
            
            elif name == "sim_load":
                session_id = arguments["session_id"]
                binary_path = arguments["binary_path"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    session.load_binary(binary_path)
                    return [TextContent(
                        type="text",
                        text=f"Loaded binary: {binary_path}"
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error loading binary: {str(e)}"
                    )]
            
            elif name == "sim_reset":
                session_id = arguments["session_id"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                session.reset()
                return [TextContent(
                    type="text",
                    text=f"Reset session: {session_id}"
                )]
            
            elif name == "sim_destroy":
                session_id = arguments["session_id"]
                
                if self.session_manager.destroy_session(session_id):
                    return [TextContent(
                        type="text",
                        text=f"Destroyed session: {session_id}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
            
            elif name == "sim_step":
                session_id = arguments["session_id"]
                count = arguments.get("count", 1)
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    result = session.step(count)
                    status_str = f"Status: {result.status}\n"
                    status_str += f"Instructions executed: {result.instruction_count}\n"
                    status_str += f"PC: 0x{result.pc:08x}\n"
                    if result.error:
                        status_str += f"Error: {result.error}"
                    return [TextContent(type="text", text=status_str)]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error stepping: {str(e)}"
                    )]
            
            elif name == "sim_run":
                session_id = arguments["session_id"]
                max_steps = arguments.get("max_steps", 1000000)
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    result = session.run(max_steps)
                    status_str = f"Status: {result.status}\n"
                    status_str += f"Instructions executed: {result.instruction_count}\n"
                    status_str += f"PC: 0x{result.pc:08x}\n"
                    if result.error:
                        status_str += f"Error: {result.error}"
                    return [TextContent(type="text", text=status_str)]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error running: {str(e)}"
                    )]
            
            elif name == "sim_run_until_output":
                session_id = arguments["session_id"]
                max_steps = arguments.get("max_steps", 1000000)
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    result = session.run_until_output(max_steps)
                    status_str = f"Status: {result.status}\n"
                    status_str += f"Instructions executed: {result.instruction_count}\n"
                    status_str += f"PC: 0x{result.pc:08x}\n"
                    if result.error:
                        status_str += f"Error: {result.error}"
                    return [TextContent(type="text", text=status_str)]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error running: {str(e)}"
                    )]
            
            elif name == "sim_get_status":
                session_id = arguments["session_id"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                status = session.get_status()
                status_str = f"PC: 0x{status['pc']:08x}\n"
                status_str += f"Instructions executed: {status['instruction_count']}\n"
                status_str += f"Halted: {status['halted']}\n"
                status_str += f"UART has data: {status['uart_has_data']}"
                return [TextContent(type="text", text=status_str)]
            
            elif name == "sim_uart_read":
                session_id = arguments["session_id"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                data = session.uart_read()
                return [TextContent(type="text", text=data)]
            
            elif name == "sim_uart_write":
                session_id = arguments["session_id"]
                data = arguments["data"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                session.uart_write(data)
                return [TextContent(
                    type="text",
                    text=f"Wrote {len(data)} bytes to UART"
                )]
            
            elif name == "sim_uart_has_data":
                session_id = arguments["session_id"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                has_data = session.uart_has_data()
                return [TextContent(
                    type="text",
                    text=f"UART has data: {has_data}"
                )]
            
            elif name == "sim_get_registers":
                session_id = arguments["session_id"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                regs = session.get_registers()
                reg_str = ""
                for i in range(0, 32, 4):
                    reg_str += f"x{i:2d}=0x{regs[i]:08x}  x{i+1:2d}=0x{regs[i+1]:08x}  x{i+2:2d}=0x{regs[i+2]:08x}  x{i+3:2d}=0x{regs[i+3]:08x}\n"
                return [TextContent(type="text", text=reg_str)]
            
            elif name == "sim_get_register":
                session_id = arguments["session_id"]
                register = arguments["register"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    value = session.get_register(register)
                    return [TextContent(
                        type="text",
                        text=f"{register} = 0x{value:08x}"
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error reading register: {str(e)}"
                    )]
            
            elif name == "sim_set_register":
                session_id = arguments["session_id"]
                register = arguments["register"]
                value = int(arguments["value"], 16)
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    session.set_register(register, value)
                    return [TextContent(
                        type="text",
                        text=f"Set {register} = 0x{value:08x}"
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error setting register: {str(e)}"
                    )]
            
            elif name == "sim_read_memory":
                session_id = arguments["session_id"]
                address = int(arguments["address"], 16)
                length = arguments["length"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    data = session.read_memory(address, length)
                    hex_str = data.hex()
                    # Format as hex dump
                    result = f"Memory at 0x{address:08x} ({length} bytes):\n"
                    for i in range(0, len(hex_str), 32):
                        chunk = hex_str[i:i+32]
                        addr_offset = i // 2
                        result += f"0x{address+addr_offset:08x}: {chunk}\n"
                    return [TextContent(type="text", text=result)]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error reading memory: {str(e)}"
                    )]
            
            elif name == "sim_write_memory":
                session_id = arguments["session_id"]
                address = int(arguments["address"], 16)
                data_hex = arguments["data"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                try:
                    data = bytes.fromhex(data_hex)
                    session.write_memory(address, data)
                    return [TextContent(
                        type="text",
                        text=f"Wrote {len(data)} bytes to 0x{address:08x}"
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error writing memory: {str(e)}"
                    )]
            
            elif name == "sim_add_breakpoint":
                session_id = arguments["session_id"]
                address = int(arguments["address"], 16)
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                session.add_breakpoint(address)
                return [TextContent(
                    type="text",
                    text=f"Added breakpoint at 0x{address:08x}"
                )]
            
            elif name == "sim_remove_breakpoint":
                session_id = arguments["session_id"]
                address = int(arguments["address"], 16)
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                if session.remove_breakpoint(address):
                    return [TextContent(
                        type="text",
                        text=f"Removed breakpoint at 0x{address:08x}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"No breakpoint at 0x{address:08x}"
                    )]
            
            elif name == "sim_list_breakpoints":
                session_id = arguments["session_id"]
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    return [TextContent(
                        type="text",
                        text=f"Error: Session {session_id} not found"
                    )]
                
                breakpoints = session.list_breakpoints()
                if breakpoints:
                    bp_str = "Breakpoints:\n"
                    for addr in breakpoints:
                        bp_str += f"  0x{addr:08x}\n"
                    return [TextContent(type="text", text=bp_str)]
                else:
                    return [TextContent(
                        type="text",
                        text="No breakpoints set"
                    )]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown tool {name}"
                )]
    
    async def run(self):
        """Run the MCP server with stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                self.app.create_initialization_options()
            )


async def main():
    """Main entry point."""
    server = PyRV32Server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
