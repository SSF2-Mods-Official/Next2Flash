#!/usr/bin/env python3
"""
Test suite for char_id_allocator.py

Tests Bug Fix #1: CharID 0 validation
Ensures charID 0 (reserved for root timeline) cannot be allocated.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from char_id_allocator import CharIDAllocator


def test_char_id_zero_rejection():
    """Bug Fix #1: charID 0 should be rejected."""
    allocator = CharIDAllocator()
    
    with pytest.raises(ValueError, match="charID 0 is reserved"):
        allocator.register(0)


def test_valid_char_ids():
    """Valid charIDs (1+) should be accepted."""
    allocator = CharIDAllocator()
    
    # Register valid IDs
    allocator.register(1)
    allocator.register(2)
    allocator.register(100)
    allocator.register(9999)
    
    allocator.finalize()
    
    # Check remapping
    assert allocator.remap(1) == 0
    assert allocator.remap(2) == 1
    assert allocator.remap(100) == 2
    assert allocator.remap(9999) == 3


def test_negative_char_id():
    """Negative charIDs should be rejected."""
    allocator = CharIDAllocator()
    
    # Negative IDs should be rejected
    with pytest.raises(ValueError, match="must be non-negative"):
        allocator.register(-1)


def test_sparse_char_id_compaction():
    """Sparse charID ranges should be compacted."""
    allocator = CharIDAllocator()
    
    # Register sparse IDs: [1, 2, 500, 1000]
    allocator.register(1)
    allocator.register(2)
    allocator.register(500)
    allocator.register(1000)
    
    allocator.finalize()
    
    # Should compact to [0, 1, 2, 3]
    assert allocator.remap(1) == 0
    assert allocator.remap(2) == 1
    assert allocator.remap(500) == 2
    assert allocator.remap(1000) == 3


def test_duplicate_registration():
    """Duplicate charID registration should be idempotent."""
    allocator = CharIDAllocator()
    
    # Register same ID multiple times
    allocator.register(10)
    allocator.register(10)
    allocator.register(10)
    
    allocator.finalize()
    
    # Should only appear once in mapping
    assert allocator.remap(10) == 0


def test_unregistered_remap():
    """Remapping unregistered charID should raise KeyError."""
    allocator = CharIDAllocator()
    
    allocator.register(1)
    allocator.register(2)
    allocator.finalize()
    
    # Unregistered ID should raise error
    with pytest.raises(KeyError, match="charID 999 not registered"):
        allocator.remap(999)


def test_empty_allocator():
    """Empty allocator remap should raise error."""
    allocator = CharIDAllocator()
    
    # Finalize without registrations
    allocator.finalize()
    
    # Remap of any ID should raise KeyError
    with pytest.raises(KeyError, match="not registered"):
        allocator.remap(1)
    with pytest.raises(KeyError, match="not registered"):
        allocator.remap(100)


def test_large_char_id():
    """Very large charIDs should be handled."""
    allocator = CharIDAllocator()
    
    # Register large ID (SWF uses 16-bit charIDs, max 65535)
    allocator.register(65535)
    allocator.finalize()
    
    assert allocator.remap(65535) == 0


def test_sequential_allocation():
    """Sequential IDs should maintain order."""
    allocator = CharIDAllocator()
    
    # Register in order
    for i in range(1, 11):
        allocator.register(i)
    
    allocator.finalize()
    
    # Should map sequentially starting from 0
    for i in range(1, 11):
        assert allocator.remap(i) == i - 1


def test_reverse_allocation():
    """Reverse-order registration should still compact correctly."""
    allocator = CharIDAllocator()
    
    # Register in reverse order
    allocator.register(10)
    allocator.register(9)
    allocator.register(8)
    allocator.register(7)
    
    allocator.finalize()
    
    # Should still map to 0-3 (sorted order)
    assert allocator.remap(7) == 0
    assert allocator.remap(8) == 1
    assert allocator.remap(9) == 2
    assert allocator.remap(10) == 3


def test_finalize_multiple_times():
    """Multiple finalize() calls should be safe."""
    allocator = CharIDAllocator()
    
    allocator.register(1)
    allocator.register(2)
    
    allocator.finalize()
    first_remap = allocator.remap(1)
    
    # Finalize again
    allocator.finalize()
    second_remap = allocator.remap(1)
    
    # Should be stable
    assert first_remap == second_remap


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
