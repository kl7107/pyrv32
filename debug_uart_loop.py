#!/usr/bin/env python3
import sys
import os
import socket
import json
import time
import re

class MCPClient:
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.request_id = 0

    def _send(self, method, params=None):
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.sendall((json.dumps(request) + "\n").encode('utf-8'))
            data = sock.recv(4096)
            sock.close()
            response = json.loads(data.decode('utf-8').strip())
            if "error" in response:
                raise RuntimeError(f"MCP Error: {response['error']}")
            return response.get("result")
        except Exception as e:
            raise RuntimeError(f"Communication error: {e}")

    def call_tool(self, name, arguments=None):
        params = {
            "name": name,
            "arguments": arguments or {}
        }
        result = self._send("tools/call", params)
        if result and "content" in result:
            text_content = "".join([c["text"] for c in result["content"] if c["type"] == "text"])
            return text_content
        return result

def main():
    client = MCPClient()
    
    print("Creating session...")
    output = client.call_tool("sim_create", {"start_addr": "0x80000000"})
    match = re.search(r"Created session: ([a-f0-9\-]+)", output)
    if not match:
        print("Could not parse session ID")
        return
    session_id = match.group(1)
    print(f"Session ID: {session_id}")

    try:
        print("Loading NetHack ELF...")
        elf_path = os.path.abspath("nethack-3.4.3/src/nethack.elf")
        client.call_tool("sim_load_elf", {
            "session_id": session_id,
            "elf_path": elf_path
        })
        
        print("Running until console status read...")
        client.call_tool("sim_run_until_console_status_read", {
            "session_id": session_id,
            "max_steps": 2000000
        })
        
        status = client.call_tool("sim_get_status", {"session_id": session_id})
        print(f"Status 1: {status}")
        
        # Disassemble around PC
        match = re.search(r"PC: (0x[0-9a-fA-F]+)", status)
        if match:
            pc = match.group(1)
            print(f"Disassembling around {pc}...")
            # Convert hex string to int, add offset, convert back
            pc_val = int(pc, 16)
            end_val = pc_val + 32
            end_str = hex(end_val)
            
            disasm = client.call_tool("sim_disassemble", {
                "session_id": session_id,
                "start_addr": pc,
                "end_addr": end_str
            })
            print(disasm)

        print("Injecting 'l'...")
        client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "l"})
        
        # Check UART status register (0x10001008)
        # Note: Reading it might clear it if it was a read-to-clear register, but status usually isn't.
        # However, sim_read_memory might not trigger side effects in some sims, but in pyrv32 it might.
        # Let's just run again and see if it advances more than 10 instructions.
        
        print("Running again...")
        client.call_tool("sim_run_until_console_status_read", {
            "session_id": session_id,
            "max_steps": 2000000
        })
        
        status = client.call_tool("sim_get_status", {"session_id": session_id})
        print(f"Status 2: {status}")

    finally:
        client.call_tool("sim_destroy", {"session_id": session_id})

if __name__ == "__main__":
    main()
