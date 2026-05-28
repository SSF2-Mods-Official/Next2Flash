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
import sys as _sys
# Force UTF-8 on Windows stdout/stderr so non-ASCII progress messages
# (e.g. the × in "width×height") don't crash on non-Latin codepages.
if hasattr(_sys.stdout, 'reconfigure'):
    _sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(_sys.stderr, 'reconfigure'):
    _sys.stderr.reconfigure(encoding='utf-8', errors='replace')
sys = _sys  # keep the bare 'sys' name available for the rest of the module
import shutil
import struct
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
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller-bundled exe.
    # Electron sets cwd to resources/app/ (contains index.html, assets/, etc.)
    # and also passes N2F_WEB_ROOT for safety. __file__ would be sys._MEIPASS
    # which only has the extracted Python runtime — NOT the web files.
    SERVER_DIR = os.environ.get('N2F_WEB_ROOT', os.getcwd())
else:
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

def _enumerate_system_fonts():
    """Scan system font directories and return a list of available fonts.

    Returns list of dicts: [{name, path, style}, ...]
    Grouped by family — picks Regular style where possible.
    """
    import glob

    font_dirs = []
    if os.name == 'nt':
        font_dirs.append(os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts'))
        local_fonts = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
        if os.path.isdir(local_fonts):
            font_dirs.append(local_fonts)
    else:
        for d in ['/usr/share/fonts', '/usr/local/share/fonts',
                  os.path.expanduser('~/.fonts'),
                  os.path.expanduser('~/.local/share/fonts')]:
            if os.path.isdir(d):
                font_dirs.append(d)

    # Collect all TTF/OTF files
    ttf_files = []
    for fd in font_dirs:
        ttf_files.extend(glob.glob(os.path.join(fd, '**', '*.ttf'), recursive=True))
        ttf_files.extend(glob.glob(os.path.join(fd, '**', '*.otf'), recursive=True))

    # Read font metadata with fontTools
    families = {}  # family_name → {path, style, bold, italic}
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        log.warning('fontTools not installed — system font enumeration unavailable')
        return []

    for fp in ttf_files:
        try:
            font = TTFont(fp, fontNumber=0)
            name_table = font['name']
            family = name_table.getBestFamilyName()
            sub_family = name_table.getBestSubFamilyName() or 'Regular'
            font.close()
            if not family:
                continue
            # Prefer Regular style; skip duplicates
            if family not in families or sub_family.lower() == 'regular':
                families[family] = {'name': family, 'path': fp, 'style': sub_family}
        except Exception:
            continue

    result = sorted(families.values(), key=lambda f: f['name'].lower())
    log.info('_enumerate_system_fonts: found %d font families', len(result))
    return result


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
    positions, filters, names etc. but lacks scripts, rawGlobalTags,
    rootTimelineDefIds.  The disk data has all of those.

    Strategy: For each library, take editor's non-roundtrip fields
    (placeObjects, timeline changes, etc.) and overlay them onto disk,
    keeping disk's asset data fields intact.
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
    bitmap_dims_changed = False
    for elib in editor_libs:
        if not elib:
            continue
        lib_id = elib.get('id')
        dlib = disk_map.get(lib_id)
        if not dlib:
            # New library added in editor — use as-is
            disk_libs.append(elib)
            continue

        # Preserve asset/roundtrip fields from disk that the editor doesn't carry.
        # MovieClip.toObject() omits totalFrame (computed getter) — without it
        # the compiler falls back to _compute_total_frames() which works, but
        # can miss trailing empty frames.  Morph shapes need endRecodes/endBounds
        # for the interpolation end-state.  rawSoundBody / rawSoundStreamHead
        # are raw binary blobs the editor never touches.
        roundtrip_keys = ('swfCharId',
                          'externalFile',
                          'fontData', 'fontTagType', 'fontFaceName',
                          'buttonData', 'binaryDataBody', 'soundFormat',
                          'isBinaryData', 'isFont', 'isButton', 'isMorphShape',
                          'fontAuxParsed', # structured font-aux data (align zones, CSM, name)
                          'buffer',        # bitmap/sound pixel data (absent in light-mode editor blobs)
                          'buttonTrackAsMenu',  # SWF button track-as-menu flag
                          'buttonActions',      # SWF ButtonCondActions (ActionScript)
                          'totalFrame',    # MovieClip frame count (computed getter, not serialized)
                          'endRecodes',    # morph shape end-state drawing commands
                          'endBounds',     # morph shape end-state bounds
                          'rawTagType',    # original SWF tag type (for metadata)
                          'soundStreamParsed', # SoundStreamHead2 inside sprites
                          'rawBitmapFormat',   # original LL2 format byte (3 or 5)
                          )
        saved = {}
        for k in roundtrip_keys:
            if k in dlib:
                saved[k] = dlib[k]

        # Track bitmap dimension changes. If an exported symbol class extends
        # BitmapData, constructor defaults must be regenerated when width/height
        # changes; raw DoABC passthrough would keep stale dimensions.
        old_w = dlib.get('width')
        old_h = dlib.get('height')
        is_bitmap_symbol = (
            dlib.get('type') == 'bitmap' and
            bool(dlib.get('symbol'))
        )

        # Save swfDepth per-layer by name so we can restore it after the merge.
        # Layer.toObject() does not include swfDepth, so it's lost otherwise,
        # causing layer depths to be reassigned sequentially on the next compile.
        # Also save per-character reinstated flags (the editor doesn't serialize them).
        disk_layer_depths: dict = {}
        disk_layer_char_reinstated: dict = {}  # layer_name → [bool, ...]
        for dl in dlib.get('layers', []):
            lname = dl.get('name')
            if lname and 'swfDepth' in dl:
                disk_layer_depths[lname] = dl['swfDepth']
            if lname:
                ri_flags = []
                has_any = False
                for ch in dl.get('characters', []):
                    ri = ch.get('reinstated')
                    ri_flags.append(ri)
                    if ri:
                        has_any = True
                if has_any:
                    disk_layer_char_reinstated[lname] = ri_flags

        # Take all fields from editor (has updated positions etc.)
        dlib.clear()
        dlib.update(elib)

        # Restore roundtrip fields
        for k, v in saved.items():
            if k not in dlib or not dlib[k]:
                dlib[k] = v

        if is_bitmap_symbol:
            new_w = dlib.get('width')
            new_h = dlib.get('height')
            if old_w != new_w or old_h != new_h:
                bitmap_dims_changed = True

        # Restore swfDepth on layers that match by name (existing layers).
        # New layers (e.g. a freshly drawn pencil shape layer) won't match and
        # will fall back to sequential depth assignment at compile time.
        if disk_layer_depths or disk_layer_char_reinstated:
            for el in dlib.get('layers', []):
                lname = el.get('name')
                if not lname:
                    continue
                if lname in disk_layer_depths and 'swfDepth' not in el:
                    el['swfDepth'] = disk_layer_depths[lname]
                # Restore reinstated flags on characters by index
                ri_flags = disk_layer_char_reinstated.get(lname)
                if ri_flags:
                    chars = el.get('characters', [])
                    if len(chars) == len(ri_flags):
                        for ci, ri in enumerate(ri_flags):
                            if ri and 'reinstated' not in chars[ci]:
                                chars[ci]['reinstated'] = ri

    if bitmap_dims_changed:
        disk['scriptsModified'] = True
        log.info('_merge_editor_into_disk: bitmap dimensions changed; marked scriptsModified=True')


def _apply_text_patches_to_n2d(n2d_path: str, text_patches: list,
                                project_dir: str) -> 'str | None':
    """Apply lightweight text-field patches from the editor to a disk N2D.

    Loads the project.n2d ZIP, parses it, overlays the editor's text fields
    onto the matching library entries (by id), re-packs as a temp ZIP, and
    returns the path to the patched temp file.  The caller is responsible
    for cleaning up the temp file.

    The text_patches list contains objects from TextField.toObject() in the
    editor, each with at least {id, text, font, ...}.  Only text-related
    fields are overlaid; roundtrip keys (fontData, swfCharId etc.) are
    preserved from disk.
    """
    import zipfile as _zipfile
    import io as _io

    if not text_patches:
        return None

    # Build lookup: id → patch
    patch_map = {}
    for p in text_patches:
        pid = p.get('id')
        if pid is not None:
            patch_map[pid] = p

    if not patch_map:
        return None

    # Load existing n2d
    with open(n2d_path, 'rb') as f:
        raw = f.read()

    is_msgpack = False
    with _zipfile.ZipFile(_io.BytesIO(raw)) as zf:
        if 'project.msgpack' in zf.namelist():
            is_msgpack = True
            data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
        else:
            data = json.loads(zf.read('project.json'))

    # Apply patches
    roundtrip_keys = frozenset((
        'swfCharId', 'externalFile',
        'fontData', 'fontTagType', 'buttonData', 'binaryDataBody',
        'soundFormat', 'isBinaryData', 'isFont', 'isButton',
        'isMorphShape',
    ))
    patched = 0
    for lib in data.get('libraries', []):
        if not lib:
            continue
        lib_id = lib.get('id')
        patch = patch_map.get(lib_id)
        if not patch:
            continue
        # Only patch if the disk entry is a text type
        if lib.get('type') != 'text':
            continue
        # Save roundtrip fields from disk
        saved = {k: lib[k] for k in roundtrip_keys if k in lib}
        original_font = lib.get('font', '')
        # Overlay editor text fields onto disk entry
        for key, val in patch.items():
            if key not in roundtrip_keys:
                lib[key] = val
        # Restore roundtrip fields
        for k, v in saved.items():
            lib[k] = v
        # If font was changed, the raw DefineText binary contains glyph
        # indices specific to the old font and cannot be reused.  Strip it
        # so _emit_text() rebuilds as DefineEditText with the new font.
        if lib.get('font', '') != original_font:
            lib.pop('rawTagBody', None)
            lib.pop('rawTagType', None)
        patched += 1
        log.info('_apply_text_patches: patched lib id=%s text="%s"',
                 lib_id, patch.get('text', '')[:50])

    if patched == 0:
        log.info('_apply_text_patches: no matching text libs to patch')
        return None

    log.info('_apply_text_patches: patched %d/%d text fields',
             patched, len(patch_map))

    # Write patched data to temp ZIP
    buf = _io.BytesIO()
    with _zipfile.ZipFile(buf, 'w', _zipfile.ZIP_DEFLATED) as zf:
        if is_msgpack:
            zf.writestr('project.msgpack', msgpack.packb(data, use_bin_type=True))
        else:
            zf.writestr('project.json', json.dumps(data))
    temp_path = n2d_path + '.patched.n2d'
    with open(temp_path, 'wb') as f:
        f.write(buf.getvalue())

    return temp_path


def _apply_text_patches_inline(data: dict, text_patches: list) -> int:
    """Apply text-field patches to an already-loaded N2D dict (in-place).

    Same logic as _apply_text_patches_to_n2d but operates on the dict
    directly (used by save-and-compile's disk-only path where we already
    have the parsed data in memory).  Returns number of patches applied.
    """
    if not text_patches:
        return 0

    patch_map = {p['id']: p for p in text_patches if 'id' in p}
    if not patch_map:
        return 0

    roundtrip_keys = frozenset((
        'swfCharId', 'externalFile',
        'fontData', 'fontTagType', 'buttonData', 'binaryDataBody',
        'soundFormat', 'isBinaryData', 'isFont', 'isButton',
        'isMorphShape',
    ))
    patched = 0
    for lib in data.get('libraries', []):
        if not lib or lib.get('type') != 'text':
            continue
        patch = patch_map.get(lib.get('id'))
        if not patch:
            continue
        saved = {k: lib[k] for k in roundtrip_keys if k in lib}
        original_font = lib.get('font', '')
        for key, val in patch.items():
            if key not in roundtrip_keys:
                lib[key] = val
        for k, v in saved.items():
            lib[k] = v
        # If font was changed, the raw DefineText binary contains glyph
        # indices specific to the old font and cannot be reused.  Strip it
        # so _emit_text() rebuilds as DefineEditText with the new font.
        if lib.get('font', '') != original_font:
            lib.pop('rawTagBody', None)
            lib.pop('rawTagType', None)
        patched += 1
        log.info('_apply_text_patches_inline: lib id=%s text="%s"',
                 lib.get('id'), patch.get('text', '')[:50])

    log.info('_apply_text_patches_inline: patched %d/%d', patched, len(patch_map))
    return patched


def _parse_script_patches_payload(script_patches):
    """Normalize script patch payload to (scripts, scripts_modified)."""
    if not script_patches:
        return [], False

    if isinstance(script_patches, dict):
        scripts = script_patches.get('scripts', [])
        scripts_modified = bool(script_patches.get('scriptsModified', False))
    elif isinstance(script_patches, list):
        scripts = script_patches
        scripts_modified = False
    else:
        return [], False

    if not isinstance(scripts, list):
        return [], scripts_modified

    clean = []
    for s in scripts:
        if not isinstance(s, dict):
            continue
        source = s.get('source', '')
        if not isinstance(source, str):
            source = ''
        item = dict(s)
        item['source'] = source
        clean.append(item)

    return clean, scripts_modified


def _apply_script_patches_inline(data: dict, script_patches) -> int:
    """Apply script patches to an already-loaded N2D dict (in-place)."""
    scripts, scripts_modified = _parse_script_patches_payload(script_patches)
    if not scripts:
        return 0

    existing = data.get('scripts', [])
    if not isinstance(existing, list):
        existing = []

    def _script_key(s: dict) -> str:
        if not isinstance(s, dict):
            return ''
        p = s.get('path', '')
        n = s.get('name', '')
        key = p or n
        return key.replace('\\', '/').strip().lower() if isinstance(key, str) else ''

    existing_by_key = {}
    for i, s in enumerate(existing):
        k = _script_key(s)
        if k:
            existing_by_key[k] = i

    updated = 0
    added = 0
    for patch in scripts:
        k = _script_key(patch)
        if not k:
            continue

        idx = existing_by_key.get(k)
        if idx is None:
            item = dict(patch)
            p = item.get('path') or item.get('name') or ''
            if p and not item.get('name'):
                item['name'] = os.path.basename(str(p))
            if p and not item.get('path'):
                item['path'] = str(p).replace('\\', '/')
            existing_by_key[k] = len(existing)
            existing.append(item)
            added += 1
            continue

        target = existing[idx]
        if not isinstance(target, dict):
            target = {}
            existing[idx] = target

        # Keep existing metadata (e.g. scriptOrigin/externalFile) unless patch
        # explicitly overrides. Always update source text.
        target['source'] = patch.get('source', target.get('source', ''))
        for field in ('name', 'path', 'scriptOrigin', 'externalFile'):
            if field in patch and patch.get(field) not in (None, ''):
                target[field] = patch.get(field)
        updated += 1

    data['scripts'] = existing
    if scripts_modified or updated > 0 or added > 0:
        data['scriptsModified'] = True

    log.info('_apply_script_patches_inline: merged %d patches (%d updated, %d added, scriptsModified=%s)',
             len(scripts), updated, added, scripts_modified)
    return updated + added


def _write_script_files(project_dir: str, scripts: list) -> int:
    """Write script sources to project scripts/ so compile overlay sees edits."""
    if not project_dir or not scripts:
        return 0

    scripts_dir = os.path.normpath(os.path.join(project_dir, 'scripts'))
    os.makedirs(scripts_dir, exist_ok=True)

    written = 0
    for script in scripts:
        if not isinstance(script, dict):
            continue
        source = script.get('source', '')
        if not isinstance(source, str) or source == '':
            continue

        rel = script.get('path') or script.get('name') or ''
        if not isinstance(rel, str) or not rel.strip():
            continue

        rel = rel.replace('\\', '/').lstrip('/')
        if rel.lower().startswith('scripts/'):
            rel = rel[8:]
        if not rel.lower().endswith('.as'):
            rel += '.as'

        full_path = os.path.normpath(os.path.join(scripts_dir, rel))
        if not (full_path == scripts_dir or full_path.startswith(scripts_dir + os.sep)):
            log.warning('_write_script_files: skipping unsafe script path %s', rel)
            continue

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(source)

        # Keep externalFile in sync for save/load cycles
        script['externalFile'] = 'scripts/' + rel.replace('\\', '/')
        written += 1

    log.info('_write_script_files: wrote %d script files', written)
    return written


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
    1. The bitmap library entry (buffer, width, height).
    2. Any embedded {buffer, width, height} dicts baked into shape recodes,
       matched back to the correct bitmap via the original buffer contents.
    """
    from PIL import Image

    BITMAP_FILL   = 13
    BITMAP_STROKE = 14
    FP_BYTES      = 32  # fingerprint length in bytes (8 RGBA pixels)

    libraries = n2d_json.get("libraries", [])
    log.info('_overlay_external_bitmaps: project_dir=%s, libraries=%d', project_dir, len(libraries))

    def _buffer_to_rgba_list(buf_value):
        """Decode common buffer encodings into an RGBA byte-list."""
        if not buf_value:
            return []
        if isinstance(buf_value, list):
            return list(buf_value)
        if isinstance(buf_value, (bytes, bytearray)):
            return list(buf_value)
        if isinstance(buf_value, str):
            raw = buf_value[4:] if buf_value.startswith('b64:') else buf_value
            try:
                return list(base64.b64decode(raw))
            except Exception:
                return list(buf_value.encode('latin-1'))
        return []

    def _rgba_to_storage(rgba_bytes: bytes):
        """Store RGBA in the same compact encoding used by N2D JSON blobs."""
        return 'b64:' + base64.b64encode(rgba_bytes).decode('ascii')

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
    bitmap_dims_changed = 0

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
            old_list = _buffer_to_rgba_list(orig_buf)
            fp = _fingerprint(old_list) if old_list else None

            old_w = lib.get('width')
            old_h = lib.get('height')

            img  = Image.open(fpath).convert("RGBA")
            rgba = img.tobytes()
            new_buf = _rgba_to_storage(rgba)

            # Update library entry using compact b64 encoding (tool-friendly JSON)
            lib["buffer"] = new_buf
            lib["width"]  = img.width
            lib["height"] = img.height

            if lib.get('symbol') and (old_w != img.width or old_h != img.height):
                bitmap_dims_changed += 1

            payload = (rgba, img.width, img.height)
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
                    buf = _buffer_to_rgba_list(buf)
                    fp  = _fingerprint(buf)
                    new_data = fingerprint_to_new.get(fp)

            if new_data is not None:
                new_rgba, new_w, new_h = new_data
                if isinstance(fv, dict):
                    old_buf = fv.get('buffer')
                    if isinstance(old_buf, list):
                        fv["buffer"] = list(new_rgba)
                    elif isinstance(old_buf, (bytes, bytearray)):
                        fv["buffer"] = bytes(new_rgba)
                    elif isinstance(old_buf, str) and not old_buf.startswith('b64:'):
                        # Shape recode bitmap dicts are typically stored as raw latin-1 strings.
                        # Preserve that encoding so parser behavior remains stable.
                        fv["buffer"] = new_rgba.decode('latin-1')
                    else:
                        fv["buffer"] = _rgba_to_storage(new_rgba)
                    fv["width"]  = new_w
                    fv["height"] = new_h
                fills_updated += 1

            i += step

    log.info('_overlay_external_bitmaps: updated %d embedded shape fill dicts', fills_updated)
    if bitmap_dims_changed:
        n2d_json['scriptsModified'] = True
        log.info('_overlay_external_bitmaps: %d bitmap dimensions changed; marked scriptsModified=True', bitmap_dims_changed)
    print(f'[N2F] bitmap overlay: {updated_libs} bitmaps, {fills_updated} shape fills updated')


# ---------------------------------------------------------------------------
#  Recents helpers
# ---------------------------------------------------------------------------
_RECENTS_FILE = os.path.join(SERVER_DIR, 'converted', '.n2f_recents.json')
_RECENTS_LOCK = threading.Lock()


def _load_recents_data():
    """Load recents JSON, returning {projects:[...], imports:[...]}."""
    try:
        os.makedirs(os.path.join(SERVER_DIR, 'converted'), exist_ok=True)
        if os.path.exists(_RECENTS_FILE):
            with open(_RECENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {'projects': [], 'imports': []}


def _save_recents_data(data):
    """Persist recents JSON to disk (silent on error)."""
    try:
        os.makedirs(os.path.join(SERVER_DIR, 'converted'), exist_ok=True)
        with open(_RECENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log.warning('Could not save recents: %s', e)


def _add_recent_entry(key, path, name):
    """Add an entry to the given key ('projects' or 'imports'). Max 100 kept."""
    with _RECENTS_LOCK:
        data = _load_recents_data()
        entries = data.get(key, [])
        entries = [e for e in entries if e.get('path') != path]  # remove duplicate
        entries.insert(0, {'path': path, 'name': name, 'ts': int(time.time())})
        data[key] = entries[:100]
        _save_recents_data(data)


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
        elif self.path.startswith("/api/font/"):
            self._handle_font_ttf()
        elif self.path == "/api/system-fonts":
            self._handle_system_fonts()
        elif self.path.startswith("/api/system-font-data/"):
            self._handle_system_font_data()
        elif self.path == "/api/recents":
            self._handle_get_recents()
        elif self.path.startswith("/api/check-project-name"):
            self._handle_check_project_name()
        elif self.path == "/api/current-project-dir":
            self._json_response({'projDir': Next2FlashHandler._current_project_dir or ''})
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
        elif self.path == "/api/save-as-project":
            self._handle_save_as_project()
        elif self.path == "/api/save-and-compile":
            self._handle_save_and_compile()
        elif self.path == "/api/compile-disk":
            self._handle_compile_disk()
        elif self.path == "/api/import-swf-path":
            self._handle_import_swf_path()
        elif self.path == "/api/new-project":
            self._handle_new_project()
        elif self.path == "/api/add-recent":
            self._handle_add_recent()
        elif self.path == "/api/remove-recent":
            self._handle_remove_recent()
        elif self.path == "/api/reveal-path":
            self._handle_reveal_path()
        elif self.path == "/api/import-asset":
            self._handle_import_asset()
        elif self.path == "/api/open-project-path":
            self._handle_open_project_path()
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

            # Use client-provided project name if available, else derive from filename
            client_name = self._extract_form_field(body, "projectName")
            name = client_name or (os.path.splitext(filename)[0] if filename else "converted")
            # Sanitize: strip path separators and dangerous characters
            name = os.path.basename(name).replace('..', '').strip('. ') or 'converted'
            # Use client-provided save directory if given and valid absolute path
            client_dir = (self._extract_form_field(body, "saveDir") or '').strip()
            overwrite = (self._extract_form_field(body, "overwrite") or '').strip() in ('1', 'true', 'True')
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
            if client_dir and os.path.isabs(client_dir):
                project_dir = os.path.join(client_dir, name)
            else:
                project_dir = os.path.join(SERVER_DIR, "converted", name)
            if overwrite and os.path.isdir(project_dir):
                import shutil as _shutil
                _shutil.rmtree(project_dir)
                log.info('_handle_swf_to_project: removed existing folder for overwrite: %s', project_dir)
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
            # Font manifest for @font-face registration
            _swf2proj_fonts = []
            for _lib in n2d_json.get('libraries', []):
                if _lib.get('isFont') and _lib.get('fontData'):
                    _swf2proj_fonts.append({
                        'id': _lib['id'],
                        'faceName': _lib.get('fontFaceName', _lib.get('name', ''))
                    })
            if _swf2proj_fonts:
                self.send_header('X-N2D-Fonts', json.dumps(_swf2proj_fonts))
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
                # Re-read latest scripts from disk (bitmaps already embedded in n2d)
                scripts_refreshed = _read_scripts_from_disk(n2d_json, project_dir)
                log.info('_handle_open_project: refreshed %d scripts from disk', scripts_refreshed)
                
                # ── Backfill & normalize scripts (Phase 2 + Phase 4) ──
                # For existing projects without scriptOrigin field, infer based on source.
                # Drop linkage stubs, extract frame bodies, mark remaining.
                try:
                    from swf_to_n2d import normalize_imported_scripts
                    libs = n2d_json.get('libraries', [])
                    scripts = n2d_json.get('scripts', [])
                    if scripts:
                        # Backfill: mark scripts that already have scriptOrigin,
                        # for those that don't, normalization will infer
                        for s in scripts:
                            if 'scriptOrigin' not in s:
                                # Will be classified during normalize
                                pass
                        normalized = normalize_imported_scripts(scripts, libs)
                        n2d_json['scripts'] = normalized
                        log.info('_handle_open_project: normalized scripts; %d kept', len(normalized))
                except Exception as e:
                    log.warning('_handle_open_project: script normalization failed (continuing): %s', e)
            else:
                project_dir = None

            # Return zlib-compressed N2D for loading into the tool
            # Return ZIP + MessagePack (same modern format used elsewhere) to
            # avoid JSON string roundtrips for large/binary-heavy projects.
            import zipfile
            import io as _io
            zip_buffer = _io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                msgpack_data = msgpack.packb(n2d_json, use_bin_type=True)
                zf.writestr('project.msgpack', msgpack_data)
            compressed = zip_buffer.getvalue()

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

    def _handle_save_as_project(self):
        """POST /api/save-as-project — Create a new project folder from a scratch N2D blob.

        Accepts: multipart/form-data with 'n2d' (blob), 'name' (string), optional 'saveDir'.
        Creates {saveDir}/{name}/project.n2d (or converted/{name}/ by default),
        sets the active project dir, and returns { ok, projDir }.
        """
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, 'No data received')

            n2d_data, _ = self._extract_upload(body, 'n2d')
            name = (self._extract_form_field(body, 'name') or '').strip() or 'untitled'
            save_dir = (self._extract_form_field(body, 'saveDir') or '').strip()

            # Sanitize name (prevent path traversal)
            name = os.path.basename(name).replace('..', '').strip('. ') or 'untitled'

            if save_dir and os.path.isabs(save_dir):
                project_dir = os.path.join(save_dir, name)
            else:
                project_dir = os.path.join(SERVER_DIR, 'converted', name)

            os.makedirs(project_dir, exist_ok=True)
            n2d_path = os.path.join(project_dir, 'project.n2d')
            with open(n2d_path, 'wb') as f:
                f.write(n2d_data)

            with self._project_lock:
                Next2FlashHandler._current_project_dir = project_dir

            log.info('_handle_save_as_project: created %s (%d bytes)', project_dir, len(n2d_data))
            resp = json.dumps({'ok': True, 'projDir': project_dir})
            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp.encode('utf-8'))

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_save_as_project: %s', e)
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
                    names = zf.namelist()
                    if 'project.msgpack' in names:
                        n2d_json = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
                    else:
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

        Fast path: receives 'editorBlob' (raw zlib tool save, lightweight).
        Server loads existing project.n2d (which has scripts, etc.),
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
            text_patches_raw = self._extract_form_field(body, 'textPatches')
            script_patches_raw = self._extract_form_field(body, 'scriptPatches')
            text_patches = []
            script_patches = None
            if text_patches_raw:
                try:
                    text_patches = json.loads(text_patches_raw)
                except Exception as e:
                    log.warning('Failed to parse text patches: %s', e)
            if script_patches_raw:
                try:
                    script_patches = json.loads(script_patches_raw)
                except Exception as e:
                    log.warning('Failed to parse script patches: %s', e)
            # disk-only flag: compile from existing project.n2d without any editor overlay
            disk_only = b'diskOnly' in body and not editor_blob and not n2d_data
            # Optional: write SWF to a specific file path (Electron mode) instead of HTTP response
            output_path_override = self._extract_form_field(body, 'outputPath') or ''

            n2d_path = os.path.join(project_dir, 'project.n2d')

            if editor_blob:
                # === FAST PATH: merge editor blob with on-disk project ===
                _t2 = _time.perf_counter()

                # Parse the lightweight editor blob
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

                # Load existing project.n2d from disk (has scripts, etc.)
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
                # rawGlobalTags, scripts, rootTimelineDefIds.
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

            # Apply lightweight inline patches before compile.
            if text_patches:
                try:
                    _apply_text_patches_inline(n2d_json, text_patches)
                except Exception as e:
                    log.warning('Failed to apply text patches: %s', e)

            scripts_applied = 0
            if script_patches:
                try:
                    scripts_applied = _apply_script_patches_inline(n2d_json, script_patches)
                except Exception as e:
                    log.warning('Failed to apply script patches: %s', e)

            # External script files are source-of-truth during compile overlay.
            if scripts_applied > 0 and project_dir:
                try:
                    _write_script_files(project_dir, n2d_json.get('scripts', []))
                except Exception as e:
                    log.warning('Failed to write script files: %s', e)

            # Compile SWF from in-memory merged data (skip save_project_folder)
            _t3 = _time.perf_counter()
            name = os.path.basename(project_dir)
            shared_dir = os.path.join(SERVER_DIR, "..", "shared")

            import compilation_pipeline as _cp
            with tempfile.TemporaryDirectory() as tmpdir:
                swf_path = os.path.join(tmpdir, f"{name}.swf")
                if not os.path.isdir(shared_dir):
                    shared_dir = tmpdir

                ctx = _cp.CompilationContext(
                    n2d_path=n2d_path,
                    shared_dir=shared_dir,
                    output_path=swf_path,
                    data_override=n2d_json,
                    project_dir_override=project_dir,
                )
                pipeline = _cp.create_default_pipeline()
                pipeline.execute(ctx)
                _t4 = _time.perf_counter()
                print(f"[PERF] compile (in-memory): {(_t4-_t3)*1000:.0f}ms")

                with open(swf_path, "rb") as f:
                    swf_bytes = f.read()

            # Persist project state to disk (fast: skips bitmaps already on disk)
            _t4b = _time.perf_counter()
            mod_swf = _get_swf_to_n2d()
            mod_swf.save_project_folder(n2d_json, project_dir)
            _t4c = _time.perf_counter()
            print(f"[PERF] save project (post-compile): {(_t4c-_t4b)*1000:.0f}ms")

            if output_path_override:
                # Electron mode: write SWF to the requested file path
                out_dir = os.path.dirname(output_path_override)
                if out_dir:
                    os.makedirs(out_dir, exist_ok=True)
                with open(output_path_override, 'wb') as f_out:
                    f_out.write(swf_bytes)
                resp_json = json.dumps({'ok': True, 'swfPath': output_path_override, 'size': len(swf_bytes)}).encode('utf-8')
                self.send_response(200)
                self._cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp_json)))
                self.end_headers()
                self.wfile.write(resp_json)
            else:
                # Browser mode: stream SWF bytes directly
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
            msg = str(e) if str(e) else repr(e)
            self._error_response(500, msg)

    def _handle_compile_disk(self):
        """POST /api/compile-disk — Compile SWF directly from on-disk project.

        Expects JSON body: {"projectDir": "...", "outputPath": "...",
                            "textPatches": [...]}
        No file upload — reads project.n2d from disk, compiles, writes SWF to
        outputPath (or returns bytes if no outputPath given). This is the
        Electron fast path that completely bypasses HTTP file transfer.

        If textPatches is provided, the patches (text-field objects from the
        editor) are applied to the in-memory N2D data before compiling, so
        that editor text edits appear in the exported SWF without needing to
        serialise the full 225 MB+ workspace.
        """
        import time as _time
        try:
            _t0 = _time.perf_counter()
            body = self._read_body()
            req = json.loads(body)
            project_dir = req.get('projectDir', '')
            output_path = req.get('outputPath', '')
            text_patches = req.get('textPatches', [])
            script_patches = req.get('scriptPatches')

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
                swf_path = output_path
            else:
                swf_path = os.path.join(tempfile.mkdtemp(), f'{name}.swf')

            # If script patches were provided, write them to scripts/ before
            # compile so _overlay_external_scripts picks up latest edits.
            if script_patches:
                scripts, scripts_modified = _parse_script_patches_payload(script_patches)
                if scripts:
                    _write_script_files(project_dir, scripts)
                    if scripts_modified:
                        log.info('_handle_compile_disk: script patches marked scriptsModified=True')

            # ── Apply text patches if provided ─────────────────────────
            compile_n2d_path = n2d_path
            temp_n2d_path = None
            if text_patches:
                temp_n2d_path = _apply_text_patches_to_n2d(
                    n2d_path, text_patches, project_dir
                )
                if temp_n2d_path:
                    compile_n2d_path = temp_n2d_path

            try:
                compiler = mod_compile.N2DCompiler(
                    n2d_path=compile_n2d_path,
                    shared_dir=shared_dir,
                    output_path=swf_path,
                )
                compiler.compile()
            finally:
                # Clean up temp patched n2d
                if temp_n2d_path and os.path.isfile(temp_n2d_path):
                    try:
                        os.unlink(temp_n2d_path)
                    except OSError:
                        pass

            _t2 = _time.perf_counter()
            patched_msg = f' ({len(text_patches)} text patches applied)' if text_patches else ''
            print(f"[PERF] compile-disk: compile={(_t2-_t1)*1000:.0f}ms total={(_t2-_t0)*1000:.0f}ms{patched_msg}")

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
            msg = str(e) if str(e) else repr(e)
            self._error_response(500, msg)

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
            # Use client-provided project name if available, else derive from filename
            client_name = req.get('projectName', '').strip()
            name = client_name or os.path.splitext(os.path.basename(swf_path))[0]
            # Sanitize: strip path separators and dangerous characters
            name = os.path.basename(name).replace('..', '').strip('. ') or 'converted'
            # Use client-provided save directory if given and valid absolute path
            client_dir = req.get('saveDir', '').strip()
            overwrite = bool(req.get('overwrite', False))

            # Check for cached conversion on disk
            if client_dir and os.path.isabs(client_dir):
                project_dir = os.path.join(client_dir, name)
            else:
                project_dir = os.path.join(SERVER_DIR, 'converted', name)
            if overwrite and os.path.isdir(project_dir):
                import shutil as _shutil
                _shutil.rmtree(project_dir)
                log.info('_handle_import_swf_path: removed existing folder for overwrite: %s', project_dir)
            cached_n2d = os.path.join(project_dir, 'project.n2d')
            n2d_json = None

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
            _HEAVY_FIELDS = ('buffer', 'recodes')

            if lazy:
                # Build skeleton in-memory from project.n2d (no separate skeleton file)
                # Store full libraries server-side for on-demand loading
                with self._lazy_lock:
                    Next2FlashHandler._lazy_libraries.clear()
                    Next2FlashHandler._lazy_bulk_cache = None  # invalidate cache
                    Next2FlashHandler._font_ttf_cache.clear()
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

                _tick(f"skeleton ZIP: {len(compressed):,} bytes -> DONE")
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

            # Build font manifest for @font-face registration on client
            font_manifest = []
            if n2d_json:
                for lib in n2d_json.get('libraries', []):
                    if lib.get('isFont') and lib.get('fontData'):
                        font_manifest.append({
                            'id': lib['id'],
                            'faceName': lib.get('fontFaceName', lib.get('name', ''))
                        })

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{name}.n2d"')
            self.send_header('X-N2D-Name', name)
            self.send_header('X-N2D-Libraries', str(lib_count))
            self.send_header('X-N2D-Scripts', str(script_count))
            self.send_header('X-N2D-Format', 'msgpack')
            self.send_header('X-Project-Dir', project_dir)
            if font_manifest:
                self.send_header('X-N2D-Fonts', json.dumps(font_manifest))
            self.send_header('Content-Length', str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_import_swf_path: %s', e)
            self._error_response(500, f'SWF import from path failed: {e}')

    def _handle_new_project(self):
        """POST /api/new-project - Create a blank project (no SWF import needed).

        Accepts JSON body with optional stage settings:
            { "name": "my_project", "width": 1280, "height": 720,
              "frameRate": 30, "backgroundColor": 16777215 }

        Creates a minimal N2D with a root MovieClip (ID 0, one empty layer).
        If 'saveFolder' is true, also creates a project folder on disk.
        Returns the N2D as a ZIP-msgpack blob (same format as swf-to-project).
        """
        try:
            body = self._read_body()
            if body:
                try:
                    params = json.loads(body.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    params = {}
            else:
                params = {}

            name = str(params.get('name', 'untitled'))[:128]
            width = max(1, min(4096, int(params.get('width', 550))))
            height = max(1, min(4096, int(params.get('height', 400))))
            fps = max(1, min(120, int(params.get('frameRate', 24))))
            bg_raw = params.get('backgroundColor', 0xFFFFFF)
            if isinstance(bg_raw, str):
                bg_raw = bg_raw.lstrip('#')
                bg = int(bg_raw, 16) & 0xFFFFFF
            else:
                bg = int(bg_raw) & 0xFFFFFF

            bg_hex = f'#{bg:06x}'
            n2d_json = {
                'name': name,
                'width': width,
                'height': height,
                'stage': {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'bgColor': bg_hex,
                    'lock': False,
                },
                'characterId': 0,
                'swfVersion': 25,
                'backgroundColor': bg_hex,
                'frameRate': fps,
                'libraries': [
                    {
                        'id': 0,
                        'type': 'container',
                        'name': 'main',
                        'symbol': '',
                        'totalFrame': 1,
                        'layers': [
                            {
                                'name': 'Layer 1',
                                'disable': False,
                                'mode': 0,
                                'characters': [],
                            }
                        ],
                        'labels': {},
                        'actions': {},
                    }
                ],
                'scripts': [],
                'rawGlobalTags': [],
            }

            log.info('_handle_new_project: %s %dx%d @%dfps bg=#%06x',
                      name, width, height, fps, bg)

            # Optionally create on-disk project folder
            if params.get('saveFolder'):
                project_dir = os.path.join(SERVER_DIR, 'converted', name)
                mod = _get_swf_to_n2d()
                mod.save_project_folder(n2d_json, project_dir)
                with self._project_lock:
                    Next2FlashHandler._current_project_dir = project_dir

            # Return ZIP-msgpack (same format as swf-to-project)
            import zipfile as _zipfile
            import io as _io
            zip_buffer = _io.BytesIO()
            with _zipfile.ZipFile(zip_buffer, 'w', _zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                msgpack_data = msgpack.packb(n2d_json, use_bin_type=True)
                zf.writestr('project.msgpack', msgpack_data)

            compressed = zip_buffer.getvalue()

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{name}.n2d"')
            self.send_header('X-N2D-Name', name)
            self.send_header('X-N2D-Libraries', '1')
            self.send_header('X-N2D-Scripts', '0')
            self.send_header('X-N2D-Format', 'msgpack')
            proj_dir_hdr = ''
            if params.get('saveFolder'):
                with self._project_lock:
                    proj_dir_hdr = Next2FlashHandler._current_project_dir or ''
            self.send_header('X-Project-Dir', proj_dir_hdr)
            self.send_header('Content-Length', str(len(compressed)))
            self.end_headers()
            self.wfile.write(compressed)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_new_project: %s', e)
            self._error_response(500, f'New project creation failed: {e}')

    # ------------------------------------------------------------------
    # Recents helpers (module-level functions called by handlers)
    # ------------------------------------------------------------------

    def _handle_check_project_name(self):
        """GET /api/check-project-name?name=X&saveDir=Y — Check if folder already exists."""
        try:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            name = (qs.get('name', [''])[0]).strip()
            save_dir = (qs.get('saveDir', [''])[0]).strip()
            if not name:
                return self._json_response({'exists': False})
            base = save_dir if save_dir else os.path.join(SERVER_DIR, 'converted')
            target = os.path.join(base, name)
            self._json_response({'exists': os.path.exists(target)})
        except Exception as e:
            self._error_response(500, str(e))

    def _handle_remove_recent(self):
        """POST /api/remove-recent — Remove an entry from recents. Body: {category, path}."""
        try:
            body = self._read_body()
            data = json.loads(body.decode('utf-8')) if body else {}
            category = str(data.get('category', 'project'))
            path = str(data.get('path', ''))
            if path:
                key = 'projects' if category == 'project' else 'imports'
                with _RECENTS_LOCK:
                    recents = _load_recents_data()
                    entries = recents.get(key, [])
                    entries = [e for e in entries if e.get('path') != path]
                    recents[key] = entries
                    _save_recents_data(recents)
            resp = json.dumps({'ok': True}).encode('utf-8')
            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self._error_response(500, str(e))

    def _handle_reveal_path(self):
        """POST /api/reveal-path — Reveal a path in the OS file explorer."""
        try:
            import subprocess
            import platform
            body = self._read_body()
            data = json.loads(body.decode('utf-8')) if body else {}
            path = str(data.get('path', ''))
            if path:
                sys_name = platform.system()
                norm = os.path.normpath(path)
                if sys_name == 'Windows':
                    # Use explorer /select, to highlight the item
                    subprocess.Popen(['explorer', '/select,', norm])
                elif sys_name == 'Darwin':
                    subprocess.Popen(['open', '-R', norm])
                else:
                    # Linux: open parent directory
                    parent = os.path.dirname(norm)
                    subprocess.Popen(['xdg-open', parent])
            self._json_response({'ok': True})
        except Exception as e:
            self._error_response(500, str(e))

    def _handle_get_recents(self):
        """GET /api/recents — Return {projects:[...], imports:[...]}."""
        try:
            data = _load_recents_data()
            resp = json.dumps(data).encode('utf-8')
            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self._error_response(500, str(e))

    def _handle_add_recent(self):
        """POST /api/add-recent — Add an entry to recents. Body: {category, path, name}."""
        try:
            body = self._read_body()
            data = json.loads(body.decode('utf-8')) if body else {}
            category = str(data.get('category', 'project'))
            path = str(data.get('path', ''))
            name = str(data.get('name', path.split(os.sep)[-1] if path else ''))
            if path:
                key = 'projects' if category == 'project' else 'imports'
                _add_recent_entry(key, path, name)
            resp = json.dumps({'ok': True}).encode('utf-8')
            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self._error_response(500, str(e))

    def _handle_import_asset(self):
        """POST /api/import-asset — Copy uploaded files into {projectDir}/assets/."""
        try:
            body = self._read_body()
            if not body:
                return self._error_response(400, 'No data received')

            project_dir = Next2FlashHandler._current_project_dir
            if not project_dir:
                return self._error_response(400, 'No active project folder — save or open a project first')

            assets_dir = os.path.join(project_dir, 'assets')
            os.makedirs(assets_dir, exist_ok=True)

            content_type = self.headers.get('Content-Type', '')
            boundary = None
            for part in content_type.split(';'):
                part = part.strip()
                if part.startswith('boundary='):
                    boundary = part[9:].strip('"')
                    break

            if not boundary:
                return self._error_response(400, 'No multipart boundary')

            boundary_bytes = f'--{boundary}'.encode()
            parts = body.split(boundary_bytes)

            saved_files = []
            for part in parts:
                if b'name="files"' not in part:
                    continue
                if b'filename=' not in part:
                    continue
                header_end = part.find(b'\r\n\r\n')
                if header_end < 0:
                    continue
                header = part[:header_end].decode('utf-8', errors='replace')
                filename = None
                for line in header.split('\r\n'):
                    if 'filename=' in line:
                        try:
                            start = line.index('filename="') + 10
                            end = line.index('"', start)
                            filename = line[start:end]
                        except ValueError:
                            pass
                        break
                if not filename:
                    continue
                file_data = part[header_end + 4:]
                if file_data.endswith(b'\r\n'):
                    file_data = file_data[:-2]
                if file_data.endswith(b'--'):
                    file_data = file_data[:-2]
                if file_data.endswith(b'\r\n'):
                    file_data = file_data[:-2]

                safe_name = os.path.basename(filename).replace('..', '')
                if not safe_name:
                    continue
                dest = os.path.join(assets_dir, safe_name)
                with open(dest, 'wb') as f:
                    f.write(file_data)
                saved_files.append(safe_name)
                log.info('Imported asset: %s (%d bytes)', safe_name, len(file_data))

            resp = json.dumps({'ok': True, 'count': len(saved_files),
                               'files': saved_files, 'folder': assets_dir}).encode('utf-8')
            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_import_asset: %s', e)
            self._error_response(500, str(e))

    def _handle_open_project_path(self):
        """POST /api/open-project-path — Open a project from a disk path (for Recent Projects).

        Accepts JSON body: {"projDir": "...", "lazy": true/false}
        When lazy=true (default), returns a skeleton project (no heavy buffer/recodes data)
        and populates the server-side lazy library store for background hydration.
        This makes project opening much faster since the client receives a small skeleton
        immediately and loads full library data in the background.
        """
        try:
            body = self._read_body()
            params = json.loads(body.decode('utf-8')) if body else {}
            proj_dir = str(params.get('projDir', '')).strip()
            lazy = bool(params.get('lazy', True))  # lazy by default for fast open

            if not proj_dir or not os.path.isdir(proj_dir):
                return self._error_response(404, f'Project folder not found: {proj_dir}')

            n2d_path = os.path.join(proj_dir, 'project.n2d')
            if not os.path.exists(n2d_path):
                return self._error_response(404, f'project.n2d not found in {proj_dir}')

            with open(n2d_path, 'rb') as f:
                n2d_data = f.read()

            name = os.path.basename(proj_dir)

            # Parse the N2D to get library data
            import zipfile as _zf, io as _io2
            n2d_json = None
            try:
                with _zf.ZipFile(_io2.BytesIO(n2d_data)) as zf:
                    names = zf.namelist()
                    if 'project.msgpack' in names:
                        n2d_json = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
                    elif 'project.json' in names:
                        n2d_json = json.loads(zf.read('project.json'))
            except Exception as e:
                log.warning('_handle_open_project_path: failed to parse n2d: %s', e)

            with self._project_lock:
                Next2FlashHandler._current_project_dir = proj_dir

            lib_count = len(n2d_json.get('libraries', [])) if n2d_json else 0
            script_count = len(n2d_json.get('scripts', [])) if n2d_json else 0
            n2d_name = (n2d_json.get('name', name) if n2d_json else name)

            # Build font manifest
            font_manifest = []
            if n2d_json:
                for lib in n2d_json.get('libraries', []):
                    if lib.get('isFont') and lib.get('fontData'):
                        font_manifest.append({
                            'id': lib['id'],
                            'faceName': lib.get('fontFaceName', lib.get('name', ''))
                        })

            if lazy and n2d_json:
                # Build skeleton and set up lazy library store for background hydration
                _HEAVY_FIELDS = ('buffer', 'recodes')
                with self._lazy_lock:
                    Next2FlashHandler._lazy_libraries.clear()
                    Next2FlashHandler._lazy_bulk_cache = None
                    Next2FlashHandler._font_ttf_cache.clear()
                    for lib in n2d_json.get('libraries', []):
                        lib_id = lib.get('id')
                        if lib_id is not None:
                            Next2FlashHandler._lazy_libraries[int(lib_id)] = lib
                log.info('_handle_open_project_path: stored %d libs in lazy store', len(Next2FlashHandler._lazy_libraries))

                skeleton_libs = []
                for lib in n2d_json.get('libraries', []):
                    skel = {k: v for k, v in lib.items() if k not in _HEAVY_FIELDS}
                    skel['_lazy'] = True
                    skeleton_libs.append(skel)

                skeleton = dict(n2d_json)
                skeleton['libraries'] = skeleton_libs

                msgpack_data = msgpack.packb(skeleton, use_bin_type=True)
                import zipfile as _zipfile
                zip_buffer = _io2.BytesIO()
                with _zipfile.ZipFile(zip_buffer, 'w', _zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                    zf.writestr('project.msgpack', msgpack_data)
                response_data = zip_buffer.getvalue()
                log.info('_handle_open_project_path: skeleton %d bytes (full was %d bytes)',
                         len(response_data), len(n2d_data))
            else:
                response_data = n2d_data

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{n2d_name}.n2d"')
            self.send_header('X-N2D-Name', n2d_name)
            self.send_header('X-N2D-Libraries', str(lib_count))
            self.send_header('X-N2D-Scripts', str(script_count))
            self.send_header('X-Project-Dir', proj_dir)
            if font_manifest:
                self.send_header('X-N2D-Fonts', json.dumps(font_manifest))
            self.send_header('Content-Length', str(len(response_data)))
            self.end_headers()
            self.wfile.write(response_data)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_open_project_path: %s', e)
            self._error_response(500, str(e))

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
                            Next2FlashHandler._font_ttf_cache.clear()
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

    # ── Font TTF endpoint ────────────────────────────────────────────────

    # Cache: lib_id → TTF bytes (cleared on new SWF import)
    _font_ttf_cache: dict = {}

    def _handle_font_ttf(self):
        """GET /api/font/<lib_id> — Serve an embedded SWF font as a TTF file.

        Converts the DefineFont3/DefineFont2 glyph outlines stored in the
        font library entry to a TrueType font on the fly (cached).
        """
        try:
            lib_id_str = self.path.rsplit('/', 1)[-1]
            try:
                lib_id = int(lib_id_str)
            except ValueError:
                return self._error_response(400, f'Invalid library ID: {lib_id_str}')

            # Check cache first
            if lib_id in Next2FlashHandler._font_ttf_cache:
                ttf_bytes = Next2FlashHandler._font_ttf_cache[lib_id]
            else:
                # Find the font library entry in the lazy store
                with self._lazy_lock:
                    lib_data = Next2FlashHandler._lazy_libraries.get(lib_id)

                if lib_data is None:
                    # Lazy store may be empty after restart with cached skeleton;
                    # try loading from the full project N2D on disk.
                    with self._project_lock:
                        proj_dir = Next2FlashHandler._current_project_dir
                    if proj_dir:
                        cached_n2d = os.path.join(proj_dir, 'project.n2d')
                        if os.path.isfile(cached_n2d):
                            import zipfile as _zipfile
                            import io as _io
                            with _zipfile.ZipFile(cached_n2d, 'r') as zf:
                                names = zf.namelist()
                                if 'project.msgpack' in names:
                                    raw = zf.read('project.msgpack')
                                    n2d_json = msgpack.unpackb(raw, raw=False)
                                elif 'project.json' in names:
                                    raw = zf.read('project.json')
                                    n2d_json = json.loads(raw)
                                else:
                                    n2d_json = {}
                            with self._lazy_lock:
                                for lib in n2d_json.get('libraries', []):
                                    lid = lib.get('id')
                                    if lid is not None:
                                        Next2FlashHandler._lazy_libraries[int(lid)] = lib
                                lib_data = Next2FlashHandler._lazy_libraries.get(lib_id)

                if lib_data is None:
                    return self._error_response(404, f'Library {lib_id} not found')

                font_data_b64 = lib_data.get('fontData')
                if not font_data_b64:
                    return self._error_response(404, f'Library {lib_id} has no fontData')

                import base64
                if isinstance(font_data_b64, bytes):
                    raw_body = font_data_b64
                else:
                    raw_body = base64.b64decode(font_data_b64)

                tag_type = lib_data.get('fontTagType', 75)

                from swf_font_to_ttf import swf_font_to_ttf
                ttf_bytes = swf_font_to_ttf(raw_body, tag_type)
                Next2FlashHandler._font_ttf_cache[lib_id] = ttf_bytes
                log.info('_handle_font_ttf: generated TTF for lib %d (%d bytes)', lib_id, len(ttf_bytes))

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'font/ttf')
            self.send_header('Content-Length', str(len(ttf_bytes)))
            self.send_header('Access-Control-Expose-Headers', 'Content-Length')
            self.end_headers()
            self.wfile.write(ttf_bytes)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_font_ttf: %s', e)
            self._error_response(500, str(e))

    # ── System fonts endpoints ───────────────────────────────────────────

    _system_fonts_cache: list | None = None  # cached [{name, path, style}, ...]

    def _handle_system_fonts(self):
        """GET /api/system-fonts — List fonts installed on the system."""
        try:
            if Next2FlashHandler._system_fonts_cache is None:
                Next2FlashHandler._system_fonts_cache = _enumerate_system_fonts()
            self._json_response(Next2FlashHandler._system_fonts_cache)
        except Exception as e:
            traceback.print_exc()
            log.error('_handle_system_fonts: %s', e)
            self._error_response(500, str(e))

    def _handle_system_font_data(self):
        """GET /api/system-font-data/<font_name> — Serve a system font's TTF bytes."""
        try:
            from urllib.parse import unquote
            font_name = unquote(self.path.split('/api/system-font-data/', 1)[-1])
            if not font_name:
                return self._error_response(400, 'No font name provided')

            # Find the font path from the cache
            if Next2FlashHandler._system_fonts_cache is None:
                Next2FlashHandler._system_fonts_cache = _enumerate_system_fonts()

            font_path = None
            for f in Next2FlashHandler._system_fonts_cache:
                if f['name'] == font_name:
                    font_path = f['path']
                    break

            if not font_path or not os.path.isfile(font_path):
                return self._error_response(404, f'System font not found: {font_name}')

            with open(font_path, 'rb') as fh:
                data = fh.read()

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'font/ttf')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        except Exception as e:
            traceback.print_exc()
            log.error('_handle_system_font_data: %s', e)
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

            # Re-read external sound files (MP3/WAV) → update buffer
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
                    buf_b64 = base64.b64encode(audio_bytes).decode("ascii")
                    lib["buffer"] = buf_b64
                    ext_lower = ext_file.lower()
                    if ext_lower.endswith(".mp3"):
                        lib["soundFormat"] = "mp3"
                    elif ext_lower.endswith(".wav"):
                        lib["soundFormat"] = "wav"
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

            # Return ZIP + MessagePack payload (same format as open/import paths).
            import zipfile
            import io as _io
            zip_buffer = _io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                msgpack_data = msgpack.packb(n2d_json, use_bin_type=True)
                zf.writestr('project.msgpack', msgpack_data)
            compressed = zip_buffer.getvalue()

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.n2d"')
            self.send_header("X-N2D-Name", name)
            self.send_header("X-N2D-Libraries", str(len(n2d_json.get("libraries", []))))
            self.send_header("X-Refreshed-Scripts", str(scripts_refreshed))
            self.send_header("X-Refreshed-Bitmaps", str(bitmaps_refreshed))
            self.send_header("X-Refreshed-Sounds", str(sounds_refreshed))
            self.send_header("X-N2D-Format", "msgpack")
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

    def _extract_form_field(self, body: bytes, field_name: str):
        """Extract a plain text field value from multipart/form-data. Returns str or None."""
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

        target = f'name="{field_name}"'.encode()
        for part in parts:
            if target not in part:
                continue
            # Skip file fields (they have filename=)
            if b'filename=' in part:
                continue
            header_end = part.find(b"\r\n\r\n")
            if header_end < 0:
                continue
            val = part[header_end + 4:]
            if val.endswith(b"\r\n"):
                val = val[:-2]
            if val.endswith(b"--"):
                val = val[:-2]
            if val.endswith(b"\r\n"):
                val = val[:-2]
            return val.decode("utf-8", errors="replace").strip()

        return None

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Requested-With")
        self.send_header("Access-Control-Expose-Headers",
                         "X-N2D-Name, X-N2D-Libraries, X-N2D-Scripts, X-N2D-Fonts, X-N2D-Format, X-Project-Dir, X-Refreshed-Scripts, X-Refreshed-Bitmaps, X-Refreshed-Sounds")

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
        rt_fields = ("swfCharId", "inBitmap", "grid", "bitmapId",
                      "fontData", "fontTagType", "fontAuxParsed",
                      "buttonData", "binaryDataBody", "soundFormat")
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

        for key in ("swfVersion", "swfCompressed",
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

    # Write PID file so the Electron main process can kill us on next startup
    # if we were orphaned (e.g. Electron crashed without calling stopPythonServer).
    pid_file = os.path.join(SERVER_DIR, 'server.pid')
    import atexit
    try:
        with open(pid_file, 'w') as _pf:
            _pf.write(str(os.getpid()))
        atexit.register(lambda: os.remove(pid_file) if os.path.exists(pid_file) else None)
    except OSError:
        pass  # non-fatal if we can't write the PID file

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
