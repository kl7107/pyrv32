#!/usr/bin/env python3
"""Restart MCP server and verify tools are registered."""

import subprocess
import sys
import time
import os

os.chdir('/home/dev/git/zesarux/pyrv32/pyrv32_mcp')

# Step 1: Kill old servers
print("Step 1: Stopping old MCP servers...")
subprocess.run(['pkill', '-f', 'sim_server_mcp_v2'], capture_output=True)
subprocess.run(['pkill', '-f', 'run_server.py'], capture_output=True)
time.sleep(2)

# Step 2: Start new server
print("Step 2: Starting MCP server on port 5555...")
proc = subprocess.Popen([
    '../venv/bin/python3',
    '-u',
    'sim_server_mcp_v2.py'
], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Wait for startup
time.sleep(3)

# Check if running
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'sim_server_mcp_v2' in result.stdout:
    print("✓ MCP server is running")
    
    # Get some output
    import select
    if select.select([proc.stdout], [], [], 0)[0]:
        output = proc.stdout.read(500)
        print(f"Server output:\n{output}")
else:
    print("✗ Server failed to start")
    sys.exit(1)

print("\nStep 3: Test connection with nc...")
test_msg = '{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n'
result = subprocess.run(
    ['timeout', '2', 'bash', '-c', f'echo \'{test_msg}\' | nc localhost 5555'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    import json
    try:
        response = json.loads(result.stdout)
        tools = response.get('result', {}).get('tools', [])
        print(f"✓ Got {len(tools)} tools")
        
        console_tools = [t['name'] for t in tools if 'console' in t['name']]
        print(f"Console UART tools: {console_tools}")
        
        if console_tools:
            print("✓ Console UART tools are registered!")
        else:
            print("✗ Console UART tools missing!")
            sys.exit(1)
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Response: {result.stdout}")
else:
    print(f"✗ Connection failed: {result.stderr}")
    sys.exit(1)

print("\nStep 4: Trigger VS Code reconnect...")
subprocess.run(['pkill', '-f', 'run_server.py'], capture_output=True)

print("\n" + "="*60)
print("MCP SERVER READY")
print("="*60)
print("Console UART tools should now be available in VS Code")
print("Wait a few seconds for VS Code to reconnect")
