#!/usr/bin/env python3
"""Test console UART via MCP tools directly (bypassing VS Code client)."""

import socket
import json
import time

def send_mcp_request(sock, method, params=None):
    """Send MCP request and get response."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method
    }
    if params:
        request["params"] = params
    
    sock.sendall((json.dumps(request) + '\n').encode())
    
    response = b''
    while b'\n' not in response:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    
    return json.loads(response.decode())

def test_interpreter():
    """Test interpreter_test.bin through MCP console UART tools."""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5555))
    
    print("="*60)
    print("TESTING CONSOLE UART VIA MCP")
    print("="*60)
    
    # Step 1: Create session
    print("\n1. Creating session...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_create",
        "arguments": {"fs_root": ".", "start_addr": "0x80000000"}
    })
    session_id = result['result']['content'][0]['text'].split(": ")[1]
    print(f"   Session ID: {session_id}")
    
    # Step 2: Load interpreter
    print("\n2. Loading interpreter_test.bin...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_load",
        "arguments": {
            "session_id": session_id,
            "binary_path": "/home/dev/git/zesarux/pyrv32/firmware/interpreter_test.bin"
        }
    })
    print(f"   {result['result']['content'][0]['text']}")
    
    # Step 3: Run program to initialize
    print("\n3. Running program (5000 steps)...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_run",
        "arguments": {"session_id": session_id, "max_steps": 5000}
    })
    print(f"   {result['result']['content'][0]['text']}")
    
    # Step 4: Read console UART output (banner + prompt)
    print("\n4. Reading console UART output...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_console_uart_read",
        "arguments": {"session_id": session_id}
    })
    output = result['result']['content'][0]['text']
    print(f"   Output:\n{output}")
    
    # Step 5: Send "ADD 42 13" command
    print("\n5. Sending command: ADD 42 13")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_console_uart_write",
        "arguments": {"session_id": session_id, "data": "ADD 42 13\n"}
    })
    print(f"   {result['result']['content'][0]['text']}")
    
    # Step 6: Run to process command
    print("\n6. Running to process command...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_run",
        "arguments": {"session_id": session_id, "max_steps": 5000}
    })
    print(f"   {result['result']['content'][0]['text']}")
    
    # Step 7: Read response
    print("\n7. Reading response...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_console_uart_read",
        "arguments": {"session_id": session_id}
    })
    response = result['result']['content'][0]['text']
    print(f"   Response:\n{response}")
    
    # Verify we got "55"
    if "55" in response:
        print("\n✓ SUCCESS: Got correct response (55)!")
    else:
        print(f"\n✗ FAIL: Expected '55' in response")
    
    # Step 8: Test ECHO command
    print("\n8. Sending command: ECHO Hello MCP")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_console_uart_write",
        "arguments": {"session_id": session_id, "data": "ECHO Hello MCP\n"}
    })
    
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_run",
        "arguments": {"session_id": session_id, "max_steps": 5000}
    })
    
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_console_uart_read",
        "arguments": {"session_id": session_id}
    })
    response = result['result']['content'][0]['text']
    print(f"   Response:\n{response}")
    
    if "Hello MCP" in response:
        print("\n✓ SUCCESS: ECHO command works!")
    else:
        print(f"\n✗ FAIL: Expected 'Hello MCP' in response")
    
    sock.close()
    
    print("\n" + "="*60)
    print("CONSOLE UART INTERACTIVE TEST COMPLETE")
    print("="*60)

if __name__ == '__main__':
    test_interpreter()
