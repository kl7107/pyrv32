# pyrv32 MCP Server

MCP (Model Context Protocol) server for the pyrv32 RISC-V simulator. This server exposes the simulator as a set of tools that AI assistants can use to:

- Create and manage simulator sessions
- Load and execute RISC-V binaries  
- Control execution (step, run, breakpoints)
- Perform interactive I/O via UART (enables NetHack gameplay!)
- Inspect and modify registers and memory
- Debug programs with breakpoints

## Installation

1. Create virtual environment and install MCP SDK:
```bash
cd pyrv32
python3 -m venv venv
venv/bin/pip install -r pyrv32_mcp/requirements.txt
```

2. Configure your MCP client (e.g., Claude Desktop) to use this server:

Add to your MCP client configuration:
```json
{
  "mcpServers": {
    "pyrv32": {
      "command": "/path/to/zesarux/pyrv32/venv/bin/python",
      "args": ["/path/to/zesarux/pyrv32/pyrv32_mcp/run_server.py"]
    }
  }
}
```

## Testing

Run integration test to verify the server works:
```bash
venv/bin/python pyrv32_mcp/test_integration.py
```

This tests the complete workflow: session creation, binary loading, execution, UART I/O, register/memory access.

## Available Tools

### Session Management
- `sim_create` - Create new simulator session, returns session_id
- `sim_destroy` - Destroy session and free resources
- `sim_reset` - Reset session to initial state

### Program Loading
- `sim_load` - Load RISC-V ELF binary into session

### Execution Control
- `sim_step` - Execute one or more instructions
- `sim_run` - Run until halt/breakpoint/max_steps
- `sim_run_until_output` - Run until UART output available
- `sim_get_status` - Get current PC, instruction count, halt status

### Interactive I/O (KEY for NetHack)
- `sim_uart_read` - Read available UART output
- `sim_uart_write` - Write data to UART input
- `sim_uart_has_data` - Check if output available

### Debugging
- `sim_get_registers` - Get all register values
- `sim_get_register` - Get single register by name/number
- `sim_set_register` - Set register value
- `sim_read_memory` - Read memory range
- `sim_write_memory` - Write to memory
- `sim_add_breakpoint` - Add breakpoint at address
- `sim_remove_breakpoint` - Remove breakpoint
- `sim_list_breakpoints` - List all breakpoints

## Example Workflow: Interactive NetHack

```python
# AI assistant workflow:
session = sim_create()
sim_load(session, "nethack/nethack.bin")

# Run until first prompt
sim_run_until_output(session)
output = sim_uart_read(session)  # "NetHack, Copyright..."

# Respond to prompt
sim_uart_write(session, "\n")
sim_run_until_output(session)
output = sim_uart_read(session)  # "Who are you?"

# Enter character name
sim_uart_write(session, "Gandalf\n")
sim_run_until_output(session)
output = sim_uart_read(session)  # Game starts!

# Continue interactive gameplay...
```

## Architecture

- `pyrv32_server.py` - MCP server with 19 tool definitions
- `session_manager.py` - Manages multiple RV32System instances
- `run_server.py` - Startup script
- `test_integration.py` - End-to-end test
- Uses `pyrv32_system.py` from parent directory (stateful simulator)

**Note**: Package renamed from `mcp` to `pyrv32_mcp` to avoid shadowing the MCP library.

## Development

The server uses stdio transport for communication with MCP clients. All tools are async and return TextContent responses.

Session IDs are UUIDs, allowing multiple independent simulator sessions.
