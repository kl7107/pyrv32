#!/usr/bin/env python3
"""
Persistent TCP-based simulator server.

This server runs continuously and manages RV32System sessions.
The MCP server acts as a thin proxy to this server.

Run with: python3 sim_server.py
"""

import sys
import os
import json
import socketserver
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session_manager import SessionManager


class SimulatorRequestHandler(socketserver.BaseRequestHandler):
    """Handler for simulator server requests."""
    
    def handle(self):
        """Handle a single request."""
        try:
            # Read request (JSON terminated by newline)
            data = b""
            while True:
                chunk = self.request.recv(1024)
                if not chunk:
                    return
                data += chunk
                if b'\n' in data:
                    break
            
            request_str = data.decode('utf-8').strip()
            if not request_str:
                return
            
            request = json.loads(request_str)
            
            # Process request
            response = self.process_request(request)
            
            # Send response
            response_str = json.dumps(response) + "\n"
            self.request.sendall(response_str.encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e)
            }
            response_str = json.dumps(error_response) + "\n"
            self.request.sendall(response_str.encode('utf-8'))
    
    def process_request(self, request):
        """Process a simulator request."""
        method = request.get("method")
        args = request.get("args", {})
        
        session_manager = self.server.session_manager
        
        # Session management
        if method == "create_session":
            start_addr = int(args.get("start_addr", "0x80000000"), 16)
            fs_root = args.get("fs_root", ".")
            session_id = session_manager.create_session(start_addr, fs_root)
            return {"success": True, "session_id": session_id}
        
        elif method == "destroy_session":
            session_id = args["session_id"]
            success = session_manager.destroy_session(session_id)
            return {"success": success}
        
        elif method == "list_sessions":
            sessions = session_manager.list_sessions()
            return {"success": True, "sessions": sessions}
        
        # Session operations
        session_id = args.get("session_id")
        if not session_id:
            return {"success": False, "error": "session_id required"}
        
        session = session_manager.get_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}
        
        if method == "load_binary":
            session.load_binary(args["binary_path"])
            return {"success": True}
        
        elif method == "reset":
            session.reset()
            return {"success": True}
        
        elif method == "step":
            count = args.get("count", 1)
            result = session.step(count)
            return {
                "success": True,
                "status": result.status,
                "instruction_count": result.instruction_count,
                "pc": result.pc,
                "error": result.error
            }
        
        elif method == "run":
            max_steps = args.get("max_steps", 1000000)
            result = session.run(max_steps)
            return {
                "success": True,
                "status": result.status,
                "instruction_count": result.instruction_count,
                "pc": result.pc,
                "error": result.error
            }
        
        elif method == "run_until_output":
            max_steps = args.get("max_steps", 1000000)
            result = session.run_until_output(max_steps)
            return {
                "success": True,
                "status": result.status,
                "instruction_count": result.instruction_count,
                "pc": result.pc,
                "error": result.error
            }
        
        elif method == "get_status":
            status = session.get_status()
            return {"success": True, "status": status}
        
        elif method == "uart_read":
            data = session.uart_read()
            return {"success": True, "data": data}
        
        elif method == "uart_write":
            session.uart_write(args["data"])
            return {"success": True}
        
        elif method == "uart_has_data":
            has_data = session.uart_has_data()
            return {"success": True, "has_data": has_data}
        
        elif method == "get_registers":
            regs = session.get_registers()
            return {"success": True, "registers": regs}
        
        elif method == "get_register":
            value = session.get_register(args["register"])
            return {"success": True, "value": value}
        
        elif method == "set_register":
            value = int(args["value"], 16) if isinstance(args["value"], str) else args["value"]
            session.set_register(args["register"], value)
            return {"success": True}
        
        elif method == "read_memory":
            address = int(args["address"], 16)
            length = args["length"]
            data = session.read_memory(address, length)
            return {"success": True, "data": data.hex()}
        
        elif method == "write_memory":
            address = int(args["address"], 16)
            data = bytes.fromhex(args["data"])
            session.write_memory(address, data)
            return {"success": True}
        
        elif method == "add_breakpoint":
            address = int(args["address"], 16)
            session.add_breakpoint(address)
            return {"success": True}
        
        elif method == "remove_breakpoint":
            address = int(args["address"], 16)
            session.remove_breakpoint(address)
            return {"success": True}
        
        elif method == "list_breakpoints":
            breakpoints = session.list_breakpoints()
            return {"success": True, "breakpoints": [hex(bp) for bp in breakpoints]}
        
        else:
            return {"success": False, "error": f"Unknown method: {method}"}


class SimulatorServer(socketserver.ThreadingTCPServer):
    """Multi-threaded TCP server for simulator."""
    
    # Allow reusing the address immediately after restart
    allow_reuse_address = True
    
    def __init__(self, server_address, handler_class):
        super().__init__(server_address, handler_class)
        self.session_manager = SessionManager()
        print(f"Simulator server started on {server_address[0]}:{server_address[1]}")
        print(f"Session manager initialized: {id(self.session_manager)}")


def main():
    """Start the simulator server."""
    HOST = "127.0.0.1"
    PORT = 5555
    
    server = SimulatorServer((HOST, PORT), SimulatorRequestHandler)
    
    print(f"pyrv32 Simulator Server")
    print(f"Listening on {HOST}:{PORT}")
    print(f"Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
