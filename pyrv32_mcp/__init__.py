"""
MCP (Model Context Protocol) server for pyrv32 RISC-V simulator.

Provides an MCP server that exposes the pyrv32 simulator as tools for AI control.
Main entry point: sim_server_mcp_v2.py
"""

from .session_manager import SessionManager

__all__ = ['SessionManager']
