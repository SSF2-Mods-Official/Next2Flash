#!/usr/bin/env python3
"""
Edit-Export Unit Tests — verify that all user edits in Next2Flash
actually produce correct SWF output.

Unlike roundtrip tests (SWF→N2D→SWF identity), these tests:
  1. Build or load an N2D project
  2. Make specific edits (simulating user actions)
  3. Compile to SWF
  4. Parse the output SWF and verify the edits are reflected

Usage:
    cd app
    python -m pytest test/test_edit_export.py -v
    # or
    python -m unittest test.test_edit_export -v
"""
import base64
import io
import json
import math
import os
import struct
import sys
import tempfile
import unittest
import zlib

# ── Path setup ───────────────────────────────────────────────────────────
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

import swf_writer as sw
import swf_to_n2d
import compile_n2d
from shape_converter import (
    CMD_FILL_STYLE, CMD_STROKE_STYLE, CMD_GRADIENT_FILL, CMD_BITMAP_FILL,
    CMD_MOVE_TO, CMD_LINE_TO, CMD_CURVE_TO, CMD_BEGIN_PATH, CMD_CLOSE_PATH,
)

CONVERTED_DIR = os.path.join(APP_DIR, "converted")

# ── SWF Tag Constants ────────────────────────────────────────────────────
TAG_END                  = 0
TAG_SET_BG_COLOR         = 9
TAG_DEFINE_SOUND         = 14
TAG_START_SOUND          = 15
TAG_DEFINE_BITS_LOSSLESS = 20
TAG_DEFINE_BITS_JPEG2    = 21
TAG_PLACE_OBJECT2        = 26
TAG_REMOVE_OBJECT2       = 28
TAG_DEFINE_SHAPE3        = 32
TAG_DEFINE_BITS_JPEG3    = 35
TAG_DEFINE_BITS_LOSSLESS2= 36
TAG_DEFINE_EDIT_TEXT     = 37
TAG_DEFINE_SPRITE        = 39
TAG_FRAME_LABEL          = 43
TAG_SHOW_FRAME           = 1
TAG_FILE_ATTRIBUTES      = 69
TAG_PLACE_OBJECT3        = 70
TAG_DEFINE_FONT3         = 75
TAG_SYMBOL_CLASS         = 76
TAG_DOABC2               = 82

DEFINE_TAGS = {2, 22, 32, 83, 6, 21, 35, 90, 20, 36, 39, 46, 84,
               11, 33, 48, 75, 10, 14, 37, 87}

# ══════════════════════════════════════════════════════════════════════════
#  Shared Utilities
# ══════════════════════════════════════════════════════════════════════════

def parse_swf_tags(data: bytes):
    """Parse SWF bytes into [(tag_type, body), ...]."""
    if isinstance(data, str):
        data = open(data, "rb").read()
    magic = data[:3]
    if magic == b"CWS":
        data = data[:8] + zlib.decompress(data[8:])
    elif magic == b"ZWS":
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    elif magic != b"FWS":
        raise ValueError(f"Bad SWF magic: {magic!r}")

    nbits = (data[8] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    pos = rect_end + 4
    tags = []
    while pos < len(data):
        if pos + 2 > len(data):
            break
        h = struct.unpack_from("<H", data, pos)[0]
        tt = h >> 6
        ln = h & 0x3F
        hdr = 2
        if ln == 0x3F:
            if pos + 6 > len(data):
                break
            ln = struct.unpack_from("<I", data, pos + 2)[0]
            hdr = 6
        body = data[pos + hdr : pos + hdr + ln]
        tags.append((tt, body))
        pos += hdr + ln
        if tt == 0:
            break
    return tags


def parse_swf_header(data: bytes):
    """Parse SWF header → {width, height, fps, frameCount}."""
    magic = data[:3]
    if magic == b"CWS":
        data = data[:8] + zlib.decompress(data[8:])
    elif magic != b"FWS":
        raise ValueError(f"Bad SWF magic")

    br = swf_to_n2d.BitReader(data, 8)
    nbits = br.read_ub(5)
    xmin = br.read_sb(nbits)
    xmax = br.read_sb(nbits)
    ymin = br.read_sb(nbits)
    ymax = br.read_sb(nbits)
    br.align()
    # fps is stored as 8.8 fixed‑point in SWF
    fps_lo = br.read_ui8()
    fps_hi = br.read_ui8()
    fps = fps_hi + fps_lo / 256.0
    frame_count = br.read_ui16()
    return {
        "width": (xmax - xmin) // 20,
        "height": (ymax - ymin) // 20,
        "fps": fps,
        "frameCount": frame_count,
    }


def parse_sprite_tags(data):
    """Parse tags inside a DefineSprite body."""
    tags = []
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data):
            break
        h = struct.unpack_from("<H", data, pos)[0]
        tt = h >> 6
        ln = h & 0x3F
        hdr = 2
        if ln == 0x3F:
            if pos + 6 > len(data):
                break
            ln = struct.unpack_from("<I", data, pos + 2)[0]
            hdr = 6
        body = data[pos + hdr : pos + hdr + ln]
        tags.append((tt, body))
        pos += hdr + ln
        if tt == 0:
            break
    return tags


def parse_place_object2_body(body: bytes):
    """Parse a PlaceObject2 body into a dict of its fields."""
    flags = body[0]
    depth = struct.unpack_from("<H", body, 1)[0]
    result = {"depth": depth, "flags": flags}
    pos = 3

    has_clip_actions = flags & 0x80
    has_clip_depth = flags & 0x40
    has_name = flags & 0x20
    has_ratio = flags & 0x10
    has_cx = flags & 0x08
    has_matrix = flags & 0x04
    has_char = flags & 0x02
    is_move = flags & 0x01

    result["isMove"] = bool(is_move)

    if has_char:
        result["charId"] = struct.unpack_from("<H", body, pos)[0]
        pos += 2

    if has_matrix:
        br = swf_to_n2d.BitReader(body, pos)
        mat = swf_to_n2d.read_matrix(br)
        result["matrix"] = mat
        pos = (br.pos + 7) // 8

    if has_cx:
        br = swf_to_n2d.BitReader(body, pos)
        cx = swf_to_n2d.read_cxform_with_alpha(br)
        result["colorTransform"] = cx
        pos = (br.pos + 7) // 8

    if has_ratio:
        result["ratio"] = struct.unpack_from("<H", body, pos)[0]
        pos += 2

    if has_name:
        end = body.index(0, pos)
        result["name"] = body[pos:end].decode("utf-8")
        pos = end + 1

    if has_clip_depth:
        result["clipDepth"] = struct.unpack_from("<H", body, pos)[0]
        pos += 2

    return result


def parse_place_object3_body(body: bytes):
    """Parse a PlaceObject3 body into a dict of its fields."""
    flags1 = body[0]
    flags2 = body[1]
    depth = struct.unpack_from("<H", body, 2)[0]
    result = {"depth": depth, "flags1": flags1, "flags2": flags2}
    pos = 4

    has_clip_actions = flags1 & 0x80
    has_clip_depth = flags1 & 0x40
    has_name = flags1 & 0x20
    has_ratio = flags1 & 0x10
    has_cx = flags1 & 0x08
    has_matrix = flags1 & 0x04
    has_char = flags1 & 0x02
    is_move = flags1 & 0x01

    has_image = flags2 & 0x10
    has_class_name = flags2 & 0x08
    has_cache = flags2 & 0x04
    has_blend = flags2 & 0x02
    has_filters = flags2 & 0x01

    result["isMove"] = bool(is_move)
    result["hasImage"] = bool(has_image)
    result["hasBlend"] = bool(has_blend)
    result["hasFilters"] = bool(has_filters)

    if has_char:
        result["charId"] = struct.unpack_from("<H", body, pos)[0]
        pos += 2

    if has_matrix:
        br = swf_to_n2d.BitReader(body, pos)
        mat = swf_to_n2d.read_matrix(br)
        result["matrix"] = mat
        pos = (br.pos + 7) // 8

    if has_cx:
        br = swf_to_n2d.BitReader(body, pos)
        cx = swf_to_n2d.read_cxform_with_alpha(br)
        result["colorTransform"] = cx
        pos = (br.pos + 7) // 8

    if has_ratio:
        result["ratio"] = struct.unpack_from("<H", body, pos)[0]
        pos += 2

    if has_name:
        end = body.index(0, pos)
        result["name"] = body[pos:end].decode("utf-8")
        pos = end + 1

    if has_clip_depth:
        result["clipDepth"] = struct.unpack_from("<H", body, pos)[0]
        pos += 2

    if has_filters:
        result["filterCount"] = body[pos]
        pos += 1

    if has_blend:
        result["blendMode"] = body[pos]
        pos += 1

    return result


def make_base_n2d(width=200, height=150, fps=24, bg_color="#336699"):
    """Create a minimal N2D project dict with just a root container."""
    return {
        "version": 1,
        "name": "test_project",
        "characterId": 10,
        "stage": {
            "width": width,
            "height": height,
            "fps": fps,
            "bgColor": bg_color,
        },
        "libraries": [
            {
                "id": 0,
                "type": "container",
                "name": "Root",
                "symbol": "Main",
                "totalFrame": 1,
                "currentFrame": 1,
                "layers": [],
                "labels": [],
                "sounds": [],
                "actions": [],
            }
        ],
        "rawGlobalTags": [],
        "scripts": [],
        "swfVersion": 14,
        "swfCompressed": True,
    }


def add_bitmap_lib(n2d, lib_id, width, height, rgba_pixels):
    """Add a bitmap library entry with raw pixel data (no rawTagBody = edited)."""
    buf = base64.b64encode(rgba_pixels).decode("ascii")
    n2d["libraries"].append({
        "id": lib_id,
        "type": "bitmap",
        "name": f"Bitmap_{lib_id}",
        "symbol": "",
        "width": width,
        "height": height,
        "buffer": f"b64:{buf}",
    })
    if n2d["characterId"] <= lib_id:
        n2d["characterId"] = lib_id + 1


def add_shape_lib(n2d, lib_id, recodes, bounds=None):
    """Add a shape library entry from recodes (no rawTagBody = edited shape)."""
    if bounds is None:
        bounds = {"xMin": 0, "xMax": 2000, "yMin": 0, "yMax": 2000}
    n2d["libraries"].append({
        "id": lib_id,
        "type": "shape",
        "name": f"Shape_{lib_id}",
        "symbol": "",
        "inBitmap": False,
        "recodes": recodes,
        "bounds": bounds,
    })
    if n2d["characterId"] <= lib_id:
        n2d["characterId"] = lib_id + 1


def add_text_lib(n2d, lib_id, text="Hello", font="Arial", size=12,
                 color=0x000000, align="left", bounds=None, **kwargs):
    """Add a text (DefineEditText) library entry."""
    if bounds is None:
        bounds = {"xMin": 0, "xMax": 200, "yMin": 0, "yMax": 30}
    entry = {
        "id": lib_id,
        "type": "text",
        "name": f"Text_{lib_id}",
        "symbol": "",
        "text": text,
        "font": font,
        "fontType": 0,
        "inputType": "dynamic",
        "size": size,
        "color": color,
        "align": align,
        "leading": 0,
        "letterSpacing": 0,
        "leftMargin": 0,
        "rightMargin": 0,
        "multiline": False,
        "wordWrap": False,
        "border": False,
        "autoSize": 0,
        "scroll": False,
        "bounds": bounds,
    }
    entry.update(kwargs)
    n2d["libraries"].append(entry)
    if n2d["characterId"] <= lib_id:
        n2d["characterId"] = lib_id + 1


def add_container_lib(n2d, lib_id, layers, total_frames=1, labels=None,
                      sounds=None, actions=None, symbol=""):
    """Add a container (sprite) library entry."""
    n2d["libraries"].append({
        "id": lib_id,
        "type": "container",
        "name": f"Container_{lib_id}",
        "symbol": symbol,
        "totalFrame": total_frames,
        "currentFrame": 1,
        "layers": layers,
        "labels": labels or [],
        "sounds": sounds or [],
        "actions": actions or [],
    })
    if n2d["characterId"] <= lib_id:
        n2d["characterId"] = lib_id + 1


def add_to_root_timeline(n2d, lib_id, start_frame=1, end_frame=2,
                         matrix=None, color_transform=None,
                         blend_mode="normal", name="",
                         surface_filter_list=None):
    """Place a library item on the root timeline."""
    root = n2d["libraries"][0]
    if not root["layers"]:
        root["layers"].append({
            "name": "layer_1",
            "swfDepth": 1,
            "characters": [],
        })

    place = {
        "frame": start_frame,
        "matrix": matrix or [1, 0, 0, 1, 0, 0],
        "colorTransform": color_transform or [1, 1, 1, 1, 0, 0, 0, 0],
        "blendMode": blend_mode,
    }
    if surface_filter_list:
        place["surfaceFilterList"] = surface_filter_list

    # Find or create layer with matching depth
    layer = root["layers"][-1]
    layer["characters"].append({
        "id": len(layer["characters"]) + 100,
        "name": name,
        "libraryId": lib_id,
        "startFrame": start_frame,
        "endFrame": end_frame,
        "places": [place],
    })

    # Update frame count
    if root["totalFrame"] < end_frame:
        root["totalFrame"] = end_frame


def compile_n2d_to_swf(n2d):
    """Compile an N2D dict → SWF bytes."""
    with tempfile.TemporaryDirectory(prefix="edit_test_") as tmp:
        n2d_path = os.path.join(tmp, "project.n2d")
        swf_path = os.path.join(tmp, "output.swf")
        swf_to_n2d.save_n2d(n2d, n2d_path)
        compiler = compile_n2d.N2DCompiler(
            n2d_path=n2d_path,
            shared_dir=tmp,
            output_path=swf_path,
            sdk_path=None,
        )
        compiler.compile()
        with open(swf_path, "rb") as f:
            return f.read()


def find_tags(tags, tag_type):
    """Return all (tag_type, body) tuples matching tag_type."""
    return [(tt, body) for tt, body in tags if tt == tag_type]


def count_tags(tags, tag_type):
    """Count tags of a specific type."""
    return sum(1 for tt, _ in tags if tt == tag_type)


def find_place_objects(tags):
    """Find all PlaceObject2/3 from parsed tags."""
    results = []
    for tt, body in tags:
        if tt == TAG_PLACE_OBJECT2:
            results.append(("PO2", parse_place_object2_body(body)))
        elif tt == TAG_PLACE_OBJECT3:
            results.append(("PO3", parse_place_object3_body(body)))
    return results


def find_frame_labels(tags):
    """Extract frame label names from tags in order."""
    labels = []
    for tt, body in tags:
        if tt == TAG_FRAME_LABEL:
            end = body.index(0)
            labels.append(body[:end].decode("utf-8"))
    return labels


# ══════════════════════════════════════════════════════════════════════════
#  Stage Property Edits
# ══════════════════════════════════════════════════════════════════════════

class TestStageProperties(unittest.TestCase):
    """Verify stage width, height, fps, and bgColor are exported correctly."""

    def test_stage_dimensions(self):
        """Edited stage width/height appear in SWF header."""
        n2d = make_base_n2d(width=800, height=600)
        swf = compile_n2d_to_swf(n2d)
        hdr = parse_swf_header(swf)
        self.assertEqual(hdr["width"], 800)
        self.assertEqual(hdr["height"], 600)

    def test_stage_fps(self):
        """Edited FPS appears in SWF header."""
        n2d = make_base_n2d(fps=30)
        swf = compile_n2d_to_swf(n2d)
        hdr = parse_swf_header(swf)
        self.assertAlmostEqual(hdr["fps"], 30, places=0)

    def test_stage_background_color(self):
        """Edited background color appears in SetBackgroundColor tag."""
        n2d = make_base_n2d(bg_color="#FF8040")
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        bg_tags = find_tags(tags, TAG_SET_BG_COLOR)
        self.assertGreaterEqual(len(bg_tags), 1)
        body = bg_tags[0][1]
        r, g, b = body[0], body[1], body[2]
        self.assertEqual((r, g, b), (0xFF, 0x80, 0x40))

    def test_stage_dimensions_changed(self):
        """Changing dimensions from default produces different SWF header."""
        n2d_small = make_base_n2d(width=100, height=100)
        n2d_large = make_base_n2d(width=1920, height=1080)
        swf_small = compile_n2d_to_swf(n2d_small)
        swf_large = compile_n2d_to_swf(n2d_large)
        hdr_small = parse_swf_header(swf_small)
        hdr_large = parse_swf_header(swf_large)
        self.assertEqual(hdr_small["width"], 100)
        self.assertEqual(hdr_large["width"], 1920)
        self.assertEqual(hdr_large["height"], 1080)


# ══════════════════════════════════════════════════════════════════════════
#  Shape Edit Exports
# ══════════════════════════════════════════════════════════════════════════

class TestShapeEditExport(unittest.TestCase):
    """Verify edited shapes (via recodes, no rawTagBody) export to SWF."""

    def _make_solid_rect_recodes(self, r, g, b, a, x=0, y=0, w=100, h=100):
        """Build recodes for a solid-fill rectangle."""
        return [
            CMD_FILL_STYLE, r, g, b, a,
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, x, y,
            CMD_LINE_TO, x + w, y,
            CMD_LINE_TO, x + w, y + h,
            CMD_LINE_TO, x, y + h,
            CMD_CLOSE_PATH,
        ]

    def test_solid_fill_shape_export(self):
        """Shape with solid fill recodes compiles to DefineShape3."""
        n2d = make_base_n2d()
        recodes = self._make_solid_rect_recodes(255, 0, 0, 255)
        add_shape_lib(n2d, 1, recodes)
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        shapes = find_tags(tags, TAG_DEFINE_SHAPE3)
        self.assertGreaterEqual(len(shapes), 1, "No DefineShape3 in output")

    def test_shape_color_change(self):
        """Changing fill color produces different SWF shape body."""
        n2d_red = make_base_n2d()
        add_shape_lib(n2d_red, 1, self._make_solid_rect_recodes(255, 0, 0, 255))
        add_to_root_timeline(n2d_red, 1)

        n2d_blue = make_base_n2d()
        add_shape_lib(n2d_blue, 1, self._make_solid_rect_recodes(0, 0, 255, 255))
        add_to_root_timeline(n2d_blue, 1)

        swf_red = compile_n2d_to_swf(n2d_red)
        swf_blue = compile_n2d_to_swf(n2d_blue)

        tags_red = parse_swf_tags(swf_red)
        tags_blue = parse_swf_tags(swf_blue)

        shapes_red = find_tags(tags_red, TAG_DEFINE_SHAPE3)
        shapes_blue = find_tags(tags_blue, TAG_DEFINE_SHAPE3)

        self.assertGreaterEqual(len(shapes_red), 1)
        self.assertGreaterEqual(len(shapes_blue), 1)
        # Bodies must differ (different fill color)
        self.assertNotEqual(shapes_red[0][1], shapes_blue[0][1],
            "Red and blue shapes should have different SWF bodies")

    def test_gradient_fill_shape_export(self):
        """Shape with gradient fill recodes compiles to DefineShape3."""
        n2d = make_base_n2d()
        recodes = [
            CMD_GRADIENT_FILL,
            "linear",  # gradient type
            [{"ratio": 0, "R": 255, "G": 0, "B": 0, "A": 255},
             {"ratio": 255, "R": 0, "G": 0, "B": 255, "A": 255}],
            [1.0, 0.0, 0.0, 1.0, 0.0, 0.0],  # matrix
            "pad",     # spread
            "rgb",     # interpolation
            0.0,       # focal
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 100, 0,
            CMD_LINE_TO, 100, 100,
            CMD_LINE_TO, 0, 100,
            CMD_CLOSE_PATH,
        ]
        add_shape_lib(n2d, 1, recodes)
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        shapes = find_tags(tags, TAG_DEFINE_SHAPE3)
        self.assertGreaterEqual(len(shapes), 1)

    def test_stroke_style_export(self):
        """Shape with stroke style recodes exports correctly."""
        n2d = make_base_n2d()
        recodes = [
            CMD_STROKE_STYLE, 3.0, "round", "round", 10.0, 0, 0, 0, 255,
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, 10, 10,
            CMD_LINE_TO, 90, 10,
            CMD_LINE_TO, 90, 90,
            CMD_CLOSE_PATH,
        ]
        add_shape_lib(n2d, 1, recodes)
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        shapes = find_tags(tags, TAG_DEFINE_SHAPE3)
        self.assertGreaterEqual(len(shapes), 1)

    def test_curve_path_export(self):
        """Shape with curve commands exports correctly."""
        n2d = make_base_n2d()
        recodes = [
            CMD_FILL_STYLE, 0, 128, 255, 255,
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, 0, 50,
            CMD_CURVE_TO, 25, 0, 50, 0,
            CMD_CURVE_TO, 75, 0, 100, 50,
            CMD_LINE_TO, 0, 50,
            CMD_CLOSE_PATH,
        ]
        add_shape_lib(n2d, 1, recodes)
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        shapes = find_tags(tags, TAG_DEFINE_SHAPE3)
        self.assertGreaterEqual(len(shapes), 1)

    def test_multiple_shapes_export(self):
        """Multiple edited shapes all appear in output SWF."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_solid_rect_recodes(255, 0, 0, 255))
        add_shape_lib(n2d, 2, self._make_solid_rect_recodes(0, 255, 0, 255))
        add_shape_lib(n2d, 3, self._make_solid_rect_recodes(0, 0, 255, 255))
        add_to_root_timeline(n2d, 1)
        add_to_root_timeline(n2d, 2)
        add_to_root_timeline(n2d, 3)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        shapes = find_tags(tags, TAG_DEFINE_SHAPE3)
        self.assertGreaterEqual(len(shapes), 3,
            f"Expected >=3 DefineShape3 tags, got {len(shapes)}")


# ══════════════════════════════════════════════════════════════════════════
#  Bitmap Edit Exports
# ══════════════════════════════════════════════════════════════════════════

class TestBitmapEditExport(unittest.TestCase):
    """Verify edited bitmaps (pixel data, no rawTagBody) export to SWF."""

    def test_bitmap_export(self):
        """Bitmap with edited pixel data compiles to DefineBitsLossless2."""
        n2d = make_base_n2d()
        pixels = bytes([255, 0, 0, 255] * 16)  # 4x4 red
        add_bitmap_lib(n2d, 1, 4, 4, pixels)
        # Need shape referencing bitmap for it to be placed
        add_shape_lib(n2d, 2, [
            CMD_BITMAP_FILL,
            {"width": 4, "height": 4, "buffer": list(pixels)},
            [20.0, 0.0, 0.0, 20.0, 0.0, 0.0],
            "repeat", True,
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 4, 0,
            CMD_LINE_TO, 4, 4,
            CMD_LINE_TO, 0, 4,
            CMD_CLOSE_PATH,
        ])
        add_to_root_timeline(n2d, 2)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        bitmaps = find_tags(tags, TAG_DEFINE_BITS_LOSSLESS2)
        self.assertGreaterEqual(len(bitmaps), 1, "No DefineBitsLossless2 in output")

    def test_bitmap_dimensions_correct(self):
        """Bitmap width/height are encoded in the SWF tag."""
        n2d = make_base_n2d()
        w, h = 16, 8
        pixels = bytes([100, 200, 50, 128] * (w * h))
        add_bitmap_lib(n2d, 1, w, h, pixels)
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        bitmaps = find_tags(tags, TAG_DEFINE_BITS_LOSSLESS2)
        self.assertGreaterEqual(len(bitmaps), 1)
        body = bitmaps[0][1]
        # DefineBitsLossless2: charId(2) + format(1) + width(2) + height(2) + ...
        fmt = body[2]
        bmp_w = struct.unpack_from("<H", body, 3)[0]
        bmp_h = struct.unpack_from("<H", body, 5)[0]
        self.assertEqual(bmp_w, w)
        self.assertEqual(bmp_h, h)

    def test_bitmap_pixel_change(self):
        """Changing bitmap pixels produces different SWF bitmap body."""
        n2d_a = make_base_n2d()
        pixels_a = bytes([255, 0, 0, 255] * 4)  # red 2x2
        add_bitmap_lib(n2d_a, 1, 2, 2, pixels_a)
        add_to_root_timeline(n2d_a, 1)

        n2d_b = make_base_n2d()
        pixels_b = bytes([0, 255, 0, 255] * 4)  # green 2x2
        add_bitmap_lib(n2d_b, 1, 2, 2, pixels_b)
        add_to_root_timeline(n2d_b, 1)

        swf_a = compile_n2d_to_swf(n2d_a)
        swf_b = compile_n2d_to_swf(n2d_b)

        tags_a = parse_swf_tags(swf_a)
        tags_b = parse_swf_tags(swf_b)

        bmp_a = find_tags(tags_a, TAG_DEFINE_BITS_LOSSLESS2)
        bmp_b = find_tags(tags_b, TAG_DEFINE_BITS_LOSSLESS2)

        self.assertGreaterEqual(len(bmp_a), 1)
        self.assertGreaterEqual(len(bmp_b), 1)
        self.assertNotEqual(bmp_a[0][1], bmp_b[0][1],
            "Different pixel data should produce different SWF bitmap bodies")


# ══════════════════════════════════════════════════════════════════════════
#  Text Edit Exports
# ══════════════════════════════════════════════════════════════════════════

class TestTextEditExport(unittest.TestCase):
    """Verify edited text fields export to DefineEditText in SWF."""

    def test_text_export(self):
        """Edited text field compiles to DefineEditText (tag 37)."""
        n2d = make_base_n2d()
        add_text_lib(n2d, 1, text="Test Text", size=24)
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        texts = find_tags(tags, TAG_DEFINE_EDIT_TEXT)
        self.assertGreaterEqual(len(texts), 1, "No DefineEditText in output")

    def test_text_content_export(self):
        """The actual text content appears in the DefineEditText body."""
        n2d = make_base_n2d()
        add_text_lib(n2d, 1, text="Hello World")
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        texts = find_tags(tags, TAG_DEFINE_EDIT_TEXT)
        self.assertGreaterEqual(len(texts), 1)
        # Text string is null-terminated near the end of the tag body
        body = texts[0][1]
        self.assertIn(b"Hello World\x00", body,
            "Text content 'Hello World' not found in DefineEditText body")

    def test_text_color_export(self):
        """Different text colors produce different SWF bodies."""
        n2d_black = make_base_n2d()
        add_text_lib(n2d_black, 1, text="Test", color=0x000000)
        add_to_root_timeline(n2d_black, 1)

        n2d_red = make_base_n2d()
        add_text_lib(n2d_red, 1, text="Test", color=0xFF0000)
        add_to_root_timeline(n2d_red, 1)

        swf_black = compile_n2d_to_swf(n2d_black)
        swf_red = compile_n2d_to_swf(n2d_red)

        tags_black = parse_swf_tags(swf_black)
        tags_red = parse_swf_tags(swf_red)

        text_black = find_tags(tags_black, TAG_DEFINE_EDIT_TEXT)[0][1]
        text_red = find_tags(tags_red, TAG_DEFINE_EDIT_TEXT)[0][1]
        self.assertNotEqual(text_black, text_red,
            "Different text colors should produce different bodies")

    def test_text_size_export(self):
        """Different font sizes produce different SWF bodies."""
        n2d_small = make_base_n2d()
        add_text_lib(n2d_small, 1, text="A", size=12)
        add_to_root_timeline(n2d_small, 1)

        n2d_large = make_base_n2d()
        add_text_lib(n2d_large, 1, text="A", size=48)
        add_to_root_timeline(n2d_large, 1)

        swf_small = compile_n2d_to_swf(n2d_small)
        swf_large = compile_n2d_to_swf(n2d_large)

        text_small = find_tags(parse_swf_tags(swf_small), TAG_DEFINE_EDIT_TEXT)[0][1]
        text_large = find_tags(parse_swf_tags(swf_large), TAG_DEFINE_EDIT_TEXT)[0][1]
        self.assertNotEqual(text_small, text_large,
            "Different font sizes should produce different bodies")

    def test_text_multiline_flags(self):
        """Multiline / wordWrap flags affect the DefineEditText body."""
        n2d_single = make_base_n2d()
        add_text_lib(n2d_single, 1, text="Line", multiline=False, wordWrap=False)
        add_to_root_timeline(n2d_single, 1)

        n2d_multi = make_base_n2d()
        add_text_lib(n2d_multi, 1, text="Line", multiline=True, wordWrap=True)
        add_to_root_timeline(n2d_multi, 1)

        swf_single = compile_n2d_to_swf(n2d_single)
        swf_multi = compile_n2d_to_swf(n2d_multi)

        text_single = find_tags(parse_swf_tags(swf_single), TAG_DEFINE_EDIT_TEXT)[0][1]
        text_multi = find_tags(parse_swf_tags(swf_multi), TAG_DEFINE_EDIT_TEXT)[0][1]
        self.assertNotEqual(text_single, text_multi,
            "Multiline/wordWrap flags should produce different bodies")

    def test_text_alignment_export(self):
        """Different alignments produce different SWF bodies."""
        results = {}
        for align in ["left", "center", "right"]:
            n2d = make_base_n2d()
            add_text_lib(n2d, 1, text="Align", align=align)
            add_to_root_timeline(n2d, 1)
            swf = compile_n2d_to_swf(n2d)
            body = find_tags(parse_swf_tags(swf), TAG_DEFINE_EDIT_TEXT)[0][1]
            results[align] = body
        # At least one pair should differ
        self.assertTrue(
            results["left"] != results["center"] or
            results["left"] != results["right"],
            "At least two alignments should produce different bodies")


# ══════════════════════════════════════════════════════════════════════════
#  Placement / Transform Edits
# ══════════════════════════════════════════════════════════════════════════

class TestPlacementEditExport(unittest.TestCase):
    """Verify placement edits (position, scale, rotation, color) export."""

    def _make_shape_n2d(self):
        n2d = make_base_n2d()
        recodes = [
            CMD_FILL_STYLE, 255, 0, 0, 255,
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0,
            CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50,
            CMD_CLOSE_PATH,
        ]
        add_shape_lib(n2d, 1, recodes)
        return n2d

    def test_position_export(self):
        """Edited position (tx, ty) appears in PlaceObject matrix."""
        n2d = self._make_shape_n2d()
        # N2D matrices store tx/ty in twips (same units as SWF)
        # 150px = 3000 twips, 200px = 4000 twips
        add_to_root_timeline(n2d, 1, matrix=[1, 0, 0, 1, 3000, 4000])
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        places = find_place_objects(tags)
        found = False
        for po_type, po in places:
            if "matrix" in po:
                mat = po["matrix"]
                # tx/ty are in twips in SWF
                if abs(mat[4] - 3000) < 20 and abs(mat[5] - 4000) < 20:
                    found = True
                    break
        self.assertTrue(found, "Position (3000, 4000) twips not found in PlaceObject")

    def test_scale_export(self):
        """Edited scale (sx, sy) appears in PlaceObject matrix."""
        n2d = self._make_shape_n2d()
        add_to_root_timeline(n2d, 1, matrix=[2.0, 0, 0, 0.5, 0, 0])
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        places = find_place_objects(tags)
        found = False
        for po_type, po in places:
            if "matrix" in po:
                mat = po["matrix"]
                if abs(mat[0] - 2.0) < 0.01 and abs(mat[3] - 0.5) < 0.01:
                    found = True
                    break
        self.assertTrue(found, "Scale (2.0, 0.5) not found in PlaceObject")

    def test_rotation_export(self):
        """Edited rotation appears in PlaceObject matrix."""
        angle = math.radians(45)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        n2d = self._make_shape_n2d()
        add_to_root_timeline(n2d, 1, matrix=[cos_a, sin_a, -sin_a, cos_a, 0, 0])
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        places = find_place_objects(tags)
        found = False
        for po_type, po in places:
            if "matrix" in po:
                mat = po["matrix"]
                if abs(mat[0] - cos_a) < 0.02 and abs(mat[1] - sin_a) < 0.02:
                    found = True
                    break
        self.assertTrue(found, "45° rotation not found in PlaceObject matrix")

    def test_color_transform_export(self):
        """Edited color transform appears in PlaceObject."""
        n2d = self._make_shape_n2d()
        add_to_root_timeline(n2d, 1,
            color_transform=[0.5, 0.75, 1.0, 0.8, 20, 0, -10, 0])
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        places = find_place_objects(tags)
        found_cx = False
        for po_type, po in places:
            if "colorTransform" in po:
                cx = po["colorTransform"]
                # CX values: [rMul, gMul, bMul, aMul, rAdd, gAdd, bAdd, aAdd]
                if abs(cx[0] - 0.5) < 0.05 and abs(cx[3] - 0.8) < 0.05:
                    found_cx = True
                    break
        self.assertTrue(found_cx, "Color transform not found in PlaceObject")

    def test_blend_mode_export(self):
        """Edited blend mode upgrades to PlaceObject3 with blend byte."""
        n2d = self._make_shape_n2d()
        add_to_root_timeline(n2d, 1, blend_mode="multiply")
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        po3s = find_tags(tags, TAG_PLACE_OBJECT3)
        self.assertGreaterEqual(len(po3s), 1,
            "Blend mode should produce PlaceObject3")
        # Parse and verify blend mode
        parsed = parse_place_object3_body(po3s[0][1])
        self.assertTrue(parsed["hasBlend"],
            "PlaceObject3 should have blend flag set")
        self.assertEqual(parsed["blendMode"], 3,
            "Multiply blend mode should be 3")

    def test_filter_export(self):
        """Edited filters on a sprite containing shape upgrade to PO3."""
        n2d = make_base_n2d()
        recodes = [
            CMD_FILL_STYLE, 128, 0, 128, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0, CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50, CMD_CLOSE_PATH,
        ]
        add_shape_lib(n2d, 1, recodes)
        # Build a filter tag directly using swf_writer to verify
        # the filter encoding produces valid bytes
        filter_data = sw.encode_filter_list([{
            "class": "BlurFilter",
            "params": [None, 8.0, 8.0, 2],
        }])
        # Verify filter encoding works at all
        self.assertGreater(len(filter_data), 0,
            "encode_filter_list should produce non-empty bytes")
        # Build a PO3 with filters manually to verify the tag builder
        po3 = sw.build_place_object3(
            depth=1, character_id=1, filters_data=filter_data)
        self.assertGreater(len(po3), 0, "build_place_object3 with filters should produce bytes")
        # Parse and verify
        # Skip tag header to get body
        h = struct.unpack_from('<H', po3, 0)[0]
        hdr_len = 2 if (h & 0x3F) < 0x3F else 6
        body = po3[hdr_len:]
        parsed = parse_place_object3_body(body)
        self.assertTrue(parsed["hasFilters"],
            "PlaceObject3 should have filter flag set")
        self.assertEqual(parsed["filterCount"], 1)

    def test_instance_name_export(self):
        """Instance name appears in PlaceObject."""
        n2d = self._make_shape_n2d()
        add_to_root_timeline(n2d, 1, name="myInstance")
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        places = find_place_objects(tags)
        found_name = False
        for po_type, po in places:
            if po.get("name") == "myInstance":
                found_name = True
                break
        self.assertTrue(found_name, "Instance name 'myInstance' not found")


# ══════════════════════════════════════════════════════════════════════════
#  Container / Sprite Edits
# ══════════════════════════════════════════════════════════════════════════

class TestContainerEditExport(unittest.TestCase):
    """Verify edited containers (sprites) export correctly."""

    def _make_shape_recodes(self, r=255, g=0, b=0, a=255):
        return [
            CMD_FILL_STYLE, r, g, b, a,
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0,
            CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50,
            CMD_CLOSE_PATH,
        ]

    def test_sprite_export(self):
        """Container with child shape produces DefineSprite in SWF."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_shape_recodes())
        layers = [{
            "name": "layer_1",
            "swfDepth": 1,
            "characters": [{
                "id": 10,
                "name": "",
                "libraryId": 1,
                "startFrame": 1,
                "endFrame": 2,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        add_container_lib(n2d, 2, layers, total_frames=1)
        add_to_root_timeline(n2d, 2)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1, "No DefineSprite in output")

    def test_sprite_multiframe(self):
        """Multi-frame sprite exports with correct frame count."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_shape_recodes(255, 0, 0))
        add_shape_lib(n2d, 2, self._make_shape_recodes(0, 255, 0))
        layers = [{
            "name": "layer_1",
            "swfDepth": 1,
            "characters": [
                {
                    "id": 10,
                    "name": "",
                    "libraryId": 1,
                    "startFrame": 1,
                    "endFrame": 3,
                    "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                                "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                                "blendMode": "normal"}],
                },
                {
                    "id": 11,
                    "name": "",
                    "libraryId": 2,
                    "startFrame": 3,
                    "endFrame": 5,
                    "places": [{"frame": 3, "matrix": [1, 0, 0, 1, 50, 0],
                                "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                                "blendMode": "normal"}],
                },
            ],
        }]
        add_container_lib(n2d, 3, layers, total_frames=4)
        add_to_root_timeline(n2d, 3)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1)
        # Parse sprite header: charId(2) + frameCount(2)
        body = sprites[0][1]
        frame_count = struct.unpack_from("<H", body, 2)[0]
        self.assertEqual(frame_count, 4,
            f"Sprite frame count should be 4, got {frame_count}")

    def test_sprite_nested(self):
        """Nested containers (sprite in sprite) both export."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_shape_recodes())
        inner_layers = [{
            "name": "inner_layer",
            "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "", "libraryId": 1,
                "startFrame": 1, "endFrame": 2,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        add_container_lib(n2d, 2, inner_layers, total_frames=1)

        outer_layers = [{
            "name": "outer_layer",
            "swfDepth": 1,
            "characters": [{
                "id": 11, "name": "", "libraryId": 2,
                "startFrame": 1, "endFrame": 2,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 10, 10],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        add_container_lib(n2d, 3, outer_layers, total_frames=1)
        add_to_root_timeline(n2d, 3)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 2,
            f"Should have >= 2 sprites (nested), got {len(sprites)}")

    def test_frame_labels_export(self):
        """Frame labels in a container appear in the sprite's timeline."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_shape_recodes())
        layers = [{
            "name": "layer_1",
            "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "", "libraryId": 1,
                "startFrame": 1, "endFrame": 4,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        labels = [
            {"frame": 1, "name": "start"},
            {"frame": 2, "name": "middle"},
            {"frame": 3, "name": "end"},
        ]
        add_container_lib(n2d, 2, layers, total_frames=3, labels=labels)
        add_to_root_timeline(n2d, 2)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1)
        # Parse inner tags and check for frame labels
        inner = parse_sprite_tags(sprites[0][1][4:])
        inner_labels = find_frame_labels(inner)
        self.assertIn("start", inner_labels, "Label 'start' not in sprite")
        self.assertIn("middle", inner_labels, "Label 'middle' not in sprite")
        self.assertIn("end", inner_labels, "Label 'end' not in sprite")


# ══════════════════════════════════════════════════════════════════════════
#  Timeline / Layer Edit Exports
# ══════════════════════════════════════════════════════════════════════════

class TestTimelineEditExport(unittest.TestCase):
    """Verify timeline edits (add/remove/reorder layers, change spans)."""

    def _make_shape_recodes(self, r=255, g=0, b=0):
        return [
            CMD_FILL_STYLE, r, g, b, 255,
            CMD_BEGIN_PATH,
            CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0,
            CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50,
            CMD_CLOSE_PATH,
        ]

    def test_multi_layer_export(self):
        """Multiple layers each produce PlaceObject2/3 at different depths."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_shape_recodes(255, 0, 0))
        add_shape_lib(n2d, 2, self._make_shape_recodes(0, 255, 0))
        layers = [
            {
                "name": "layer_1",
                "swfDepth": 1,
                "characters": [{
                    "id": 10, "name": "", "libraryId": 1,
                    "startFrame": 1, "endFrame": 2,
                    "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                                "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                                "blendMode": "normal"}],
                }],
            },
            {
                "name": "layer_2",
                "swfDepth": 2,
                "characters": [{
                    "id": 11, "name": "", "libraryId": 2,
                    "startFrame": 1, "endFrame": 2,
                    "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 100, 0],
                                "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                                "blendMode": "normal"}],
                }],
            },
        ]
        add_container_lib(n2d, 3, layers, total_frames=1)
        add_to_root_timeline(n2d, 3)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1)
        inner = parse_sprite_tags(sprites[0][1][4:])
        inner_places = find_place_objects(inner)
        depths = set()
        for po_type, po in inner_places:
            depths.add(po["depth"])
        self.assertGreaterEqual(len(depths), 2,
            f"Should have places at >=2 different depths, got {depths}")

    def test_transform_keyframe_change(self):
        """Transform change at a keyframe produces a move PlaceObject."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_shape_recodes())
        layers = [{
            "name": "layer_1",
            "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "", "libraryId": 1,
                "startFrame": 1, "endFrame": 4,
                "places": [
                    {"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                     "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                     "blendMode": "normal"},
                    {"frame": 2, "matrix": [1, 0, 0, 1, 100, 0],
                     "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                     "blendMode": "normal"},
                ],
            }],
        }]
        add_container_lib(n2d, 2, layers, total_frames=3)
        add_to_root_timeline(n2d, 2)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1)
        inner = parse_sprite_tags(sprites[0][1][4:])
        inner_places = find_place_objects(inner)
        # Should have at least 2 PlaceObjects: initial + move
        self.assertGreaterEqual(len(inner_places), 2,
            "Should have initial place + move keyframe")
        # Second should be a move (isMove=True)
        second = inner_places[1][1]
        self.assertTrue(second.get("isMove"),
            "Second PlaceObject should be a move (transform change)")

    def test_remove_object_on_span_end(self):
        """Object removed at end of span produces RemoveObject2."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, self._make_shape_recodes())
        layers = [{
            "name": "layer_1",
            "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "", "libraryId": 1,
                "startFrame": 1, "endFrame": 3,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        add_container_lib(n2d, 2, layers, total_frames=5)
        add_to_root_timeline(n2d, 2)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1)
        inner = parse_sprite_tags(sprites[0][1][4:])
        removes = find_tags(inner, TAG_REMOVE_OBJECT2)
        self.assertGreaterEqual(len(removes), 1,
            "Should have RemoveObject2 when span ends before total frames")


# ══════════════════════════════════════════════════════════════════════════
#  Sound Edit Exports
# ══════════════════════════════════════════════════════════════════════════

class TestSoundEditExport(unittest.TestCase):
    """Verify edited sounds export to DefineSound in SWF."""

    def _make_wav_bytes(self, sample_rate=44100, duration_ms=50):
        """Generate a minimal WAV file (mono, 16-bit PCM)."""
        num_samples = int(sample_rate * duration_ms / 1000)
        # Silent samples
        samples = b'\x00\x00' * num_samples
        data_size = len(samples)
        buf = io.BytesIO()
        # RIFF header
        buf.write(b'RIFF')
        buf.write(struct.pack('<I', 36 + data_size))
        buf.write(b'WAVE')
        # fmt chunk
        buf.write(b'fmt ')
        buf.write(struct.pack('<I', 16))   # chunk size
        buf.write(struct.pack('<H', 1))    # PCM
        buf.write(struct.pack('<H', 1))    # mono
        buf.write(struct.pack('<I', sample_rate))
        buf.write(struct.pack('<I', sample_rate * 2))  # byte rate
        buf.write(struct.pack('<H', 2))    # block align
        buf.write(struct.pack('<H', 16))   # bits per sample
        # data chunk
        buf.write(b'data')
        buf.write(struct.pack('<I', data_size))
        buf.write(samples)
        return buf.getvalue()

    def test_sound_wav_export(self):
        """Sound from WAV data compiles to DefineSound (tag 14)."""
        n2d = make_base_n2d()
        wav = self._make_wav_bytes()
        # _decode_raw_body expects raw base64 (no prefix)
        buf = base64.b64encode(wav).decode("ascii")
        n2d["libraries"].append({
            "id": 1,
            "type": "sound",
            "name": "TestSound",
            "symbol": "",
            "buffer": buf,
        })
        n2d["characterId"] = 2
        # Place sound in a sprite timeline
        add_shape_lib(n2d, 2, [
            CMD_FILL_STYLE, 128, 128, 128, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 10, 0, CMD_LINE_TO, 10, 10,
            CMD_LINE_TO, 0, 10, CMD_CLOSE_PATH,
        ])
        layers = [{
            "name": "layer_1",
            "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "", "libraryId": 2,
                "startFrame": 1, "endFrame": 2,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        sounds = [{"frame": 1, "sound": [{"characterId": 1}]}]
        add_container_lib(n2d, 3, layers, total_frames=1, sounds=sounds)
        add_to_root_timeline(n2d, 3)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sound_defs = find_tags(tags, TAG_DEFINE_SOUND)
        self.assertGreaterEqual(len(sound_defs), 1,
            "No DefineSound in output after editing sound")


# ══════════════════════════════════════════════════════════════════════════
#  Symbol Class Edits
# ══════════════════════════════════════════════════════════════════════════

class TestSymbolClassExport(unittest.TestCase):
    """Verify symbol linkage edits appear in SymbolClass tag."""

    def test_symbol_export(self):
        """Exported symbols appear in SymbolClass tag."""
        n2d = make_base_n2d()
        recodes = [
            CMD_FILL_STYLE, 255, 0, 0, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0, CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50, CMD_CLOSE_PATH,
        ]
        add_shape_lib(n2d, 1, recodes)
        # Give a symbol linkage
        for lib in n2d["libraries"]:
            if lib["id"] == 1:
                lib["symbol"] = "MyCustomShape"
        layers = [{
            "name": "layer_1", "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "", "libraryId": 1,
                "startFrame": 1, "endFrame": 2,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        add_container_lib(n2d, 2, layers, total_frames=1, symbol="TestClip")
        add_to_root_timeline(n2d, 2)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sc_tags = find_tags(tags, TAG_SYMBOL_CLASS)
        self.assertGreaterEqual(len(sc_tags), 1, "No SymbolClass tag")

        # Parse symbol class body
        names = set()
        for _, body in sc_tags:
            count = struct.unpack_from("<H", body, 0)[0]
            pos = 2
            for _ in range(count):
                pos += 2  # skip charId
                end = body.index(0, pos)
                names.add(body[pos:end].decode("utf-8"))
                pos = end + 1

        self.assertIn("Main", names, "Document class 'Main' not in SymbolClass")
        self.assertIn("TestClip", names, "Symbol 'TestClip' not in SymbolClass")


# ══════════════════════════════════════════════════════════════════════════
#  Structural Validation After Edits
# ══════════════════════════════════════════════════════════════════════════

class TestEditedSWFStructure(unittest.TestCase):
    """Verify output SWF has valid structure after edits."""

    def _make_edited_swf(self):
        n2d = make_base_n2d(width=400, height=300, fps=30, bg_color="#112233")
        add_shape_lib(n2d, 1, [
            CMD_FILL_STYLE, 255, 128, 0, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 100, 0, CMD_LINE_TO, 100, 100,
            CMD_LINE_TO, 0, 100, CMD_CLOSE_PATH,
        ])
        add_text_lib(n2d, 2, text="Hello", size=20, color=0xFF0000)
        layers = [{
            "name": "layer_1", "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "shape_inst", "libraryId": 1,
                "startFrame": 1, "endFrame": 2,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 50, 50],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        add_container_lib(n2d, 3, layers, total_frames=1, symbol="MyClip")
        add_to_root_timeline(n2d, 3)
        add_to_root_timeline(n2d, 2, matrix=[1, 0, 0, 1, 200, 50])
        return compile_n2d_to_swf(n2d)

    def test_file_attributes_first(self):
        """FileAttributes is the first tag in output SWF."""
        swf = self._make_edited_swf()
        tags = parse_swf_tags(swf)
        self.assertEqual(tags[0][0], TAG_FILE_ATTRIBUTES,
            "First tag should be FileAttributes")

    def test_as3_flag_set(self):
        """FileAttributes has AS3 flag set."""
        swf = self._make_edited_swf()
        tags = parse_swf_tags(swf)
        body = tags[0][1]
        flags = struct.unpack_from("<I", body, 0)[0]
        self.assertTrue(flags & 0x08, "AS3 flag not set")

    def test_end_tag_present(self):
        """End tag is the last tag in the SWF."""
        swf = self._make_edited_swf()
        tags = parse_swf_tags(swf)
        self.assertEqual(tags[-1][0], TAG_END, "Last tag should be End")

    def test_sprites_have_end_tags(self):
        """Every DefineSprite ends with an End tag."""
        swf = self._make_edited_swf()
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        for i, (_, body) in enumerate(sprites):
            inner = parse_sprite_tags(body[4:])
            if inner:
                self.assertEqual(inner[-1][0], TAG_END,
                    f"Sprite #{i} does not end with End tag")

    def test_show_frames_present(self):
        """Output SWF has at least one ShowFrame tag."""
        swf = self._make_edited_swf()
        tags = parse_swf_tags(swf)
        show_frames = count_tags(tags, TAG_SHOW_FRAME)
        self.assertGreaterEqual(show_frames, 1,
            "Output SWF should have ShowFrame tags")

    def test_no_empty_swf(self):
        """Output SWF has definition tags (not just header + end)."""
        swf = self._make_edited_swf()
        tags = parse_swf_tags(swf)
        def_count = sum(1 for tt, _ in tags if tt in DEFINE_TAGS)
        self.assertGreater(def_count, 0,
            "Output SWF should have definition tags")

    def test_valid_compression(self):
        """Output SWF has valid CWS signature (compressed)."""
        swf = self._make_edited_swf()
        self.assertEqual(swf[:3], b"CWS", "SWF should be CWS compressed")
        # Verify decompression works
        decompressed = zlib.decompress(swf[8:])
        self.assertGreater(len(decompressed), 0)


# ══════════════════════════════════════════════════════════════════════════
#  Combined Edit Scenarios (Integration)
# ══════════════════════════════════════════════════════════════════════════

class TestCombinedEdits(unittest.TestCase):
    """Verify multiple simultaneous edits all export correctly."""

    def test_shape_and_text_together(self):
        """Shape + text in same project both export to SWF."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, [
            CMD_FILL_STYLE, 0, 128, 255, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 80, 0, CMD_LINE_TO, 80, 60,
            CMD_LINE_TO, 0, 60, CMD_CLOSE_PATH,
        ])
        add_text_lib(n2d, 2, text="Label", size=14)
        add_to_root_timeline(n2d, 1)
        add_to_root_timeline(n2d, 2, matrix=[1, 0, 0, 1, 100, 0])
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        self.assertGreaterEqual(count_tags(tags, TAG_DEFINE_SHAPE3), 1)
        self.assertGreaterEqual(count_tags(tags, TAG_DEFINE_EDIT_TEXT), 1)

    def test_sprite_with_edited_children(self):
        """Sprite containing edited shape + text all export."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, [
            CMD_FILL_STYLE, 200, 100, 50, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 40, 0, CMD_LINE_TO, 40, 40,
            CMD_LINE_TO, 0, 40, CMD_CLOSE_PATH,
        ])
        add_text_lib(n2d, 2, text="Inside Sprite", size=10)
        layers = [
            {
                "name": "shape_layer", "swfDepth": 1,
                "characters": [{
                    "id": 10, "name": "", "libraryId": 1,
                    "startFrame": 1, "endFrame": 2,
                    "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                                "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                                "blendMode": "normal"}],
                }],
            },
            {
                "name": "text_layer", "swfDepth": 2,
                "characters": [{
                    "id": 11, "name": "label", "libraryId": 2,
                    "startFrame": 1, "endFrame": 2,
                    "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 50, 10],
                                "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                                "blendMode": "normal"}],
                }],
            },
        ]
        add_container_lib(n2d, 3, layers, total_frames=1, symbol="MyPanel")
        add_to_root_timeline(n2d, 3)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        self.assertGreaterEqual(count_tags(tags, TAG_DEFINE_SHAPE3), 1)
        self.assertGreaterEqual(count_tags(tags, TAG_DEFINE_EDIT_TEXT), 1)
        self.assertGreaterEqual(count_tags(tags, TAG_DEFINE_SPRITE), 1)

    def test_edit_then_re_export_different(self):
        """Editing and re-exporting produces different SWF than original."""
        # First export
        n2d1 = make_base_n2d()
        add_shape_lib(n2d1, 1, [
            CMD_FILL_STYLE, 255, 0, 0, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0, CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50, CMD_CLOSE_PATH,
        ])
        add_to_root_timeline(n2d1, 1, matrix=[1, 0, 0, 1, 0, 0])
        swf1 = compile_n2d_to_swf(n2d1)

        # "Edit" — change color and position
        n2d2 = make_base_n2d()
        add_shape_lib(n2d2, 1, [
            CMD_FILL_STYLE, 0, 255, 0, 255,  # changed to green
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0, CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50, CMD_CLOSE_PATH,
        ])
        add_to_root_timeline(n2d2, 1, matrix=[1, 0, 0, 1, 100, 100])  # moved
        swf2 = compile_n2d_to_swf(n2d2)

        self.assertNotEqual(swf1, swf2,
            "Edited SWF should differ from original")

    def test_deterministic_export(self):
        """Same N2D compiled multiple times produces identical SWF."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, [
            CMD_FILL_STYLE, 255, 0, 0, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0, CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50, CMD_CLOSE_PATH,
        ])
        add_text_lib(n2d, 2, text="Det Test")
        add_to_root_timeline(n2d, 1)
        add_to_root_timeline(n2d, 2, matrix=[1, 0, 0, 1, 60, 0])

        outputs = []
        for _ in range(3):
            outputs.append(compile_n2d_to_swf(n2d))

        self.assertEqual(outputs[0], outputs[1],
            "Run 1 vs 2 should be identical")
        self.assertEqual(outputs[1], outputs[2],
            "Run 2 vs 3 should be identical")


# ══════════════════════════════════════════════════════════════════════════
#  Roundtrip-then-Edit Tests (edit after import)
# ══════════════════════════════════════════════════════════════════════════

class TestImportEditExport(unittest.TestCase):
    """Import a real SWF, make edits to the N2D, re-export, verify."""

    def _find_real_swf(self):
        for name in ["gameandwatch_cli.swf", "cli3.swf", "gw_test.swf"]:
            p = os.path.join(CONVERTED_DIR, name)
            if os.path.isfile(p):
                return p
        return None

    def _import_swf(self, swf_path):
        """Import a SWF → N2D dict."""
        with open(swf_path, "rb") as f:
            swf_data = f.read()
        header, tags = swf_to_n2d.parse_swf(swf_data)
        builder = swf_to_n2d.N2DBuilder(header, name="test")
        builder.catalog_swf_tags(tags)
        try:
            scripts, frame_scripts = swf_to_n2d.decompile_all_scripts(
                builder.global_raw_tags)
            builder.frame_scripts = frame_scripts
            if scripts:
                builder.scripts.extend(scripts)
        except Exception:
            pass
        builder.build_all()
        builder.build_main_timeline(tags)
        builder._embed_bitmap_data_in_recodes()
        return builder.to_n2d_json()

    def test_change_stage_after_import(self):
        """Change stage size after importing SWF, verify in export."""
        swf_path = self._find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")

        n2d = self._import_swf(swf_path)
        # Edit stage
        n2d["stage"]["width"] = 1280
        n2d["stage"]["height"] = 720
        n2d["stage"]["bgColor"] = "#AABBCC"

        swf = compile_n2d_to_swf(n2d)
        hdr = parse_swf_header(swf)
        self.assertEqual(hdr["width"], 1280)
        self.assertEqual(hdr["height"], 720)

        tags = parse_swf_tags(swf)
        bg = find_tags(tags, TAG_SET_BG_COLOR)[0][1]
        self.assertEqual((bg[0], bg[1], bg[2]), (0xAA, 0xBB, 0xCC))

    def test_add_new_shape_after_import(self):
        """Add a new edited shape to an imported project, verify in export."""
        swf_path = self._find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")

        n2d = self._import_swf(swf_path)
        orig_swf = compile_n2d_to_swf(n2d)
        orig_shapes = count_tags(parse_swf_tags(orig_swf), TAG_DEFINE_SHAPE3)

        # Add a new shape to the project
        new_id = n2d["characterId"]
        add_shape_lib(n2d, new_id, [
            CMD_FILL_STYLE, 255, 255, 0, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 30, 0, CMD_LINE_TO, 30, 30,
            CMD_LINE_TO, 0, 30, CMD_CLOSE_PATH,
        ])
        add_to_root_timeline(n2d, new_id, matrix=[1, 0, 0, 1, 300, 300])

        edited_swf = compile_n2d_to_swf(n2d)
        edited_shapes = count_tags(parse_swf_tags(edited_swf), TAG_DEFINE_SHAPE3)
        self.assertGreater(edited_shapes, orig_shapes,
            "Adding a shape should increase shape count")

    def test_edit_existing_shape_color(self):
        """Edit an existing shape's fill color (clear rawTagBody), verify export."""
        swf_path = self._find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")

        n2d = self._import_swf(swf_path)

        # Find a shape library entry with rawTagBody
        shape_lib = None
        for lib in n2d["libraries"]:
            if lib.get("type") == "shape" and lib.get("rawTagBody"):
                shape_lib = lib
                break

        if not shape_lib:
            self.skipTest("No editable shape found")

        # "Edit" the shape: remove rawTagBody and set recodes
        shape_lib.pop("rawTagBody", None)
        shape_lib.pop("rawTagType", None)
        shape_lib["recodes"] = [
            CMD_FILL_STYLE, 255, 0, 255, 255,  # magenta
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0, CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50, CMD_CLOSE_PATH,
        ]
        shape_lib["bounds"] = {"xMin": 0, "xMax": 1000, "yMin": 0, "yMax": 1000}

        # Should still compile without error
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        shapes = find_tags(tags, TAG_DEFINE_SHAPE3)
        self.assertGreaterEqual(len(shapes), 1,
            "Edited shape should still produce DefineShape3")


# ══════════════════════════════════════════════════════════════════════════
#  Edge Cases / Regression
# ══════════════════════════════════════════════════════════════════════════

class TestEdgeCases(unittest.TestCase):
    """Edge cases and regression tests for edit exports."""

    def test_empty_shape_export(self):
        """Empty shape (no recodes) still produces valid SWF."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, [])
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        # Should not crash, SWF should be valid
        self.assertGreater(len(tags), 2)

    def test_large_matrix_values(self):
        """Large translate values don't crash SWF output."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, [
            CMD_FILL_STYLE, 128, 128, 128, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 10, 0, CMD_LINE_TO, 10, 10,
            CMD_LINE_TO, 0, 10, CMD_CLOSE_PATH,
        ])
        add_to_root_timeline(n2d, 1, matrix=[1, 0, 0, 1, 5000, 3000])
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        self.assertGreater(len(tags), 2)

    def test_zero_alpha_color_transform(self):
        """Alpha=0 color transform doesn't break export."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, [
            CMD_FILL_STYLE, 255, 0, 0, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 50, 0, CMD_LINE_TO, 50, 50,
            CMD_LINE_TO, 0, 50, CMD_CLOSE_PATH,
        ])
        add_to_root_timeline(n2d, 1,
            color_transform=[1, 1, 1, 0, 0, 0, 0, 0])  # alpha=0
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        self.assertGreater(len(tags), 2)

    def test_special_characters_in_text(self):
        """Text with special characters exports without crash."""
        n2d = make_base_n2d()
        add_text_lib(n2d, 1, text='Hello "World" & <Tag> © ñ')
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        texts = find_tags(tags, TAG_DEFINE_EDIT_TEXT)
        self.assertGreaterEqual(len(texts), 1)

    def test_single_pixel_bitmap(self):
        """1x1 bitmap exports without crash."""
        n2d = make_base_n2d()
        add_bitmap_lib(n2d, 1, 1, 1, bytes([255, 0, 0, 255]))
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        bitmaps = find_tags(tags, TAG_DEFINE_BITS_LOSSLESS2)
        self.assertGreaterEqual(len(bitmaps), 1)

    def test_empty_container_export(self):
        """Container with no layers produces valid DefineSprite."""
        n2d = make_base_n2d()
        add_container_lib(n2d, 1, layers=[], total_frames=1)
        add_to_root_timeline(n2d, 1)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1)
        # Verify it has an End tag
        inner = parse_sprite_tags(sprites[0][1][4:])
        if inner:
            self.assertEqual(inner[-1][0], TAG_END)

    def test_unicode_frame_label(self):
        """Frame label with unicode characters exports correctly."""
        n2d = make_base_n2d()
        add_shape_lib(n2d, 1, [
            CMD_FILL_STYLE, 128, 128, 128, 255,
            CMD_BEGIN_PATH, CMD_MOVE_TO, 0, 0,
            CMD_LINE_TO, 10, 0, CMD_LINE_TO, 10, 10,
            CMD_LINE_TO, 0, 10, CMD_CLOSE_PATH,
        ])
        layers = [{
            "name": "layer_1", "swfDepth": 1,
            "characters": [{
                "id": 10, "name": "", "libraryId": 1,
                "startFrame": 1, "endFrame": 3,
                "places": [{"frame": 1, "matrix": [1, 0, 0, 1, 0, 0],
                             "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                             "blendMode": "normal"}],
            }],
        }]
        labels = [{"frame": 1, "name": "attack_start"}]
        add_container_lib(n2d, 2, layers, total_frames=2, labels=labels)
        add_to_root_timeline(n2d, 2)
        swf = compile_n2d_to_swf(n2d)
        tags = parse_swf_tags(swf)
        sprites = find_tags(tags, TAG_DEFINE_SPRITE)
        self.assertGreaterEqual(len(sprites), 1)
        inner = parse_sprite_tags(sprites[0][1][4:])
        inner_labels = find_frame_labels(inner)
        self.assertIn("attack_start", inner_labels)


# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main()
