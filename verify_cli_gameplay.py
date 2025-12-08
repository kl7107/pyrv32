import subprocess
import re
import time
import os
import sys
import select

def verify_cli_gameplay():
    print("Starting pyrv32 CLI with NetHack ELF...")
    
    # Start the simulator
    process = subprocess.Popen(
        ['python3', 'pyrv32.py', '--no-test', 'nethack-3.4.3/src/nethack.elf'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    pty_path = None
    
    # Read stderr to find PTY path
    print("Waiting for PTY creation...")
    start_time = time.time()
    while time.time() - start_time < 10:
        line = process.stderr.readline()
        if not line:
            continue
        print(f"Simulator stderr: {line.strip()}")
        
        match = re.search(r"PTY created: (/dev/pts/\d+)", line)
        if match:
            pty_path = match.group(1)
            print(f"Found PTY: {pty_path}")
            break
    
    if not pty_path:
        print("Failed to find PTY path within timeout")
        process.kill()
        sys.exit(1)
        
    # Give simulator a moment to initialize
    time.sleep(1)
    
    # Open the PTY
    try:
        print(f"Opening PTY {pty_path}...")
        pty_fd = os.open(pty_path, os.O_RDWR | os.O_NOCTTY)
        
        # Helper to read from PTY with timeout
        def read_until(pattern, timeout=30):
            buffer = ""
            start_read = time.time()
            while time.time() - start_read < timeout:
                r, _, _ = select.select([pty_fd], [], [], 0.1)
                if r:
                    try:
                        chunk = os.read(pty_fd, 1024).decode('utf-8', errors='ignore')
                        buffer += chunk
                        # print(f"Received: {chunk}") # Debug
                        if pattern in buffer:
                            return True, buffer
                    except OSError:
                        break
            return False, buffer

        # Helper to write to PTY
        def write_pty(text):
            print(f"Sending: {repr(text)}")
            os.write(pty_fd, text.encode('utf-8'))

        # 1. Wait for "Who are you?" or "Shall I pick"
        print("Waiting for initial prompt...")
        found, output = read_until("Who are you")
        
        if found:
            print("SUCCESS: Saw name prompt")
            write_pty("Agent\n")
            
            # Now wait for "Shall I pick"
            print("Waiting for character selection prompt...")
            found, output = read_until("Shall I pick")
            if not found:
                print("FAILED: Did not see character selection prompt after name")
                print(f"Last output:\n{output}")
                process.kill()
                sys.exit(1)
            print("SUCCESS: Saw character selection prompt")
            write_pty("y")
            
        else:
            # Maybe it skipped name? Check for "Shall I pick"
            if "Shall I pick" in output:
                print("SUCCESS: Saw character selection prompt (skipped name)")
                write_pty("y")
            else:
                print("FAILED: Did not see expected prompts")
                print(f"Last output:\n{output}")
                process.kill()
                sys.exit(1)

        # 5. Wait for "Welcome to NetHack"
        print("Waiting for Welcome message...")
        found, output = read_until("Welcome to NetHack")
        if not found:
            print("FAILED: Did not see Welcome message")
            print(f"Last output:\n{output}")
            process.kill()
            sys.exit(1)
        print("SUCCESS: Saw Welcome message")
        
        # 6. Clear message (Space)
        write_pty(" ")
        
        # 7. Wait for map (look for top line border or status line)
        # Status line usually has "St:" or "Dx:" or "Agent"
        print("Waiting for game map/status line...")
        found, output = read_until("Agent") # Name should appear in status line
        if not found:
            print("FAILED: Did not see status line")
            print(f"Last output:\n{output}")
            process.kill()
            sys.exit(1)
        print("SUCCESS: Entered game (saw status line)")
        
        print("\nVERIFICATION SUCCESSFUL: CLI PTY gameplay works!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'pty_fd' in locals():
            os.close(pty_fd)
        process.kill()

if __name__ == "__main__":
    verify_cli_gameplay()
