#!/usr/bin/env python3
"""
swf_validator.py — Input validation for SWF files

Provides comprehensive validation with user-friendly error messages.
Validates SWF headers, tag structures, and common malformed patterns.
"""

from __future__ import annotations

import logging
import struct
from typing import List, Optional, Tuple
from enum import Enum

log = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"      # Blocks conversion
    WARNING = "warning"  # Allows conversion with warnings
    INFO = "info"        # Informational only


class ValidationResult:
    """Result of a validation check."""
    
    def __init__(self, level: ValidationLevel, message: str, context: str = ""):
        self.level = level
        self.message = message
        self.context = context
    
    @classmethod
    def ok(cls) -> 'ValidationResult':
        """Create success result."""
        return cls(ValidationLevel.INFO, "OK")
    
    @classmethod
    def error(cls, message: str, context: str = "") -> 'ValidationResult':
        """Create error result."""
        return cls(ValidationLevel.ERROR, message, context)
    
    @classmethod
    def warning(cls, message: str, context: str = "") -> 'ValidationResult':
        """Create warning result."""
        return cls(ValidationLevel.WARNING, message, context)
    
    def is_ok(self) -> bool:
        """Check if validation passed."""
        return self.level != ValidationLevel.ERROR
    
    def __repr__(self):
        ctx = f" ({self.context})" if self.context else ""
        return f"<ValidationResult {self.level.value}: {self.message}{ctx}>"


class SWFValidator:
    """
    Validates SWF file structure and content.
    
    Provides comprehensive validation with clear error messages for:
    - File signatures and headers
    - Tag structures and lengths
    - Character ID ranges
    - Data bounds and integrity
    
    Example:
        >>> validator = SWFValidator()
        >>> result = validator.validate_swf_data(swf_bytes)
        >>> if not result.is_ok():
        ...     print(f"Validation failed: {result.message}")
    """
    
    def __init__(self, strict: bool = False):
        """
        Initialize validator.
        
        Args:
            strict: If True, warnings are treated as errors
        """
        self.strict = strict
        self.results: List[ValidationResult] = []
    
    def validate_swf_data(self, swf_data: bytes) -> ValidationResult:
        """
        Validate complete SWF file data.
        
        Args:
            swf_data: Raw SWF file bytes
            
        Returns:
            ValidationResult with overall status
        """
        self.results = []
        
        # Check minimum size
        if not swf_data or len(swf_data) < 8:
            return ValidationResult.error(
                f"SWF file too small: {len(swf_data)} bytes (minimum 8 bytes required)",
                "file_size"
            )
        
        # Validate signature
        result = self._validate_signature(swf_data)
        self.results.append(result)
        if not result.is_ok():
            return result
        
        # Validate version
        version = swf_data[3]
        result = self._validate_version(version)
        self.results.append(result)
        if not result.is_ok() and self.strict:
            return result
        
        # Validate file length
        try:
            file_length = struct.unpack_from('<I', swf_data, 4)[0]
            result = self._validate_file_length(len(swf_data), file_length)
            self.results.append(result)
            if not result.is_ok() and self.strict:
                return result
        except struct.error as e:
            return ValidationResult.error(
                f"Failed to read file length: {e}",
                "file_length"
            )
        
        # All checks passed
        errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
        
        if errors:
            return errors[0]  # Return first error
        elif warnings and self.strict:
            return warnings[0]
        else:
            return ValidationResult.ok()
    
    def _validate_signature(self, swf_data: bytes) -> ValidationResult:
        """Validate SWF signature."""
        sig = swf_data[0:3]
        valid_sigs = (b'FWS', b'CWS', b'ZWS')
        
        if sig not in valid_sigs:
            return ValidationResult.error(
                f"Invalid SWF signature: {sig!r} (expected FWS, CWS, or ZWS)",
                "signature"
            )
        
        return ValidationResult.ok()
    
    def _validate_version(self, version: int) -> ValidationResult:
        """Validate SWF version number."""
        if version < 1:
            return ValidationResult.error(
                f"Invalid SWF version: {version} (must be ≥1)",
                "version"
            )
        
        if version > 50:
            return ValidationResult.warning(
                f"Unusual SWF version: {version} (expected 1-40)",
                "version"
            )
        
        return ValidationResult.ok()
    
    def _validate_file_length(self, actual: int, declared: int) -> ValidationResult:
        """Validate file length matches header."""
        # Allow some tolerance for compressed files
        if declared > actual * 10:
            return ValidationResult.warning(
                f"Declared file length ({declared}) much larger than actual ({actual})",
                "file_length"
            )
        
        return ValidationResult.ok()
    
    def validate_tag(self, tag_type: int, tag_data: bytes, expected_min_size: int = 0) -> ValidationResult:
        """
        Validate a single SWF tag.
        
        Args:
            tag_type: Tag type code
            tag_data: Tag data bytes
            expected_min_size: Minimum expected data size
            
        Returns:
            ValidationResult
        """
        if expected_min_size > 0 and len(tag_data) < expected_min_size:
            return ValidationResult.error(
                f"Tag {tag_type} too short: {len(tag_data)} bytes (expected ≥{expected_min_size})",
                f"tag_{tag_type}"
            )
        
        return ValidationResult.ok()
    
    def validate_char_id(self, char_id: int) -> ValidationResult:
        """
        Validate SWF character ID.
        
        Args:
            char_id: Character ID to validate
            
        Returns:
            ValidationResult
        """
        if not (1 <= char_id <= 65535):
            return ValidationResult.error(
                f"Invalid character ID: {char_id} (must be 1-65535)",
                "char_id"
            )
        
        return ValidationResult.ok()
    
    def validate_dimensions(self, width: int, height: int) -> ValidationResult:
        """
        Validate bitmap or stage dimensions.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            
        Returns:
            ValidationResult
        """
        if width < 1 or width > 8191:
            return ValidationResult.error(
                f"Invalid width: {width} (must be 1-8191 pixels)",
                "dimensions"
            )
        
        if height < 1 or height > 8191:
            return ValidationResult.error(
                f"Invalid height: {height} (must be 1-8191 pixels)",
                "dimensions"
            )
        
        return ValidationResult.ok()


# ══════════════════════════════════════════════════════════════════════
#  MODULE EXPORTS
# ══════════════════════════════════════════════════════════════════════

__all__ = [
    'SWFValidator',
    'ValidationResult',
    'ValidationLevel',
]
