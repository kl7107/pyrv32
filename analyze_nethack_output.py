#!/usr/bin/env python3
"""Run NetHack via MCP and capture raw console output for analysis."""

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

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5555))
    
    print("Creating session...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_create",
        "arguments": {"fs_root": ".", "start_addr": "0x80000000"}
    })
    session_id = result['result']['content'][0]['text'].split(": ")[1]
    print(f"Session: {session_id}")
    
    print("\nLoading nethack.bin...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_load",
        "arguments": {
            "session_id": session_id,
            "binary_path": "/home/dev/git/zesarux/pyrv32/firmware/nethack.bin"
        }
    })
    print(result['result']['content'][0]['text'])
    
    # Run initial setup - NetHack waits for newline to start
    print("\nRunning initial steps...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_run",
        "arguments": {"session_id": session_id, "max_steps": 10000}
    })
    print(result['result']['content'][0]['text'])
    
    # Send newline to start
    print("\nSending newline to start NetHack...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_console_uart_write",
        "arguments": {"session_id": session_id, "data": "\n"}
    })
    
    # Run more
    print("Running more steps...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_run",
        "arguments": {"session_id": session_id, "max_steps": 100000}
    })
    print(result['result']['content'][0]['text'])
    
    # Read output
    print("\nReading console output...")
    result = send_mcp_request(sock, "tools/call", {
        "name": "sim_console_uart_read",
        "arguments": {"session_id": session_id}
    })
    output = result['result']['content'][0]['text']
    
    # Save raw output
    raw_file = '/tmp/nethack_raw_output.txt'
    with open(raw_file, 'w') as f:
        f.write(output)
    
    print(f"\nRaw output saved to: {raw_file}")
    print(f"Output length: {len(output)} characters")
    
    # Analyze output
    print("\n" + "="*70)
    print("OUTPUT ANALYSIS")
    print("="*70)
    
    # Count escape sequences
    esc_count = output.count('\x1b')
    print(f"Escape sequences: {esc_count}")
    
    # Show first 500 chars with escapes visible
    print("\nFirst 500 characters (with escape codes):")
    print(repr(output[:500]))
    
    # Extract escape sequences
    import re
    escapes = re.findall(r'\x1b\[[^a-zA-Z]*[a-zA-Z]', output)
    unique_escapes = set(escapes)
    print(f"\nUnique escape sequences found: {len(unique_escapes)}")
    for esc in sorted(unique_escapes)[:20]:  # Show first 20
        print(f"  {repr(esc)}")
    
    # Check for common patterns
    if '\x1b[2J' in output:
        print("\n✓ Found clear screen (ESC[2J)")
    if '\x1b[H' in output:
        print("✓ Found cursor home (ESC[H)")
    if '\x1b[B' in output:
        print("✓ Found cursor down (ESC[B)")
    if '\x1b[D' in output:
        print("✓ Found cursor left (ESC[D)")
    
    sock.close()

if __name__ == '__main__':
    main()
