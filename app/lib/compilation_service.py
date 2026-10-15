#!/usr/bin/env python3
"""
compilation_service.py — Business Logic for N2D → SWF Compilation

Provides clean service layer for compilation operations, decoupled from
HTTP handling and file I/O. Supports progress callbacks and error handling.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

log = logging.getLogger(__name__)


class CompilationError(Exception):
    """Raised when N2D→SWF compilation fails."""
    pass


class CompilationService:
    """
    Service for compiling N2D projects to SWF format.
    
    Encapsulates all compilation logic, decoupled from HTTP/file I/O.
    Supports dependency injection for testing.
    
    Example:
        >>> service = CompilationService()
        >>> swf_bytes = service.compile_n2d_to_swf(n2d_json, "output.swf")
        >>> print(f"Compiled SWF: {len(swf_bytes)} bytes")
    """
    
    def __init__(self, compiler_module=None):
        """
        Initialize compilation service.
        
        Args:
            compiler_module: Optional compiler module (defaults to compile_n2d)
        """
        self._compiler = compiler_module
    
    def _get_compiler(self):
        """Lazy-load compiler module."""
        if self._compiler is None:
            try:
                import compile_n2d as mod
                import importlib
                importlib.reload(mod)  # Always reload for dev changes
                self._compiler = mod
            except ImportError as e:
                raise CompilationError(f"Failed to import compile_n2d: {e}")
        return self._compiler
    
    def compile_n2d_to_swf(
        self,
        n2d_json: Dict,
        output_name: str = "output.swf",
        shared_dir: Optional[str] = None,
        main_class: str = "Main",
        progress_callback: Optional[callable] = None
    ) -> bytes:
        """
        Compile N2D JSON to SWF binary.
        
        Args:
            n2d_json: N2D JSON dict with libraries, scripts, etc.
            output_name: Output filename (for logging)
            shared_dir: Optional shared code directory
            main_class: Main class name (default: "Main")
            progress_callback: Optional callable(message: str) for progress
            
        Returns:
            SWF binary data as bytes
            
        Raises:
            CompilationError: If compilation fails
        """
        try:
            compiler_mod = self._get_compiler()
            
            def _progress(msg: str):
                if progress_callback:
                    progress_callback(msg)
                log.debug(f"[CompilationService] {msg}")
            
            t0 = time.time()
            
            # Validate input
            if not n2d_json:
                raise CompilationError("Empty N2D JSON")
            
            if not n2d_json.get('libraries'):
                raise CompilationError("N2D JSON missing 'libraries' array")
            
            _progress(f"Compiling N2D project '{n2d_json.get('name', 'unnamed')}'...")
            
            # Create compiler instance
            # Note: compile_n2d.N2DCompiler expects a file path, but we have JSON.
            # We need to either:
            # 1. Write JSON to temp file
            # 2. Refactor N2DCompiler to accept JSON directly
            # For now, we'll use a temp file approach
            
            import tempfile
            import json
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(n2d_json, f)
                temp_n2d_path = f.name
            
            try:
                with tempfile.NamedTemporaryFile(suffix='.swf', delete=False) as f:
                    temp_swf_path = f.name
                
                try:
                    # Create compiler
                    compiler = compiler_mod.N2DCompiler(
                        temp_n2d_path,
                        shared_dir or "",
                        output_swf_path=temp_swf_path,
                        main_class=main_class
                    )
                    
                    _progress("Compiling...")
                    
                    # Compile
                    compiler.compile()
                    
                    # Read output
                    with open(temp_swf_path, 'rb') as f:
                        swf_bytes = f.read()
                    
                    elapsed = time.time() - t0
                    _progress(f"Compilation complete in {elapsed:.2f}s: {len(swf_bytes):,} bytes")
                    
                    return swf_bytes
                    
                finally:
                    # Clean up temp SWF
                    if os.path.exists(temp_swf_path):
                        os.unlink(temp_swf_path)
            finally:
                # Clean up temp N2D
                if os.path.exists(temp_n2d_path):
                    os.unlink(temp_n2d_path)
            
        except CompilationError:
            raise
        except Exception as e:
            log.exception("Unexpected error during compilation")
            raise CompilationError(f"Compilation failed: {e}")
    
    def validate_n2d(self, n2d_json: Dict) -> Dict[str, any]:
        """
        Validate N2D JSON structure without full compilation.
        
        Args:
            n2d_json: N2D JSON dict
            
        Returns:
            Dict with validation results:
                {
                    "valid": bool,
                    "name": str,
                    "libraryCount": int,
                    "scriptCount": int,
                    "warnings": List[str],
                    "errors": List[str]
                }
        """
        warnings = []
        errors = []
        
        if not isinstance(n2d_json, dict):
            return {
                "valid": False,
                "errors": ["N2D data is not a dictionary"]
            }
        
        # Check required fields
        if 'libraries' not in n2d_json:
            errors.append("Missing 'libraries' array")
        
        if 'stage' not in n2d_json:
            warnings.append("Missing 'stage' config (will use defaults)")
        
        # Validate libraries
        libraries = n2d_json.get('libraries', [])
        if not isinstance(libraries, list):
            errors.append("'libraries' must be an array")
        else:
            # Check root container exists
            if not libraries or len(libraries) == 0:
                errors.append("No libraries defined")
            elif libraries[0].get('id') != 0:
                errors.append("Root container (id=0) must be first library entry")
            elif libraries[0].get('type') != 'container':
                errors.append("Root library entry must be type 'container'")
        
        # Check for duplicate IDs
        if isinstance(libraries, list):
            ids = [lib.get('id') for lib in libraries if isinstance(lib, dict)]
            if len(ids) != len(set(ids)):
                errors.append("Duplicate library IDs detected")
        
        # Validate scripts
        scripts = n2d_json.get('scripts', [])
        if scripts and not isinstance(scripts, list):
            errors.append("'scripts' must be an array")
        
        return {
            "valid": len(errors) == 0,
            "name": n2d_json.get('name', 'unnamed'),
            "libraryCount": len(libraries) if isinstance(libraries, list) else 0,
            "scriptCount": len(scripts) if isinstance(scripts, list) else 0,
            "warnings": warnings,
            "errors": errors
        }
