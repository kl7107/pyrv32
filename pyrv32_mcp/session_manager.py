"""
Session manager for pyrv32 MCP server.

Manages multiple simulator instances (sessions), each with its own
RV32System. Clients receive session IDs and use them to reference
specific simulator instances in tool calls.
"""

import uuid
from typing import Dict, Optional
from pyrv32_system import RV32System


class SessionManager:
    """Manages multiple RV32System simulator sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, RV32System] = {}
    
    def create_session(self, start_addr: int = 0x80000000, 
                      fs_root: str = ".", 
                      trace_buffer_size: int = 1000) -> str:
        """
        Create a new simulator session.
        
        Args:
            start_addr: Initial PC value (default 0x80000000)
            fs_root: Root directory for filesystem syscalls
            trace_buffer_size: Size of instruction trace buffer
        
        Returns:
            session_id: Unique identifier for this session
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = RV32System(
            start_addr=start_addr,
            fs_root=fs_root,
            trace_buffer_size=trace_buffer_size
        )
        with open("/tmp/mcp_debug.log", "a") as f:
            f.write(f"[DEBUG] Created session {session_id}, total sessions: {len(self.sessions)}, manager_id={id(self)}\n")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[RV32System]:
        """
        Get simulator session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            RV32System instance, or None if not found
        """
        session = self.sessions.get(session_id)
        with open("/tmp/mcp_debug.log", "a") as f:
            f.write(f"[DEBUG] get_session({session_id}): {'FOUND' if session else 'NOT FOUND'}, total sessions: {len(self.sessions)}, keys: {list(self.sessions.keys())}, manager_id={id(self)}\n")
        return session
    
    def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a simulator session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if session existed and was destroyed, False otherwise
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> list[str]:
        """
        List all active session IDs.
        
        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())
    
    def get_session_count(self) -> int:
        """
        Get number of active sessions.
        
        Returns:
            Session count
        """
        return len(self.sessions)
