#!/usr/bin/env python3
"""
Next2Flash — Local server for the Next2D Animation Tool with SWF round-trip.

Serves the web-based animation tool on http://localhost:5000 and exposes
REST endpoints for SWF↔N2D conversion so everything works in one app.

Usage:
    python server.py                     # start on port 5000
    python server.py --port 8080         # custom port
    python server.py --no-browser        # don't auto-open browser
"""

import argparse
import base64
import io
import json
import logging
import msgpack
import os
import shutil
import struct
import sys
import tempfile
import threading
import time
import traceback
import webbrowser
import zlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import unquote, quote

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
#  Locate converter modules (they live alongside this server.py)
# ---------------------------------------------------------------------------
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = SERVER_DIR  # In STABLE, HTML/CSS/JS are at the root level

# Make sure our converter scripts are importable
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

# ── M3.3: Service layer imports ──
from conversion_service import ConversionService, ConversionError
from compilation_service import CompilationService, CompilationError

# ── Phase 1: Session management and error handling ──
from session_manager import SessionManager
from error_handler import ErrorHandler
from swf_validator import SWFValidator

# Lazy-import converters (fail gracefully with clear messages)
_swf_to_n2d = None
_compile_n2d = None
# M3.3: Initialize services
_conversion_service = ConversionService()
_compilation_service = CompilationService()
# Phase 1: Initialize session manager (30-minute TTL)
_session_manager = SessionManager(ttl=1800)
_error_handler = ErrorHandler()
_swf_validator = SWFValidator()

def _get_swf_to_n2d():
    global _swf_to_n2d
    if _swf_to_n2d is None:
        log.debug('_get_swf_to_n2d: lazy-importing swf_to_n2d module')
        import swf_to_n2d as mod
        _swf_to_n2d = mod
    return _swf_to_n2d

def _get_compile_n2d():
    global _compile_n2d
    import compile_n2d as mod
    import importlib
    importlib.reload(mod)
    _compile_n2d = mod
    log.debug('_get_compile_n2d: (re)loaded compile_n2d module')
    return _compile_n2d


def _merge_editor_into_disk(editor: dict, disk: dict) -> None:
    """Merge lightweight editor state into full disk project data.

    The editor blob (from the Next2D tool save) contains updated timeline,
    positions, filters, names etc. but lacks rawTagBody, scripts,
    rawGlobalTags, rootTimelineDefIds.  The disk data has all of those.

    Strategy: For each library, take editor's non-roundtrip fields
    (placeObjects, timeline changes, etc.) and overlay them onto disk,
    keeping disk's rawTagBody and other roundtrip data intact.
    Also update top-level stage/root properties from editor.
    """
    # Update top-level properties that the editor may change
    for key in ('stage', 'name', 'backgroundColor', 'frameRate',
                'width', 'height'):
        if key in editor:
            disk[key] = editor[key]

    # Build lookup of disk libraries by id
    disk_libs = disk.get('libraries', [])
    disk_map = {}
    for lib in disk_libs:
        if lib:
            disk_map[lib.get('id')] = lib

    # Overlay editor library changes onto disk libraries
    editor_libs = editor.get('libraries', [])
    for elib in editor_libs:
        if not elib:
            continue
        lib_id = elib.get('id')
        dlib = disk_map.get(lib_id)
        if not dlib:
            # New library added in editor — use as-is
            disk_libs.append(elib)
            continue

        # Preserve roundtrip fields from disk
        roundtrip_keys = ('rawTagBody', 'rawTagType', 'swfCharId',
                          'fontAuxTags', 'externalFile')
        saved = {}
        for k in roundtrip_keys:
            if k in dlib:
                saved[k] = dlib[k]

        # Take all fields from editor (has updated positions etc.)
        dlib.clear()
        dlib.update(elib)

        # Restore roundtrip fields
        for k, v in saved.items():
            if k not in dlib or not dlib[k]:
                dlib[k] = v

    # Ensure critical roundtrip top-level fields stay from disk
    # (editor blob won't have these)
    # They're already in disk, we just don't overwrite them


def _read_scripts_from_disk(n2d_json: dict, project_dir: str) -> int:
    """For every script with an externalFile, read its .as file from disk.

    Returns the number of scripts refreshed.
    """
    count = 0
    scripts_dir = os.path.join(project_dir, 'scripts')
    for script in n2d_json.get('scripts', []):
        ext_file = script.get('externalFile', '')
        if ext_file:
            fpath = os.path.join(project_dir, ext_file)
        else:
            # Fallback: derive path from script.path
            rel = script.get('path', script.get('name', ''))
            fpath = os.path.join(scripts_dir, rel) if rel else ''
        if fpath and os.path.isfile(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                script['source'] = f.read()
            count += 1
    return count


def _overlay_external_bitmaps(n2d_json: dict, project_dir: str) -> None:
    """Read external PNG/JPG bitmap files and update:
    1. The bitmap library entry (buffer, width, height, rawTagBody).
    2. Any embedded {buffer, width, height} dicts baked into shape recodes,
       matched back to the correct bitmap via the original buffer contents.
    """
    from PIL import Image

    BITMAP_FILL   = 13
    BITMAP_STROKE = 14
    FP_BYTES      = 32  # fingerprint length in bytes (8 RGBA pixels)

    libraries = n2d_json.get("libraries", [])
    log.info('_overlay_external_bitmaps: project_dir=%s, libraries=%d', project_dir, len(libraries))

    def _fingerprint(buf_list):
        """Take a reliable fingerprint: skip leading transparent pixels, grab FP_BYTES."""
        for px in range(0, len(buf_list) - 3, 4):
            if buf_list[px + 3] != 0:   # found non-transparent pixel
                return tuple(buf_list[px: px + FP_BYTES])
        return tuple(buf_list[:FP_BYTES])  # all-transparent fallback

    # Phase 1 — Build fingerprint map from existing bitmap library buffers BEFORE
    # we overwrite them. Maps old_fingerprint → (lib_id, new_rgba_list, new_w, new_h)
    fingerprint_to_new = {}
    lib_id_to_new      = {}   # for int-id recode entries
    updated_libs = 0

    for lib in libraries:
        if not lib or lib.get("type") != "bitmap":
            continue
        ext_file = lib.get("externalFile", "")
        if not ext_file:
            continue
        fpath = os.path.join(project_dir, ext_file)
        if not os.path.isfile(fpath):
            continue
        try:
            # Fingerprint OLD buffer before overwriting
            orig_buf = lib.get("buffer", "")
            if orig_buf:
                # Handle both string buffers (JSON) and list buffers (MessagePack)
                if isinstance(orig_buf, str):
                    old_list = list(orig_buf.encode('latin-1'))
                elif isinstance(orig_buf, (list, bytes)):
                    old_list = list(orig_buf) if not isinstance(orig_buf, list) else orig_buf
                else:
                    old_list = []
                fp = _fingerprint(old_list) if old_list else None
            else:
                fp = None

            img  = Image.open(fpath).convert("RGBA")
            rgba = img.tobytes()
            new_list = list(rgba)

            # Update library entry (use list for MessagePack compatibility)
            lib["buffer"] = new_list
            lib["width"]  = img.width
            lib["height"] = img.height

            # Rebuild rawTagBody (ARGB premultiplied, zlib-compressed)
            argb = bytearray()
            for idx in range(0, len(rgba), 4):
                r, g, b, a = rgba[idx], rgba[idx+1], rgba[idx+2], rgba[idx+3]
                if a == 0:
                    argb.extend([0, 0, 0, 0])
                elif a == 255:
                    argb.extend([a, r, g, b])
                else:
                    argb.extend([a, (r*a+127)//255, (g*a+127)//255, (b*a+127)//255])
            compressed = zlib.compress(bytes(argb), 9)
            raw_body = struct.pack('<BHH', 5, img.width, img.height) + compressed
            lib["rawTagBody"] = base64.b64encode(raw_body).decode("ascii")
            lib["rawTagType"] = 36  # DefineBitsLossless2

            payload = (new_list, img.width, img.height)
            if fp:
                fingerprint_to_new[fp] = payload
            lib_id_to_new[lib["id"]] = payload
            updated_libs += 1
        except Exception as e:
            log.warning('_overlay_external_bitmaps: %s: %s', ext_file, e)

    log.info('_overlay_external_bitmaps: updated %d bitmap library entries', updated_libs)

    # Phase 2 — Walk shape recodes and replace embedded bitmap dicts.
    if not lib_id_to_new and not fingerprint_to_new:
        return

    fills_updated = 0
    for lib in libraries:
        if lib.get("type") != "shape" or not lib.get("inBitmap"):
            continue
        recodes = lib.get("recodes", [])
        i = 0
        while i < len(recodes):
            cmd = recodes[i]
            if cmd == BITMAP_FILL and i + 1 < len(recodes):
                fv      = recodes[i + 1]
                fill_at = i + 1
                step    = 5
            elif cmd == BITMAP_STROKE and i + 5 < len(recodes):
                fv      = recodes[i + 5]
                fill_at = i + 5
                step    = 9
            else:
                i += 1
                continue

            new_data = None
            if isinstance(fv, int):
                # Integer library ID reference
                new_data = lib_id_to_new.get(fv)
            elif isinstance(fv, dict):
                bmp_id = fv.get("bitmapId")
                if bmp_id is not None:
                    # Newer format with explicit ID
                    new_data = lib_id_to_new.get(bmp_id)
                else:
                    # Fingerprint match against old buffer
                    buf = fv.get("buffer") or []
                    fp  = _fingerprint(buf)
                    new_data = fingerprint_to_new.get(fp)

            if new_data is not None:
                new_rgba, new_w, new_h = new_data
                if isinstance(fv, dict):
                    fv["buffer"] = new_rgba
                    fv["width"]  = new_w
                    fv["height"] = new_h
                else:
                    recodes[fill_at] = {"buffer": new_rgba, "width": new_w, "height": new_h}
                fills_updated += 1

            i += step

    log.info('_overlay_external_bitmaps: updated %d embedded shape fill dicts', fills_updated)
    print(f'[N2F] bitmap overlay: {updated_libs} bitmaps, {fills_updated} shape fills updated')


# ---------------------------------------------------------------------------
#  Request handler
# ---------------------------------------------------------------------------
class Next2FlashHandler(SimpleHTTPRequestHandler):
    """Serves static files from app/ and handles API routes."""

    def __init__(self, *args, **kwargs):
        # Serve from the app/ directory
        super().__init__(*args, directory=APP_DIR, **kwargs)

    # ---------- Routing ----------

    def do_GET(self):
        log.debug('do_GET: %s', self.path)
        if self.path == "/api/health":
            self._json_response({"status": "ok", "name": "Next2Flash"})
        elif self.path == "/api/capabilities":
            self._json_response({
                "swf_to_n2d": True,
                "n2d_to_swf": True,
                "as3_decompiler": self._has_as3_decompiler(),
            })
        elif self.path.startswith("/api/test-file/"):
            self._handle_test_file()
        elif self.path.startswith("/api/lazy/library/"):
            self._handle_lazy_library()
        elif self.path == "/api/lazy/bulk":
            self._handle_lazy_bulk()
        else:
            super().do_GET()

    def end_headers(self):
        """Add no-cache headers to all responses so dev changes take effect immediately."""
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_POST(self):
        log.debug('do_POST: %s', self.path)
        if self.path == "/api/swf-to-n2d":
            self._handle_swf_to_n2d()
        elif self.path == "/api/n2d-to-swf":
            self._handle_n2d_to_swf()
        elif self.path == "/api/swf-to-project":
            self._handle_swf_to_project()
        elif self.path == "/api/open-project":
            self._handle_open_project()
        elif self.path == "/api/refresh-assets":
            self._handle_refresh_assets()
        elif self.path == "/api/decompile-abc":
            self._handle_decompile_abc()
        elif self.path == "/api/log":
            self._handle_client_log()
        elif self.path == "/api/profile":
            self._handle_profile_log()
        elif self.path == "/api/test-report":
            self._handle_test_report()
        elif self.path == "/api/save-script":
            self._handle_save_script()
        elif self.path == "/api/save-project":
            self._handle_save_project()
        elif self.path == "/api/save-and-compile":
            self._handle_save_and_compile()
        elif self.path == "/api/compile-disk":
            self._handle_compile_disk()
        elif self.path == "/api/import-swf-path":
            self._handle_import_swf_path()
        else:
            self.send_error(404, "Not found")

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    # ---------- API handlers ----------

    def _handle_client_log(self):
        """POST /api/log — Print browser-side log messages to terminal."""
        try:
            body = self._read_body()
            if body:
                data = json.loads(body)
                # Support batch logging: { entries: [...] } or single { level, message }
                entries = data.get('entries', None)
                if entries:
                    for entry in entries:
                        level = entry.get('level', 'INFO').upper()
                        mod = entry.get('module', '?')
                        msg = entry.get('message', '')
                        ts = entry.get('ts', '')
                        print(f"[WebView][{ts}s][{mod}][{level}] {msg}", flush=True)
                else:
                    level = data.get('level', 'INFO').upper()
                    msg = data.get('message', '')
                    mod = data.get('module', '?')
                    print(f"[WebView][{mod}][{level}] {msg}", flush=True)
            self._json_response({"ok": True})
        except Exception as e:
            print(f"[WebView][ERROR] Failed to parse log: {e}", flush=True)
            self._json_response({"ok": False})

    # ---- Profile log file path (shared across requests) ----
    _profile_path = os.path.join(SERVER_DIR, "_profile.log")
    _profile_lock = threading.Lock()

    def _handle_profile_log(self):
        """POST /api/profile — Append performance profile lines to _profile.log."""
        try:
            body = self._read_body()
            if body:
                data = json.loads(body)
                lines = data.get('lines', [])
                if lines:
                    with self._profile_lock:
                        with open(self._profile_path, 'a', encoding='utf-8') as f:
                            for line in lines:
                                f.write(line + '\n')
            self._json_response({"ok": True})
        except Exception as e:
            print(f"[Profile][ERROR] {e}", flush=True)
            self._json_response({"ok": False})

    # ---- Test report (written by profiler test harness) ----
    _test_report_path = os.path.join(SERVER_DIR, "_test_report.json")
    _test_report_lock = threading.Lock()
    _test_report_received = threading.Event()

    def _handle_test_file(self):
        """GET /api/test-file/<filename> — Serve a test file from SERVER_DIR."""
        log.debug('_handle_test_file: %s', self.path)
        try:
            filename = unquote(self.path.split("/api/test-file/", 1)[1])
            # Security: only allow files in SERVER_DIR, no path traversal
            filename = os.path.basename(filename)
            filepath = os.path.join(SERVER_DIR, filename)
            if not os.path.isfile(filepath):
                self.send_error(404, f"File not found: {filename}")
                return
            fsize = os.path.getsize(filepath)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(fsize))
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self._cors_headers()
            self.end_headers()
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except Exception as e:
            print(f"[TestFile][ERROR] {e}", flush=True)
            self.send_error(500, str(e))

    def _handle_test_report(self):
        """POST /api/test-report — Receive performance test report from browser."""
        try:
            body = self._read_body()
            if body:
                data = json.loads(body)
                with self._test_report_lock:
                    with open(self._test_report_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                # Print report text to console
                text = data.get('text', '')
                if text:
                    print(f"\n{text}\n", flush=True)
                passed = data.get('pass', False)
                print(f"[Test] Report saved to {self._test_report_path}", flush=True)
                print(f"[Test] Result: {'PASS' if passed else 'FAIL'}", flush=True)
                self.__class__._test_report_received.set()
            self._json_response({"ok": True})
        except Exception as e:
            print(f"[Test][ERROR] {e}", flush=True)
            self._json_response({"ok": False})

    def _handle_swf_to_n2d(self):
        """POST /api/swf-to-n2d — Convert uploaded SWF to N2D.
        
        Accepts: multipart/form-data with 'file' field, or raw SWF bytes.
        Returns: N2D file as application/octet-stream.
        
        ── M3.3: Refactored to use ConversionService ──
        ── Phase 1: Added input validation ──
        """
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, "No data received")

            # Detect if it's a raw SWF or form-data
            swf_data, filename = self._extract_upload(body, "file")
            if not swf_data:
                swf_data = body
                filename = "upload.swf"

            # ── Phase 1: Validate SWF data ──
            validation_result = _swf_validator.validate_swf_data(swf_data)
            if not validation_result.is_ok():
                log.warning(f'_handle_swf_to_n2d: validation failed: {validation_result.message}')
                return self._error_response(400, validation_result.message)

            name = os.path.splitext(filename)[0] if filename else "converted"
            log.info('_handle_swf_to_n2d: converting %s (%d bytes)', filename, len(swf_data))

            # ── M3.3: Use ConversionService ──
            progress_lines = []
            def progress_callback(msg: str):
                progress_lines.append(msg)
                print(f"[SWF->N2D] {msg}", flush=True)
            
            try:
                n2d_json = _conversion_service.convert_swf_to_n2d(
                    swf_data,
                    name=name,
                    include_scripts=True,
                    embed_bitmaps=True,
                    progress_callback=progress_callback
                )
            except ConversionError as e:
                log.error(f'_handle_swf_to_n2d: conversion failed: {e}')
                error_msg = _error_handler.format_error(e)
                return self._error_response(500, error_msg)
            except Exception as e:
                log.error(f'_handle_swf_to_n2d: unexpected error: {e}')
                error_msg = _error_handler.format_error(e)
                return self._error_response(500, error_msg)

            # Create ZIP with MessagePack format (new format that bypasses string length limit)
            import zipfile
            import io as _io
            
            zip_buffer = _io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                # Write MessagePack binary (preferred format)
                msgpack_data = msgpack.packb(n2d_json, use_bin_type=True)
                zf.writestr('project.msgpack', msgpack_data)
            
            compressed = zip_buffer.getvalue()

            # Also produce the sidecar meta
            meta_json = self._build_sidecar(n2d_json)
            meta_compressed = zlib.compress(
                json.dumps(meta_json, separators=(",", ":"), ensure_ascii=False).encode("utf-8"), 1
            )

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
            self.send_header("X-N2D-Name", name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-N2D-Scripts", str(len(n2d_json.get("scripts", []))))
            self.send_header("X-N2D-Format", "msgpack")
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_swf_to_n2d: unexpected error: %s', e)
            self._error_response(500, f"SWF->N2D conversion failed: {e}")

    # ── Project folder persistent path ──
    _current_project_dir = None
    _project_lock = threading.Lock()

    # ── Lazy loading: per-library data stored in memory ──
    _lazy_libraries = {}  # {library_id: library_data_dict}
    _lazy_bulk_cache = None  # cached msgpack bytes for /api/lazy/bulk
    _lazy_lock = threading.Lock()

    def _handle_swf_to_project(self):
        """POST /api/swf-to-project — Import SWF into an editable project folder.

        Extracts bitmaps as PNG/JPG, sounds as MP3/WAV, scripts as .as files.
        Returns the N2D zlib blob for loading into the tool, plus sets the
        project directory for subsequent refresh/export operations.
        
        ── M3.3: Refactored to use ConversionService ──
        """
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, "No data received")

            swf_data, filename = self._extract_upload(body, "file")
            if not swf_data:
                swf_data = body
                filename = "upload.swf"

            name = os.path.splitext(filename)[0] if filename else "converted"
            log.info('_handle_swf_to_project: converting %s (%d bytes)', filename, len(swf_data))

            _t0 = time.time()
            def _tick(label):
                elapsed = time.time() - _t0
                print(f"[IMPORT {elapsed:6.2f}s] {label}", flush=True)

            _tick(f"start - {len(swf_data):,} bytes")

            # ── M3.3: Use ConversionService ──
            def progress_callback(msg: str):
                _tick(msg)
            
            try:
                n2d_json = _conversion_service.convert_swf_to_n2d(
                    swf_data,
                    name=name,
                    include_scripts=True,
                    embed_bitmaps=True,
                    progress_callback=progress_callback
                )
            except ConversionError as e:
                log.error(f'_handle_swf_to_project: conversion failed: {e}')
                return self._error_response(500, f"SWF->Project conversion failed: {e}")

            _tick(f"conversion complete: {len(n2d_json.get('libraries', []))} libs")

            # Save as project folder
            project_dir = os.path.join(SERVER_DIR, "converted", name)
            mod = _get_swf_to_n2d()
            mod.save_project_folder(n2d_json, project_dir)
            _tick("save_project_folder")

            with self._project_lock:
                Next2FlashHandler._current_project_dir = project_dir

            # Return ZIP with MessagePack for loading into the tool (bypasses string length limit).
            # New format: ZIP archive containing project.msgpack binary
            import zipfile
            import io as _io
            
            zip_buffer = _io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                # Write MessagePack binary (preferred format - no string length limit)
                msgpack_data = msgpack.packb(n2d_json, use_bin_type=True)
                zf.writestr('project.msgpack', msgpack_data)
                _tick(f"msgpack.packb: {len(msgpack_data):,} bytes")
            
            compressed = zip_buffer.getvalue()
            _tick(f"ZIP: {len(compressed):,} bytes -> DONE")

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
            self.send_header("X-N2D-Name", name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-N2D-Scripts", str(len(n2d_json.get("scripts", []))))
            self.send_header("X-N2D-Format", "msgpack")
            self.send_header("X-Project-Dir", project_dir)
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_swf_to_project: failed: %s', e)
            self._error_response(500, f"SWF->Project conversion failed: {e}")

    def _handle_open_project(self):
        """POST /api/open-project — Open an .n2d file.

        Accepts: multipart/form-data with 'file' field containing .n2d data.
        If the .n2d lives inside a project folder (with bitmaps/sounds/scripts),
        that folder becomes the active project for refresh/export.
        Returns the N2D zlib blob for loading into the tool.
        """
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, "No data received")

            n2d_data, filename = self._extract_upload(body, "file")
            if not n2d_data:
                n2d_data = body
                filename = "upload.n2d"

            name = os.path.splitext(filename)[0] if filename else "project"
            log.info('_handle_open_project: opening %s (%d bytes)', filename, len(n2d_data))

            # Parse the .n2d to get JSON/MessagePack (ZIP or zlib format)
            import zipfile as _zipfile
            import io as _io
            if n2d_data[:2] == b'PK':
                with _zipfile.ZipFile(_io.BytesIO(n2d_data)) as zf:
                    # Try MessagePack first (new format), then JSON (legacy)
                    if 'project.msgpack' in zf.namelist():
                        msgpack_data = zf.read('project.msgpack')
                        n2d_json = msgpack.unpackb(msgpack_data, raw=False)
                        log.info('_handle_open_project: loaded MessagePack format')
                    else:
                        n2d_json = json.loads(zf.read('project.json'))
                        log.info('_handle_open_project: loaded JSON format')
            else:
                decompressed = zlib.decompress(n2d_data)
                text = decompressed.decode('utf-8')
                try:
                    n2d_json = json.loads(unquote(text))
                except (json.JSONDecodeError, ValueError):
                    n2d_json = json.loads(text)

            # Check if this .n2d lives in a project folder.
            # The N2D's internal "name" field is the actual project folder name
            # (e.g. "gameandwatchOG"), while the uploaded filename is always
            # "project.n2d", so prefer the JSON name for the lookup.
            proj_name = n2d_json.get("name", name)
            project_dir = os.path.join(SERVER_DIR, "converted", proj_name)
            has_project = (
                os.path.isdir(project_dir) and
                os.path.isdir(os.path.join(project_dir, "bitmaps"))
            )
            print(f'[N2F DEBUG] _handle_open_project: filename={filename!r}, json_name={proj_name!r}')
            print(f'[N2F DEBUG]   project_dir={project_dir!r}, has_project={has_project}')
            # Fallback: try filename-derived name in case JSON name differs
            if not has_project and proj_name != name:
                alt_dir = os.path.join(SERVER_DIR, "converted", name)
                alt_has = os.path.isdir(alt_dir) and os.path.isdir(os.path.join(alt_dir, "bitmaps"))
                print(f'[N2F DEBUG]   fallback alt_dir={alt_dir!r}, alt_has={alt_has}')
                if alt_has:
                    project_dir = alt_dir
                    has_project = True

            if has_project:
                with self._project_lock:
                    Next2FlashHandler._current_project_dir = project_dir
                log.info('_handle_open_project: found project folder at %s', project_dir)
                # Overlay external bitmaps and re-read latest scripts from disk
                _overlay_external_bitmaps(n2d_json, project_dir)
                scripts_refreshed = _read_scripts_from_disk(n2d_json, project_dir)
                log.info('_handle_open_project: refreshed %d scripts from disk', scripts_refreshed)
            else:
                project_dir = None

            # Return zlib-compressed N2D for loading into the tool
            json_str = json.dumps(n2d_json, separators=(",", ":"), ensure_ascii=True)
            url_encoded = json_str.replace('%', '%25')
            compressed = zlib.compress(url_encoded.encode("ascii"), 1)

            n2d_name = n2d_json.get("name", name)

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{n2d_name}.n2d"')
            self.send_header("X-N2D-Name", n2d_name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-N2D-Scripts", str(len(n2d_json.get("scripts", []))))
            self.send_header("X-Project-Dir", project_dir or "")
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_open_project: failed: %s', e)
            self._error_response(500, f"Open project failed: {e}")

    def _handle_save_script(self):
        """POST /api/save-script — Write a single script file to the project scripts folder.

        Accepts JSON: {"path": "com/example/Foo.as", "source": "..."}.
        Writes to {current_project_dir}/scripts/{path}.
        """
        try:
            body = self._read_body()
            payload = json.loads(body)
            rel_path = payload.get('path', '')
            source = payload.get('source', '')

            if not rel_path:
                return self._error_response(400, 'Missing path')

            with self._project_lock:
                project_dir = Next2FlashHandler._current_project_dir

            if not project_dir:
                return self._error_response(409, 'No project loaded - import a SWF first')

            # Sanitize: prevent path traversal
            scripts_dir = os.path.join(project_dir, 'scripts')
            target = os.path.realpath(os.path.join(scripts_dir, rel_path))
            if not target.startswith(os.path.realpath(scripts_dir) + os.sep):
                return self._error_response(400, 'Invalid path')

            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'w', encoding='utf-8') as f:
                f.write(source)
            log.info('save-script: wrote %s (%d chars)', target, len(source))

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', '2')
            self.end_headers()
            self.wfile.write(b'{}')
        except Exception as e:
            log.error('_handle_save_script: %s', e)
            self._error_response(500, str(e))

    def _handle_save_project(self):
        """POST /api/save-project — Save the current editor state back to the project folder.

        Accepts: multipart/form-data with 'n2d' field containing the N2D blob.
        Parses the N2D (ZIP or zlib), then calls save_project_folder() to
        update bitmaps/sounds/scripts and project.n2d on disk.
        """
        try:
            with self._project_lock:
                project_dir = Next2FlashHandler._current_project_dir

            if not project_dir:
                return self._error_response(409, 'No project loaded - import a SWF or open a project first')

            body = self._read_body()
            if not body:
                return self._error_response(400, 'No data received')

            n2d_data, _ = self._extract_upload(body, 'n2d')
            if not n2d_data:
                n2d_data = body

            log.info('_handle_save_project: saving to %s (%d bytes)', project_dir, len(n2d_data))

            # Parse N2D (ZIP or zlib)
            import zipfile as _zipfile
            import io as _io
            if n2d_data[:2] == b'PK':
                with _zipfile.ZipFile(_io.BytesIO(n2d_data)) as zf:
                    n2d_json = json.loads(zf.read('project.json'))
            else:
                decompressed = zlib.decompress(n2d_data)
                text = decompressed.decode('utf-8')
                try:
                    n2d_json = json.loads(unquote(text))
                except (json.JSONDecodeError, ValueError):
                    n2d_json = json.loads(text)

            mod = _get_swf_to_n2d()
            mod.save_project_folder(n2d_json, project_dir)

            resp = json.dumps({'ok': True, 'folder': project_dir})
            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp.encode('utf-8'))

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_save_project: %s', e)
            self._error_response(500, str(e))

    def _handle_save_and_compile(self):
        """POST /api/save-and-compile — Merge editor state + compile to SWF.

        Fast path: receives 'editorBlob' (raw zlib tool save, no rawTagBody).
        Server loads existing project.n2d (which has rawTagBody, scripts, etc.),
        overlays editor timeline/position changes, saves, and compiles.
        This avoids the huge JS-side decompress→parse→merge→stringify→recompress.

        Also supports legacy 'n2d' field (full N2D blob) for backward compat.
        """
        import time as _time
        try:
            _t0 = _time.perf_counter()
            with self._project_lock:
                project_dir = Next2FlashHandler._current_project_dir

            if not project_dir:
                return self._error_response(409, 'No project loaded')

            body = self._read_body()
            if not body:
                return self._error_response(400, 'No data received')
            _t1 = _time.perf_counter()
            print(f"[PERF] read body: {(_t1-_t0)*1000:.0f}ms, size={len(body)/1048576:.1f}MB")

            # Check if this is the fast editorBlob path, disk-only, or legacy n2d path
            editor_blob, _ = self._extract_upload(body, 'editorBlob')
            n2d_data, _ = self._extract_upload(body, 'n2d')
            # disk-only flag: compile from existing project.n2d without any editor overlay
            disk_only = b'diskOnly' in body and not editor_blob and not n2d_data

            n2d_path = os.path.join(project_dir, 'project.n2d')

            if editor_blob:
                # === FAST PATH: merge editor blob with on-disk project ===
                _t2 = _time.perf_counter()

                # Parse the lightweight editor blob (no rawTagBody)
                editor_decompressed = zlib.decompress(editor_blob)
                try:
                    import orjson as _orjson
                    try:
                        editor_json = _orjson.loads(unquote(editor_decompressed))
                    except Exception:
                        editor_json = _orjson.loads(editor_decompressed)
                except ImportError:
                    editor_text = editor_decompressed.decode('utf-8')
                    try:
                        editor_json = json.loads(unquote(editor_text))
                    except (json.JSONDecodeError, ValueError):
                        editor_json = json.loads(editor_text)
                _t2a = _time.perf_counter()
                print(f"[PERF] parse editor blob: {(_t2a-_t2)*1000:.0f}ms")

                # Load existing project.n2d from disk (has rawTagBody, scripts, etc.)
                if not os.path.isfile(n2d_path):
                    return self._error_response(400, 'No project.n2d on disk')

                import zipfile as _zipfile
                import io as _io
                import msgpack as _msgpack
                with _zipfile.ZipFile(n2d_path) as zf:
                    zf_names = zf.namelist()
                    if 'project.msgpack' in zf_names:
                        disk_json = _msgpack.unpackb(zf.read('project.msgpack'), raw=False)
                    elif 'project.json' in zf_names:
                        disk_json = json.loads(zf.read('project.json'))
                    else:
                        return self._error_response(400, 'Invalid project.n2d format')
                _t2b = _time.perf_counter()
                print(f"[PERF] load disk n2d: {(_t2b-_t2a)*1000:.0f}ms")

                # Merge: overlay editor changes onto disk data
                # The editor blob has updated timeline/position data but lacks
                # rawTagBody, rawGlobalTags, scripts, rootTimelineDefIds.
                # Keep those from disk, take everything else from editor.
                _merge_editor_into_disk(editor_json, disk_json)
                n2d_json = disk_json
                _t2c = _time.perf_counter()
                print(f"[PERF] merge: {(_t2c-_t2b)*1000:.0f}ms")

            elif disk_only:
                # === DISK-ONLY PATH: compile from existing project.n2d ===
                _t2 = _time.perf_counter()
                if not os.path.isfile(n2d_path):
                    return self._error_response(400, 'No project.n2d on disk')
                import zipfile as _zipfile
                import msgpack as _msgpack
                with _zipfile.ZipFile(n2d_path) as zf:
                    zf_names = zf.namelist()
                    if 'project.msgpack' in zf_names:
                        n2d_json = _msgpack.unpackb(zf.read('project.msgpack'), raw=False)
                    elif 'project.json' in zf_names:
                        n2d_json = json.loads(zf.read('project.json'))
                    else:
                        return self._error_response(400, 'Invalid project.n2d format')
                _t2a = _time.perf_counter()
                print(f"[PERF] disk-only load: {(_t2a-_t2)*1000:.0f}ms")

            elif n2d_data:
                # === LEGACY PATH: full N2D blob ===
                _t2 = _time.perf_counter()
                import zipfile as _zipfile
                import io as _io
                if n2d_data[:2] == b'PK':
                    with _zipfile.ZipFile(_io.BytesIO(n2d_data)) as zf:
                        n2d_json = json.loads(zf.read('project.json'))
                else:
                    decompressed = zlib.decompress(n2d_data)
                    text = decompressed.decode('utf-8')
                    try:
                        n2d_json = json.loads(unquote(text))
                    except (json.JSONDecodeError, ValueError):
                        n2d_json = json.loads(text)
            else:
                return self._error_response(400, 'No editorBlob or n2d field')

            # Save project
            _t3 = _time.perf_counter()
            mod_swf = _get_swf_to_n2d()
            mod_swf.save_project_folder(n2d_json, project_dir)
            _t3a = _time.perf_counter()
            print(f"[PERF] save project: {(_t3a-_t3)*1000:.0f}ms")

            # Compile from saved project
            if not os.path.isfile(n2d_path):
                return self._error_response(400, 'No project.n2d after save')

            name = os.path.basename(project_dir)
            mod_compile = _get_compile_n2d()

            with tempfile.TemporaryDirectory() as tmpdir:
                swf_path = os.path.join(tmpdir, f"{name}.swf")
                shared_dir = os.path.join(SERVER_DIR, "..", "shared")
                if not os.path.isdir(shared_dir):
                    shared_dir = tmpdir

                compiler = mod_compile.N2DCompiler(
                    n2d_path=n2d_path,
                    shared_dir=shared_dir,
                    output_path=swf_path,
                )
                compiler.compile()
                _t4 = _time.perf_counter()
                print(f"[PERF] compile: {(_t4-_t3a)*1000:.0f}ms")

                with open(swf_path, "rb") as f:
                    swf_bytes = f.read()

                self.send_response(200)
                self._cors_headers()
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{name}.swf"')
                self.send_header("Content-Length", str(len(swf_bytes)))
                self.end_headers()
                self.wfile.write(swf_bytes)
                _t5 = _time.perf_counter()
                print(f"[PERF] save-and-compile total: {(_t5-_t0)*1000:.0f}ms")

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_save_and_compile: %s', e)
            self._error_response(500, str(e))

    def _handle_compile_disk(self):
        """POST /api/compile-disk — Compile SWF directly from on-disk project.

        Expects JSON body: {"projectDir": "...", "outputPath": "..."}
        No file upload — reads project.n2d from disk, compiles, writes SWF to
        outputPath (or returns bytes if no outputPath given). This is the
        Electron fast path that completely bypasses HTTP file transfer.
        """
        import time as _time
        try:
            _t0 = _time.perf_counter()
            body = self._read_body()
            req = json.loads(body)
            project_dir = req.get('projectDir', '')
            output_path = req.get('outputPath', '')

            if not project_dir:
                with self._project_lock:
                    project_dir = Next2FlashHandler._current_project_dir
            if not project_dir:
                return self._error_response(409, 'No project loaded')

            n2d_path = os.path.join(project_dir, 'project.n2d')
            if not os.path.isfile(n2d_path):
                return self._error_response(400, f'No project.n2d in {project_dir}')

            _t1 = _time.perf_counter()
            name = os.path.basename(project_dir)
            mod_compile = _get_compile_n2d()
            shared_dir = os.path.join(SERVER_DIR, '..', 'shared')
            if not os.path.isdir(shared_dir):
                shared_dir = tempfile.mkdtemp()

            if output_path:
                # Write directly to the requested path (Electron native save)
                swf_path = output_path
            else:
                swf_path = os.path.join(tempfile.mkdtemp(), f'{name}.swf')

            compiler = mod_compile.N2DCompiler(
                n2d_path=n2d_path,
                shared_dir=shared_dir,
                output_path=swf_path,
            )
            compiler.compile()
            _t2 = _time.perf_counter()
            print(f"[PERF] compile-disk: compile={(_t2-_t1)*1000:.0f}ms total={(_t2-_t0)*1000:.0f}ms")

            if output_path:
                # SWF written to disk — just return success + path
                stat = os.stat(swf_path)
                self._json_response({
                    'ok': True,
                    'swfPath': swf_path,
                    'size': stat.st_size,
                })
            else:
                # Return SWF bytes over HTTP (non-Electron fallback)
                with open(swf_path, 'rb') as f:
                    swf_bytes = f.read()
                self.send_response(200)
                self._cors_headers()
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{name}.swf"')
                self.send_header('Content-Length', str(len(swf_bytes)))
                self.end_headers()
                self.wfile.write(swf_bytes)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_compile_disk: %s', e)
            self._error_response(500, str(e))

    def _handle_import_swf_path(self):
        """POST /api/import-swf-path — Import SWF by filesystem path.

        Expects JSON body: {"swfPath": "...", "lazy": true/false}
        Reads the SWF directly from disk instead of receiving it as an upload.
        This is the Electron fast path for import.

        When lazy=true, stores full library data server-side and returns only
        a skeleton project (metadata for each library, no heavy binary data).
        The client can then fetch individual libraries via /api/lazy/library/<id>.
        """
        try:
            body = self._read_body()
            req = json.loads(body)
            swf_path = req.get('swfPath', '')
            lazy = req.get('lazy', False)

            if not swf_path or not os.path.isfile(swf_path):
                return self._error_response(400, f'SWF file not found: {swf_path}')

            _t0 = time.time()
            def _tick(label):
                print(f"[IMPORT {time.time()-_t0:6.2f}s] {label}", flush=True)

            swf_data = None  # defer reading
            name = os.path.splitext(os.path.basename(swf_path))[0]

            # Check for cached conversion on disk
            project_dir = os.path.join(SERVER_DIR, 'converted', name)
            cached_n2d = os.path.join(project_dir, 'project.n2d')
            skeleton_cache = os.path.join(project_dir, 'skeleton.n2d')
            n2d_json = None

            # Fast path: if lazy and skeleton cache exists, serve immediately
            if lazy and os.path.isfile(skeleton_cache):
                swf_mtime = os.path.getmtime(swf_path)
                cache_mtime = os.path.getmtime(skeleton_cache)
                if cache_mtime >= swf_mtime:
                    compressed = open(skeleton_cache, 'rb').read()
                    _tick(f"serving cached skeleton: {len(compressed):,} bytes")

                    # Read lib/script counts from the full N2D cache
                    _skel_lib_count = 0
                    _skel_script_count = 0
                    _full_n2d = os.path.join(project_dir, 'project.n2d')
                    if os.path.isfile(_full_n2d):
                        try:
                            import zipfile as _zipfile
                            import io as _io
                            with _zipfile.ZipFile(_full_n2d, 'r') as _zf:
                                _names = _zf.namelist()
                                if 'project.msgpack' in _names:
                                    _raw = _zf.read('project.msgpack')
                                    _n2d = msgpack.unpackb(_raw, raw=False)
                                elif 'project.json' in _names:
                                    _raw = _zf.read('project.json')
                                    _n2d = json.loads(_raw)
                                else:
                                    _n2d = {}
                                _skel_lib_count = len(_n2d.get('libraries', []))
                                _skel_script_count = len(_n2d.get('scripts', []))
                            _tick(f"skeleton lib count from full N2D: {_skel_lib_count}")
                        except Exception as _e:
                            _tick(f"could not read lib count from full N2D: {_e}")

                    with self._project_lock:
                        Next2FlashHandler._current_project_dir = project_dir

                    self.send_response(200)
                    self._cors_headers()
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{name}.n2d"')
                    self.send_header('X-N2D-Name', name)
                    self.send_header('X-N2D-Libraries', str(_skel_lib_count))
                    self.send_header('X-N2D-Scripts', str(_skel_script_count))
                    self.send_header('X-N2D-Format', 'msgpack')
                    self.send_header('X-Project-Dir', project_dir)
                    self.send_header('Content-Length', str(len(compressed)))
                    self.end_headers()
                    self.wfile.write(compressed)
                    return

            # Load from full cache or reconvert
            if os.path.isfile(cached_n2d):
                swf_mtime = os.path.getmtime(swf_path)
                cache_mtime = os.path.getmtime(cached_n2d)
                if cache_mtime >= swf_mtime:
                    _tick(f"loading cached N2D from {cached_n2d}")
                    try:
                        import zipfile as _zipfile
                        import io as _io
                        with _zipfile.ZipFile(cached_n2d, 'r') as zf:
                            names = zf.namelist()
                            if 'project.msgpack' in names:
                                raw = zf.read('project.msgpack')
                                n2d_json = msgpack.unpackb(raw, raw=False)
                                _tick(f"loaded from cache: {len(n2d_json.get('libraries', []))} libs")
                            elif 'project.json' in names:
                                raw = zf.read('project.json')
                                n2d_json = json.loads(raw)
                                _tick(f"loaded JSON from cache: {len(n2d_json.get('libraries', []))} libs")
                    except Exception as e:
                        _tick(f"cache load failed ({e}), reconverting...")
                        n2d_json = None

            if n2d_json is None:
                swf_data = open(swf_path, 'rb').read()
                _tick(f"read {len(swf_data):,} bytes from disk: {swf_path}")

                def progress_callback(msg):
                    _tick(msg)

                try:
                    n2d_json = _conversion_service.convert_swf_to_n2d(
                        swf_data,
                        name=name,
                        include_scripts=True,
                        embed_bitmaps=True,
                        progress_callback=progress_callback
                    )
                except ConversionError as e:
                    log.error(f'_handle_import_swf_path: conversion failed: {e}')
                    return self._error_response(500, f'SWF conversion failed: {e}')

                _tick(f"conversion complete: {len(n2d_json.get('libraries', []))} libs")

                mod = _get_swf_to_n2d()
                mod.save_project_folder(n2d_json, project_dir)
                _tick('save_project_folder')

            with self._project_lock:
                Next2FlashHandler._current_project_dir = project_dir

            # Heavy fields to strip for skeleton mode
            _HEAVY_FIELDS = ('buffer', 'recodes', 'rawTagBody')

            if lazy:
                # Build skeleton (first time — no cached skeleton existed)
                skeleton_cache = os.path.join(project_dir, 'skeleton.n2d')

                # Store full libraries server-side for on-demand loading
                with self._lazy_lock:
                    Next2FlashHandler._lazy_libraries.clear()
                    Next2FlashHandler._lazy_bulk_cache = None  # invalidate cache
                    for lib in n2d_json.get('libraries', []):
                        lib_id = lib.get('id')
                        if lib_id is not None:
                            Next2FlashHandler._lazy_libraries[int(lib_id)] = lib
                _tick(f"stored {len(Next2FlashHandler._lazy_libraries)} libs for lazy loading")

                # Build skeleton: libraries with only metadata, no heavy binary data
                skeleton_libs = []
                for lib in n2d_json.get('libraries', []):
                    skel = {}
                    for k, v in lib.items():
                        if k in _HEAVY_FIELDS:
                            continue
                        skel[k] = v
                    skel['_lazy'] = True
                    skeleton_libs.append(skel)

                skeleton = dict(n2d_json)
                skeleton['libraries'] = skeleton_libs
                _tick(f"skeleton built: {len(skeleton_libs)} libs (heavy fields stripped)")

                # Pack skeleton
                msgpack_data = msgpack.packb(skeleton, use_bin_type=True)
                _tick(f"skeleton msgpack: {len(msgpack_data):,} bytes")

                # ZIP it
                import zipfile as _zipfile
                import io as _io
                zip_buffer = _io.BytesIO()
                with _zipfile.ZipFile(zip_buffer, 'w', _zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                    zf.writestr('project.msgpack', msgpack_data)
                compressed = zip_buffer.getvalue()

                # Save skeleton cache for next time
                os.makedirs(project_dir, exist_ok=True)
                with open(skeleton_cache, 'wb') as f:
                    f.write(compressed)
                _tick(f"skeleton cached + ZIP: {len(compressed):,} bytes -> DONE")
            else:
                msgpack_data = msgpack.packb(n2d_json, use_bin_type=True)
                _tick(f"msgpack: {len(msgpack_data):,} bytes")

                import zipfile as _zipfile
                import io as _io
                zip_buffer = _io.BytesIO()
                with _zipfile.ZipFile(zip_buffer, 'w', _zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                    zf.writestr('project.msgpack', msgpack_data)
                compressed = zip_buffer.getvalue()
                _tick(f"ZIP: {len(compressed):,} bytes -> DONE")

            lib_count = len(n2d_json.get('libraries', [])) if n2d_json else 0
            script_count = len(n2d_json.get('scripts', [])) if n2d_json else 0

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{name}.n2d"')
            self.send_header('X-N2D-Name', name)
            self.send_header('X-N2D-Libraries', str(lib_count))
            self.send_header('X-N2D-Scripts', str(script_count))
            self.send_header('X-N2D-Format', 'msgpack')
            self.send_header('X-Project-Dir', project_dir)
            self.send_header('Content-Length', str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_import_swf_path: %s', e)
            self._error_response(500, f'SWF import from path failed: {e}')

    def _handle_lazy_library(self):
        """GET /api/lazy/library/<id> — Return full library data for on-demand loading.

        Returns the full library data (including heavy fields like buffer, recodes)
        as msgpack for a single library item, fetched from the server-side store.
        """
        try:
            # Extract library ID from URL path
            lib_id_str = self.path.rsplit('/', 1)[-1]
            try:
                lib_id = int(lib_id_str)
            except ValueError:
                return self._error_response(400, f'Invalid library ID: {lib_id_str}')

            with self._lazy_lock:
                lib_data = Next2FlashHandler._lazy_libraries.get(lib_id)

            if lib_data is None:
                return self._error_response(404, f'Library {lib_id} not found in lazy store')

            data = msgpack.packb(lib_data, use_bin_type=True)

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/x-msgpack')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_lazy_library: %s', e)
            self._error_response(500, str(e))

    def _handle_lazy_bulk(self):
        """GET /api/lazy/bulk — Return ALL lazy library data in a single msgpack response.

        Returns a dict mapping library_id (int) -> full library data.
        Uses a cached packed representation to avoid re-packing on every request.
        """
        try:
            with self._lazy_lock:
                libs = dict(Next2FlashHandler._lazy_libraries)
                cached_pack = getattr(Next2FlashHandler, '_lazy_bulk_cache', None)

            if not libs:
                # Try to load from cached N2D on disk
                with self._project_lock:
                    proj_dir = Next2FlashHandler._current_project_dir
                if proj_dir:
                    cached_n2d = os.path.join(proj_dir, 'project.n2d')
                    if os.path.isfile(cached_n2d):
                        import zipfile as _zipfile
                        _t0 = time.time()
                        with _zipfile.ZipFile(cached_n2d, 'r') as zf:
                            names = zf.namelist()
                            if 'project.msgpack' in names:
                                raw = zf.read('project.msgpack')
                                n2d_json = msgpack.unpackb(raw, raw=False)
                            elif 'project.json' in names:
                                raw = zf.read('project.json')
                                n2d_json = json.loads(raw)
                            else:
                                return self._error_response(404, 'No lazy libraries stored')
                        with self._lazy_lock:
                            Next2FlashHandler._lazy_libraries.clear()
                            for lib in n2d_json.get('libraries', []):
                                lib_id = lib.get('id')
                                if lib_id is not None:
                                    Next2FlashHandler._lazy_libraries[int(lib_id)] = lib
                            libs = dict(Next2FlashHandler._lazy_libraries)
                            Next2FlashHandler._lazy_bulk_cache = None  # invalidate
                            cached_pack = None
                        print(f'[LAZY-BULK] loaded {len(libs)} libs from disk in {time.time()-_t0:.2f}s', flush=True)

            if not libs:
                return self._error_response(404, 'No lazy libraries stored')

            # Use cached pack if available
            if cached_pack is not None:
                data = cached_pack
                print(f'[LAZY-BULK] served cached pack -> {len(data):,} bytes', flush=True)
            else:
                _t0 = time.time()
                data = msgpack.packb(libs, use_bin_type=True)
                elapsed = time.time() - _t0
                with self._lazy_lock:
                    Next2FlashHandler._lazy_bulk_cache = data
                print(f'[LAZY-BULK] packed {len(libs)} libs -> {len(data):,} bytes in {elapsed:.2f}s', flush=True)

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/x-msgpack')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()

            # Stream in chunks to avoid blocking
            CHUNK = 1024 * 1024  # 1MB chunks
            offset = 0
            while offset < len(data):
                self.wfile.write(data[offset:offset + CHUNK])
                offset += CHUNK

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_lazy_bulk: %s', e)
            self._error_response(500, str(e))

    def _handle_refresh_assets(self):
        """POST /api/refresh-assets — Re-read external assets from project folder.

        Re-reads PNG/WAV/MP3/AS files from the project folder and returns
        an updated N2D blob. This lets users edit bitmap/sound/script files
        externally and reload them without re-importing the SWF.
        """
        try:
            with self._project_lock:
                project_dir = Next2FlashHandler._current_project_dir

            if not project_dir or not os.path.isdir(project_dir):
                return self._error_response(400, "No project folder loaded. Import a SWF first.")

            mod = _get_swf_to_n2d()
            n2d_data, _ = __import__('compile_n2d').load_n2d(
                os.path.join(project_dir, 'project.n2d')
            )
            n2d_json = n2d_data

            # Re-read external script source files from disk
            scripts_refreshed = _read_scripts_from_disk(n2d_json, project_dir)

            # Re-read external bitmap files — use the same full pipeline as open-project:
            # Phase 1 (library entries) + Phase 2 (embedded fill dicts in shape recodes)
            _overlay_external_bitmaps(n2d_json, project_dir)
            bitmaps_refreshed = sum(
                1 for lib in n2d_json.get("libraries", [])
                if lib and lib.get("type") == "bitmap" and lib.get("externalFile")
                and os.path.isfile(os.path.join(project_dir, lib["externalFile"]))
            )

            # Re-read external sound files (MP3/WAV) → update rawTagBody
            sounds_refreshed = 0
            for lib in n2d_json.get("libraries", []):
                if not lib or lib.get("type") != "sound":
                    continue
                ext_file = lib.get("externalFile", "")
                if not ext_file:
                    continue
                fpath = os.path.join(project_dir, ext_file)
                if not os.path.isfile(fpath):
                    continue
                try:
                    with open(fpath, "rb") as af:
                        audio_bytes = af.read()
                    ext_lower = ext_file.lower()
                    if ext_lower.endswith(".mp3"):
                        compile_mod = _get_compile_n2d()
                        raw_body = compile_mod._build_mp3_sound_body(audio_bytes)
                        if raw_body:
                            lib["rawTagBody"] = base64.b64encode(raw_body).decode("ascii")
                            lib["rawTagType"] = 14  # DefineSound
                            sounds_refreshed += 1
                    elif ext_lower.endswith(".wav"):
                        compile_mod = _get_compile_n2d()
                        raw_body = compile_mod._build_wav_sound_body(audio_bytes)
                        if raw_body:
                            lib["rawTagBody"] = base64.b64encode(raw_body).decode("ascii")
                            lib["rawTagType"] = 14  # DefineSound
                            sounds_refreshed += 1
                except Exception as se:
                    print(f"[Refresh] WARN: could not refresh sound {ext_file}: {se}")

            name = n2d_json.get("name", os.path.basename(project_dir))
            print(f"[Refresh] {scripts_refreshed} scripts, {bitmaps_refreshed} bitmaps, {sounds_refreshed} sounds refreshed from {project_dir}")

            # Save refreshed data back to project.n2d so Export SWF picks it up
            try:
                mod = _get_swf_to_n2d()
                mod.save_n2d(n2d_json, os.path.join(project_dir, "project.n2d"))
            except Exception as save_err:
                print(f"[Refresh] WARN: could not save updated project.n2d: {save_err}")

            json_str = json.dumps(n2d_json, separators=(",", ":"), ensure_ascii=True)
            url_encoded = json_str.replace('%', '%25')
            compressed = zlib.compress(url_encoded.encode("ascii"), 1)

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
            self.send_header("X-N2D-Name", name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-Refreshed-Scripts", str(scripts_refreshed))
            self.send_header("X-Refreshed-Bitmaps", str(bitmaps_refreshed))
            self.send_header("X-Refreshed-Sounds", str(sounds_refreshed))
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_refresh_assets: failed: %s', e)
            self._error_response(500, f"Refresh assets failed: {e}")

    def _handle_n2d_to_swf(self):
        """POST /api/n2d-to-swf — Convert uploaded N2D back to SWF.
        
        Accepts either:
          - Multipart with fromProject=true → compile from existing project.n2d
          - Multipart with file upload → legacy browser-blob pipeline
        Returns: SWF file as application/octet-stream.
        """
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, "No data received")

            mod = _get_compile_n2d()

            with self._project_lock:
                project_dir = Next2FlashHandler._current_project_dir

            # Check if this is a "compile from project folder" request
            from_project = self._extract_form_field(body, "fromProject")
            if from_project and project_dir and os.path.isdir(project_dir):
                n2d_path = os.path.join(project_dir, "project.n2d")
                if not os.path.isfile(n2d_path):
                    return self._error_response(400, "No project.n2d in project folder")

                name = os.path.basename(project_dir)
                log.info('_handle_n2d_to_swf: compiling from project folder %s', project_dir)

                with tempfile.TemporaryDirectory() as tmpdir:
                    swf_path = os.path.join(tmpdir, f"{name}.swf")
                    shared_dir = os.path.join(SERVER_DIR, "..", "shared")
                    if not os.path.isdir(shared_dir):
                        shared_dir = tmpdir

                    compiler = mod.N2DCompiler(
                        n2d_path=n2d_path,
                        shared_dir=shared_dir,
                        output_path=swf_path,
                    )
                    print(f"[DEBUG] Compiling from project folder: {project_dir}")
                    print(f"[DEBUG] Compiler SDK path: {compiler.sdk_path}")
                    compiler.compile()

                    with open(swf_path, "rb") as f:
                        swf_bytes = f.read()

                    # Debug copies
                    debug_swf = os.path.join(SERVER_DIR, "converted", "_last_export.swf")
                    try:
                        with open(debug_swf, "wb") as df:
                            df.write(swf_bytes)
                        print(f"[DEBUG] Saved export SWF to {debug_swf} ({len(swf_bytes)} bytes)")
                    except Exception as de:
                        print(f"[DEBUG] Could not save debug SWF: {de}")

                    self.send_response(200)
                    self._cors_headers()
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Disposition", f'attachment; filename="{name}.swf"')
                    self.send_header("Content-Length", str(len(swf_bytes)))
                    self.end_headers()
                    self.wfile.write(swf_bytes)
                return

            # Legacy path: browser uploaded an N2D blob
            n2d_data, filename = self._extract_upload(body, "file")
            if not n2d_data:
                n2d_data = body
                filename = "project.n2d"

            name = os.path.splitext(filename)[0] if filename else "output"
            log.info('_handle_n2d_to_swf: compiling %s (%d bytes)', filename, len(n2d_data))

            # Write N2D to a temp file and use N2DCompiler
            with tempfile.TemporaryDirectory() as tmpdir:
                n2d_path = os.path.join(tmpdir, f"{name}.n2d")
                swf_path = os.path.join(tmpdir, f"{name}.swf")
                with open(n2d_path, "wb") as f:
                    f.write(n2d_data)
                shared_dir = os.path.join(SERVER_DIR, "..", "shared")
                if not os.path.isdir(shared_dir):
                    shared_dir = tmpdir  # fallback

                # Debug: save a copy of the N2D for inspection
                debug_n2d = os.path.join(SERVER_DIR, "converted", "_last_export.n2d")
                debug_swf = os.path.join(SERVER_DIR, "converted", "_last_export.swf")
                try:
                    with open(debug_n2d, "wb") as df:
                        df.write(n2d_data)
                    print(f"[DEBUG] Saved export N2D to {debug_n2d} ({len(n2d_data)} bytes)")
                except Exception as de:
                    print(f"[DEBUG] Could not save debug N2D: {de}")

                compiler = mod.N2DCompiler(
                    n2d_path=n2d_path,
                    shared_dir=shared_dir,
                    output_path=swf_path,
                )
                print(f"[DEBUG] Compiler SDK path: {compiler.sdk_path}")
                compiler.compile()
                print(f"[DEBUG] scriptsModified: {compiler.data.get('scriptsModified', False)}")

                with open(swf_path, "rb") as f:
                    swf_bytes = f.read()

                # Debug: also save a copy of the output SWF
                try:
                    with open(debug_swf, "wb") as df:
                        df.write(swf_bytes)
                    print(f"[DEBUG] Saved export SWF to {debug_swf} ({len(swf_bytes)} bytes)")
                except Exception as de:
                    print(f"[DEBUG] Could not save debug SWF: {de}")

                self.send_response(200)
                self._cors_headers()
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{name}.swf"')
                self.send_header("Content-Length", str(len(swf_bytes)))
                self.end_headers()
                self.wfile.write(swf_bytes)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_n2d_to_swf: compilation failed: %s', e)
            self._error_response(500, f"N2D->SWF compilation failed: {e}")

    def _handle_decompile_abc(self):
        """POST /api/decompile-abc — Decompile raw DoABC tag data to AS3 source."""
        log.debug('_handle_decompile_abc: entry')
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, "No data received")

            content_type = self.headers.get("Content-Type", "")
            if "json" in content_type:
                req = json.loads(body)
                # Expect {"tags": [{"tagType": 82, "body": "..."}, ...]}
                tags = req.get("tags", [])
            else:
                return self._error_response(400, "Expected JSON body")

            mod = _get_swf_to_n2d()
            # Handle both base64 and latin-1 encoded bodies
            raw_tags = []
            for t in tags:
                body_str = t["body"]
                try:
                    body_bytes = list(base64.b64decode(body_str))
                except Exception:
                    body_bytes = [ord(c) for c in body_str]
                raw_tags.append((t["tagType"], body_bytes))
            scripts, _frame_scripts = mod.decompile_all_scripts(raw_tags)

            self._json_response({"scripts": scripts, "count": len(scripts)})

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_decompile_abc: failed: %s', e)
            self._error_response(500, f"ABC decompilation failed: {e}")

    # ---------- Helpers ----------

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return b""
        return self.rfile.read(length)

    def _extract_form_field(self, body: bytes, field_name: str):
        """Extract a simple (non-file) form field value from multipart/form-data."""
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return None
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                boundary = part[9:].strip('"')
                break
        else:
            return None
        boundary_bytes = f"--{boundary}".encode()
        parts = body.split(boundary_bytes)
        needle = f'name="{field_name}"'.encode()
        for part in parts:
            if needle not in part:
                continue
            # Skip parts that also have a filename (those are file uploads)
            if b"filename=" in part:
                continue
            header_end = part.find(b"\r\n\r\n")
            if header_end < 0:
                continue
            value = part[header_end + 4:]
            if value.endswith(b"\r\n"):
                value = value[:-2]
            if value.endswith(b"--"):
                value = value[:-2]
            if value.endswith(b"\r\n"):
                value = value[:-2]
            return value.decode("utf-8", errors="replace").strip()
        return None

    def _extract_upload(self, body: bytes, field_name: str):
        """Try to extract a file from multipart/form-data. Returns (data, filename) or (None, None)."""
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return None, None

        # Parse boundary
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                boundary = part[9:].strip('"')
                break
        else:
            return None, None

        boundary_bytes = f"--{boundary}".encode()
        parts = body.split(boundary_bytes)

        for part in parts:
            if field_name.encode() not in part:
                continue

            # Find the filename
            filename = None
            header_end = part.find(b"\r\n\r\n")
            if header_end < 0:
                continue
            header = part[:header_end].decode("utf-8", errors="replace")
            for line in header.split("\r\n"):
                if "filename=" in line:
                    start = line.index('filename="') + 10
                    end = line.index('"', start)
                    filename = line[start:end]
                    break

            file_data = part[header_end + 4:]
            # Strip trailing \r\n-- if present
            if file_data.endswith(b"\r\n"):
                file_data = file_data[:-2]
            if file_data.endswith(b"--"):
                file_data = file_data[:-2]
            if file_data.endswith(b"\r\n"):
                file_data = file_data[:-2]

            return file_data, filename

        return None, None

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Requested-With")
        self.send_header("Access-Control-Expose-Headers",
                         "X-N2D-Name, X-N2D-Libraries, X-N2D-Scripts, X-Project-Dir, X-Refreshed-Scripts, X-Refreshed-Bitmaps, X-Refreshed-Sounds")

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error_response(self, status, message):
        self._json_response({"error": message}, status)

    def _has_as3_decompiler(self):
        try:
            import as3_decompiler
            return True
        except ImportError:
            return False

    def _build_sidecar(self, n2d_json):
        """Build sidecar metadata dictionary."""
        sidecar = {}
        rt_fields = ("rawTagBody", "rawTagType", "swfCharId",
                      "inBitmap", "grid", "bitmapId")
        lib_meta = {}
        for lib in n2d_json.get("libraries", []):
            meta = {}
            for f in rt_fields:
                if f in lib:
                    meta[f] = lib[f]
            if meta:
                lib_meta[str(lib["id"])] = meta
        if lib_meta:
            sidecar["libraries"] = lib_meta

        for key in ("rawGlobalTags", "swfVersion", "swfCompressed",
                     "rootTimelineDefIds", "characterId", "scripts"):
            if key in n2d_json:
                sidecar[key] = n2d_json[key]

        return sidecar

    def log_message(self, format, *args):
        """Custom log format."""
        try:
            msg = str(args[0]) if args else ""
        except Exception:
            msg = ""
        if "/api/" in msg:
            sys.stderr.write(f"[Next2Flash] {msg}\n")
        elif msg and not any(ext in msg for ext in ('.js ', '.css ', '.html ', '.png ', '.jpg ', '.ico ', '.svg ', '.woff')):
            sys.stderr.write(f"[Next2Flash] {msg}\n")
        # Suppress static file logs for cleanliness


# ---------------------------------------------------------------------------
#  Server startup
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Next2Flash - SWF/N2D Animation Tool")
    default_port = int(os.environ.get('N2F_PORT', '5000'))
    parser.add_argument("--port", type=int, default=default_port, help="Port to listen on (default: 5000)")
    # Auto-disable browser when launched by Electron
    is_electron = os.environ.get('N2F_ELECTRON') == '1'
    parser.add_argument("--no-browser", action="store_true", default=is_electron, help="Don't auto-open browser")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug logging (WARNING+ only)")
    args = parser.parse_args()

    # ── Configure logging so log.debug() etc. actually print to terminal ──
    # Default is DEBUG so user sees everything; use --quiet to suppress
    log_level = logging.WARNING if args.quiet else logging.DEBUG
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout,
    )
    # Also set for all our modules
    for mod_name in ('server', 'swf_to_n2d', 'compile_n2d', 'swf_writer',
                     'shape_converter', 'bitmap_converter', 'text_converter',
                     'swf_shape_to_recodes', 'as3_decompiler'):
        logging.getLogger(mod_name).setLevel(log_level)
    # Suppress verbose third-party debug output
    logging.getLogger('PIL').setLevel(logging.WARNING)
    log.info('Logging initialized at %s level', logging.getLevelName(log_level))

    # Verify app directory exists
    if not os.path.isdir(APP_DIR):
        print(f"Error: App directory not found: {APP_DIR}")
        print("Make sure index.html is next to server.py")
        return 1

    if not os.path.isfile(os.path.join(APP_DIR, "index.html")):
        print(f"Error: index.html not found in {APP_DIR}")
        return 1

    class ThreadedServer(ThreadingMixIn, HTTPServer):
        daemon_threads = True
    server = ThreadedServer((args.host, args.port), Next2FlashHandler)
    url = f"http://{args.host}:{args.port}"
    log.info('main: starting server at %s', url)

    print(r"""
    _   _           _   ____  _____ _           _
   | \ | | _____  _| |_|___ \|  ___| | __ _ ___| |__
   |  \| |/ _ \ \/ / __| __) | |_  | |/ _` / __| '_ \
   | |\  |  __/>  <| |_ / __/|  _| | | (_| \__ \ | | |
   |_| \_|\___/_/\_\\__|_____|_|   |_|\__,_|___/_| |_|
    """)
    print(f"  Server running at {url}")
    print(f"  Serving app from: {APP_DIR}")
    print()
    print(f"  API endpoints:")
    print(f"    POST /api/swf-to-n2d    - Convert SWF to N2D")
    print(f"    POST /api/n2d-to-swf    - Convert N2D to SWF")
    print(f"    POST /api/decompile-abc - Decompile ABC bytecode")
    print(f"    GET  /api/health        - Health check")
    print(f"    GET  /api/capabilities  - Available features")
    print()

    print(f"  Press Ctrl+C to stop.")
    print()

    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('main: shutting down server')
        print("\n[Next2Flash] Shutting down...")
        server.shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(main())
