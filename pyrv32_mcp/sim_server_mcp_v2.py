#!/usr/bin/env python3
"""
Persistent TCP-based simulator server using MCP protocol via JSON-RPC.

This server speaks MCP protocol (JSON-RPC 2.0) over TCP, allowing
a dumb byte relay to connect VS Code to the simulator.

Run with: python3 sim_server_mcp_v2.py
"""

import sys
import os
import asyncio
import json
from typing import Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session_manager import SessionManager


class MCPSimulatorServer:
    """MCP simulator server with JSON-RPC over TCP."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        print(f"Session manager initialized: {id(self.session_manager)}")
        
        # Create log file for this server run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"/tmp/mcp_server_{timestamp}.log"
        self.log_fp = open(self.log_file, 'w')
        print(f"MCP traffic logging to: {self.log_file}")
        self._log(f"=== MCP Server Started at {timestamp} ===\n")
    
    def _log(self, message: str):
        """Write message to log file and flush immediately."""
        self.log_fp.write(message)
        self.log_fp.flush()
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a single client connection using JSON-RPC over TCP."""
        addr = writer.get_extra_info('peername')
        print(f"Client connected: {addr}")
        self._log(f"\n=== Client connected: {addr} ===\n")
        
        try:
            while True:
                # Read one line of JSON-RPC
                line = await reader.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.decode('utf-8'))
                    method = request.get('method', 'unknown')
                    print(f"Request: {method}")
                    
                    # Log received request
                    timestamp = datetime.now().isoformat()
                    self._log(f"\n>>> RECV [{timestamp}]: {json.dumps(request, indent=2)}\n")
                    
                    # Handle the request
                    response = await self.handle_jsonrpc(request)
                    
                    # Log response
                    timestamp = datetime.now().isoformat()
                    self._log(f"\n<<< SEND [{timestamp}]: {json.dumps(response, indent=2)}\n")
                    
                    # Send response
                    response_json = json.dumps(response) + '\n'
                    writer.write(response_json.encode('utf-8'))
                    await writer.drain()
                    
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Parse error: {e}"},
                        "id": None
                    }
                    timestamp = datetime.now().isoformat()
                    self._log(f"\n<<< ERROR [{timestamp}]: {json.dumps(error_response, indent=2)}\n")
                    writer.write((json.dumps(error_response) + '\n').encode('utf-8'))
                    await writer.drain()
                    
        except Exception as e:
            import traceback
            print(f"Error handling client {addr}: {e}")
            traceback.print_exc()
        finally:
            print(f"Client disconnected: {addr}")
            self._log(f"\n=== Client disconnected: {addr} ===\n")
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
    
    async def handle_jsonrpc(self, request: dict) -> dict:
        """Handle a JSON-RPC 2.0 request for MCP protocol."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            # Handle MCP protocol methods
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "pyrv32-simulator", "version": "1.0.0"}
                    },
                    "id": req_id
                }
            
            elif method == "tools/list":
                tools = self.get_tools()
                return {
                    "jsonrpc": "2.0",
                    "result": {"tools": tools},
                    "id": req_id
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await self.call_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": result},
                    "id": req_id
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": req_id
                }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": req_id
            }
    
    def get_tools(self) -> list[dict]:
        """Return list of available tools in MCP format."""
        return [
            {
                "name": "sim_create",
                "description": "Create a new simulator session. Returns session_id for use with other tools.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_addr": {"type": "string", "description": "Initial PC value in hex (default: 0x80000000)", "default": "0x80000000"},
                        "fs_root": {"type": "string", "description": "Root directory for filesystem syscalls (default: 'pyrv32_sim_fs')", "default": "pyrv32_sim_fs"}
                    }
                }
            },
            {
                "name": "sim_load",
                "description": "Load a RISC-V binary into simulator session.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "binary_path": {"type": "string", "description": "Path to RISC-V binary file"}
                    },
                    "required": ["session_id", "binary_path"]
                }
            },
            {
                "name": "sim_reset",
                "description": "Reset simulator session to initial state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_destroy",
                "description": "Destroy a simulator session.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_step",
                "description": "Execute one or more instructions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "count": {"type": "integer", "description": "Number of instructions (default: 1)", "default": 1}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_run",
                "description": "Run until halt, breakpoint, or max steps.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_run_until_output",
                "description": "Run until UART output is available or halt.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_get_status",
                "description": "Get current status of simulator session.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_debug_uart_read",
                "description": "Read available debug UART (0x10000000) output from simulator.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_debug_uart_has_data",
                "description": "Check if debug UART has new output data available.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_console_uart_read",
                "description": "Read available console UART (0x10001000) TX output from simulator.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_console_uart_write",
                "description": "Write data to console UART (0x10001000) RX input.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "data": {"type": "string", "description": "Data to write to UART RX"}
                    },
                    "required": ["session_id", "data"]
                }
            },
            {
                "name": "sim_console_uart_has_data",
                "description": "Check if console UART has new output data available.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_get_registers",
                "description": "Get all register values.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_get_register",
                "description": "Get single register value by number or name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "register": {"type": "string", "description": "Register number (0-31) or name (x0-x31, zero, ra, sp, etc.)"}
                    },
                    "required": ["session_id", "register"]
                }
            },
            {
                "name": "sim_set_register",
                "description": "Set register value by number or name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "register": {"type": "string", "description": "Register number or name"},
                        "value": {"type": "string", "description": "Value to set (hex string like '0x12345678')"}
                    },
                    "required": ["session_id", "register", "value"]
                }
            },
            {
                "name": "sim_read_memory",
                "description": "Read memory from simulator.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex (like '0x80000000')"},
                        "length": {"type": "integer", "description": "Number of bytes to read"}
                    },
                    "required": ["session_id", "address", "length"]
                }
            },
            {
                "name": "sim_write_memory",
                "description": "Write memory to simulator.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex"},
                        "data": {"type": "string", "description": "Hex string of bytes to write (like 'deadbeef')"}
                    },
                    "required": ["session_id", "address", "data"]
                }
            },
            {
                "name": "sim_add_breakpoint",
                "description": "Add breakpoint at address.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Breakpoint address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_remove_breakpoint",
                "description": "Remove breakpoint at address.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Breakpoint address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_list_breakpoints",
                "description": "List all breakpoints.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> list[dict]:
        """Call a tool and return results in MCP format."""
        try:
            # Session management
            if name == "sim_create":
                start_addr = int(arguments.get("start_addr", "0x80000000"), 16)
                fs_root = arguments.get("fs_root", "pyrv32_sim_fs")
                session_id = self.session_manager.create_session(start_addr, fs_root)
                return [{"type": "text", "text": f"Created session: {session_id}"}]
            
            elif name == "sim_destroy":
                success = self.session_manager.destroy_session(arguments["session_id"])
                msg = f"Destroyed session: {arguments['session_id']}" if success else "Error: Session not found"
                return [{"type": "text", "text": msg}]
            
            # Get session for all other operations
            session_id = arguments.get("session_id")
            if not session_id:
                return [{"type": "text", "text": "Error: session_id required"}]
            
            session = self.session_manager.get_session(session_id)
            if not session:
                return [{"type": "text", "text": f"Error: Session {session_id} not found"}]
            
            # Binary operations
            if name == "sim_load":
                session.load_binary(arguments["binary_path"])
                return [{"type": "text", "text": f"Loaded binary: {arguments['binary_path']}"}]
            
            elif name == "sim_reset":
                session.reset()
                return [{"type": "text", "text": f"Reset session: {session_id}"}]
            
            # Execution
            elif name == "sim_step":
                result = session.step(arguments.get("count", 1))
                text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                if result.error:
                    text += f"\nError: {result.error}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_run":
                result = session.run(arguments.get("max_steps", 1000000))
                text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                if result.error:
                    text += f"\nError: {result.error}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_run_until_output":
                result = session.run_until_output(arguments.get("max_steps", 1000000))
                text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                if result.error:
                    text += f"\nError: {result.error}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_get_status":
                status = session.get_status()
                text = f"PC: 0x{status['pc']:08x}\nInstructions: {status['instruction_count']}\nHalted: {status['halted']}\nUART has data: {status['uart_has_data']}"
                return [{"type": "text", "text": text}]
            
            # Debug UART
            elif name == "sim_debug_uart_read":
                data = session.debug_uart_read()
                return [{"type": "text", "text": data}]
            
            elif name == "sim_debug_uart_has_data":
                has_data = session.debug_uart_has_data()
                return [{"type": "text", "text": str(has_data)}]
            
            elif name == "sim_console_uart_read":
                data = session.console_uart_read()
                return [{"type": "text", "text": data}]
            
            elif name == "sim_console_uart_write":
                session.console_uart_write(arguments["data"])
                return [{"type": "text", "text": "Data written to console UART RX"}]
            
            elif name == "sim_console_uart_has_data":
                has_data = session.console_uart_has_data()
                return [{"type": "text", "text": str(has_data)}]
            
            # Registers
            elif name == "sim_get_registers":
                regs = session.get_registers()
                text = "\n".join([f"{k}: 0x{v:08x}" for k, v in sorted(regs.items())])
                return [{"type": "text", "text": text}]
            
            elif name == "sim_get_register":
                value = session.get_register(arguments["register"])
                return [{"type": "text", "text": f"0x{value:08x}"}]
            
            elif name == "sim_set_register":
                value = int(arguments["value"], 16) if isinstance(arguments["value"], str) else arguments["value"]
                session.set_register(arguments["register"], value)
                return [{"type": "text", "text": f"Set {arguments['register']} = {arguments['value']}"}]
            
            # Memory
            elif name == "sim_read_memory":
                address = int(arguments["address"], 16)
                data = session.read_memory(address, arguments["length"])
                return [{"type": "text", "text": data.hex()}]
            
            elif name == "sim_write_memory":
                address = int(arguments["address"], 16)
                data = bytes.fromhex(arguments["data"])
                session.write_memory(address, data)
                return [{"type": "text", "text": "Memory written"}]
            
            # Breakpoints
            elif name == "sim_add_breakpoint":
                address = int(arguments["address"], 16)
                session.add_breakpoint(address)
                return [{"type": "text", "text": f"Added breakpoint at {arguments['address']}"}]
            
            elif name == "sim_remove_breakpoint":
                address = int(arguments["address"], 16)
                session.remove_breakpoint(address)
                return [{"type": "text", "text": f"Removed breakpoint at {arguments['address']}"}]
            
            elif name == "sim_list_breakpoints":
                breakpoints = session.list_breakpoints()
                text = "\n".join([hex(bp) for bp in breakpoints]) if breakpoints else "No breakpoints"
                return [{"type": "text", "text": text}]
            
            else:
                return [{"type": "text", "text": f"Error: Unknown tool {name}"}]
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return [{"type": "text", "text": f"Error: {str(e)}"}]
    
    async def run(self, host="127.0.0.1", port=5555):
        """Run the TCP server."""
        server = await asyncio.start_server(
            self.handle_client,
            host,
            port
        )
        
        addr = server.sockets[0].getsockname()
        print(f"pyrv32 MCP Simulator Server (JSON-RPC over TCP)")
        print(f"Listening on {addr[0]}:{addr[1]}")
        print(f"Press Ctrl+C to stop")
        
        async with server:
            await server.serve_forever()


async def main():
    """Main entry point."""
    server = MCPSimulatorServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    asyncio.run(main())
