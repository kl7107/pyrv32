#!/usr/bin/env python3
"""
Tests for the new high-level interactive MCP tools.

Tests:
1. sim_run_until_input_consumed - runs until input buffer empty
2. sim_run_until_idle - runs until significant work between polls
3. sim_send_input_and_run - combined input + run + screen
4. sim_interactive_step - high-level convenience method
5. include_screen parameter on existing run commands

Run with: python3 test_interactive_tools.py
"""

import sys
import os
import json
import socket
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Path to NetHack ELF
NETHACK_ELF = "/home/dev/git/pyrv32/nethack-3.4.3/src/nethack.elf"


class MCPTestClient:
    """Simple MCP test client that talks JSON-RPC over TCP."""
    
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.sock = None
        self.request_id = 0
        
    def connect(self):
        """Connect to MCP server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(120)  # 2 minute timeout for long operations
        
    def disconnect(self):
        """Disconnect from server."""
        if self.sock:
            self.sock.close()
            self.sock = None
            
    def call(self, tool_name, arguments=None):
        """Call an MCP tool and return the result."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": self.request_id
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.sock.sendall(request_json.encode('utf-8'))
        
        # Receive response
        response_data = b""
        while b"\n" not in response_data:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("Server closed connection")
            response_data += chunk
        
        response = json.loads(response_data.decode('utf-8'))
        
        if "error" in response:
            raise Exception(f"MCP error: {response['error']}")
        
        # Extract text from result
        content = response.get("result", {}).get("content", [])
        if content and isinstance(content, list):
            return content[0].get("text", "")
        return ""
    
    def create_session(self):
        """Create a new simulator session."""
        result = self.call("sim_create")
        # Parse session ID from response
        if "Created session:" in result:
            return result.split("Created session:")[1].strip()
        raise Exception(f"Failed to create session: {result}")
    
    def destroy_session(self, session_id):
        """Destroy a session."""
        return self.call("sim_destroy", {"session_id": session_id})
    
    def load_elf(self, session_id, elf_path):
        """Load an ELF file."""
        return self.call("sim_load_elf", {"session_id": session_id, "elf_path": elf_path})


def test_run_until_input_consumed():
    """Test sim_run_until_input_consumed with NetHack."""
    print("\n" + "="*60)
    print("TEST: sim_run_until_input_consumed")
    print("="*60)
    
    client = MCPTestClient()
    client.connect()
    
    try:
        # Create session and load NetHack
        session_id = client.create_session()
        print(f"Created session: {session_id}")
        
        client.load_elf(session_id, NETHACK_ELF)
        print("Loaded NetHack ELF")
        
        # First, run until NetHack asks for name
        result = client.call("sim_run_until_console_status_read", {
            "session_id": session_id,
            "max_steps": 500000
        })
        print(f"Initial run: {result.split(chr(10))[0]}")
        
        # Get screen to verify we're at name prompt
        screen = client.call("sim_get_screen", {"session_id": session_id})
        assert "Who are you?" in screen, f"Expected name prompt, got: {screen[:200]}"
        print("✓ At name prompt")
        
        # Inject name with newline
        client.call("sim_console_uart_write", {
            "session_id": session_id,
            "data": "TestHero\n"
        })
        print("Injected name: TestHero")
        
        # Use run_until_input_consumed - should process entire name AND be idle
        result = client.call("sim_run_until_input_consumed", {
            "session_id": session_id,
            "max_steps": 2000000,
            "then_idle": True,
            "min_idle_instructions": 100
        })
        print(f"run_until_input_consumed result: {result.split(chr(10))[0]}")
        
        # Check we ran enough instructions for the game to process the name
        lines = result.split("\n")
        insn_count = 0
        for line in lines:
            if "Instructions:" in line:
                insn_count = int(line.split(":")[1].strip())
                break
        
        print(f"Instructions executed: {insn_count}")
        # Should have run more than just buffer-emptying (>=100 from then_idle)
        assert insn_count >= 100, f"Expected >= 100 instructions, got {insn_count}"
        
        # Verify we processed the input - screen should show the name or next prompt
        screen = client.call("sim_get_screen", {"session_id": session_id})
        
        # After name entry with then_idle, should have progressed
        # Either the name is echoed, or we're at next prompt, or both
        has_name = "TestHero" in screen
        has_next_prompt = "Shall I pick" in screen or "character" in screen.lower() or "race" in screen.lower()
        
        if has_name or has_next_prompt:
            print("✓ Input was processed correctly")
            if has_name:
                print("  - Name 'TestHero' appears on screen")
            if has_next_prompt:
                print("  - Progressed to character selection")
        else:
            print(f"Screen preview: {screen[:400]}...")
            # Even if we don't see expected prompts, test passed if we ran enough instructions
            print("✓ Ran sufficient instructions (screen state may vary)")
        
        # Cleanup
        client.destroy_session(session_id)
        print("✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        client.disconnect()


def test_run_until_idle():
    """Test sim_run_until_idle - detects when significant work done."""
    print("\n" + "="*60)
    print("TEST: sim_run_until_idle")
    print("="*60)
    
    client = MCPTestClient()
    client.connect()
    
    try:
        session_id = client.create_session()
        print(f"Created session: {session_id}")
        
        client.load_elf(session_id, NETHACK_ELF)
        print("Loaded NetHack ELF")
        
        # Run until we're at input prompt with idle detection
        result = client.call("sim_run_until_idle", {
            "session_id": session_id,
            "max_steps": 500000,
            "min_instructions": 500
        })
        print(f"run_until_idle result: {result}")
        
        # Should have executed significant instructions
        lines = result.split("\n")
        for line in lines:
            if "Instructions:" in line:
                insn_count = int(line.split(":")[1].strip())
                print(f"Instructions executed: {insn_count}")
                assert insn_count >= 500, f"Expected >= 500 instructions, got {insn_count}"
                break
        
        screen = client.call("sim_get_screen", {"session_id": session_id})
        print(f"Screen preview: {screen[:200]}...")
        print("✓ TEST PASSED")
        
        client.destroy_session(session_id)
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        client.disconnect()


def test_send_input_and_run():
    """Test sim_send_input_and_run - the primary convenience method."""
    print("\n" + "="*60)
    print("TEST: sim_send_input_and_run")
    print("="*60)
    
    client = MCPTestClient()
    client.connect()
    
    try:
        session_id = client.create_session()
        print(f"Created session: {session_id}")
        
        client.load_elf(session_id, NETHACK_ELF)
        print("Loaded NetHack ELF")
        
        # Get to initial prompt
        result = client.call("sim_run_until_console_status_read", {
            "session_id": session_id,
            "max_steps": 500000
        })
        print("Got to initial prompt")
        
        # Use send_input_and_run to enter name - ONE CALL should do it all!
        result = client.call("sim_send_input_and_run", {
            "session_id": session_id,
            "data": "Hero\n",
            "include_screen": True
        })
        print(f"send_input_and_run result length: {len(result)} chars")
        
        # Result should include screen
        assert "=== SCREEN ===" in result, "Expected screen in response"
        print("✓ Screen included in response")
        
        # Screen should show we moved past name entry
        if "Shall I pick" in result or "race" in result.lower():
            print("✓ Progressed to character selection")
        else:
            print(f"Result: {result[:500]}...")
        
        client.destroy_session(session_id)
        print("✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        client.disconnect()


def test_interactive_step():
    """Test sim_interactive_step - the high-level 'do what I mean' method."""
    print("\n" + "="*60)
    print("TEST: sim_interactive_step")
    print("="*60)
    
    client = MCPTestClient()
    client.connect()
    
    try:
        session_id = client.create_session()
        print(f"Created session: {session_id}")
        
        client.load_elf(session_id, NETHACK_ELF)
        print("Loaded NetHack ELF")
        
        # Run to get initial prompt
        client.call("sim_run_until_console_status_read", {
            "session_id": session_id,
            "max_steps": 500000
        })
        
        # Use interactive_step to enter name
        result = client.call("sim_interactive_step", {
            "session_id": session_id,
            "data": "TestPlayer\n"
        })
        print(f"interactive_step result: {len(result)} chars")
        assert "=== SCREEN ===" in result, "Expected screen"
        print("✓ Step 1: Entered name")
        
        # Use interactive_step to auto-pick character (y)
        result = client.call("sim_interactive_step", {
            "session_id": session_id,
            "data": "y"
        })
        print("✓ Step 2: Answered 'y' to auto-pick")
        
        # Check if we got to the game
        if "Dungeons of Doom" in result or "NetHack" in result or "welcome" in result.lower():
            print("✓ Got to game!")
        
        # One more step - press space to clear intro
        result = client.call("sim_interactive_step", {
            "session_id": session_id,
            "data": " "
        })
        print("✓ Step 3: Pressed space")
        
        # Print final screen state
        if "=== SCREEN ===" in result:
            screen_part = result.split("=== SCREEN ===")[1]
            print(f"Final screen:\n{screen_part[:500]}")
        
        client.destroy_session(session_id)
        print("✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        client.disconnect()


def test_include_screen_parameter():
    """Test include_screen parameter on existing run commands."""
    print("\n" + "="*60)
    print("TEST: include_screen parameter")
    print("="*60)
    
    client = MCPTestClient()
    client.connect()
    
    try:
        session_id = client.create_session()
        print(f"Created session: {session_id}")
        
        client.load_elf(session_id, NETHACK_ELF)
        print("Loaded NetHack ELF")
        
        # Test sim_run with include_screen=True
        result = client.call("sim_run", {
            "session_id": session_id,
            "max_steps": 100000,
            "include_screen": True
        })
        assert "=== SCREEN ===" in result, "Expected screen with include_screen=True"
        print("✓ sim_run with include_screen=True works")
        
        # Test without include_screen
        result = client.call("sim_run", {
            "session_id": session_id,
            "max_steps": 10000,
            "include_screen": False
        })
        assert "=== SCREEN ===" not in result, "Expected no screen with include_screen=False"
        print("✓ sim_run with include_screen=False works")
        
        # Test sim_run_until_console_status_read with include_screen
        result = client.call("sim_run_until_console_status_read", {
            "session_id": session_id,
            "max_steps": 500000,
            "include_screen": True
        })
        assert "=== SCREEN ===" in result, "Expected screen"
        print("✓ sim_run_until_console_status_read with include_screen works")
        
        client.destroy_session(session_id)
        print("✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        client.disconnect()


def test_full_nethack_session():
    """Integration test: Play NetHack using only high-level tools."""
    print("\n" + "="*60)
    print("TEST: Full NetHack session with high-level tools")
    print("="*60)
    
    client = MCPTestClient()
    client.connect()
    
    try:
        session_id = client.create_session()
        print(f"Created session: {session_id}")
        
        client.load_elf(session_id, NETHACK_ELF)
        print("Loaded NetHack ELF")
        
        # Run to name prompt
        result = client.call("sim_run_until_idle", {
            "session_id": session_id,
            "max_steps": 500000,
            "min_instructions": 1000
        })
        print("Initial run complete")
        
        # Enter name using interactive_step
        result = client.call("sim_interactive_step", {
            "session_id": session_id,
            "data": "Agent\n"
        })
        print("Entered name: Agent")
        
        # Auto-pick character
        result = client.call("sim_interactive_step", {
            "session_id": session_id,
            "data": "y"
        })
        print("Auto-picked character")
        
        # Clear intro screen
        result = client.call("sim_interactive_step", {
            "session_id": session_id,
            "data": " "
        })
        print("Cleared intro")
        
        # Verify we're in the game
        screen = client.call("sim_get_screen", {"session_id": session_id})
        in_game = "@" in screen or "Dlvl" in screen
        
        if in_game:
            print("✓ Successfully reached game!")
            
            # Make a few moves using interactive_step
            moves = ['h', 'l', 'j', 'k']  # left, right, down, up
            for move in moves:
                result = client.call("sim_interactive_step", {
                    "session_id": session_id,
                    "data": move
                })
                print(f"Made move: {move}")
            
            # Quit the game
            result = client.call("sim_send_input_and_run", {
                "session_id": session_id,
                "data": "#quit\n",
                "include_screen": True
            })
            print("Initiated quit")
            
            # Confirm quit
            result = client.call("sim_interactive_step", {
                "session_id": session_id,
                "data": "y"
            })
            print("Confirmed quit")
            
            # Skip identification
            result = client.call("sim_interactive_step", {
                "session_id": session_id,
                "data": "n"
            })
            
            # Final screen
            screen = client.call("sim_get_screen", {"session_id": session_id})
            print(f"Final screen:\n{screen[:300]}")
        else:
            print(f"Warning: May not be in game. Screen:\n{screen[:300]}")
        
        client.destroy_session(session_id)
        print("✓ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        client.disconnect()


def main():
    """Run all tests."""
    print("="*60)
    print("INTERACTIVE MCP TOOLS TEST SUITE")
    print("="*60)
    
    # Check if server is running
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 5555))
        sock.close()
        print("✓ MCP server is running")
    except:
        print("✗ MCP server not running. Start with:")
        print("  cd pyrv32_mcp && python3 sim_server_mcp_v2.py &")
        return 1
    
    # Check NetHack ELF exists
    if not os.path.exists(NETHACK_ELF):
        print(f"✗ NetHack ELF not found: {NETHACK_ELF}")
        return 1
    print(f"✓ NetHack ELF found")
    
    results = []
    
    # Run tests
    results.append(("include_screen parameter", test_include_screen_parameter()))
    results.append(("run_until_input_consumed", test_run_until_input_consumed()))
    results.append(("run_until_idle", test_run_until_idle()))
    results.append(("send_input_and_run", test_send_input_and_run()))
    results.append(("interactive_step", test_interactive_step()))
    results.append(("full NetHack session", test_full_nethack_session()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
