"""test_edit_persistence.py — Verify that all editable content types survive
the full compile roundtrip (N2D JSON → SWF binary).

Each test builds a minimal N2D library entry, runs it through the compilation
pipeline, parses the output SWF, and asserts the edited value is present.
No SWF file on disk is required — everything is constructed in memory.
"""

import base64
import io
import struct
import sys
import os
import zlib
import zipfile
import json
import pytest

# ── helpers to build a minimal compilable N2D dict ──────────────────────

# Minimal stage / root container expected by the compiler
def _base_n2d(libraries=None):
    libs = [
        # Root timeline (id=0, totalFrame=1, 1 layer, 1 empty char)
        {
            "id": 0,
            "type": "container",
            "name": "Main",
            "totalFrame": 1,
            "currentFrame": 1,
            "leftFrame": 1,
            "symbol": "Main",
            "folderId": 0,
            "layers": [
                {
                    "name": "layer_0",
                    "light": False,
                    "disable": False,
                    "lock": False,
                    "mode": 0,
                    "maskId": None,
                    "guideId": None,
                    "color": "#ff0000",
                    "characters": [],
                    "emptyCharacters": [{"startFrame": 1, "endFrame": 2}],
                }
            ],
            "labels": [],
            "actions": [],
            "sounds": [],
        }
    ]
    if libraries:
        libs.extend(libraries)
    return {
        "stage": {"width": 550, "height": 400},
        "width": 550,
        "height": 400,
        "frameRate": 24,
        "backgroundColor": "#ffffff",
        "swfVersion": 14,
        "swfCompressed": True,
        "libraries": libs,
        "abcBlocks": [],
        "sceneAndFrameLabels": None,
    }


def _compile(n2d_dict):
    """Run the compilation pipeline and return raw SWF bytes."""
    import tempfile, os
    from compilation_pipeline import create_default_pipeline, CompilationContext

    # Write a temporary .n2d ZIP file
    fd, n2d_path = tempfile.mkstemp(suffix=".n2d")
    os.close(fd)
    swf_path = n2d_path.replace(".n2d", ".swf")
    try:
        payload = json.dumps(n2d_dict).encode("utf-8")
        with zipfile.ZipFile(n2d_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("project.json", payload)

        ctx = CompilationContext(
            n2d_path=n2d_path,
            shared_dir="",
            output_path=swf_path,
            sdk_path=None,
        )
        pipeline = create_default_pipeline()
        pipeline.execute(ctx)

        with open(swf_path, "rb") as f:
            return f.read()
    finally:
        for p in (n2d_path, swf_path):
            try:
                os.unlink(p)
            except Exception:
                pass


# ── SWF tag scanner ──────────────────────────────────────────────────────

def _iter_swf_tags(swf_bytes):
    """Yield (tag_type, body) for every tag in a SWF file."""
    # SWF header: signature (3) + version (1) + file_length (4)
    sig = swf_bytes[:3]
    if sig == b"CWS":
        # zlib-compressed
        data = swf_bytes[:8] + zlib.decompress(swf_bytes[8:])
    elif sig == b"FWS":
        data = swf_bytes
    else:
        raise ValueError(f"Not a SWF: {sig}")

    off = 8  # skip header (3 sig + 1 version + 4 length)
    # Skip RECT (variable length)
    if off < len(data):
        nbits = (data[off] >> 3) & 0x1F
        rect_bits = 5 + nbits * 4
        off += (rect_bits + 7) // 8
    off += 4  # frame_rate (UI16) + frame_count (UI16)

    while off + 2 <= len(data):
        tag_code_and_length = struct.unpack_from("<H", data, off)[0]
        off += 2
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        if length == 0x3F:
            length = struct.unpack_from("<I", data, off)[0]
            off += 4
        body = data[off: off + length]
        off += length
        yield tag_type, body
        if tag_type == 0:  # TAG_END
            break


def _find_tag(swf_bytes, tag_type):
    """Return the first tag body matching tag_type, or None."""
    for t, body in _iter_swf_tags(swf_bytes):
        if t == tag_type:
            return body
    return None


def _find_all_tags(swf_bytes, tag_type):
    return [body for t, body in _iter_swf_tags(swf_bytes) if t == tag_type]


# ═══════════════════════════════════════════════════════════════════════════
# TEST 1 — Text edit persists
# ═══════════════════════════════════════════════════════════════════════════

class TestTextEditPersists:
    """User edits the `text` field of a DefineEditText — verify it appears in SWF."""

    def test_text_field_emitted(self):
        EDITED_TEXT = "Hello World EDITED"
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 10,
                "type": "text",
                "name": "MyText",
                "symbol": "",
                "folderId": 0,
                "text": EDITED_TEXT,
                "font": "Arial",
                "size": 24,
                "color": 0xFF0000,
                "inputType": "static",
                "multiline": False,
                "wordWrap": False,
                "border": False,
                "autoSize": 0,
                "html": False,
                "bounds": {"xMin": 0, "xMax": 200, "yMin": 0, "yMax": 40},
            }
        ])
        swf = _compile(n2d)
        # Tag 37 = DefineEditText
        bodies = _find_all_tags(swf, 37)
        assert bodies, "No DefineEditText (tag 37) found in output SWF"
        found = any(EDITED_TEXT.encode("utf-8") in body for body in bodies)
        assert found, f"Edited text '{EDITED_TEXT}' not found in any DefineEditText tag"

    def test_html_field_does_not_override_text(self):
        """When html=True and htmlText holds old value, text field must still be emitted."""
        USER_TEXT = "NEW TEXT FROM EDITOR"
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 10,
                "type": "text",
                "name": "HtmlText",
                "symbol": "",
                "folderId": 0,
                "text": USER_TEXT,
                "htmlText": "<p>OLD STALE HTML TEXT</p>",  # must NOT appear
                "font": "Arial",
                "size": 14,
                "color": 0x000000,
                "inputType": "static",
                "html": True,
                "multiline": False,
                "wordWrap": False,
                "border": False,
                "autoSize": 0,
                "bounds": {"xMin": 0, "xMax": 300, "yMin": 0, "yMax": 30},
            }
        ])
        swf = _compile(n2d)
        bodies = _find_all_tags(swf, 37)
        assert bodies, "No DefineEditText tag found"
        # User text must be present
        found_new = any(USER_TEXT.encode("utf-8") in body for body in bodies)
        assert found_new, f"User-edited text '{USER_TEXT}' not found in SWF"
        # Old html text must NOT be present
        found_old = any(b"OLD STALE HTML TEXT" in body for body in bodies)
        assert not found_old, "Stale htmlText leaked into SWF — html passthrough bug"

    def test_empty_text_field(self):
        """Empty text should emit a DefineEditText with no initial text."""
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 10,
                "type": "text",
                "name": "Empty",
                "symbol": "",
                "folderId": 0,
                "text": "",
                "font": "Arial",
                "size": 12,
                "color": 0,
                "inputType": "input",
                "html": False,
                "multiline": False,
                "wordWrap": False,
                "border": True,
                "autoSize": 0,
                "bounds": {"xMin": 0, "xMax": 150, "yMin": 0, "yMax": 25},
            }
        ])
        swf = _compile(n2d)
        bodies = _find_all_tags(swf, 37)
        assert bodies, "No DefineEditText tag found for empty text field"


# ═══════════════════════════════════════════════════════════════════════════
# TEST 2 — Sound buffer persists (new sound replaces original)
# ═══════════════════════════════════════════════════════════════════════════

def _minimal_wav(duration_samples=100, sample_rate=22050):
    """Build a minimal mono 16-bit WAV with `duration_samples` silence samples."""
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = duration_samples * block_align
    pcm = b"\x00" * data_size
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_size, b"WAVE",
        b"fmt ", 16,
        1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample,
        b"data", data_size,
    )
    return header + pcm


class TestSoundBufferPersists:
    """Sound with a buffer field is emitted as DefineSound (tag 14)."""

    def test_wav_sound_emitted(self):
        wav = _minimal_wav()
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 20,
                "type": "sound",
                "name": "MySound",
                "symbol": "",
                "folderId": 0,
                "buffer": base64.b64encode(wav).decode("ascii"),
                "soundFormat": "wav",
                "volume": 100,
                "loopCount": 0,
            }
        ])
        swf = _compile(n2d)
        # Tag 14 = DefineSound
        bodies = _find_all_tags(swf, 14)
        assert bodies, "No DefineSound (tag 14) found — sound buffer not emitted"

    def test_sound_without_buffer_skipped_gracefully(self):
        """Sound with empty buffer should be skipped without crashing."""
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 20,
                "type": "sound",
                "name": "NullSound",
                "symbol": "",
                "folderId": 0,
                "buffer": "",
                "soundFormat": "unknown",
                "volume": 100,
                "loopCount": 0,
            }
        ])
        swf = _compile(n2d)  # must not raise
        assert swf[:3] in (b"CWS", b"FWS"), "Not a valid SWF output"

    def test_no_raw_sound_body_passthrough(self):
        """rawSoundBody must not appear in the N2D output of a fresh import path."""
        # If rawSoundBody were present, the old binary would pass through
        # regardless of what the user set as the buffer — verify this field
        # is not read by the compiler.
        from compile_n2d import N2DCompiler
        import inspect
        src = inspect.getsource(N2DCompiler._emit_sound)
        assert "rawSoundBody" not in src, (
            "_emit_sound still references rawSoundBody — passthrough not fully removed"
        )


# ═══════════════════════════════════════════════════════════════════════════
# TEST 3 — Bitmap buffer persists
# ═══════════════════════════════════════════════════════════════════════════

def _solid_rgba_pixels(w, h, r=255, g=0, b=0, a=255):
    """RGBA pixel buffer, solid colour."""
    import struct
    row = struct.pack("BBBB", r, g, b, a) * w
    return row * h


class TestBitmapBufferPersists:
    """Bitmap with a buffer field is emitted as DefineBitsLossless2 (tag 36)."""

    def test_bitmap_emitted(self):
        w, h = 4, 4
        pixels = _solid_rgba_pixels(w, h, r=200, g=100, b=50)
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 30,
                "type": "bitmap",
                "name": "MyBitmap",
                "symbol": "",
                "folderId": 0,
                "width": w,
                "height": h,
                "buffer": base64.b64encode(pixels).decode("ascii"),
            }
        ])
        swf = _compile(n2d)
        # Tag 36 = DefineBitsLossless2
        bodies = _find_all_tags(swf, 36)
        assert bodies, "No DefineBitsLossless2 (tag 36) found — bitmap not emitted"

    def test_bitmap_emits_correct_tag_type(self):
        """Bitmap must be emitted as tag 36 (LL2) for normal bitmaps.
        JPEG-sourced bitmaps may use tag 35 (JPEG3) to preserve the original
        pool count and prevent Flash Player Error #2015.
        rawTagType is allowed as a format hint in _emit_bitmap."""
        from compile_n2d import N2DCompiler
        import inspect
        src = inspect.getsource(N2DCompiler._emit_bitmap)
        # Ensure the LL2 path (tag 36) is present
        assert "build_define_bits_lossless2" in src, (
            "_emit_bitmap must emit DefineBitsLossless2 (tag 36) for non-JPEG bitmaps"
        )


# ═══════════════════════════════════════════════════════════════════════════
# TEST 4 — Container / movie clip timeline edit persists
# ═══════════════════════════════════════════════════════════════════════════

class TestContainerTimelineEditPersists:
    """Movie clip's layer/place data is emitted as DefineSprite (tag 39)."""

    def test_sprite_emitted_with_frames(self):
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 40,
                "type": "container",
                "name": "MyClip",
                "symbol": "",
                "folderId": 0,
                "totalFrame": 3,
                "currentFrame": 1,
                "leftFrame": 1,
                "layers": [
                    {
                        "name": "layer_0",
                        "light": False,
                        "disable": False,
                        "lock": False,
                        "mode": 0,
                        "maskId": None,
                        "guideId": None,
                        "color": "#00ff00",
                        "characters": [],
                        "emptyCharacters": [{"startFrame": 1, "endFrame": 4}],
                    }
                ],
                "labels": [],
                "actions": [],
                "sounds": [],
            }
        ])
        swf = _compile(n2d)
        # Tag 39 = DefineSprite
        bodies = _find_all_tags(swf, 39)
        assert bodies, "No DefineSprite (tag 39) found"
        # First 4 bytes of DefineSprite body: spriteID (UI16) + frameCount (UI16)
        sprite_body = bodies[0]
        frame_count = struct.unpack_from("<H", sprite_body, 2)[0]
        assert frame_count == 3, f"Expected 3 frames, got {frame_count}"

    def test_label_edit_persists(self):
        """FrameLabel (tag 43) inside a sprite matches the edited label name."""
        LABEL_NAME = "MY_EDITED_LABEL"
        n2d = _base_n2d([
            {
                "id": 1,
                "swfCharId": 40,
                "type": "container",
                "name": "LabelledClip",
                "symbol": "",
                "folderId": 0,
                "totalFrame": 2,
                "currentFrame": 1,
                "leftFrame": 1,
                "layers": [
                    {
                        "name": "layer_0",
                        "light": False,
                        "disable": False,
                        "lock": False,
                        "mode": 0,
                        "maskId": None,
                        "guideId": None,
                        "color": "#0000ff",
                        "characters": [],
                        "emptyCharacters": [{"startFrame": 1, "endFrame": 3}],
                    }
                ],
                "labels": [{"frame": 1, "name": LABEL_NAME}],
                "actions": [],
                "sounds": [],
            }
        ])
        swf = _compile(n2d)
        raw_swf = swf
        # Find the DefineSprite body and scan inside it for FrameLabel
        sprite_bodies = _find_all_tags(raw_swf, 39)
        assert sprite_bodies, "No DefineSprite found"
        # The label should appear as a null-terminated string inside a FrameLabel tag
        label_bytes = LABEL_NAME.encode("utf-8") + b"\x00"
        found = any(label_bytes in body for body in sprite_bodies)
        assert found, f"Label '{LABEL_NAME}' not found inside DefineSprite"


# ═══════════════════════════════════════════════════════════════════════════
# TEST 5 — Button state edit persists
# ═══════════════════════════════════════════════════════════════════════════

class TestButtonEditPersists:
    """Button stored as 4-frame container is emitted as DefineButton2 (tag 34)."""

    def _button_n2d_with_shape(self):
        # A button container referencing a shape lib entry
        return _base_n2d([
            # Shape that button references
            {
                "id": 1,
                "swfCharId": 50,
                "type": "shape",
                "name": "BtnShape",
                "symbol": "",
                "folderId": 0,
                "recodes": [],
                "bounds": {"xMin": 0, "xMax": 100, "yMin": 0, "yMax": 50},
            },
            # Button as 4*3=12-frame container
            {
                "id": 2,
                "swfCharId": 51,
                "type": "container",
                "isButton": True,
                "buttonTrackAsMenu": False,
                "buttonActions": [],
                "name": "MyButton",
                "symbol": "",
                "folderId": 0,
                "totalFrame": 12,
                "currentFrame": 1,
                "leftFrame": 1,
                "labels": [
                    {"frame": 1, "name": "up"},
                    {"frame": 4, "name": "over"},
                    {"frame": 7, "name": "down"},
                    {"frame": 10, "name": "hit"},
                ],
                "layers": [
                    {
                        "name": "depth_1",
                        "swfDepth": 1,
                        "light": False,
                        "disable": False,
                        "lock": False,
                        "mode": 0,
                        "maskId": None,
                        "guideId": None,
                        "color": "#ff0000",
                        "characters": [
                            {
                                "id": 100,
                                "name": "",
                                "libraryId": 1,
                                "startFrame": 1,
                                "endFrame": 13,
                                "tween": [],
                                "places": [
                                    {
                                        "frame": 1,
                                        "depth": 0,
                                        "blendMode": "normal",
                                        "filter": [],
                                        "matrix": [1, 0, 0, 1, 0, 0],
                                        "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                                    }
                                ],
                            }
                        ],
                        "emptyCharacters": [],
                    }
                ],
                "actions": [],
                "sounds": [],
                "bounds": {"xMin": 0, "xMax": 100, "yMin": 0, "yMax": 50},
            },
        ])

    def test_button_emitted_as_definebutton2(self):
        n2d = self._button_n2d_with_shape()
        swf = _compile(n2d)
        bodies = _find_all_tags(swf, 34)  # DefineButton2
        assert bodies, "No DefineButton2 (tag 34) found — button not emitted"

    def test_button_has_all_state_bits(self):
        """A shape present in all 4 states must have state bits 0x0F."""
        n2d = self._button_n2d_with_shape()
        swf = _compile(n2d)
        bodies = _find_all_tags(swf, 34)
        assert bodies
        # DefineButton2 body: charID(2) + trackFlags(1) + actionOffset(2) + ButtonRecords
        # Each ButtonRecord starts with state flags byte
        btn_body = bodies[0]
        parsed_ok = False
        if len(btn_body) >= 6:
            off = 5  # skip charID(2) + trackFlags(1) + actionOffset(2)
            while off < len(btn_body):
                state_flags = btn_body[off]
                if state_flags == 0:
                    break
                # All four states: 0x01|0x02|0x04|0x08 = 0x0F
                if state_flags & 0x0F == 0x0F:
                    parsed_ok = True
                    break
                off += 1
        assert parsed_ok, "Button record with all-states (0x0F) not found in DefineButton2"

    def test_no_button_aux_tags_in_output(self):
        """buttonAuxTags (DefineButtonSound=17, DefineButtonCxform=23) must not appear."""
        n2d = self._button_n2d_with_shape()
        swf = _compile(n2d)
        # Tag 17 = DefineButtonSound, tag 23 = DefineButtonCxform
        for t in (17, 23):
            bodies = _find_all_tags(swf, t)
            assert not bodies, f"Unexpected raw button aux tag {t} in output SWF"


# ═══════════════════════════════════════════════════════════════════════════
# TEST 6 — No legacy raw passthrough fields in compiler source
# ═══════════════════════════════════════════════════════════════════════════

class TestNoRawPassthroughInSource:
    """Static analysis: ensure banned passthrough fields are absent from compiler."""

    def _get_source(self, module_name):
        import importlib, inspect
        mod = importlib.import_module(module_name)
        return inspect.getsource(mod)

    def test_no_raw_global_tags_in_pipeline(self):
        src = self._get_source("compilation_pipeline")
        # Legacy fallback block must be gone
        assert "for rgt in raw_global" not in src, \
            "rawGlobalTags legacy loop still exists in compilation_pipeline"

    def test_no_raw_sound_body_in_compiler(self):
        src = self._get_source("compile_n2d")
        assert "rawSoundBody" not in src, \
            "rawSoundBody still read in compile_n2d"

    def test_no_raw_tag_type_dispatch_in_compiler(self):
        src = self._get_source("compile_n2d")
        # rawTagType is allowed only as a bitmap format hint (JPEG vs LL2) read
        # during emission.  Banned uses are raw shape/sprite passthrough — e.g.
        # re-emitting the original tag body verbatim based on rawTagType.
        # These banned patterns were already removed; verify they are absent.
        banned_patterns = ["rawTagType in (26", "rawTagType == 82", "rawTagType in (82"]
        for pat in banned_patterns:
            assert pat not in src, f"Banned rawTagType passthrough pattern found: {pat!r}"

    def test_no_font_aux_tags_legacy_in_pipeline(self):
        src = self._get_source("compilation_pipeline")
        # Only check actual code lines (not docstrings/comments)
        code_lines = [
            l for l in src.splitlines()
            if "fontAuxTags" in l
            and not l.strip().startswith("#")
            and not l.strip().startswith('"""')
            and not l.strip().startswith("'")
            and "lib.get" in l
        ]
        assert not code_lines, \
            f"fontAuxTags legacy lib.get() still exists in compilation_pipeline: {code_lines}"

    def test_no_button_aux_tags_in_compiler(self):
        src = self._get_source("compile_n2d")
        lines = [
            l for l in src.splitlines()
            if "buttonAuxTags" in l and not l.strip().startswith("#")
        ]
        assert not lines, \
            f"buttonAuxTags still emitted in compile_n2d: {lines}"

    def test_no_button_aux_tags_written_in_importer(self):
        src = self._get_source("swf_to_n2d")
        lines = [
            l for l in src.splitlines()
            if "buttonAuxTags" in l
            and "entry[" in l
            and not l.strip().startswith("#")
        ]
        assert not lines, \
            f"buttonAuxTags still written by swf_to_n2d importer: {lines}"


# ═══════════════════════════════════════════════════════════════════════════
# TEST 7 — _merge_editor_into_disk: editor text overwrites disk text
# ═══════════════════════════════════════════════════════════════════════════

class TestMergeEditorIntoDisk:
    """server._merge_editor_into_disk must let editor text win over disk text."""

    def _merge(self, disk_lib, editor_lib):
        from server import _merge_editor_into_disk
        disk = {"libraries": [disk_lib.copy()]}
        editor = {"libraries": [editor_lib.copy()]}
        _merge_editor_into_disk(editor, disk)
        return disk["libraries"][0]

    def _base_text_lib(self, text, extra=None):
        lib = {
            "id": 5,
            "swfCharId": 99,
            "type": "text",
            "name": "T",
            "symbol": "",
            "folderId": 0,
            "text": text,
            "html": False,
            "font": "Arial",
            "size": 12,
            "color": 0,
            "bounds": {"xMin": 0, "xMax": 100, "yMin": 0, "yMax": 20},
        }
        if extra:
            lib.update(extra)
        return lib

    def test_editor_text_wins(self):
        disk = self._base_text_lib("ORIGINAL")
        editor = self._base_text_lib("EDITED BY USER")
        result = self._merge(disk, editor)
        assert result["text"] == "EDITED BY USER", \
            f"Editor text not applied; got: {result['text']}"

    def test_swf_char_id_preserved_from_disk(self):
        """swfCharId must come from disk, not editor (editor doesn't carry it)."""
        disk = self._base_text_lib("orig")
        editor = self._base_text_lib("new")
        editor.pop("swfCharId", None)  # editor blob never has this
        result = self._merge(disk, editor)
        assert result.get("swfCharId") == 99, \
            "swfCharId lost after merge"

    def test_html_not_locked_to_disk(self):
        """`html` field must come from editor, not be forced from disk."""
        disk = self._base_text_lib("old", {"html": True, "htmlText": "<p>old</p>"})
        editor = self._base_text_lib("new text", {"html": False})
        result = self._merge(disk, editor)
        assert result.get("html") is False, \
            "html flag locked to disk value — roundtrip key bug"

    def test_font_change_triggers_rebuild(self):
        """Changing font must result in new font in merged lib (no locked font key)."""
        disk = self._base_text_lib("text", {"font": "OldFont"})
        editor = self._base_text_lib("text", {"font": "NewFont"})
        result = self._merge(disk, editor)
        assert result.get("font") == "NewFont", \
            f"Font change lost; got: {result.get('font')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
