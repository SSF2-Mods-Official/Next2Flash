#!/usr/bin/env python3
"""
conversion_service.py — Business Logic for SWF ↔ N2D Conversion

Provides clean service layer for conversion operations, decoupled from
HTTP handling and file I/O. Supports dependency injection for testing.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Optional, Tuple

from profiler import Profiler

log = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raised when SWF→N2D conversion fails."""
    pass


class ConversionService:
    """
    Service for converting SWF files to N2D format.
    
    Encapsulates all conversion logic, decoupled from HTTP/file I/O.
    Supports dependency injection for testing with mock parsers/builders.
    
    Example:
        >>> service = ConversionService()
        >>> n2d_json = service.convert_swf_to_n2d(swf_bytes, name="MyAnimation")
        >>> print(f"Converted {len(n2d_json['libraries'])} library entries")
    """
    
    def __init__(self, swf_parser=None, n2d_builder_factory=None):
        """
        Initialize conversion service.
        
        Args:
            swf_parser: Optional parser module (defaults to swf_to_n2d)
            n2d_builder_factory: Optional builder factory for testing
        """
        self._parser = swf_parser
        self._builder_factory = n2d_builder_factory
    
    def _get_parser(self):
        """Lazy-load SWF parser module."""
        if self._parser is None:
            try:
                import swf_to_n2d as mod
                self._parser = mod
            except ImportError as e:
                raise ConversionError(f"Failed to import swf_to_n2d: {e}")
        return self._parser
    
    def convert_swf_to_n2d(
        self,
        swf_data: bytes,
        name: str = "converted",
        include_scripts: bool = True,
        embed_bitmaps: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Convert SWF binary to N2D JSON format.
        
        Args:
            swf_data: SWF file content as bytes
            name: Project name (default: "converted")
            include_scripts: Whether to decompile AS3 scripts (default: True)
            embed_bitmaps: Whether to embed bitmap data in shapes (default: True)
            progress_callback: Optional callable(message: str) for progress updates
            
        Returns:
            N2D JSON dict with libraries, scripts, stage info
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            parser = self._get_parser()
            
            Profiler.start_session("swf-import")
            Profiler.size("input_swf", len(swf_data))
            
            def _progress(msg: str):
                if progress_callback:
                    progress_callback(msg)
                log.debug(f"[ConversionService] {msg}")
            
            t0 = time.time()
            
            # Validate input
            if not swf_data or len(swf_data) < 8:
                raise ConversionError(f"Invalid SWF data: too short ({len(swf_data)} bytes)")
            
            _progress(f"Parsing SWF ({len(swf_data):,} bytes)...")
            
            # Parse SWF binary
            try:
                with Profiler.timer("parse_swf"):
                    header, tags = parser.parse_swf(swf_data)
                Profiler.count("swf_tags", len(tags))
            except Exception as e:
                raise ConversionError(f"Failed to parse SWF: {e}")
            
            elapsed = time.time() - t0
            _progress(f"Parsed SWF in {elapsed:.2f}s: {len(tags)} tags, "
                     f"{header['width']}×{header['height']} @ {header['fps']}fps")
            
            # Build N2D project
            _progress("Building N2D project...")
            
            if self._builder_factory:
                builder = self._builder_factory(header, name)
            else:
                builder = parser.N2DBuilder(header, name=name)
            
            with Profiler.timer("catalog_swf_tags"):
                builder.catalog_swf_tags(tags)
            
            # Decompile AS3 scripts
            if include_scripts:
                _progress("Decompiling AS3 scripts...")
                try:
                    with Profiler.timer("decompile_scripts"):
                        scripts, frame_scripts = parser.decompile_all_scripts(builder.global_raw_tags)
                    builder.frame_scripts = frame_scripts
                    if scripts:
                        builder.scripts.extend(scripts)
                    Profiler.count("scripts", len(scripts))
                    Profiler.count("frame_scripts", len(frame_scripts))
                    _progress(f"Decompiled {len(scripts)} scripts, {len(frame_scripts)} frame scripts")
                except Exception as e:
                    log.warning(f"AS3 decompilation failed (non-fatal): {e}")
                    _progress(f"Warning: Script decompilation failed: {e}")
            
            # Build all library entries
            _progress("Building library entries...")
            with Profiler.timer("build_all"):
                builder.build_all()
            Profiler.count("libraries", len(builder.libraries) if hasattr(builder, 'libraries') else 0)
            
            # Build main timeline
            _progress("Building main timeline...")
            with Profiler.timer("build_main_timeline"):
                builder.build_main_timeline(tags)
            
            # Embed bitmap data in shape recodes
            if embed_bitmaps:
                _progress("Embedding bitmap data...")
                with Profiler.timer("embed_bitmap_data"):
                    builder._embed_bitmap_data_in_recodes()
            
            # Generate N2D JSON
            _progress("Generating N2D JSON...")
            with Profiler.timer("to_n2d_json"):
                n2d_json = builder.to_n2d_json()
            
            # ── Phase 2: Normalize imported scripts ──
            # Drop linkage stubs (regenerated at export), extract frame bodies,
            # mark scripts with scriptOrigin for later filtering
            _progress("Normalizing scripts...")
            try:
                from swf_to_n2d import normalize_imported_scripts
                libs = n2d_json.get('libraries', [])
                scripts = n2d_json.get('scripts', [])
                if scripts:
                    log.info(f"ConversionService: normalizing {len(scripts)} scripts...")
                    normalized = normalize_imported_scripts(scripts, libs)
                    n2d_json['scripts'] = normalized
                    Profiler.count("scripts_after_normalize", len(normalized))
                    _progress(f"Scripts normalized: {len(scripts)} -> {len(normalized)}")
                    log.info(f"ConversionService: scripts after normalization: {len(normalized)}")
            except Exception as e:
                log.error(f"Script normalization failed (CRITICAL): {e}", exc_info=True)
                _progress(f"ERROR: Script normalization failed: {e}")
                raise  # Don't silently continue - this is a critical error
            
            elapsed = time.time() - t0
            Profiler.count("output_libraries", len(n2d_json.get('libraries', [])))
            _progress(f"Conversion complete in {elapsed:.2f}s: "
                     f"{len(n2d_json.get('libraries', []))} library entries, "
                     f"{len(n2d_json.get('scripts', []))} scripts")
            
            report = Profiler.end_session("swf-import")
            if report:
                print(Profiler.format_report(report))
            
            return n2d_json
            
        except ConversionError:
            raise
        except Exception as e:
            log.exception("Unexpected error during conversion")
            raise ConversionError(f"Conversion failed: {e}")
    
    def convert_swf_to_project_folder(
        self,
        swf_data: bytes,
        name: str = "converted",
        progress_callback: Optional[callable] = None
    ) -> Tuple[Dict, str]:
        """
        Convert SWF to editable project folder with external assets.
        
        Args:
            swf_data: SWF file content as bytes
            name: Project name
            progress_callback: Optional progress callback
            
        Returns:
            Tuple of (n2d_json: Dict, warnings: List[str])
            
        Raises:
            ConversionError: If conversion fails
        """
        # First convert to N2D JSON
        n2d_json = self.convert_swf_to_n2d(
            swf_data,
            name=name,
            include_scripts=True,
            embed_bitmaps=True,
            progress_callback=progress_callback
        )
        
        return n2d_json, []  # No warnings for now
    
    def validate_swf(self, swf_data: bytes) -> Dict[str, any]:
        """
        Validate SWF file without full conversion.
        
        Args:
            swf_data: SWF file content as bytes
            
        Returns:
            Dict with validation results:
                {
                    "valid": bool,
                    "version": int,
                    "width": int,
                    "height": int,
                    "fps": float,
                    "frameCount": int,
                    "compressed": bool,
                    "errors": List[str]
                }
        """
        errors = []
        
        try:
            if len(swf_data) < 8:
                return {
                    "valid": False,
                    "errors": [f"File too short: {len(swf_data)} bytes"]
                }
            
            sig = swf_data[0:3]
            if sig not in (b'FWS', b'CWS', b'ZWS'):
                return {
                    "valid": False,
                    "errors": [f"Invalid SWF signature: {sig!r}"]
                }
            
            parser = self._get_parser()
            header, tags = parser.parse_swf(swf_data)
            
            return {
                "valid": True,
                "version": header.get('version', 0),
                "width": header.get('width', 0),
                "height": header.get('height', 0),
                "fps": header.get('fps', 0),
                "frameCount": header.get('frameCount', 0),
                "compressed": sig in (b'CWS', b'ZWS'),
                "tagCount": len(tags),
                "errors": []
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)]
            }
