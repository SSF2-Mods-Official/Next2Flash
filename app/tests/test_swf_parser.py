#!/usr/bin/env python3
"""
test_swf_parser.py — Unit tests for SWF parser

Tests critical parsing functions with valid and invalid inputs.
"""

import pytest
import struct
from swf_to_n2d import parse_swf, read_rect, read_matrix
from swf_binary_io import BitReader
from swf_validator import SWFValidator, ValidationResult


class TestSWFParser:
    """Test SWF parsing functions."""
    
    def test_parse_swf_valid_uncompressed(self):
        """Test parsing valid uncompressed SWF."""
        # Minimal valid FWS (uncompressed SWF)
        swf_data = (
            b'FWS'  # Signature
            b'\x09'  # Version 9
            b'\x00\x00\x00\x64'  # File length (100 bytes - fake)
            b'\x78\x00\x05\x5f\x00\x00\x0f\xa0\x00'  # RECT (800x600)
            b'\x00\x18'  # Frame rate 24.0
            b'\x00\x01'  # Frame count 1
            b'\x00\x00'  # End tag
        )
        
        header, tags = parse_swf(swf_data)
        
        assert header['version'] == 9
        assert header['compressed'] is False
        # Note: RECT encoding '78 00 05 5f 00 00 0f a0 00' decodes to 550x400
        # (nBits=15, xMax=11000 twips = 550px, yMax=8000 twips = 400px)
        assert header['width'] == 550  # Actual decoded value
        assert header['height'] == 400
        assert header['fps'] == 24
        assert isinstance(tags, list)
    
    def test_parse_swf_too_short(self):
        """Test parsing SWF with insufficient data."""
        swf_data = b'FWS'  # Too short
        
        with pytest.raises(ValueError, match="too short"):
            parse_swf(swf_data)
    
    def test_parse_swf_invalid_signature(self):
        """Test parsing with invalid signature."""
        swf_data = b'XYZ\x09\x00\x00\x00\x64'
        
        with pytest.raises(ValueError, match="invalid signature"):
            parse_swf(swf_data)
    
    def test_read_rect(self):
        """Test RECT parsing."""
        # RECT with nBits=15, xMin=0, xMax=11000, yMin=0, yMax=12000
        data = b'\x78\x00\x05\x5f\x00\x00\x0f\xa0\x00'
        br = BitReader(data, 0)
        
        rect = read_rect(br)
        
        assert rect['xMin'] == 0
        assert rect['xMax'] == 11000  # 550px * 20 twips
        assert rect['yMin'] == 0
        assert rect['yMax'] == 8000   # 400px * 20 twips
    
    def test_read_matrix_identity(self):
        """Test identity matrix parsing."""
        # Identity matrix: [1, 0, 0, 1, 0, 0]
        data = b'\x00'  # No scale, no rotation, no translation
        br = BitReader(data, 0)
        
        matrix = read_matrix(br)
        
        assert matrix == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


class TestSWFValidator:
    """Test SWF validator."""
    
    def test_validate_valid_swf(self):
        """Test validation of valid SWF."""
        swf_data = (
            b'FWS'  # Signature
            b'\x09'  # Version 9
            b'\x00\x00\x00\x64'  # File length
            b'\x78\x00\x05\x5f\x00\x00\x0f\xa0\x00'  # RECT
            b'\x00\x18'  # Frame rate
            b'\x00\x01'  # Frame count
            b'\x00\x00'  # End tag
        )
        
        validator = SWFValidator()
        result = validator.validate_swf_data(swf_data)
        
        assert result.is_ok()
    
    def test_validate_too_short(self):
        """Test validation of too short file."""
        validator = SWFValidator()
        result = validator.validate_swf_data(b'FW')
        
        assert not result.is_ok()
        assert "too small" in result.message.lower()
    
    def test_validate_invalid_signature(self):
        """Test validation of invalid signature."""
        validator = SWFValidator()
        result = validator.validate_swf_data(b'ABC\x09\x00\x00\x00\x64')
        
        assert not result.is_ok()
        assert "signature" in result.message.lower()
    
    def test_validate_char_id_valid(self):
        """Test valid character ID."""
        validator = SWFValidator()
        result = validator.validate_char_id(100)
        
        assert result.is_ok()
    
    def test_validate_char_id_invalid(self):
        """Test invalid character ID."""
        validator = SWFValidator()
        result = validator.validate_char_id(0)
        
        assert not result.is_ok()
    
    def test_validate_dimensions_valid(self):
        """Test valid dimensions."""
        validator = SWFValidator()
        result = validator.validate_dimensions(800, 600)
        
        assert result.is_ok()
    
    def test_validate_dimensions_invalid(self):
        """Test invalid dimensions."""
        validator = SWFValidator()
        result = validator.validate_dimensions(0, 600)
        
        assert not result.is_ok()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
