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
                        "fs_root": {"type": "string", "description": "Root directory for filesystem syscalls (default: '/home/dev/git/pyrv32/pyrv32_sim_fs')", "default": "/home/dev/git/pyrv32/pyrv32_sim_fs"}
                    }
                }
            },
            {
                "name": "sim_load_elf",
                "description": "Load a RISC-V ELF file into simulator session. Parses ELF structure, loads PT_LOAD segments, and sets PC to entry point.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "elf_path": {"type": "string", "description": "Path to RISC-V ELF file"},
                        "argv": {"type": "array", "description": "Optional argv list (excluding program name)", "items": {"type": "string"}},
                        "envp": {"type": "array", "description": "Optional environment variables (VAR=VALUE)", "items": {"type": "string"}}
                    },
                    "required": ["session_id", "elf_path"]
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
                "name": "sim_set_cwd",
                "description": "Set working directory for filesystem syscalls.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "cwd": {"type": "string", "description": "Working directory path"}
                    },
                    "required": ["session_id", "cwd"]
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
                "description": "Run until halt, breakpoint, or max steps. Optionally include screen state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000},
                        "include_screen": {"type": "boolean", "description": "Include VT100 screen in response (default: false)", "default": False}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_run_until_output",
                "description": "Run until UART output is available or halt. Optionally include screen state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000},
                        "include_screen": {"type": "boolean", "description": "Include VT100 screen in response (default: false)", "default": False}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_run_until_console_status_read",
                "description": "Run until a read instruction accesses Console UART RX Status (0x10001008). Useful for detecting when a program polls for input. Optionally include screen state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000},
                        "include_screen": {"type": "boolean", "description": "Include VT100 screen in response (default: false)", "default": False}
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
                "name": "sim_get_load_info",
                "description": "Get metadata about the last ELF loaded (entry point, segments, symbol count).",
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
                "name": "sim_get_screen",
                "description": "Get VT100 terminal screen as text (80x24).",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_dump_screen",
                "description": "Dump VT100 screen to /tmp/screen_dump.log and return it.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "show_cursor": {"type": "boolean", "description": "Include cursor position (default: true)"}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_inject_input",
                "description": "Legacy alias of sim_console_uart_write (simulate keyboard input).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "data": {"type": "string", "description": "Input string to inject"}
                    },
                    "required": ["session_id", "data"]
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
            },
            {
                "name": "sim_get_trace",
                "description": "Get instruction trace buffer entries (last N instructions).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "count": {"type": "integer", "description": "Number of trace entries to retrieve (default: 20)"}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_add_read_watchpoint",
                "description": "Add memory read watchpoint at address. Breaks execution when address is read.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_add_write_watchpoint",
                "description": "Add memory write watchpoint at address. Breaks execution when address is written.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_remove_read_watchpoint",
                "description": "Remove memory read watchpoint at address.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_remove_write_watchpoint",
                "description": "Remove memory write watchpoint at address.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_list_watchpoints",
                "description": "List all memory watchpoints (read and write).",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_lookup_symbol",
                "description": "Look up symbol address by name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "name": {"type": "string", "description": "Symbol name (function or variable)"}
                    },
                    "required": ["session_id", "name"]
                }
            },
            {
                "name": "sim_reverse_lookup",
                "description": "Look up symbol name by address.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_get_symbol_info",
                "description": "Get symbol information for an address (finds nearest symbol at or before address).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "address": {"type": "string", "description": "Memory address in hex"}
                    },
                    "required": ["session_id", "address"]
                }
            },
            {
                "name": "sim_disassemble",
                "description": "Disassemble code with source interleaving using objdump -d -S.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "start_addr": {"type": "string", "description": "Start address in hex"},
                        "end_addr": {"type": "string", "description": "End address in hex"}
                    },
                    "required": ["session_id", "start_addr", "end_addr"]
                }
            },
            # === NEW HIGH-LEVEL INTERACTIVE TOOLS ===
            {
                "name": "sim_run_until_input_consumed",
                "description": "Run until input buffer is empty. If then_idle=True (default), continues running until program has done significant work after consuming input, ensuring screen updates have occurred.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000},
                        "then_idle": {"type": "boolean", "description": "Continue until idle after input consumed (default: true)", "default": True},
                        "min_idle_instructions": {"type": "integer", "description": "Min instructions to consider idle (default: 100)", "default": 100}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_run_until_idle",
                "description": "Run until program executes significant work (min_instructions) between input polls. Useful for detecting when program has finished processing and is idle.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 1000000)", "default": 1000000},
                        "min_instructions": {"type": "integer", "description": "Minimum instructions between polls to consider idle (default: 1000)", "default": 1000}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "sim_send_input_and_run",
                "description": "Write input to console UART and run until consumed. Returns status and optionally screen. This is the primary convenience method for interactive programs - replaces the pattern of console_uart_write + multiple run_until_console_status_read calls.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "data": {"type": "string", "description": "Input string to send (use \\n for Enter)"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 5000000)", "default": 5000000},
                        "include_screen": {"type": "boolean", "description": "Include VT100 screen in response (default: true)", "default": True}
                    },
                    "required": ["session_id", "data"]
                }
            },
            {
                "name": "sim_interactive_step",
                "description": "High-level 'do what I mean' for interactive programs. Injects input, runs until program is idle and waiting for more input, returns screen. One call replaces 5-8 lower-level calls.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "data": {"type": "string", "description": "Input string (use \\n for Enter)"},
                        "max_steps": {"type": "integer", "description": "Maximum instructions (default: 5000000)", "default": 5000000}
                    },
                    "required": ["session_id", "data"]
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> list[dict]:
        """Call a tool and return results in MCP format."""
        try:
            # Session management
            if name == "sim_create":
                start_addr = int(arguments.get("start_addr", "0x80000000"), 16)
                
                # Resolve fs_root relative to repository root
                if "fs_root" in arguments:
                    fs_root_arg = arguments["fs_root"]
                    # If relative path, make it relative to repo root
                    if not fs_root_arg.startswith('/'):
                        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        fs_root = os.path.join(repo_root, fs_root_arg)
                    else:
                        fs_root = fs_root_arg
                else:
                    # Default to pyrv32_sim_fs in repo root
                    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    fs_root = os.path.join(repo_root, "pyrv32_sim_fs")
                
                session_id = self.session_manager.create_session(start_addr, fs_root)
                return [{"type": "text", "text": f"Created session: {session_id}"}]
            
            elif name == "sim_destroy":
                success = self.session_manager.destroy_session(arguments["session_id"])
                msg = f"Destroyed session: {arguments['session_id']}" if success else "Error: Session not found"
                return [{"type": "text", "text": msg}]
            
            elif name == "sim_set_cwd":
                success = self.session_manager.set_working_directory(arguments["session_id"], arguments["cwd"])
                msg = f"Set working directory to: {arguments['cwd']}" if success else "Error: Session not found"
                return [{"type": "text", "text": msg}]
            
            # Get session for all other operations
            session_id = arguments.get("session_id")
            if not session_id:
                return [{"type": "text", "text": "Error: session_id required"}]
            
            session = self.session_manager.get_session(session_id)
            if not session:
                return [{"type": "text", "text": f"Error: Session {session_id} not found"}]
            
            # ELF loading
            if name == "sim_load_elf":
                argv = arguments.get("argv")
                envp = arguments.get("envp")
                result = session.load_elf(arguments["elf_path"], argv=argv, envp=envp)
                text = f"Loaded ELF: {arguments['elf_path']}\n"
                text += f"Entry point: 0x{result['entry_point']:08x}\n"
                text += f"Bytes loaded: {result['bytes_loaded']}\n"
                text += f"Symbols loaded: {result['symbols_loaded']}\n"
                text += f"Segments: {len(result['segments'])}\n"
                for i, seg in enumerate(result['segments']):
                    text += f"  Segment {i}: vaddr=0x{seg['vaddr']:08x} memsz={seg['memsz']} filesz={seg['filesz']} flags=0x{seg['flags']:x}\n"
                if 'argc' in result:
                    text += f"argc: {result['argc']}\n"
                    text += f"argv: {result.get('argv', [])}\n"
                    text += f"envp: {result.get('envp', [])}\n"
                return [{"type": "text", "text": text}]
            
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
                if arguments.get("include_screen", False):
                    screen = session.get_screen_text()
                    if screen:
                        text += f"\n\n=== SCREEN ===\n{screen}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_run_until_output":
                result = session.run_until_output(arguments.get("max_steps", 1000000))
                text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                if result.error:
                    text += f"\nError: {result.error}"
                if arguments.get("include_screen", False):
                    screen = session.get_screen_text()
                    if screen:
                        text += f"\n\n=== SCREEN ===\n{screen}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_run_until_console_status_read":
                result = session.run_until_console_status_read(arguments.get("max_steps", 1000000))
                text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                if result.error:
                    text += f"\nError: {result.error}"
                if arguments.get("include_screen", False):
                    screen = session.get_screen_text()
                    if screen:
                        text += f"\n\n=== SCREEN ===\n{screen}"
                return [{"type": "text", "text": text}]
            
            # === NEW HIGH-LEVEL INTERACTIVE TOOLS ===
            
            elif name == "sim_run_until_input_consumed":
                result = session.run_until_input_consumed(
                    arguments.get("max_steps", 1000000),
                    arguments.get("then_idle", True),
                    arguments.get("min_idle_instructions", 100)
                )
                text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                if result.error:
                    text += f"\nError: {result.error}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_run_until_idle":
                result = session.run_until_idle(
                    arguments.get("max_steps", 1000000),
                    arguments.get("min_instructions", 1000)
                )
                text = f"Status: {result.status}\nInstructions: {result.instruction_count}\nPC: 0x{result.pc:08x}"
                if result.error:
                    text += f"\nError: {result.error}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_send_input_and_run":
                data = arguments["data"]
                max_steps = arguments.get("max_steps", 5000000)
                include_screen = arguments.get("include_screen", True)
                
                result = session.send_input_and_run(data, max_steps, include_screen)
                
                text = f"Status: {result['status']}\nInstructions: {result['instructions']}\nPC: 0x{result['pc']:08x}"
                if result.get('error'):
                    text += f"\nError: {result['error']}"
                if include_screen and result.get('screen'):
                    text += f"\n\n=== SCREEN ===\n{result['screen']}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_interactive_step":
                data = arguments["data"]
                max_steps = arguments.get("max_steps", 5000000)
                
                result = session.interactive_step(data, max_steps)
                
                text = f"Status: {result['status']}\nInstructions: {result['instructions']}\nPC: 0x{result['pc']:08x}"
                if result.get('error'):
                    text += f"\nError: {result['error']}"
                if result.get('screen'):
                    text += f"\n\n=== SCREEN ===\n{result['screen']}"
                return [{"type": "text", "text": text}]
            
            elif name == "sim_get_status":
                status = session.get_status()
                text = f"PC: 0x{status['pc']:08x}\nInstructions: {status['instruction_count']}\nHalted: {status['halted']}\nConsole UART has output: {status['console_has_output']}"
                return [{"type": "text", "text": text}]

            elif name == "sim_get_load_info":
                info = session.last_load_info
                if not info:
                    return [{"type": "text", "text": "No ELF has been loaded in this session"}]
                text = f"ELF path: {info['elf_path']}\n"
                text += f"Entry point: 0x{info['entry_point']:08x}\n"
                text += f"Bytes loaded: {info['bytes_loaded']}\n"
                text += f"Symbols loaded: {info['symbols_loaded']}\n"
                text += f"Segments ({len(info['segments'])}):\n"
                for i, seg in enumerate(info['segments']):
                    text += f"  {i}: vaddr=0x{seg['vaddr']:08x} memsz={seg['memsz']} filesz={seg['filesz']} flags=0x{seg['flags']:x}\n"
                if 'argc' in info:
                    text += f"argc: {info['argc']}\n"
                    text += f"argv: {info.get('argv', [])}\n"
                    text += f"envp: {info.get('envp', [])}\n"
                return [{"type": "text", "text": text.rstrip()}]
            
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
            
            elif name in ("sim_console_uart_write", "sim_inject_input"):
                data = arguments["data"]
                session.console_uart_write(data)
                verb = "written" if name == "sim_console_uart_write" else "injected via legacy alias"
                return [{"type": "text", "text": f"Data {verb} to console UART RX ({len(data)} chars)"}]
            
            elif name == "sim_console_uart_has_data":
                has_data = session.console_uart_has_data()
                return [{"type": "text", "text": str(has_data)}]
            
            elif name == "sim_get_screen":
                screen_text = session.get_screen_text()
                if screen_text:
                    return [{"type": "text", "text": screen_text}]
                else:
                    return [{"type": "text", "text": "VT100 terminal not available"}]
            
            elif name == "sim_dump_screen":
                show_cursor = arguments.get("show_cursor", True)
                screen_text = session.dump_screen(show_cursor=show_cursor)
                if screen_text:
                    return [{"type": "text", "text": f"Screen dumped to /tmp/screen_dump.log\n\n{screen_text}"}]
                else:
                    return [{"type": "text", "text": "VT100 terminal not available"}]
            
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
                breakpoints = session.list_breakpoints()
                bp_to_remove = next((bp for bp in breakpoints if bp.address == address), None)
                if bp_to_remove:
                    session.remove_breakpoint(bp_to_remove.id)
                    return [{"type": "text", "text": f"Removed breakpoint at {arguments['address']}"}]
                else:
                    return [{"type": "text", "text": f"No breakpoint found at {arguments['address']}"}]
            
            elif name == "sim_list_breakpoints":
                breakpoints = session.list_breakpoints()
                if not breakpoints:
                    return [{"type": "text", "text": "No breakpoints set"}]
                bp_list = "\n".join([f"{hex(bp.address)} (ID {bp.id})" for bp in breakpoints])
                return [{"type": "text", "text": bp_list}]
            
            # Watchpoints
            elif name == "sim_add_read_watchpoint":
                address = int(arguments["address"], 16)
                session.add_read_watchpoint(address)
                return [{"type": "text", "text": f"Added read watchpoint at {arguments['address']}"}]
            
            elif name == "sim_add_write_watchpoint":
                address = int(arguments["address"], 16)
                session.add_write_watchpoint(address)
                return [{"type": "text", "text": f"Added write watchpoint at {arguments['address']}"}]
            
            elif name == "sim_remove_read_watchpoint":
                address = int(arguments["address"], 16)
                session.remove_read_watchpoint(address)
                return [{"type": "text", "text": f"Removed read watchpoint at {arguments['address']}"}]
            
            elif name == "sim_remove_write_watchpoint":
                address = int(arguments["address"], 16)
                session.remove_write_watchpoint(address)
                return [{"type": "text", "text": f"Removed write watchpoint at {arguments['address']}"}]
            
            elif name == "sim_list_watchpoints":
                read_wps = session.list_read_watchpoints()
                write_wps = session.list_write_watchpoints()
                result = []
                if read_wps:
                    result.append("Read watchpoints:")
                    for addr in read_wps:
                        result.append(f"  {hex(addr)}")
                if write_wps:
                    result.append("Write watchpoints:")
                    for addr in write_wps:
                        result.append(f"  {hex(addr)}")
                if not result:
                    return [{"type": "text", "text": "No watchpoints set"}]
                return [{"type": "text", "text": "\n".join(result)}]
            
            elif name == "sim_list_breakpoints":
                breakpoints = session.list_breakpoints()
                text = "\n".join([f"{hex(bp.address)} (ID {bp.id})" for bp in breakpoints]) if breakpoints else "No breakpoints"
                return [{"type": "text", "text": text}]
            
            # Symbol lookup
            elif name == "sim_lookup_symbol":
                addr = session.lookup_symbol(arguments["name"])
                if addr is not None:
                    return [{"type": "text", "text": f"{hex(addr)}"}]
                else:
                    return [{"type": "text", "text": f"Symbol '{arguments['name']}' not found"}]
            
            elif name == "sim_reverse_lookup":
                addr = int(arguments["address"], 16)
                name = session.reverse_lookup(addr)
                if name:
                    return [{"type": "text", "text": name}]
                else:
                    return [{"type": "text", "text": f"No symbol at {arguments['address']}"}]
            
            elif name == "sim_get_symbol_info":
                addr = int(arguments["address"], 16)
                info = session.get_symbol_info(addr)
                if info:
                    if info['offset'] == 0:
                        text = f"{info['name']} (exact match)"
                    else:
                        text = f"{info['name']}+{info['offset']} ({info['name']} + {info['offset']} bytes)"
                    return [{"type": "text", "text": text}]
                else:
                    return [{"type": "text", "text": f"No symbol found near {arguments['address']}"}]
            
            elif name == "sim_disassemble":
                output = session.disassemble(arguments["start_addr"], arguments["end_addr"])
                return [{"type": "text", "text": output}]

            elif name == "sim_disasm_cached":
                output = session.disassemble_cached(arguments["start_addr"], arguments["end_addr"])
                return [{"type": "text", "text": output}]
            
            elif name == "sim_get_trace":
                count = arguments.get("count", 20)
                # Enable trace if not already enabled
                if not session.debugger.trace_buffer.enabled:
                    session.debugger.trace_buffer.enabled = True
                
                trace_entries = session.debugger.trace_buffer.get_last(count)
                if not trace_entries:
                    return [{"type": "text", "text": "Trace buffer empty (may need to enable tracing)"}]
                
                lines = []
                for entry in trace_entries:
                    lines.append(f"[{entry.index:06d}] PC=0x{entry.pc:08x} insn=0x{entry.insn:08x}")
                return [{"type": "text", "text": "\n".join(lines)}]
            
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
