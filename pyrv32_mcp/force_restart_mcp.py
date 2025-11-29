#!/usr/bin/env python3
"""Force restart MCP server without interactive commands."""

import subprocess
import sys
import time
import os

os.chdir('/home/dev/git/zesarux/pyrv32/pyrv32_mcp')

# Kill old servers silently
subprocess.run(['pkill', '-9', '-f', 'sim_server_mcp_v2'], capture_output=True)
subprocess.run(['pkill', '-9', '-f', 'run_server.py'], capture_output=True)
time.sleep(1)

# Start new server in background
with open('/tmp/mcp_server.log', 'w') as logfile:
    subprocess.Popen([
        '../venv/bin/python3',
        '-u',
        'sim_server_mcp_v2.py'
    ], stdout=logfile, stderr=logfile, start_new_session=True)

time.sleep(2)

# Verify it's running
result = subprocess.run(['pgrep', '-f', 'sim_server_mcp_v2'], capture_output=True)
if result.returncode == 0:
    print("✓ MCP server started")
else:
    print("✗ Server failed to start")
    sys.exit(1)

# Force VS Code to reconnect
subprocess.run(['pkill', '-f', 'run_server.py'], capture_output=True)
print("✓ Triggered VS Code reconnect")
print("\nWait 5-10 seconds for VS Code MCP client to reconnect...")
