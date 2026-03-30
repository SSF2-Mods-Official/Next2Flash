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

# Lazy-import converters (fail gracefully with clear messages)
_swf_to_n2d = None
_compile_n2d = None

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
                old_list = list(orig_buf.encode('latin-1'))
                fp = _fingerprint(old_list)
            else:
                fp = None

            img  = Image.open(fpath).convert("RGBA")
            rgba = img.tobytes()
            new_list = list(rgba)

            # Update library entry
            lib["buffer"] = rgba.decode('latin-1')
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
        elif self.path.startswith("/api/lazy/asset/"):
            self._handle_lazy_asset()
        elif self.path == "/api/autoload":
            self._handle_autoload()
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
        elif self.path == "/api/swf-to-project-fast":
            self._handle_swf_to_project_fast()
        elif self.path == "/api/lazy/hydrate":
            self._handle_lazy_hydrate()
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

            name = os.path.splitext(filename)[0] if filename else "converted"
            log.info('_handle_swf_to_n2d: converting %s (%d bytes)', filename, len(swf_data))
            # .ssf is just .swf with a different extension
            if filename and filename.lower().endswith(('.ssf', '.swf')):
                pass  # valid SWF-compatible format

            mod = _get_swf_to_n2d()

            # Parse and convert
            header, tags = mod.parse_swf(swf_data)
            builder = mod.N2DBuilder(header, name=name)
            builder.catalog_swf_tags(tags)

            # Single-pass ABC decompilation: scripts + frame scripts
            scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
            builder.frame_scripts = frame_scripts
            if scripts:
                builder.scripts.extend(scripts)

            builder.build_all()
            builder.build_main_timeline(tags)
            builder._embed_bitmap_data_in_recodes()

            n2d_json = builder.to_n2d_json()

            # Compress to zlib format (native N2D format the tool expects).
            # The tool's save pipeline: JSON → encodeURIComponent → zlib deflate.
            # The load pipeline: zlib inflate → String.fromCharCode → decodeURIComponent → JSON.
            # So we must URL-encode the JSON before compressing.
            json_str = json.dumps(n2d_json, separators=(",", ":"), ensure_ascii=True)
            url_encoded = quote(json_str, safe="")
            compressed = zlib.compress(url_encoded.encode("ascii"), 1)

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
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_swf_to_n2d: conversion failed: %s', e)
            self._error_response(500, f"SWF->N2D conversion failed: {e}")

    # ── Project folder persistent path ──
    _current_project_dir = None
    _project_lock = threading.Lock()

    def _handle_swf_to_project(self):
        """POST /api/swf-to-project — Import SWF into an editable project folder.

        Extracts bitmaps as PNG/JPG, sounds as MP3/WAV, scripts as .as files.
        Returns the N2D zlib blob for loading into the tool, plus sets the
        project directory for subsequent refresh/export operations.
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

            _tick(f"start — {len(swf_data):,} bytes")

            mod = _get_swf_to_n2d()

            header, tags = mod.parse_swf(swf_data)
            _tick(f"parse_swf: {len(tags)} tags")

            builder = mod.N2DBuilder(header, name=name)
            builder.catalog_swf_tags(tags)
            _tick(f"catalog_swf_tags: {len(builder.char_types)} chars, "
                  f"{len(builder.global_raw_tags)} raw tags")

            scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
            builder.frame_scripts = frame_scripts
            if scripts:
                builder.scripts.extend(scripts)
            _tick(f"decompile_all_scripts: {len(scripts)} scripts, "
                  f"{len(frame_scripts)} frames with scripts")

            builder.build_all()
            _tick("build_all")

            builder.build_main_timeline(tags)
            _tick("build_main_timeline")

            builder._embed_bitmap_data_in_recodes()
            _tick("_embed_bitmap_data_in_recodes")

            n2d_json = builder.to_n2d_json()
            _tick(f"to_n2d_json: {len(n2d_json.get('libraries', []))} libs")

            # Save as project folder
            project_dir = os.path.join(SERVER_DIR, "converted", name)
            mod.save_project_folder(n2d_json, project_dir)
            _tick("save_project_folder")

            with self._project_lock:
                Next2FlashHandler._current_project_dir = project_dir

            # Return zlib-compressed N2D for loading into the tool.
            # Tool pipeline: zlib inflate → decodeURIComponent → JSON.parse.
            # Only % needs encoding (%25); full quote() is ~100x slower for no benefit.
            json_str = json.dumps(n2d_json, separators=(",", ":"), ensure_ascii=True)
            _tick(f"json.dumps: {len(json_str):,} chars")
            url_encoded = json_str.replace('%', '%25')
            compressed = zlib.compress(url_encoded.encode("ascii"), 1)
            _tick(f"zlib.compress: {len(compressed):,} bytes → DONE")

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
            self.send_header("X-N2D-Name", name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-N2D-Scripts", str(len(n2d_json.get("scripts", []))))
            self.send_header("X-Project-Dir", project_dir)
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_swf_to_project: failed: %s', e)
            self._error_response(500, f"SWF->Project conversion failed: {e}")

    # ── Pending SWF data for lazy hydration ──
    _pending_swf_data = None      # raw SWF bytes
    _pending_swf_name = None      # project name
    _pending_swf_lock = threading.Lock()
    _pending_builder  = None      # cached N2DBuilder after catalog

    # ── Autoload data (set by --load CLI flag) ──
    _autoload_blob  = None        # compressed N2D bytes ready to serve
    _autoload_name  = None        # project name
    _autoload_libs  = 0           # library count
    _autoload_scripts = 0         # script count

    def _handle_swf_to_project_fast(self):
        """POST /api/swf-to-project-fast — Instant skeleton SWF import.

        Parses SWF structure and timelines only — NO bitmap/shape/sound decoding.
        All heavy assets are marked lazy. The editor fetches decoded data
        on-demand via /api/lazy/asset/<charId> when assets are first rendered.

        Stores the raw SWF + cached builder for lazy asset decoding.
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
            log.info('_handle_swf_to_project_fast: %s (%d bytes)', filename, len(swf_data))

            _t0 = time.time()
            def _tick(label):
                print(f"[FAST-IMPORT {time.time()-_t0:6.2f}s] {label}", flush=True)

            _tick(f"start — {len(swf_data):,} bytes")

            mod = _get_swf_to_n2d()

            header, tags = mod.parse_swf(swf_data)
            _tick(f"parse_swf: {len(tags)} tags")

            builder = mod.N2DBuilder(header, name=name)
            builder.catalog_swf_tags(tags)
            _tick(f"catalog: {len(builder.char_types)} chars")

            # Decompile scripts — needed for frame scripts on main timeline
            scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
            builder.frame_scripts = frame_scripts
            if scripts:
                builder.scripts.extend(scripts)
            _tick(f"decompile: {len(scripts)} scripts")

            # Skeleton build: metadata only, all heavy assets lazy
            builder.build_skeleton(tags)
            _tick("build_skeleton")

            builder.build_main_timeline(tags)
            _tick("build_main_timeline")

            n2d_json = builder.to_n2d_json()
            _tick(f"to_n2d_json: {len(n2d_json.get('libraries', []))} libs")

            # Save minimal project folder (scripts only, no bitmap/sound files)
            project_dir = os.path.join(SERVER_DIR, "converted", name)
            mod.save_project_folder(n2d_json, project_dir)
            _tick("save_project_folder")

            with self._project_lock:
                Next2FlashHandler._current_project_dir = project_dir

            # Store raw SWF + builder for lazy asset decoding
            with self._pending_swf_lock:
                Next2FlashHandler._pending_swf_data = swf_data
                Next2FlashHandler._pending_swf_name = name
                Next2FlashHandler._pending_builder = builder

            # Return compressed N2D
            json_str = json.dumps(n2d_json, separators=(",", ":"), ensure_ascii=True)
            url_encoded = json_str.replace('%', '%25')
            compressed = zlib.compress(url_encoded.encode("ascii"), 1)
            _tick(f"compressed: {len(compressed):,} bytes — DONE")

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
            self.send_header("X-N2D-Name", name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-N2D-Scripts", str(len(n2d_json.get("scripts", []))))
            self.send_header("X-Project-Dir", project_dir)
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_swf_to_project_fast: failed: %s', e)
            self._error_response(500, f"Fast SWF import failed: {e}")

    def _handle_lazy_hydrate(self):
        """POST /api/lazy/hydrate — Full conversion of the pending SWF.

        Called at save/export time to fully decode ALL assets (including
        those that were lazy stubs during priority import). Re-creates
        the project folder with complete data.

        Returns the fully-hydrated N2D blob.
        """
        try:
            with self._pending_swf_lock:
                swf_data = Next2FlashHandler._pending_swf_data
                name = Next2FlashHandler._pending_swf_name

            if not swf_data:
                return self._error_response(400, "No pending SWF — call /api/swf-to-project-fast first")

            log.info('_handle_lazy_hydrate: hydrating %s (%d bytes)', name, len(swf_data))

            _t0 = time.time()
            def _tick(label):
                print(f"[HYDRATE {time.time()-_t0:6.2f}s] {label}", flush=True)

            _tick(f"start")

            mod = _get_swf_to_n2d()

            header, tags = mod.parse_swf(swf_data)
            _tick(f"parse_swf: {len(tags)} tags")

            builder = mod.N2DBuilder(header, name=name)
            builder.catalog_swf_tags(tags)
            _tick(f"catalog: {len(builder.char_types)} chars")

            scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
            builder.frame_scripts = frame_scripts
            if scripts:
                builder.scripts.extend(scripts)
            _tick(f"decompile: {len(scripts)} scripts")

            builder.build_all()
            _tick("build_all")

            builder.build_main_timeline(tags)
            _tick("build_main_timeline")

            builder._embed_bitmap_data_in_recodes()
            _tick("embed_bitmaps")

            n2d_json = builder.to_n2d_json()
            _tick(f"to_n2d_json: {len(n2d_json.get('libraries', []))} libs")

            # Save project folder
            project_dir = os.path.join(SERVER_DIR, "converted", name)
            mod.save_project_folder(n2d_json, project_dir)
            _tick("save_project_folder")

            with self._project_lock:
                Next2FlashHandler._current_project_dir = project_dir

            # Clear pending SWF to free memory
            with self._pending_swf_lock:
                Next2FlashHandler._pending_swf_data = None
                Next2FlashHandler._pending_swf_name = None

            # Return compressed full N2D
            json_str = json.dumps(n2d_json, separators=(",", ":"), ensure_ascii=True)
            url_encoded = json_str.replace('%', '%25')
            compressed = zlib.compress(url_encoded.encode("ascii"), 1)
            _tick(f"compressed: {len(compressed):,} bytes — DONE")

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
            self.send_header("X-N2D-Name", name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-N2D-Scripts", str(len(n2d_json.get("scripts", []))))
            self.send_header("X-Project-Dir", project_dir)
            self.send_header("Content-Length", str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_lazy_hydrate: failed: %s', e)
            self._error_response(500, f"Hydration failed: {e}")

    def _handle_lazy_asset(self):
        """GET /api/lazy/asset/<swfCharId> — Decode a single asset on demand.

        Returns JSON with the decoded asset data (bitmap RGBA, shape recodes,
        or sound audio bytes). Used by the editor's lazy loading system.
        """
        try:
            # Extract character ID from URL
            char_id_str = self.path.rsplit('/', 1)[-1]
            char_id = int(char_id_str)

            with self._pending_swf_lock:
                swf_data = Next2FlashHandler._pending_swf_data
                builder = Next2FlashHandler._pending_builder

            if not swf_data:
                return self._error_response(400, "No pending SWF data")

            mod = _get_swf_to_n2d()

            # Re-use cached builder or create and cache one
            if builder is None:
                header, tags = mod.parse_swf(swf_data)
                builder = mod.N2DBuilder(header, name=Next2FlashHandler._pending_swf_name or 'lazy')
                builder.catalog_swf_tags(tags)
                with self._pending_swf_lock:
                    Next2FlashHandler._pending_builder = builder

            char_type = builder.char_types.get(char_id)
            if not char_type:
                return self._error_response(404, f"Character {char_id} not found")

            result = {'type': char_type}

            if char_type == 'bitmap':
                if char_id in builder.raw_tag_data:
                    tag_type, body = builder.raw_tag_data[char_id]
                    width, height = builder.bitmap_dims.get(char_id, (0, 0))
                    rgba = b''
                    TAG_DEFINE_BITS_LOSSLESS = 20
                    TAG_DEFINE_BITS_LOSSLESS2 = 36
                    TAG_DEFINE_BITS = 6
                    TAG_DEFINE_BITS_JPEG2 = 21
                    TAG_DEFINE_BITS_JPEG3 = 35
                    TAG_DEFINE_BITS_JPEG4 = 90
                    if tag_type in (TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2):
                        dw, dh, rgba = mod.decode_lossless_to_rgba(tag_type, body)
                        if dw and dh:
                            width, height = dw, dh
                    elif tag_type in (TAG_DEFINE_BITS, TAG_DEFINE_BITS_JPEG2,
                                      TAG_DEFINE_BITS_JPEG3, TAG_DEFINE_BITS_JPEG4):
                        dw, dh, rgba = mod.decode_jpeg_to_rgba(tag_type, b'\x00\x00' + body)
                        if dw and dh:
                            width, height = dw, dh
                    if rgba:
                        _MAX_TEX = 4096
                        if width > _MAX_TEX or height > _MAX_TEX:
                            from PIL import Image as _PilImage
                            scale = min(_MAX_TEX / width, _MAX_TEX / height)
                            new_w = max(1, int(width * scale))
                            new_h = max(1, int(height * scale))
                            img = _PilImage.frombytes('RGBA', (width, height), rgba)
                            img = img.resize((new_w, new_h), _PilImage.LANCZOS)
                            rgba = img.tobytes()
                            width, height = new_w, new_h
                        result['buffer'] = base64.b64encode(rgba).decode('ascii')
                    result['width'] = width
                    result['height'] = height

            elif char_type == 'shape':
                if char_id in builder.raw_tag_data:
                    tag_type, body = builder.raw_tag_data[char_id]
                    from swf_shape_to_recodes import parse_define_shape_to_recodes
                    # Build bitmap_id_map for shape parsing
                    bitmap_id_map = {}
                    for cid in builder.char_types:
                        if builder.char_types[cid] == 'bitmap':
                            bitmap_id_map[cid] = builder.swf_to_n2d.get(cid, 0)
                    try:
                        recodes, parsed_bounds, has_bitmap_fill = \
                            parse_define_shape_to_recodes(tag_type, bytes(body), bitmap_id_map)
                        if recodes and isinstance(recodes[-1], bool):
                            recodes.pop()
                        result['recodes'] = recodes
                        if parsed_bounds:
                            result['bounds'] = parsed_bounds
                        result['inBitmap'] = has_bitmap_fill

                        # If shape uses a bitmap fill, include that bitmap's data
                        if has_bitmap_fill:
                            for cid, n2d_id in bitmap_id_map.items():
                                # Check if this bitmap is referenced in recodes
                                if n2d_id in recodes and cid in builder.raw_tag_data:
                                    result['bitmapId'] = n2d_id
                                    bt, bb = builder.raw_tag_data[cid]
                                    bw, bh = builder.bitmap_dims.get(cid, (0, 0))
                                    brgba = b''
                                    if bt in (20, 36):
                                        dw, dh, brgba = mod.decode_lossless_to_rgba(bt, bb)
                                        if dw and dh: bw, bh = dw, dh
                                    elif bt in (6, 21, 35, 90):
                                        dw, dh, brgba = mod.decode_jpeg_to_rgba(bt, b'\x00\x00' + bb)
                                        if dw and dh: bw, bh = dw, dh
                                    if brgba:
                                        result['bitmapData'] = {
                                            'type': 'bitmap',
                                            'buffer': base64.b64encode(brgba).decode('ascii'),
                                            'width': bw, 'height': bh
                                        }
                                    break
                    except Exception as e:
                        log.warning('lazy asset shape %d parse failed: %s', char_id, e)
                        result['recodes'] = []

            elif char_type == 'sound':
                if char_id in builder.raw_tag_data:
                    tag_type, body = builder.raw_tag_data[char_id]
                    fmt_name, audio_bytes, swf_rate = mod.extract_sound_buffer(body)
                    if fmt_name == 'nellymoser' and audio_bytes:
                        try:
                            mp3 = mod.convert_nellymoser_to_mp3(audio_bytes, swf_rate)
                            if mp3:
                                audio_bytes = mp3
                        except Exception:
                            pass
                    if audio_bytes:
                        result['buffer'] = base64.b64encode(
                            audio_bytes if isinstance(audio_bytes, (bytes, bytearray))
                            else bytes(audio_bytes)
                        ).decode('ascii')

            self._json_response(result)

        except ValueError:
            self._error_response(400, "Invalid character ID")
        except Exception as e:
            traceback.print_exc()
            log.error('_handle_lazy_asset: failed: %s', e)
            self._error_response(500, f"Lazy asset decode failed: {e}")

    def _handle_autoload(self):
        """GET /api/autoload — Return pre-loaded N2D data if --load was used."""
        blob = Next2FlashHandler._autoload_blob
        if not blob:
            self._json_response({"available": False})
            return
        name = Next2FlashHandler._autoload_name or "autoload"
        self.send_response(200)
        self._cors_headers()
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
        self.send_header("X-N2D-Name", name)
        self.send_header("X-N2D-Libraries", str(Next2FlashHandler._autoload_libs))
        self.send_header("X-N2D-Scripts", str(Next2FlashHandler._autoload_scripts))
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

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

            # Parse the .n2d to get JSON (ZIP or zlib format)
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
                return self._error_response(409, 'No project loaded — import a SWF first')

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
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug logging (WARNING+ only)")
    parser.add_argument("--load", metavar="FILE", help="Auto-load an SWF or N2D file on startup (browser will open and import it)")
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
    print(f"    GET  /api/autoload      - Auto-load file (--load)")
    print()

    # ── Pre-load file if --load specified ──
    if args.load:
        load_path = os.path.abspath(args.load)
        if not os.path.isfile(load_path):
            print(f"  Error: --load file not found: {load_path}")
            return 1
        ext = os.path.splitext(load_path)[1].lower()
        name = os.path.splitext(os.path.basename(load_path))[0]
        print(f"  Auto-loading: {load_path}")
        try:
            with open(load_path, 'rb') as f:
                file_data = f.read()
            if ext == '.swf':
                mod = _get_swf_to_n2d()
                header, tags = mod.parse_swf(file_data)
                builder = mod.N2DBuilder(header, name=name)
                builder.catalog_swf_tags(tags)
                scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
                builder.frame_scripts = frame_scripts
                if scripts:
                    builder.scripts.extend(scripts)
                builder.build_skeleton(tags)
                builder.build_main_timeline(tags)
                n2d_json = builder.to_n2d_json()
                project_dir = os.path.join(SERVER_DIR, "converted", name)
                mod.save_project_folder(n2d_json, project_dir)
                Next2FlashHandler._pending_swf_data = file_data
                Next2FlashHandler._pending_swf_name = name
                Next2FlashHandler._pending_builder = builder
                Next2FlashHandler._current_project_dir = project_dir
                json_str = json.dumps(n2d_json, separators=(",", ":"), ensure_ascii=True)
                url_encoded = json_str.replace('%', '%25')
                compressed = zlib.compress(url_encoded.encode("ascii"), 1)
                Next2FlashHandler._autoload_blob = compressed
                Next2FlashHandler._autoload_name = name
                Next2FlashHandler._autoload_libs = len(n2d_json.get("libraries", []))
                Next2FlashHandler._autoload_scripts = len(n2d_json.get("scripts", []))
                print(f"  Pre-loaded SWF: {name} ({len(n2d_json.get('libraries', []))} libraries)")
            elif ext == '.n2d':
                Next2FlashHandler._autoload_blob = file_data
                Next2FlashHandler._autoload_name = name
                print(f"  Pre-loaded N2D: {name} ({len(file_data):,} bytes)")
            else:
                print(f"  Error: --load only supports .swf and .n2d files")
                return 1
        except Exception as e:
            print(f"  Error pre-loading {load_path}: {e}")
            traceback.print_exc()
            return 1

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
