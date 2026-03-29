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
        elif self.path == "/api/decompile-abc":
            self._handle_decompile_abc()
        elif self.path == "/api/log":
            self._handle_client_log()
        elif self.path == "/api/profile":
            self._handle_profile_log()
        elif self.path == "/api/test-report":
            self._handle_test_report()
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

    def _handle_n2d_to_swf(self):
        """POST /api/n2d-to-swf — Convert uploaded N2D back to SWF.
        
        Accepts: N2D file bytes (zlib-compressed).
        Returns: SWF file as application/octet-stream.
        """
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, "No data received")

            n2d_data, filename = self._extract_upload(body, "file")
            if not n2d_data:
                n2d_data = body
                filename = "project.n2d"

            name = os.path.splitext(filename)[0] if filename else "output"
            log.info('_handle_n2d_to_swf: compiling %s (%d bytes)', filename, len(n2d_data))

            mod = _get_compile_n2d()

            # Write N2D to a temp file and use N2DCompiler
            with tempfile.TemporaryDirectory() as tmpdir:
                n2d_path = os.path.join(tmpdir, f"{name}.n2d")
                swf_path = os.path.join(tmpdir, f"{name}.swf")
                shared_dir = os.path.join(SERVER_DIR, "..", "shared")
                if not os.path.isdir(shared_dir):
                    shared_dir = tmpdir  # fallback

                with open(n2d_path, "wb") as f:
                    f.write(n2d_data)

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
                         "X-N2D-Name, X-N2D-Libraries, X-N2D-Scripts")

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
