#!/usr/bin/env python3
"""
test_bitmap_converter.py — Unit tests for bitmap converter

Tests bitmap validation and conversion logic.
"""

import pytest
from bitmap_converter import build_define_bits_lossless2


class TestBitmapConverter:
    """Test bitmap conversion functions."""
    
    def test_build_define_bits_lossless2_valid(self):
        """Test building bitmap tag with valid data."""
        char_id = 1
        width = 2
        height = 2
        rgba_data = b'\xFF\x00\x00\xFF' * 4  # 2x2 red pixels
        
        tag = build_define_bits_lossless2(char_id, width, height, rgba_data)
        
        assert len(tag) > 0
        assert isinstance(tag, bytes)
    
    def test_build_define_bits_lossless2_size_mismatch(self):
        """Test with mismatched pixel data size."""
        char_id = 1
        width = 2
        height = 2
        rgba_data = b'\xFF\x00\x00\xFF'  # Too small
        
        # Should complete but log warning
        tag = build_define_bits_lossless2(char_id, width, height, rgba_data)
        assert len(tag) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
