#!/usr/bin/env python3
"""
Update MCP server to add separate debug and console UART tools.
"""

import sys

# Read the current file
with open('/home/dev/git/zesarux/pyrv32/pyrv32_mcp/sim_server_mcp_v2.py', 'r') as f:
    content = f.read()

# Find where to insert new tools (after sim_uart_has_data tool definition)
uart_has_data_tool = '''{
                "name": "sim_uart_has_data",
                "description": "Check if UART has output data available.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string", "description": "Session identifier"}},
                    "required": ["session_id"]
                }
            },'''

new_uart_tools = '''{
                "name": "sim_uart_has_data",
                "description": "Check if debug UART has output data available (legacy).",
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
            },'''

content = content.replace(uart_has_data_tool, new_uart_tools)

# Now add the handlers in call_tool method
# Find the sim_uart_has_data handler
uart_has_data_handler = '''            elif name == "sim_uart_has_data":
                has_data = session.uart_has_data()
                return [{"type": "text", "text": str(has_data)}]'''

new_uart_handlers = '''            elif name == "sim_uart_has_data":
                has_data = session.uart_has_data()
                return [{"type": "text", "text": str(has_data)}]
            
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
                return [{"type": "text", "text": str(has_data)}]'''

content = content.replace(uart_has_data_handler, new_uart_handlers)

# Write back
with open('/home/dev/git/zesarux/pyrv32/pyrv32_mcp/sim_server_mcp_v2.py', 'w') as f:
    f.write(content)

print("✓ Updated sim_server_mcp_v2.py with dual UART tools")
print("  Added tools: sim_debug_uart_read, sim_debug_uart_has_data")
print("              sim_console_uart_read, sim_console_uart_write, sim_console_uart_has_data")
