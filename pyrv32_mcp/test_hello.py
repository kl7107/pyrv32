#!/usr/bin/env python3
"""Test hello.bin through the MCP TCP server directly."""

import socket
import json
import sys

def send_request(sock, method, params=None, req_id=1):
    """Send a JSON-RPC request and get response."""
    request = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method
    }
    if params:
        request["params"] = params
    
    request_json = json.dumps(request) + '\n'
    sock.sendall(request_json.encode('utf-8'))
    
    response_line = sock.makefile('r').readline()
    return json.loads(response_line)

# Connect to MCP server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5555))

try:
    # Initialize
    print("1. Initialize...")
    resp = send_request(sock, "initialize", {})
    print(f"   Result: {resp['result']['serverInfo']['name']}")
    
    # List tools
    print("\n2. List tools...")
    resp = send_request(sock, "tools/list")
    print(f"   Found {len(resp['result']['tools'])} tools")
    
    # Create session
    print("\n3. Create session...")
    resp = send_request(sock, "tools/call", {"name": "sim_create", "arguments": {}})
    session_id = resp['result']['content'][0]['text'].split(": ")[1]
    print(f"   Session ID: {session_id}")
    
    # Load binary
    print("\n4. Load hello.bin...")
    resp = send_request(sock, "tools/call", {
        "name": "sim_load",
        "arguments": {
            "session_id": session_id,
            "binary_path": "/home/dev/git/zesarux/pyrv32/firmware/hello.bin"
        }
    })
    print(f"   {resp['result']['content'][0]['text']}")
    
    # Run
    print("\n5. Run program...")
    resp = send_request(sock, "tools/call", {
        "name": "sim_run",
        "arguments": {"session_id": session_id, "max_steps": 10000}
    })
    print(f"   {resp['result']['content'][0]['text']}")
    
    # Read UART output
    print("\n6. Read UART output...")
    resp = send_request(sock, "tools/call", {
        "name": "sim_uart_read",
        "arguments": {"session_id": session_id}
    })
    output = resp['result']['content'][0]['text']
    print(f"   Output: {repr(output)}")
    
    print("\n✓ Test complete!")
    
finally:
    sock.close()
