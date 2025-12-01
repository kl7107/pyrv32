"""
Session manager for pyrv32 MCP server.

Manages multiple simulator instances (sessions), each with its own
RV32System. Clients receive session IDs and use them to reference
specific simulator instances in tool calls.
"""

import os
import uuid
from typing import Dict, Optional
from pyrv32_system import RV32System


class SessionManager:
    """Manages multiple RV32System simulator sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, RV32System] = {}
    
    def create_session(self, start_addr: int = 0x80000000, 
                      fs_root: str = "/home/dev/git/pyrv32/pyrv32_sim_fs", 
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
        if not self._fs_root_in_use(fs_root):
            self._cleanup_nethack_locks(fs_root)

        session_id = str(uuid.uuid4())
        self.sessions[session_id] = RV32System(
            start_addr=start_addr,
            fs_root=fs_root,
            trace_buffer_size=trace_buffer_size
        )
        with open("/tmp/mcp_debug.log", "a") as f:
            f.write(f"[DEBUG] Created session {session_id}, total sessions: {len(self.sessions)}, manager_id={id(self)}\n")
        return session_id

    def _fs_root_in_use(self, fs_root: str) -> bool:
        """Return True if any active session already uses the fs_root."""
        for session in self.sessions.values():
            if getattr(session, "fs_root", None) == fs_root:
                return True
        return False

    def _cleanup_nethack_locks(self, fs_root: str) -> None:
        """Remove stale NetHack *_lock files to avoid perm lock failures."""
        lock_dir = os.path.join(fs_root, "usr/games/lib/nethackdir")
        if not os.path.isdir(lock_dir):
            return

        removed = []
        for entry in os.listdir(lock_dir):
            if not entry.endswith("_lock"):
                continue
            lock_path = os.path.join(lock_dir, entry)
            try:
                os.unlink(lock_path)
                removed.append(entry)
            except FileNotFoundError:
                continue
            except OSError as exc:
                with open("/tmp/mcp_debug.log", "a") as f:
                    f.write(f"[WARN] Failed to remove stale lock {lock_path}: {exc}\n")

        if removed:
            with open("/tmp/mcp_debug.log", "a") as f:
                names = ", ".join(removed)
                f.write(f"[INFO] Removed stale NetHack locks: {names}\n")
    
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
    
    def set_working_directory(self, session_id: str, cwd: str) -> bool:
        """
        Set working directory for a session's syscall handler.
        
        Args:
            session_id: Session identifier
            cwd: Working directory path
        
        Returns:
            True if session exists and cwd was set, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            session.syscall_handler.cwd = cwd
            return True
        return False
    
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
