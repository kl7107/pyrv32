# MCP Server Setup for VS Code - COMPLETED ✅

## Configuration Installed

Your pyrv32 MCP server is now configured in VS Code at:
`~/.vscode-server/data/Machine/settings.json`

```json
{
    "github.copilot.chat.mcp.servers": {
        "pyrv32": {
            "command": "/home/dev/git/zesarux/pyrv32/venv/bin/python",
            "args": [
                "/home/dev/git/zesarux/pyrv32/pyrv32_mcp/run_server.py"
            ]
        }
    }
}
```

## Next Steps to Activate

1. **Reload VS Code Window**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Developer: Reload Window"
   - Press Enter

2. **Verify MCP Server in Copilot Chat**
   - Open GitHub Copilot Chat panel
   - Look for MCP server status or available tools
   - You should see 19 pyrv32 tools available

3. **Test the MCP Server**
   - In Copilot Chat, try asking: "Create a new pyrv32 simulator session"
   - The AI should use the `sim_create` tool

## Available Tools (19 total)

### Session Management
- `sim_create` - Create new simulator session
- `sim_destroy` - Cleanup session
- `sim_reset` - Reset simulator
- `sim_load` - Load RISC-V ELF binary

### Execution Control
- `sim_step` - Execute N instructions
- `sim_run` - Run until halt/breakpoint
- `sim_run_until_output` - Run until UART output
- `sim_get_status` - Query execution status

### UART I/O (for interactive programs like NetHack)
- `sim_uart_read` - Read available output
- `sim_uart_write` - Write input data
- `sim_uart_has_data` - Check for data

### Debugging
- `sim_get_registers` - Read all registers
- `sim_get_register` - Read specific register
- `sim_set_register` - Modify register
- `sim_read_memory` - Read memory range
- `sim_write_memory` - Write memory
- `sim_add_breakpoint` - Set breakpoint
- `sim_remove_breakpoint` - Clear breakpoint
- `sim_list_breakpoints` - List all breakpoints

## Troubleshooting

### If MCP server doesn't appear:
1. Check the Developer Console (Help → Toggle Developer Tools)
2. Look for MCP-related errors
3. Verify the virtual environment exists:
   ```bash
   ls -la /home/dev/git/zesarux/pyrv32/venv/bin/python
   ```

### If tools aren't working:
1. Test the server manually:
   ```bash
   cd /home/dev/git/zesarux/pyrv32
   venv/bin/python pyrv32_mcp/test_integration.py
   ```

### Manual testing:
```bash
cd /home/dev/git/zesarux/pyrv32
venv/bin/python test_mcp_locally.py
```

## Example Usage in Copilot Chat

```
You: "Load and run the NetHack binary, show me the initial output"

Copilot will:
1. Create session with sim_create
2. Load binary with sim_load
3. Run until output with sim_run_until_output
4. Read UART with sim_uart_read
5. Display the NetHack welcome screen
```

## Status: READY ✅

- ✅ Virtual environment created with MCP SDK
- ✅ MCP server implemented (19 tools)
- ✅ Configuration installed in VS Code
- ✅ Server tested and working

Just **reload your VS Code window** and you're ready to use AI-assisted RISC-V debugging!
