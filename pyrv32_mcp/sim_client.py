"""
Client for communicating with the persistent TCP simulator server.
"""

import socket
import json


class SimulatorClient:
    """Client for TCP-based simulator server."""
    
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
    
    def _send_request(self, method, args=None):
        """Send a request to the simulator server."""
        if args is None:
            args = {}
        
        request = {
            "method": method,
            "args": args
        }
        
        try:
            # Create socket and connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30.0)  # 30 second timeout
            sock.connect((self.host, self.port))
            
            # Send request
            request_str = json.dumps(request) + "\n"
            sock.sendall(request_str.encode('utf-8'))
            
            # Receive response
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'\n' in data:
                    break
            
            sock.close()
            
            # Parse response
            response_str = data.decode('utf-8').strip()
            response = json.loads(response_str)
            
            return response
            
        except ConnectionRefusedError:
            raise RuntimeError(f"Cannot connect to simulator server at {self.host}:{self.port}. Is it running?")
        except socket.timeout:
            raise RuntimeError(f"Request to simulator server timed out")
        except Exception as e:
            raise RuntimeError(f"Error communicating with simulator server: {e}")
    
    # Session management
    def create_session(self, start_addr="0x80000000", fs_root="."):
        """Create a new simulator session."""
        response = self._send_request("create_session", {
            "start_addr": start_addr,
            "fs_root": fs_root
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["session_id"]
    
    def destroy_session(self, session_id):
        """Destroy a simulator session."""
        response = self._send_request("destroy_session", {"session_id": session_id})
        return response.get("success", False)
    
    def list_sessions(self):
        """List all active sessions."""
        response = self._send_request("list_sessions")
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["sessions"]
    
    # Binary loading
    def load_binary(self, session_id, binary_path):
        """Load a binary into the session."""
        response = self._send_request("load_binary", {
            "session_id": session_id,
            "binary_path": binary_path
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
    
    def reset(self, session_id):
        """Reset the session."""
        response = self._send_request("reset", {"session_id": session_id})
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
    
    # Execution
    def step(self, session_id, count=1):
        """Execute instructions."""
        response = self._send_request("step", {
            "session_id": session_id,
            "count": count
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response
    
    def run(self, session_id, max_steps=1000000):
        """Run until halt or max steps."""
        response = self._send_request("run", {
            "session_id": session_id,
            "max_steps": max_steps
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response
    
    def run_until_output(self, session_id, max_steps=1000000):
        """Run until UART output available."""
        response = self._send_request("run_until_output", {
            "session_id": session_id,
            "max_steps": max_steps
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response
    
    def get_status(self, session_id):
        """Get session status."""
        response = self._send_request("get_status", {"session_id": session_id})
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["status"]
    
    # UART
    def uart_read(self, session_id):
        """Read UART output."""
        response = self._send_request("uart_read", {"session_id": session_id})
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["data"]
    
    def uart_write(self, session_id, data):
        """Write to UART input."""
        response = self._send_request("uart_write", {
            "session_id": session_id,
            "data": data
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
    
    def uart_has_data(self, session_id):
        """Check if UART has data."""
        response = self._send_request("uart_has_data", {"session_id": session_id})
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["has_data"]
    
    # Registers
    def get_registers(self, session_id):
        """Get all registers."""
        response = self._send_request("get_registers", {"session_id": session_id})
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["registers"]
    
    def get_register(self, session_id, register):
        """Get a specific register."""
        response = self._send_request("get_register", {
            "session_id": session_id,
            "register": register
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["value"]
    
    def set_register(self, session_id, register, value):
        """Set a register value."""
        response = self._send_request("set_register", {
            "session_id": session_id,
            "register": register,
            "value": value
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
    
    # Memory
    def read_memory(self, session_id, address, length):
        """Read memory."""
        response = self._send_request("read_memory", {
            "session_id": session_id,
            "address": address,
            "length": length
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["data"]
    
    def write_memory(self, session_id, address, data):
        """Write memory."""
        response = self._send_request("write_memory", {
            "session_id": session_id,
            "address": address,
            "data": data
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
    
    # Breakpoints
    def add_breakpoint(self, session_id, address):
        """Add a breakpoint."""
        response = self._send_request("add_breakpoint", {
            "session_id": session_id,
            "address": address
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
    
    def remove_breakpoint(self, session_id, address):
        """Remove a breakpoint."""
        response = self._send_request("remove_breakpoint", {
            "session_id": session_id,
            "address": address
        })
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
    
    def list_breakpoints(self, session_id):
        """List all breakpoints."""
        response = self._send_request("list_breakpoints", {"session_id": session_id})
        if not response.get("success"):
            raise RuntimeError(response.get("error", "Unknown error"))
        return response["breakpoints"]
