#!/usr/bin/env python3
"""
test_session_manager.py — Unit tests for session manager

Tests session lifecycle and cleanup.
"""

import pytest
import time
from session_manager import SessionManager


class MockBuilder:
    """Mock N2DBuilder for testing."""
    def __init__(self, name):
        self.name = name


class TestSessionManager:
    """Test session manager."""
    
    def test_create_and_get_session(self):
        """Test creating and retrieving session."""
        manager = SessionManager(ttl=60)
        builder = MockBuilder("test")
        
        session_id = manager.create_session(builder)
        retrieved = manager.get_builder(session_id)
        
        assert retrieved is builder
        assert retrieved.name == "test"
    
    def test_delete_session(self):
        """Test deleting session."""
        manager = SessionManager(ttl=60)
        builder = MockBuilder("test")
        
        session_id = manager.create_session(builder)
        assert manager.delete_session(session_id) is True
        assert manager.get_builder(session_id) is None
    
    def test_session_expiry(self):
        """Test session expiration."""
        manager = SessionManager(ttl=1)  # 1 second TTL
        builder = MockBuilder("test")
        
        session_id = manager.create_session(builder)
        time.sleep(1.5)  # Wait for expiry
        
        retrieved = manager.get_builder(session_id)
        assert retrieved is None
    
    def test_cleanup_expired(self):
        """Test cleanup of expired sessions."""
        manager = SessionManager(ttl=1)
        
        # Create sessions
        sid1 = manager.create_session(MockBuilder("test1"))
        sid2 = manager.create_session(MockBuilder("test2"))
        
        time.sleep(1.5)  # Wait for expiry
        
        cleaned = manager.cleanup_expired()
        assert cleaned == 2
        assert len(manager.sessions) == 0
    
    def test_get_session_info(self):
        """Test getting session information."""
        manager = SessionManager(ttl=60)
        builder = MockBuilder("test")
        
        session_id = manager.create_session(builder, metadata={"name": "test"})
        info = manager.get_session_info(session_id)
        
        assert info is not None
        assert info['session_id'] == session_id
        assert info['metadata']['name'] == "test"
        assert info['remaining_seconds'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
