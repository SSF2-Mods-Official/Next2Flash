#!/usr/bin/env python3
"""
error_handler.py — User-friendly error message mapper

Maps technical exceptions to clear, actionable user messages.
Provides troubleshooting guidance and context.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

log = logging.getLogger(__name__)


class ErrorHandler:
    """
    Maps technical exceptions to user-friendly error messages.
    
    Provides clear, actionable messages with troubleshooting guidance
    instead of cryptic stack traces.
    
    Example:
        >>> handler = ErrorHandler()
        >>> try:
        ...     parse_swf(malformed_data)
        ... except Exception as e:
        ...     user_message = handler.format_error(e)
        ...     print(user_message)
    """
    
    # Error message templates
    ERROR_MESSAGES: Dict[str, str] = {
        'ValueError': (
            "Invalid file format: {message}\n\n"
            "Troubleshooting:\n"
            "- Ensure this is a valid SWF file (not renamed .fla or other format)\n"
            "- Try opening the file in Adobe Animate or another Flash tool to verify\n"
            "- The file may be corrupted or incompletely downloaded"
        ),
        'struct.error': (
            "Malformed binary data in SWF file: {message}\n\n"
            "Troubleshooting:\n"
            "- The SWF file may be truncated or corrupted\n"
            "- Try re-exporting from the original source\n"
            "- Verify file integrity (check file size matches expected)"
        ),
        'IndexError': (
            "Unexpected end of file while parsing: {message}\n\n"
            "Troubleshooting:\n"
            "- The SWF file appears to be incomplete\n"
            "- Check if file download completed successfully\n"
            "- Try re-exporting from Adobe Animate with 'Publish' instead of 'Export'"
        ),
        'FileNotFoundError': (
            "Required file not found: {filename}\n\n"
            "Troubleshooting:\n"
            "- Verify the file path is correct\n"
            "- Check file permissions\n"
            "- Ensure the file exists at the specified location"
        ),
        'MemoryError': (
            "Not enough memory to process file: {message}\n\n"
            "Troubleshooting:\n"
            "- The SWF file may be too large (>100MB)\n"
            "- Close other applications to free up memory\n"
            "- Try processing smaller sections of the animation"
        ),
        'zlib.error': (
            "Failed to decompress SWF file: {message}\n\n"
            "Troubleshooting:\n"
            "- The file may be corrupted\n"
            "- Try re-exporting as uncompressed SWF (FWS instead of CWS)\n"
            "- Verify file integrity with a hex editor"
        ),
        'ImportError': (
            "Missing required dependency: {message}\n\n"
            "Troubleshooting:\n"
            "- Run: pip install -r requirements.txt\n"
            "- Verify Python version is 3.7 or higher\n"
            "- Check virtual environment is activated"
        ),
        'subprocess.CalledProcessError': (
            "External tool failed: {message}\n\n"
            "Troubleshooting:\n"
            "- Ensure mxmlc (Adobe Flex SDK) is installed\n"
            "- Verify ffmpeg is available in PATH for audio processing\n"
            "- Check external tool configuration in settings"
        ),
        'PermissionError': (
            "Permission denied: {message}\n\n"
            "Troubleshooting:\n"
            "- Check file/folder permissions\n"
            "- Try running as administrator (Windows) or with sudo (Linux/Mac)\n"
            "- Ensure output directory is writable"
        ),
        'UnicodeDecodeError': (
            "Text encoding error: {message}\n\n"
            "Troubleshooting:\n"
            "- The SWF may contain non-standard character encodings\n"
            "- Try exporting with UTF-8 encoding in Adobe Animate\n"
            "- Check ActionScript source files for special characters"
        ),
    }
    
    # Context-specific guidance
    CONTEXT_GUIDANCE: Dict[str, str] = {
        'conversion': (
            "During SWF → N2D conversion:\n"
            "- Ensure SWF file is valid and complete\n"
            "- Try a simpler test SWF to verify tool is working\n"
            "- Check server logs for detailed error information"
        ),
        'compilation': (
            "During N2D → SWF compilation:\n"
            "- Verify mxmlc (Adobe Flex SDK) is installed correctly\n"
            "- Check ActionScript 3 code for syntax errors\n"
            "- Ensure all library assets are valid"
        ),
        'lazy_loading': (
            "During lazy asset loading:\n"
            "- Check network connectivity\n"
            "- Verify server is running and accessible\n"
            "- Try restarting the server"
        ),
    }
    
    def format_error(
        self,
        exc: Exception,
        context: Optional[str] = None,
        include_trace: bool = False
    ) -> str:
        """
        Format exception as user-friendly message.
        
        Args:
            exc: Exception to format
            context: Optional context ('conversion', 'compilation', etc.)
            include_trace: If True, append technical details
            
        Returns:
            Formatted error message with guidance
        """
        exc_type = type(exc).__name__
        exc_message = str(exc)
        
        # Get template for this exception type
        template = self.ERROR_MESSAGES.get(exc_type)
        
        if not template:
            # Fallback for unknown exception types
            template = (
                "Unexpected error: {message}\n\n"
                "Troubleshooting:\n"
                "- Check server logs for detailed error information\n"
                "- Report this issue with error details\n"
                "- Try a simpler test case to isolate the problem"
            )
        
        # Format message
        formatted = template.format(
            message=exc_message,
            filename=getattr(exc, 'filename', 'unknown'),
            exc_type=exc_type
        )
        
        # Add context-specific guidance
        if context and context in self.CONTEXT_GUIDANCE:
            formatted += "\n\n" + self.CONTEXT_GUIDANCE[context]
        
        # Optionally append technical details
        if include_trace:
            import traceback
            trace = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            formatted += f"\n\nTechnical Details:\n{trace}"
        
        # Log the error
        log.error(
            f"Error during {context or 'operation'}: {exc_type}: {exc_message}"
        )
        
        return formatted
    
    def format_validation_error(self, validation_result) -> str:
        """
        Format validation result as user message.
        
        Args:
            validation_result: ValidationResult instance
            
        Returns:
            Formatted error message
        """
        from swf_validator import ValidationLevel
        
        if validation_result.level == ValidationLevel.ERROR:
            prefix = "❌ Validation Error"
        elif validation_result.level == ValidationLevel.WARNING:
            prefix = "⚠️ Warning"
        else:
            prefix = "ℹ️ Info"
        
        message = f"{prefix}: {validation_result.message}"
        
        if validation_result.context:
            message += f"\n\nContext: {validation_result.context}"
        
        return message


# ══════════════════════════════════════════════════════════════════════
#  MODULE EXPORTS
# ══════════════════════════════════════════════════════════════════════

__all__ = ['ErrorHandler']
