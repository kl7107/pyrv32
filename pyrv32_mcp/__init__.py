"""
MCP (Model Context Protocol) server for pyrv32 RISC-V simulator.

This package provides an MCP server that exposes the pyrv32 simulator
as a set of tools, enabling AI assistants to:
- Create and manage simulator sessions
- Load and execute RISC-V binaries
- Control execution (step, run, breakpoints)
- Perform interactive I/O via UART (key for NetHack)
- Inspect registers and memory
- Debug programs

The server uses stdio transport for communication with MCP clients.
"""

# Note: Renamed from 'mcp' to 'pyrv32_mcp' to avoid shadowing the mcp library

from .session_manager import SessionManager
from .pyrv32_server import PyRV32Server

__all__ = ['SessionManager', 'PyRV32Server']
