#!/usr/bin/env python3
"""
Command helper utility - executes commands and reports their exit status, stdout, and stderr.
Usage: cmd_helper.py <command1> [command2] [command3] ...
"""

import subprocess
import sys


def run_command(cmd):
    """Execute a command and return exit status, stdout, and stderr."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            'exit_status': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'exit_status': -1,
            'stdout': '',
            'stderr': 'ERROR: Command timed out after 30 seconds'
        }
    except Exception as e:
        return {
            'exit_status': -2,
            'stdout': '',
            'stderr': f'ERROR: {str(e)}'
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: cmd_helper.py <command1> [command2] [command3] ...")
        print("Example: cmd_helper.py 'ls -la' 'echo hello' 'false'")
        sys.exit(1)
    
    commands = sys.argv[1:]
    
    for i, cmd in enumerate(commands):
        if len(commands) > 1:
            print(f"=== Command {i+1}: {cmd} ===")
        
        result = run_command(cmd)
        
        # Strip trailing newlines and add our own for consistent formatting
        stdout = result['stdout'].rstrip('\n')
        stderr = result['stderr'].rstrip('\n')
        
        print(f"EXIT STATUS: {result['exit_status']}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        
        if len(commands) > 1 and i < len(commands) - 1:
            print()  # Blank line between commands


if __name__ == '__main__':
    main()
