# pyrv32 MCP Server

MCP (Model Context Protocol) server for the pyrv32 RISC-V simulator. Enables AI assistants to interactively debug and control RISC-V programs.

## Features

- 🎮 Interactive program execution with UART I/O
- 🐛 Step-by-step debugging with breakpoints
- 📊 Register and memory inspection/modification
- 🔄 Multi-session support (multiple simultaneous debug sessions)
- 🎯 Perfect for AI-assisted NetHack gameplay and embedded debugging

## Quick Start

### Installation

```bash
git clone https://github.com/YOUR-USERNAME/zesarux.git
cd zesarux/pyrv32
python3 -m venv venv
venv/bin/pip install -r pyrv32_mcp/requirements.txt
```

### VS Code Configuration

Add to your VS Code MCP settings (`.vscode/settings.json` or Claude Desktop config):

```json
{
  "mcpServers": {
    "pyrv32": {
      "command": "/full/path/to/zesarux/pyrv32/venv/bin/python",
      "args": ["/full/path/to/zesarux/pyrv32/pyrv32_mcp/run_server.py"]
    }
  }
}
```

### Test It

```bash
venv/bin/python pyrv32_mcp/test_integration.py
```

## Available Tools

### Session Management
- `sim_create` - Create new simulator session
- `sim_load` - Load RISC-V binary
- `sim_reset` - Reset session state
- `sim_destroy` - Cleanup session

### Execution Control
- `sim_step` - Execute N instructions
- `sim_run` - Run until halt/breakpoint
- `sim_run_until_output` - Run until UART data available
- `sim_get_status` - Query execution status

### Interactive I/O (Key Feature!)
- `sim_uart_read` - Read program output
- `sim_uart_write` - Send input to program
- `sim_uart_has_data` - Check for available output

### Debugging
- `sim_get_registers` / `sim_get_register` / `sim_set_register`
- `sim_read_memory` / `sim_write_memory`
- `sim_add_breakpoint` / `sim_remove_breakpoint` / `sim_list_breakpoints`

## Example Use Cases

### AI-Assisted NetHack Gameplay
```
You: "Load NetHack and help me create a character"
AI: *uses sim_create, sim_load, sim_run_until_output*
AI: "The game is asking for your name. What would you like to be called?"
You: "Gandalf"
AI: *uses sim_uart_write to send name, continues interacting*
```

### Interactive Debugging
```
You: "Debug my program and find why it crashes"
AI: *sets breakpoints, steps through code, inspects registers/memory*
AI: "Found it - you're writing to 0x00000000. Here's the fix..."
```

## Requirements

- Python 3.8+
- RISC-V toolchain (for compiling programs to debug)
- MCP-compatible AI client (VS Code with GitHub Copilot, Claude Desktop, etc.)

## License

[Your License Here]

## Contributing

This MCP server is part of the ZEsarUX project. See main repository for contribution guidelines.

## Related Projects

- [MCP Official Servers](https://github.com/modelcontextprotocol/servers)
- [ZEsarUX Emulator](https://github.com/chernandezba/zesarux)
