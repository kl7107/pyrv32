#!/usr/bin/env python3
"""
Startup script for pyrv32 MCP relay proxy.

This is a dumb byte relay between VS Code (stdio) and the MCP TCP server.

Run with: python3 mcp/run_server.py
Or make executable and run: ./mcp/run_server.py
"""

import sys
import os

# Add parent directory to path so we can import pyrv32 modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrv32_mcp.relay_proxy import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
