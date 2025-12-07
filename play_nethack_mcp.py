#!/usr/bin/env python3
import sys
import os
import socket
import json
import time
import re
import random

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

def find_symbol(screen_lines, symbol):
    """Find coordinates (row, col) of a symbol on the screen."""
    for r, line in enumerate(screen_lines):
        if symbol in line:
            # Find all occurrences, but for @ there should be only one (usually)
            # For > there might be multiple (unlikely on one level unless special)
            c = line.find(symbol)
            return (r, c)
    return None

def get_direction(start, end):
    """Get the NetHack movement key to go from start to end."""
    r1, c1 = start
    r2, c2 = end
    
    dr = r2 - r1
    dc = c2 - c1
    
    # Normalize to -1, 0, 1
    step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
    step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
    
    if step_r == -1 and step_c == -1: return 'y'
    if step_r == -1 and step_c == 0:  return 'k'
    if step_r == -1 and step_c == 1:  return 'u'
    if step_r == 0  and step_c == -1: return 'h'
    if step_r == 0  and step_c == 1:  return 'l'
    if step_r == 1  and step_c == -1: return 'b'
    if step_r == 1  and step_c == 0:  return 'j'
    if step_r == 1  and step_c == 1:  return 'n'
    
    return None

def get_surrounding_tiles(screen_lines, r, c):
    """
    Returns a dict of direction_key -> (char, (nr, nc))
    Directions: h, j, k, l
    """
    rows = len(screen_lines)
    
    moves = {
        'k': (-1, 0), 'j': (1, 0), 'h': (0, -1), 'l': (0, 1)
    }
    
    surroundings = {}
    for key, (dr, dc) in moves.items():
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < len(screen_lines[nr]):
            char = screen_lines[nr][nc]
            surroundings[key] = (char, (nr, nc))
            
    return surroundings

def is_walkable(char):
    # . floor, # corridor, + door, > stairs, < stairs, $ gold
    # items: ) [ = " / % ? ! * (
    # traps: ^
    # fountains: {
    # altars: _
    # thrones: \
    walkable_chars = set(['.', '#', '+', '>', '<', '$', ')', '[', '=', '"', '/', '%', '?', '!', '*', '(', '_', '{', '\\', '^'])
    return char in walkable_chars

def main():
    client = MCPClient()
    
    print("Initializing...")
    try:
        client._send("initialize")
    except Exception as e:
        print(f"Failed to initialize (might be already running): {e}")

    print("Creating session...")
    session_id = None
    try:
        output = client.call_tool("sim_create", {"start_addr": "0x80000000"})
        print(f"Create output: {output}")
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

        client.call_tool("sim_load_elf", {
            "session_id": session_id,
            "elf_path": elf_path
        })
        
        print("Starting NetHack Character Creation...")
        
        step_count = 0
        max_loops = 100 # Increased for safety
        handled_prompts = set()
        game_started = False
        
        # Character Creation Loop
        while step_count < max_loops:
            step_count += 1
            
            client.call_tool("sim_run_until_console_status_read", {
                "session_id": session_id,
                "max_steps": 2000000
            })
            
            screen_output = client.call_tool("sim_get_screen", {"session_id": session_id})
            
            if "Dlvl:1" in screen_output and "St:" in screen_output:
                print("SUCCESS: Game started! Character created.")
                game_started = True
                break
            
            # Handle prompts
            if "--More--" in screen_output:
                print("Prompt: --More--")
                client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": " "})
            elif "Pick an alignment" in screen_output or "Choosing Alignment" in screen_output:
                if "pick_alignment" not in handled_prompts:
                    print("Prompt: Pick an alignment -> n")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "n"})
                    handled_prompts.add("pick_alignment")
            elif "Pick a gender" in screen_output or "Choosing Gender" in screen_output:
                if "pick_gender" not in handled_prompts:
                    print("Prompt: Pick a gender -> f")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "f"})
                    handled_prompts.add("pick_gender")
            elif "Pick a race" in screen_output or "Choosing Race" in screen_output:
                if "pick_race" not in handled_prompts:
                    print("Prompt: Pick a race -> h")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "h"})
                    handled_prompts.add("pick_race")
            elif "Pick a role" in screen_output:
                if "pick_role_menu" not in handled_prompts:
                    print("Prompt: Pick a role (Menu) -> v")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "v"})
                    handled_prompts.add("pick_role_menu")
            elif "Shall I pick a character" in screen_output:
                if "shall_i_pick" not in handled_prompts:
                    print("Prompt: Shall I pick a character? -> n")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "n"})
                    handled_prompts.add("shall_i_pick")
            elif "Who are you?" in screen_output:
                if "who_are_you" not in handled_prompts:
                    print("Prompt: Who are you? -> Player")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "Player\n"})
                    handled_prompts.add("who_are_you")
            else:
                # If we are stuck or waiting, just send a space to clear potential hidden prompts or just wait
                # But be careful not to spam
                pass

        if not game_started:
            print("Failed to start game within step limit.")
            return

        print("\n--- Entering Exploration Loop ---")
        
        exploration_steps = 0
        max_exploration_steps = 10000 # Increased to allow finding stairs
        
        last_player_pos = None
        stuck_count = 0
        visited = set()
        last_eat_attempt = -100

        while exploration_steps < max_exploration_steps:
            exploration_steps += 1
            if exploration_steps % 100 == 0:
                print(f"Exploration Step {exploration_steps}")
            
            status_output = client.call_tool("sim_run_until_console_status_read", {
                "session_id": session_id,
                "max_steps": 2000000
            })
            
            # Check PC to avoid injecting input during non-blocking checks (stdio buffering)
            pc_match = re.search(r"PC: (0x[0-9a-f]+)", status_output)
            if pc_match:
                pc = int(pc_match.group(1), 16)
                # Blocking wait is around 0x800000d8. Non-blocking is around 0x80000140.
                if 0x80000120 <= pc <= 0x80000160:
                    continue
            
            screen_output = client.call_tool("sim_get_screen", {"session_id": session_id})
            screen_lines = screen_output.split('\n')
            
            if exploration_steps % 100 == 0:
                print(screen_output)
            
            # Check for Success
            if "Dlvl:2" in screen_output:
                print("\nSUCCESS: Reached Dungeon Level 2!")
                print(screen_output)
                
                # Save the game
                print("Action: Saving game (S -> y)")
                client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "S"})
                # Wait for prompt
                client.call_tool("sim_run_until_console_status_read", {"session_id": session_id, "max_steps": 2000000})
                client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "y"})
                # Wait for save to complete
                client.call_tool("sim_run_until_console_status_read", {"session_id": session_id, "max_steps": 2000000})
                
                break
                
            # Check for Death
            if "HP:0(" in screen_output or "You die" in screen_output:
                print("\nGAME OVER: Player died.")
                print(screen_output)
                break

            # Handle prompts
            if "--More--" in screen_output:
                print("Action: Dismiss --More--")
                client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": " "})
                continue
            
            if "Do you want to see your attributes?" in screen_output:
                print("Action: Answer 'n' to attributes prompt")
                client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "n"})
                continue
                
            if "[ynq]" in screen_output:
                 print("Action: Answer 'n' to generic prompt")
                 client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "n"})
                 continue

            # Handle Inventory or Menu
            if "(end)" in screen_output or "Weapons" in screen_output or "Armor" in screen_output:
                print("Action: Close Menu/Inventory (Space)")
                client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": " "})
                continue

            # Eating Logic
            if ("Hungry" in screen_output or "Weak" in screen_output) and (exploration_steps - last_eat_attempt > 50):
                 last_eat_attempt = exploration_steps
                 print("Action: Hungry! Eating...")
                 client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "e"})
                 # Wait for prompt
                 client.call_tool("sim_run_until_console_status_read", {"session_id": session_id, "max_steps": 2000000})
                 # Try 'e' (Valkyrie food)
                 client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "e"})
                 # Wait
                 client.call_tool("sim_run_until_console_status_read", {"session_id": session_id, "max_steps": 2000000})
                 continue

            # Find Player and Stairs
            player_pos = find_symbol(screen_lines, '@')
            stairs_pos = find_symbol(screen_lines, '>')
            
            if player_pos:
                print(f"Player at {player_pos}")
                visited.add(player_pos)
                
                # Check if stuck
                if player_pos == last_player_pos:
                    stuck_count += 1
                else:
                    stuck_count = 0
                last_player_pos = player_pos
                
                # If we didn't move, maybe the screen hasn't updated yet?
                # Try running one loop without input to let it catch up
                if stuck_count == 1:
                    print("DEBUG: Player didn't move. Waiting one loop...")
                    # Don't send input, just continue to next loop which calls run_until_console_status_read
                    continue

                if stuck_count > 5:
                    print(f"WARNING: Player seems stuck! (Count: {stuck_count})")
                    
                    # Debug PC location
                    status_str = client.call_tool("sim_get_status", {"session_id": session_id})
                    print(f"Status: {status_str}")
                    
                    # Get symbol info
                    # We need to parse PC from status_str
                    pc_match = re.search(r"PC: (0x[0-9a-f]+)", status_str)
                    if pc_match:
                        pc_val = pc_match.group(1)
                        sym_info = client.call_tool("sim_get_symbol_info", {"session_id": session_id, "address": pc_val})
                        print(f"PC Symbol: {sym_info}")

                    print("Screen content:")
                    print(screen_output)
                    
                    # Try to unstuck by moving randomly (including diagonals)
                    # Don't just search, as that keeps us in place
                    # Try number keys too, in case number_pad is on
                    # Try Kick (Ctrl-D) to test responsiveness
                    unstuck_moves = ['h', 'j', 'k', 'l', 'y', 'u', 'b', 'n', '4', '2', '8', '6', '7', '9', '1', '3', '\x04']
                    move = random.choice(unstuck_moves)
                    
                    # DEBUG: Try to open help to verify input works
                    if stuck_count == 6:
                        print("DEBUG: Sending ESC to clear potential prompts")
                        client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "\x1b"})
                        continue
                    
                    if stuck_count == 7:
                        print("DEBUG: Sending Ctrl-R to redraw")
                        client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "\x12"})
                        continue

                    if stuck_count == 8:
                        print("DEBUG: Sending '?' to verify input")
                        client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "?"})
                        continue
                        
                    print(f"Action: Unstuck move ({move})")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": move})
                    
                    # If we are REALLY stuck, try to search or wait
                    if stuck_count > 15:
                         print("Action: Search (s) - desperate")
                         client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": "s"})
                         # Reset stuck count occasionally to allow trying moves again
                         if stuck_count > 20:
                             stuck_count = 0
                    
                    continue
                
                # Exploration Logic
                surroundings = get_surrounding_tiles(screen_lines, player_pos[0], player_pos[1])
                best_move = None
                
                # Priority 1: Stairs >
                for key, (char, pos) in surroundings.items():
                    if char == '>':
                        best_move = key
                        print(f"Found Stairs at {key}")
                        break
                
                # Priority 2: Gold $
                if not best_move:
                    for key, (char, pos) in surroundings.items():
                        if char == '$':
                            best_move = key
                            print(f"Found Gold at {key}")
                            break
                
                # Priority 3: Door +
                if not best_move:
                    for key, (char, pos) in surroundings.items():
                        if char == '+':
                            best_move = key
                            print(f"Found Door at {key}")
                            break
                
                # Priority 4: Unvisited Walkable
                if not best_move:
                    unvisited_moves = []
                    for key, (char, pos) in surroundings.items():
                        if is_walkable(char) and pos not in visited:
                            unvisited_moves.append(key)
                    
                    if unvisited_moves:
                        best_move = random.choice(unvisited_moves)
                        print(f"Choosing unvisited move: {best_move}")
                
                # Priority 5: Any Walkable (Backtracking)
                if not best_move:
                    valid_moves = []
                    for key, (char, pos) in surroundings.items():
                        if is_walkable(char):
                            valid_moves.append(key)
                    
                    if valid_moves:
                        best_move = random.choice(valid_moves)
                        print(f"Backtracking/Random move: {best_move}")
                
                if best_move:
                    print(f"Action: Move ({best_move})")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": best_move})
                else:
                    print("Action: No valid moves? Random fallback.")
                    client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": random.choice(['h','j','k','l'])})

            else:
                print("Player not found on screen? (Maybe obscured or in menu)")
                # If we can't see the player, maybe we are in a menu or message
                # Try space to clear
                client.call_tool("sim_console_uart_write", {"session_id": session_id, "data": " "})

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if session_id:
            print("Destroying session...")
            try:
                client.call_tool("sim_destroy", {"session_id": session_id})
            except:
                pass

if __name__ == "__main__":
    main()
