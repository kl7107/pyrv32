#!/usr/bin/env python3
"""Test MCP server directly to verify console UART tools are advertised."""

import socket
import json

def test_mcp_connection():
    # Connect to MCP server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5555))
    
    # Send tools/list request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    sock.sendall((json.dumps(request) + '\n').encode())
    
    # Read response
    response = b''
    while b'\n' not in response:
        response += sock.recv(4096)
    
    data = json.loads(response.decode())
    tools = data.get('result', {}).get('tools', [])
    
    print(f"Total tools: {len(tools)}\n")
    
    # Find console UART tools
    console_tools = [t for t in tools if 'console' in t['name']]
    
    if console_tools:
        print("✓ Console UART tools found:")
        for tool in console_tools:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
    else:
        print("✗ No console UART tools found!")
        print("\nAll tool names:")
        for tool in tools:
            print(f"  - {tool['name']}")
    
    sock.close()

if __name__ == '__main__':
    test_mcp_connection()
