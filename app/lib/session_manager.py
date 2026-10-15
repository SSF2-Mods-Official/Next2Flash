#!/usr/bin/env python3
"""
session_manager.py — Session-based lazy loading state management

Replaces global _pending_builder with session-based storage.
Implements automatic cleanup of expired sessions to prevent memory leaks.
"""

from __future__ import annotations

import logging
import time
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


@dataclass
class Session:
    """Represents a lazy loading session."""
    
    session_id: str
    builder: Any  # N2DBuilder instance
    created_at: float
    last_accessed: float
    metadata: Dict[str, Any]
    
    def is_expired(self, ttl: float) -> bool:
        """Check if session has expired."""
        return time.time() - self.last_accessed > ttl
    
    def touch(self):
        """Update last accessed time."""
        self.last_accessed = time.time()


class SessionManager:
    """
    Manages lazy loading sessions with automatic cleanup.
    
    Replaces global state with session-based storage. Sessions expire
    after inactivity to prevent memory leaks from abandoned conversions.
    
    Example:
        >>> manager = SessionManager(ttl=1800)  # 30 min TTL
        >>> session_id = manager.create_session(builder)
        >>> builder = manager.get_builder(session_id)
        >>> manager.delete_session(session_id)
    """
    
    def __init__(self, ttl: float = 1800, cleanup_interval: float = 300):
        """
        Initialize session manager.
        
        Args:
            ttl: Time-to-live for sessions in seconds (default 30 min)
            cleanup_interval: Background cleanup interval in seconds (default 5 min)
        """
        self.ttl = ttl
        self.cleanup_interval = cleanup_interval
        self.sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def start_cleanup_task(self):
        """Start background cleanup task."""
        if self._cleanup_thread is not None and self._cleanup_thread.is_alive():
            log.warning("Cleanup task already running")
            return
        
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="SessionCleanup"
        )
        self._cleanup_thread.start()
        log.info(f"Started session cleanup task (TTL={self.ttl}s, interval={self.cleanup_interval}s)")
    
    def stop_cleanup_task(self):
        """Stop background cleanup task."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        log.info("Stopped session cleanup task")
    
    def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                time.sleep(self.cleanup_interval)
                self.cleanup_expired()
            except Exception as e:
                log.error(f"Error in cleanup loop: {e}")
    
    def create_session(self, builder: Any, metadata: Dict[str, Any] = None) -> str:
        """
        Create a new session.
        
        Args:
            builder: N2DBuilder instance
            metadata: Optional metadata dict
            
        Returns:
            Session ID (UUID string)
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        now = time.time()
        
        session = Session(
            session_id=session_id,
            builder=builder,
            created_at=now,
            last_accessed=now,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.sessions[session_id] = session
        
        log.debug(f"Created session {session_id[:8]}... (total: {len(self.sessions)})")
        return session_id
    
    def get_builder(self, session_id: str) -> Optional[Any]:
        """
        Get builder for session, updating last accessed time.
        
        Args:
            session_id: Session ID
            
        Returns:
            N2DBuilder instance or None if not found
        """
        with self._lock:
            session = self.sessions.get(session_id)
            
            if session is None:
                log.warning(f"Session not found: {session_id[:8]}...")
                return None
            
            if session.is_expired(self.ttl):
                log.warning(f"Session expired: {session_id[:8]}...")
                self.delete_session(session_id)
                return None
            
            session.touch()
            return session.builder
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                log.debug(f"Deleted session {session_id[:8]}... (remaining: {len(self.sessions)})")
                return True
            return False
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        with self._lock:
            expired = [
                sid for sid, session in self.sessions.items()
                if session.is_expired(self.ttl)
            ]
            
            for sid in expired:
                del self.sessions[sid]
            
            if expired:
                log.info(f"Cleaned up {len(expired)} expired sessions (remaining: {len(self.sessions)})")
            
            return len(expired)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict with session info or None if not found
        """
        with self._lock:
            session = self.sessions.get(session_id)
            
            if session is None:
                return None
            
            age = time.time() - session.created_at
            idle = time.time() - session.last_accessed
            remaining = max(0, self.ttl - idle)
            
            return {
                'session_id': session_id,
                'age_seconds': age,
                'idle_seconds': idle,
                'remaining_seconds': remaining,
                'expires_at': datetime.fromtimestamp(session.last_accessed + self.ttl).isoformat(),
                'metadata': session.metadata
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get manager statistics.
        
        Returns:
            Dict with stats
        """
        with self._lock:
            return {
                'total_sessions': len(self.sessions),
                'ttl_seconds': self.ttl,
                'cleanup_interval_seconds': self.cleanup_interval,
                'cleanup_running': self._running
            }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager."""
    global _session_manager
    
    if _session_manager is None:
        _session_manager = SessionManager(
            ttl=1800,  # 30 minutes
            cleanup_interval=300  # 5 minutes
        )
        _session_manager.start_cleanup_task()
    
    return _session_manager


# ══════════════════════════════════════════════════════════════════════
#  MODULE EXPORTS
# ══════════════════════════════════════════════════════════════════════

__all__ = [
    'Session',
    'SessionManager',
    'get_session_manager',
]
