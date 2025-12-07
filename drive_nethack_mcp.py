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
            sock.settimeout(30.0)
            sock.connect((self.host, self.port))
            
            request_str = json.dumps(request) + "\n"
            sock.sendall(request_str.encode('utf-8'))
            
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'\n' in data:
                    break
            
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
        # MCP returns { "content": [ { "type": "text", "text": "..." } ] }
        if result and "content" in result:
            text_content = "".join([c["text"] for c in result["content"] if c["type"] == "text"])
            return text_content
        return result

def main():
    client = MCPClient()
    
    print("Initializing...")
    try:
        client._send("initialize")
    except Exception as e:
        print(f"Failed to initialize (might be already running): {e}")

    print("Creating session...")
    try:
        # sim_create returns "Created session: <uuid>"
        output = client.call_tool("sim_create", {"start_addr": "0x80000000"})
        print(f"Create output: {output}")
        # Extract session ID
        match = re.search(r"Created session: ([a-f0-9\-]+)", output)
        if not match:
            print("Could not parse session ID")
            return
        session_id = match.group(1)
        print(f"Session ID: {session_id}")
    except Exception as e:
        print(f"Failed to create session: {e}")
        return

    try:
        print("Loading NetHack ELF...")
        elf_path = os.path.abspath("nethack-3.4.3/src/nethack.elf")
        if not os.path.exists(elf_path):
            print(f"Error: ELF file not found at {elf_path}!")
            return

        load_result = client.call_tool("sim_load_elf", {
            "session_id": session_id,
            "elf_path": elf_path
        })
        print(f"Load result: {load_result}")
        
        # Check status to verify PC
        status = client.call_tool("sim_get_status", {"session_id": session_id})
        print(f"Status after load: {status}")
        
        print("Starting NetHack...")
        
        # State machine for character creation
        step_count = 0
        max_loops = 50
        handled_prompts = set()
        
        while step_count < max_loops:
            step_count += 1
            print(f"\n--- Loop {step_count} ---")
            
            print("Running until console status read...")
            
            # Check PC before run
            status_before = client.call_tool("sim_get_status", {"session_id": session_id})
            print(f"Status before run: {status_before}")

            # Run until the game polls for input
            status_output = client.call_tool("sim_run_until_console_status_read", {
                "session_id": session_id,
                "max_steps": 2000000
            })
            print(f"Run status: {status_output}")
            
            # Check screen
            screen_output = client.call_tool("sim_get_screen", {"session_id": session_id})
            print("Screen content:")
            print(screen_output)
            
            # Analyze screen and decide input
            if "Welcome to NetHack" in screen_output:
                print("SUCCESS: Reached Welcome screen!")
                break
            elif "Dlvl:1" in screen_output and "St:" in screen_output:
                print("SUCCESS: Game started! Character created.")
                break
            elif "--More--" in screen_output:
                print("Prompt: --More--")
                client.call_tool("sim_console_uart_write", {
                    "session_id": session_id,
                    "data": " "
                })
            elif "Pick an alignment" in screen_output or "Choosing Alignment" in screen_output:
                if "pick_alignment" not in handled_prompts:
                    print("Prompt: Pick an alignment")
                    # Pick Neutral
                    client.call_tool("sim_console_uart_write", {
                        "session_id": session_id,
                        "data": "n"
                    })
                    handled_prompts.add("pick_alignment")
            elif "Pick a gender" in screen_output or "Choosing Gender" in screen_output:
                if "pick_gender" not in handled_prompts:
                    print("Prompt: Pick a gender")
                    # Pick Female
                    client.call_tool("sim_console_uart_write", {
                        "session_id": session_id,
                        "data": "f"
                    })
                    handled_prompts.add("pick_gender")
            elif "Pick a race" in screen_output or "Choosing Race" in screen_output:
                print("Matched: Pick a race")
                if "pick_race" not in handled_prompts:
                    print("Prompt: Pick a race")
                    # Pick Human
                    client.call_tool("sim_console_uart_write", {
                        "session_id": session_id,
                        "data": "h"
                    })
                    handled_prompts.add("pick_race")
                else:
                    print("Already handled: pick_race")
            elif "Pick a role" in screen_output:
                if "pick_role_menu" not in handled_prompts:
                    print("Prompt: Pick a role (Menu)")
                    # Pick Valkyrie
                    client.call_tool("sim_console_uart_write", {
                        "session_id": session_id,
                        "data": "v"
                    })
                    handled_prompts.add("pick_role_menu")
            elif "Shall I pick a character" in screen_output:
                if "shall_i_pick" not in handled_prompts:
                    print("Prompt: Shall I pick a character?")
                    client.call_tool("sim_console_uart_write", {
                        "session_id": session_id,
                        "data": "n"
                    })
                    handled_prompts.add("shall_i_pick")
            elif "Who are you?" in screen_output:
                if "who_are_you" not in handled_prompts:
                    print("Prompt: Who are you? (Sending input)")
                    client.call_tool("sim_console_uart_write", {
                        "session_id": session_id,
                        "data": "Player\n"
                    })
                    handled_prompts.add("who_are_you")
                else:
                    print("Prompt: Who are you? (Waiting for processing)")
            else:
                print("Unknown state or waiting...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Destroying session...")
        try:
            client.call_tool("sim_destroy", {"session_id": session_id})
        except:
            pass

if __name__ == "__main__":
    main()
