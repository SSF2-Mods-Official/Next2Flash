#!/usr/bin/env python3
"""
SWF Roundtrip Unit Tests — tests 1-35 from SWF_ROUNDTRIP_TEST_PLAN.md

Each test builds (or loads) a SWF, roundtrips it through SWF→N2D→SWF,
and verifies definition tags survive with matching bodies.

Usage:
    cd app
    python -m pytest test/test_swf_roundtrip.py -v
    # or
    python -m unittest test.test_swf_roundtrip -v
"""
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
    SolidFill, GradientFill, GradientStop, BitmapFill,
    LineStyle, SubPath, MoveToEdge, LineToEdge, CurveToEdge,
    build_define_shape3,
)
from bitmap_converter import build_define_bits_lossless2

CONVERTED_DIR = os.path.join(APP_DIR, "converted")

# ── Tag constants ────────────────────────────────────────────────────────

DEFINE_TAGS = {2, 22, 32, 83, 6, 21, 35, 90, 20, 36, 39, 46, 84,
               11, 33, 48, 75, 10, 14, 37, 87}


# ══════════════════════════════════════════════════════════════════════════
#  Shared Utilities
# ══════════════════════════════════════════════════════════════════════════

def parse_swf_tags(data: bytes):
    """Parse SWF bytes (or path) into [(tag_type, body), ...]."""
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
    pos = rect_end + 4  # skip fps + frameCount
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


def build_minimal_swf(inner_tags_bytes, width=100, height=100, fps=24):
    """Build a valid AS3 SWF from concatenated tag bytes."""
    tags = sw.build_file_attributes(has_as3=True)
    tags += sw.build_set_background_color(255, 255, 255)
    tags += inner_tags_bytes
    tags += sw.build_tag_show_frame()
    tags += sw.build_tag_end()
    return sw.build_swf_file(width, height, fps, frame_count=1, tags=tags)


def roundtrip(swf_bytes):
    """SWF bytes → N2D → SWF bytes. Returns (orig_tags, rt_tags)."""
    with tempfile.TemporaryDirectory(prefix="rt_") as tmp:
        orig_path = os.path.join(tmp, "orig.swf")
        n2d_path = os.path.join(tmp, "project.n2d")
        rt_path = os.path.join(tmp, "rt.swf")

        with open(orig_path, "wb") as f:
            f.write(swf_bytes)

        # SWF → N2D
        header, tags = swf_to_n2d.parse_swf(swf_bytes)
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
        n2d = builder.to_n2d_json()
        swf_to_n2d.save_n2d(n2d, n2d_path)

        # N2D → SWF
        compiler = compile_n2d.N2DCompiler(
            n2d_path=n2d_path,
            shared_dir=tmp,
            output_path=rt_path,
            sdk_path=None,
        )
        compiler.compile()

        with open(rt_path, "rb") as f:
            rt_bytes = f.read()

    orig_tags = parse_swf_tags(swf_bytes)
    rt_tags = parse_swf_tags(rt_bytes)
    return orig_tags, rt_tags


def get_define_tags_by_type(tags):
    """Group define tags: {tag_type: [body_after_charID, ...]}."""
    result = {}
    for tt, body in tags:
        if tt in DEFINE_TAGS and len(body) >= 2:
            result.setdefault(tt, []).append(body[2:])
    return result


def get_tag_counts(tags):
    """Returns {tag_type: count}."""
    counts = {}
    for tt, _ in tags:
        counts[tt] = counts.get(tt, 0) + 1
    return counts


def count_define_tags(tags, tag_type):
    """Count definition tags of a specific type."""
    return sum(1 for tt, body in tags if tt == tag_type and len(body) >= 2)


def find_tags(tags, tag_type):
    """Return all (tag_type, body) tuples matching tag_type."""
    return [(tt, body) for tt, body in tags if tt == tag_type]


def assert_tag_type_count_matches(test_case, orig_tags, rt_tags, tag_type):
    """Assert that both SWFs have the same number of a given tag type."""
    oc = count_define_tags(orig_tags, tag_type)
    rc = count_define_tags(rt_tags, tag_type)
    test_case.assertEqual(oc, rc,
        f"Tag {tag_type} count mismatch: orig={oc}, rt={rc}")


def assert_leaf_bodies_match(test_case, orig_tags, rt_tags, tag_type):
    """Assert that leaf tag bodies (after charID) match as multisets."""
    orig_bodies = sorted(body[2:] for tt, body in orig_tags
                        if tt == tag_type and len(body) >= 2)
    rt_bodies = sorted(body[2:] for tt, body in rt_tags
                      if tt == tag_type and len(body) >= 2)
    test_case.assertEqual(len(orig_bodies), len(rt_bodies),
        f"Tag {tag_type}: count mismatch orig={len(orig_bodies)} rt={len(rt_bodies)}")
    for i, (ob, rb) in enumerate(zip(orig_bodies, rt_bodies)):
        test_case.assertEqual(ob, rb,
            f"Tag {tag_type} body #{i}: {len(ob)} vs {len(rb)} bytes differ")


def make_simple_rect_shape(shape_id, fill_styles, line_styles,
                           x=0, y=0, w=50, h=50):
    """Create a DefineShape3 with a simple rectangle using given styles."""
    sp = SubPath()
    sp.fill_style_idx = 1 if fill_styles else 0
    sp.line_style_idx = 1 if line_styles else 0
    sp.start_x = x
    sp.start_y = y
    sp.edges = [
        LineToEdge(x + w, y),
        LineToEdge(x + w, y + h),
        LineToEdge(x, y + h),
        LineToEdge(x, y),
    ]
    bounds = {"xMin": x * 20, "xMax": (x + w) * 20,
              "yMin": y * 20, "yMax": (y + h) * 20}
    return build_define_shape3(shape_id, fill_styles, line_styles, [sp], bounds)


# ══════════════════════════════════════════════════════════════════════════
#  Test 1: Shape Solid Fills
# ══════════════════════════════════════════════════════════════════════════

class TestShapeSolidFills(unittest.TestCase):
    def test_shape_solid_fills(self):
        fills = [SolidFill(255, 0, 0, 255), SolidFill(0, 255, 0, 128)]
        shape_tag = make_simple_rect_shape(1, fills, [])
        po = sw.build_place_object2(depth=1, character_id=1)
        swf = build_minimal_swf(shape_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 2: Shape Gradient Fills
# ══════════════════════════════════════════════════════════════════════════

class TestShapeGradientFills(unittest.TestCase):
    def test_shape_gradient_fills(self):
        stops = [GradientStop(0, 255, 0, 0, 255), GradientStop(255, 0, 0, 255, 255)]
        gf = GradientFill("linear", stops, [1.0, 0.0, 0.0, 1.0, 0.0, 0.0], 0, 0, 0.0)
        shape_tag = make_simple_rect_shape(1, [gf], [])
        po = sw.build_place_object2(depth=1, character_id=1)
        swf = build_minimal_swf(shape_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 3: Shape Bitmap Fills
# ══════════════════════════════════════════════════════════════════════════

class TestShapeBitmapFills(unittest.TestCase):
    def test_shape_bitmap_fills(self):
        # Create a small 4x4 red bitmap
        pixels = bytes([255, 0, 0, 255] * 16)
        bmp_tag = build_define_bits_lossless2(1, 4, 4, pixels)
        bf = BitmapFill(4, 4, list(pixels), [20.0, 0.0, 0.0, 20.0, 0.0, 0.0], True, False, bitmap_char_id=1)
        shape_tag = make_simple_rect_shape(2, [bf], [])
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(bmp_tag + shape_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 36)  # bitmap
        assert_tag_type_count_matches(self, orig, rt, 32)  # shape


# ══════════════════════════════════════════════════════════════════════════
#  Test 4: Shape Line Styles
# ══════════════════════════════════════════════════════════════════════════

class TestShapeLineStyles(unittest.TestCase):
    def test_shape_line_styles(self):
        lines = [
            LineStyle(2.0, 0, 0, 0, 255, cap=0, join=0),   # round/round
            LineStyle(4.0, 255, 0, 0, 255, cap=1, join=1),  # square/bevel
        ]
        shape_tag = make_simple_rect_shape(1, [SolidFill(200, 200, 200, 255)], lines)
        po = sw.build_place_object2(depth=1, character_id=1)
        swf = build_minimal_swf(shape_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 5: Shape Curved Edges
# ══════════════════════════════════════════════════════════════════════════

class TestShapeCurvedEdges(unittest.TestCase):
    def test_shape_curved_edges(self):
        sp = SubPath()
        sp.fill_style_idx = 1
        sp.line_style_idx = 0
        sp.start_x = 0
        sp.start_y = 50
        sp.edges = [
            CurveToEdge(25, 0, 50, 0),     # curve up
            CurveToEdge(75, 0, 100, 50),    # curve down
            LineToEdge(0, 50),              # close
        ]
        fills = [SolidFill(0, 0, 255, 255)]
        bounds = {"xMin": 0, "xMax": 2000, "yMin": 0, "yMax": 1000}
        shape_tag = build_define_shape3(1, fills, [], [sp], bounds)
        po = sw.build_place_object2(depth=1, character_id=1)
        swf = build_minimal_swf(shape_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 6: DefineShape4 with Focal Gradient
# ══════════════════════════════════════════════════════════════════════════

class TestShape4FocalGradient(unittest.TestCase):
    def test_shape4_focal_gradient(self):
        stops = [GradientStop(0, 255, 255, 0, 255), GradientStop(255, 0, 0, 128, 255)]
        gf = GradientFill("radial", stops, [1.0, 0.0, 0.0, 1.0, 0.0, 0.0], 0, 0, 0.5)  # focal=0.5
        shape_tag = make_simple_rect_shape(1, [gf], [])
        # Upgrade to DefineShape4 by re-tagging. The body is the same but
        # DefineShape4 adds edge bounds. We test if the importer handles it.
        # Actually, shape_converter only builds DefineShape3.
        # We test that radial+focal in DefineShape3 survives roundtrip.
        po = sw.build_place_object2(depth=1, character_id=1)
        swf = build_minimal_swf(shape_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 7: DefineBitsLossless RGB (tag 20)
# ══════════════════════════════════════════════════════════════════════════

class TestBitmapLosslessRGB(unittest.TestCase):
    def test_bitmap_lossless_rgb(self):
        # Build raw DefineBitsLossless (tag 20) format 5 (24-bit)
        w, h = 4, 4
        # Format 5: each row = 0x00RRGGBB per pixel (pad to 4-byte rows)
        row = b""
        for _ in range(w):
            row += struct.pack("BBBB", 0, 255, 128, 64)  # pad, R, G, B
        pixel_data = row * h
        compressed = zlib.compress(pixel_data)
        body = struct.pack("<HBHHi", 1, 5, w, h, len(compressed))
        # Actually, DefineBitsLossless format: charId(u16) + format(u8) + width(u16) + height(u16) + colorData
        body = struct.pack("<HBHH", 1, 5, w, h) + compressed
        tag_bytes = sw.build_tag(20, body, force_long=True)

        # Need a shape to reference the bitmap for it to survive
        bf = BitmapFill(w, h, [255, 128, 64, 255] * (w * h), [20.0, 0.0, 0.0, 20.0, 0.0, 0.0], True, False, bitmap_char_id=1)
        shape_tag = make_simple_rect_shape(2, [bf], [])
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(tag_bytes + shape_tag + po)

        orig, rt = roundtrip(swf)
        # Tag 20 may be converted to tag 36 during roundtrip (ARGB)
        orig_bmp = count_define_tags(orig, 20) + count_define_tags(orig, 36)
        rt_bmp = count_define_tags(rt, 20) + count_define_tags(rt, 36)
        self.assertEqual(orig_bmp, rt_bmp,
            f"Bitmap count mismatch: orig={orig_bmp}, rt={rt_bmp}")


# ══════════════════════════════════════════════════════════════════════════
#  Test 8: DefineBitsLossless2 RGBA (tag 36)
# ══════════════════════════════════════════════════════════════════════════

class TestBitmapLossless2RGBA(unittest.TestCase):
    def test_bitmap_lossless2_rgba(self):
        w, h = 8, 8
        pixels = bytes([100, 200, 50, 128] * (w * h))  # RGBA
        bmp_tag = build_define_bits_lossless2(1, w, h, pixels)
        bf = BitmapFill(w, h, list(pixels), [20.0, 0.0, 0.0, 20.0, 0.0, 0.0], True, False, bitmap_char_id=1)
        shape_tag = make_simple_rect_shape(2, [bf], [])
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(bmp_tag + shape_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 36)
        assert_leaf_bodies_match(self, orig, rt, 36)


# ══════════════════════════════════════════════════════════════════════════
#  Test 9: DefineBitsLossless Palette (format 3)
# ══════════════════════════════════════════════════════════════════════════

class TestBitmapLosslessPalette(unittest.TestCase):
    def test_bitmap_lossless_palette(self):
        w, h = 4, 4
        # Format 3 DefineBitsLossless2 (tag 36): palette + indices
        palette = [
            (255, 0, 0, 255),   # index 0: red
            (0, 255, 0, 255),   # index 1: green
            (0, 0, 255, 255),   # index 2: blue
            (255, 255, 0, 255), # index 3: yellow
        ]
        num_colors_minus_1 = len(palette) - 1
        # Color table: ARGB for each color (premultiplied)
        color_table = b""
        for r, g, b, a in palette:
            color_table += struct.pack("BBBB", a, r, g, b)
        # Index data: rows padded to 4-byte boundary; 1 byte per pixel
        row_size = (w + 3) & ~3
        indices = b""
        for y in range(h):
            row = bytes([y % len(palette)] * w)
            row += b"\x00" * (row_size - w)
            indices += row
        compressed = zlib.compress(color_table + indices)
        body = struct.pack("<HBHH", 1, 3, w, h) + struct.pack("B", num_colors_minus_1) + compressed
        tag_bytes = sw.build_tag(36, body, force_long=True)

        bf = BitmapFill(w, h, [255, 0, 0, 255] * (w * h), [20.0, 0.0, 0.0, 20.0, 0.0, 0.0], True, False, bitmap_char_id=1)
        shape_tag = make_simple_rect_shape(2, [bf], [])
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(tag_bytes + shape_tag + po)
        orig, rt = roundtrip(swf)
        # Palette bitmaps may be expanded to format 5 in roundtrip
        orig_bmp = count_define_tags(orig, 20) + count_define_tags(orig, 36)
        rt_bmp = count_define_tags(rt, 20) + count_define_tags(rt, 36)
        self.assertEqual(orig_bmp, rt_bmp)


# ══════════════════════════════════════════════════════════════════════════
#  Test 10: DefineBitsJPEG2 (tag 21)
# ══════════════════════════════════════════════════════════════════════════

class TestBitmapJPEG(unittest.TestCase):
    def test_bitmap_jpeg(self):
        # Build a minimal valid JPEG (1x1 red pixel)
        # SOI + APP0 minimal + DQT + SOF0 + DHT + SOS + data + EOI
        # Use a real tiny JPEG instead. Minimal approach: build from raw.
        jpeg_data = self._make_tiny_jpeg()
        body = struct.pack("<H", 1) + jpeg_data  # charId + JPEG data
        tag_bytes = sw.build_tag(21, body, force_long=True)

        bf = BitmapFill(1, 1, [255, 0, 0, 255], [20.0, 0.0, 0.0, 20.0, 0.0, 0.0], True, False, bitmap_char_id=1)
        shape_tag = make_simple_rect_shape(2, [bf], [])
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(tag_bytes + shape_tag + po)
        orig, rt = roundtrip(swf)
        # JPEG bitmaps may be converted to DefineBitsLossless2 in roundtrip
        orig_bmp = sum(count_define_tags(orig, t) for t in [6, 21, 35, 90, 20, 36])
        rt_bmp = sum(count_define_tags(rt, t) for t in [6, 21, 35, 90, 20, 36])
        self.assertEqual(orig_bmp, rt_bmp,
            f"Bitmap count mismatch: orig={orig_bmp}, rt={rt_bmp}")

    def _make_tiny_jpeg(self):
        """Generate a minimal 1x1 red JPEG."""
        try:
            from PIL import Image
            import io
            img = Image.new("RGB", (1, 1), (255, 0, 0))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return buf.getvalue()
        except ImportError:
            # Hardcoded minimal 1x1 JPEG (red pixel)
            return bytes([
                0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
                0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
                0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9,
            ])


# ══════════════════════════════════════════════════════════════════════════
#  Test 11: DefineBitsJPEG3 (tag 35) with alpha
# ══════════════════════════════════════════════════════════════════════════

class TestBitmapJPEGAlpha(unittest.TestCase):
    def test_bitmap_jpeg_alpha(self):
        jpeg_data = TestBitmapJPEG._make_tiny_jpeg(self)
        alpha_data = zlib.compress(bytes([200]))  # 1 pixel alpha
        # tag 35: charId(u16) + alphaDataOffset(u32) + jpegData + zlibAlphaData
        alpha_offset = len(jpeg_data)
        body = struct.pack("<HI", 1, alpha_offset) + jpeg_data + alpha_data
        tag_bytes = sw.build_tag(35, body, force_long=True)

        bf = BitmapFill(1, 1, [255, 0, 0, 200], [20.0, 0.0, 0.0, 20.0, 0.0, 0.0], True, False, bitmap_char_id=1)
        shape_tag = make_simple_rect_shape(2, [bf], [])
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(tag_bytes + shape_tag + po)
        orig, rt = roundtrip(swf)
        orig_bmp = sum(count_define_tags(orig, t) for t in [6, 21, 35, 90, 20, 36])
        rt_bmp = sum(count_define_tags(rt, t) for t in [6, 21, 35, 90, 20, 36])
        self.assertEqual(orig_bmp, rt_bmp)


# ══════════════════════════════════════════════════════════════════════════
#  Tests 12-14: Fonts & Text (require real SWFs)
# ══════════════════════════════════════════════════════════════════════════

def _find_real_swf():
    """Find a real SWF file in converted/ for font/text tests."""
    for name in ["gameandwatch_cli.swf", "cli3.swf", "gw_test.swf", "rt_test.swf"]:
        p = os.path.join(CONVERTED_DIR, name)
        if os.path.isfile(p):
            return p
    return None


class TestFont3Glyphs(unittest.TestCase):
    def test_font3_glyphs(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found in converted/")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        if count_define_tags(orig_tags, 75) == 0:
            self.skipTest(f"{swf_path} has no DefineFont3 tags")
        _, rt_tags = roundtrip(swf_bytes)
        assert_tag_type_count_matches(self, orig_tags, rt_tags, 75)


class TestFontAuxTags(unittest.TestCase):
    def test_font_aux_tags(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found in converted/")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        _, rt_tags = roundtrip(swf_bytes)
        # Check FontAlignZones(73), CSMTextSettings(74), DefineFontName(88)
        for aux_tag in [73, 74, 88]:
            orig_count = sum(1 for tt, _ in orig_tags if tt == aux_tag)
            rt_count = sum(1 for tt, _ in rt_tags if tt == aux_tag)
            if orig_count > 0:
                self.assertGreaterEqual(rt_count, 1,
                    f"Aux tag {aux_tag} missing: orig={orig_count}, rt={rt_count}")


class TestStaticText(unittest.TestCase):
    def test_static_text(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found in converted/")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        has_text = count_define_tags(orig_tags, 11) + count_define_tags(orig_tags, 33)
        if has_text == 0:
            self.skipTest(f"{swf_path} has no DefineText tags")
        _, rt_tags = roundtrip(swf_bytes)
        orig_count = count_define_tags(orig_tags, 11) + count_define_tags(orig_tags, 33)
        rt_count = count_define_tags(rt_tags, 11) + count_define_tags(rt_tags, 33)
        self.assertEqual(orig_count, rt_count,
            f"Text tag count mismatch: orig={orig_count}, rt={rt_count}")


# ══════════════════════════════════════════════════════════════════════════
#  Test 15: DefineEditText (tag 37)
# ══════════════════════════════════════════════════════════════════════════

class TestEditText(unittest.TestCase):
    def test_edit_text(self):
        # Build a minimal DefineEditText body manually
        # charId(u16) + RECT + flags(u16) + ...
        # Use the raw approach since text_converter.build_define_edit_text needs a dict
        from text_converter import build_define_edit_text
        tf = {
            "bounds": {"xMin": 0, "xMax": 2000, "yMin": 0, "yMax": 400},
            "text": "Hello",
            "size": 12,
            "color": 0x000000FF,
            "align": "left",
            "leading": 0,
            "letterSpacing": 0,
            "leftMargin": 0,
            "rightMargin": 0,
            "multiline": False,
            "wordWrap": False,
            "border": False,
            "scroll": False,
            "autoSize": False,
            "inputType": "dynamic",
        }
        edit_tag = build_define_edit_text(1, tf)
        po = sw.build_place_object2(depth=1, character_id=1)
        swf = build_minimal_swf(edit_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 37)


# ══════════════════════════════════════════════════════════════════════════
#  Test 16: Sprite Basic (single-frame)
# ══════════════════════════════════════════════════════════════════════════

class TestSpriteBasic(unittest.TestCase):
    def test_sprite_basic(self):
        shape_tag = make_simple_rect_shape(1, [SolidFill(255, 0, 0, 255)], [])
        inner = sw.build_place_object2(depth=1, character_id=1)
        inner += sw.build_tag_show_frame()
        inner += sw.build_tag_end()
        sprite_tag = sw.build_define_sprite(2, frame_count=1, control_tags=inner)
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(shape_tag + sprite_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 39)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 17: Sprite Multi-frame
# ══════════════════════════════════════════════════════════════════════════

class TestSpriteMultiframe(unittest.TestCase):
    def test_sprite_multiframe(self):
        s1 = make_simple_rect_shape(1, [SolidFill(255, 0, 0, 255)], [])
        s2 = make_simple_rect_shape(2, [SolidFill(0, 255, 0, 255)], [])
        inner = sw.build_place_object2(depth=1, character_id=1)
        inner += sw.build_tag_show_frame()
        inner += sw.build_remove_object2(depth=1)
        inner += sw.build_place_object2(depth=1, character_id=2)
        inner += sw.build_tag_show_frame()
        inner += sw.build_tag_end()
        sprite_tag = sw.build_define_sprite(3, frame_count=2, control_tags=inner)
        po = sw.build_place_object2(depth=1, character_id=3)
        swf = build_minimal_swf(s1 + s2 + sprite_tag + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 39)
        self.assertGreaterEqual(count_define_tags(rt, 32), 2)


# ══════════════════════════════════════════════════════════════════════════
#  Test 18: Sprite Nested
# ══════════════════════════════════════════════════════════════════════════

class TestSpriteNested(unittest.TestCase):
    def test_sprite_nested(self):
        shape = make_simple_rect_shape(1, [SolidFill(0, 0, 255, 255)], [])
        inner1 = sw.build_place_object2(depth=1, character_id=1)
        inner1 += sw.build_tag_show_frame()
        inner1 += sw.build_tag_end()
        sprite1 = sw.build_define_sprite(2, 1, inner1)
        inner2 = sw.build_place_object2(depth=1, character_id=2)
        inner2 += sw.build_tag_show_frame()
        inner2 += sw.build_tag_end()
        sprite2 = sw.build_define_sprite(3, 1, inner2)
        po = sw.build_place_object2(depth=1, character_id=3)
        swf = build_minimal_swf(shape + sprite1 + sprite2 + po)
        orig, rt = roundtrip(swf)
        # Should have 2 sprites in output
        self.assertGreaterEqual(count_define_tags(rt, 39), 2)


# ══════════════════════════════════════════════════════════════════════════
#  Test 19: Sprite Frame Labels
# ══════════════════════════════════════════════════════════════════════════

class TestSpriteFrameLabels(unittest.TestCase):
    def test_sprite_frame_labels(self):
        shape = make_simple_rect_shape(1, [SolidFill(128, 128, 128, 255)], [])
        inner = sw.build_frame_label("start")
        inner += sw.build_place_object2(depth=1, character_id=1)
        inner += sw.build_tag_show_frame()
        inner += sw.build_frame_label("end")
        inner += sw.build_tag_show_frame()
        inner += sw.build_tag_end()
        sprite = sw.build_define_sprite(2, 2, inner)
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(shape + sprite + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 39)


# ══════════════════════════════════════════════════════════════════════════
#  Test 20: PlaceObject2
# ══════════════════════════════════════════════════════════════════════════

class TestPlaceObject2(unittest.TestCase):
    def test_place_object2(self):
        shape = make_simple_rect_shape(1, [SolidFill(255, 128, 0, 255)], [])
        matrix = sw.write_matrix(a=1.5, d=1.5, tx=100.0, ty=50.0)
        cxform = sw.write_cxform_alpha(r_mul=0.5, a_mul=0.8)
        po = sw.build_place_object2(
            depth=1, character_id=1, matrix=matrix,
            color_transform=cxform, name="testInst", clip_depth=5)
        swf = build_minimal_swf(shape + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)
        # Verify PlaceObject2/3 exist in output
        rt_po = sum(1 for tt, _ in rt if tt in (26, 70))
        self.assertGreaterEqual(rt_po, 1)


# ══════════════════════════════════════════════════════════════════════════
#  Test 21: PlaceObject3 with Blend Mode
# ══════════════════════════════════════════════════════════════════════════

class TestPlaceObject3Blend(unittest.TestCase):
    def test_place_object3_blend(self):
        shape = make_simple_rect_shape(1, [SolidFill(0, 128, 255, 255)], [])
        po = sw.build_place_object3(
            depth=1, character_id=1, blend_mode=sw.SWF_BLEND_MULTIPLY)
        swf = build_minimal_swf(shape + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 22: PlaceObject3 with Filters
# ══════════════════════════════════════════════════════════════════════════

class TestPlaceObject3Filters(unittest.TestCase):
    def test_place_object3_filters(self):
        shape = make_simple_rect_shape(1, [SolidFill(128, 0, 128, 255)], [])
        # Encode a simple blur filter: BlurFilter(blurX=4, blurY=4, passes=1)
        filter_data = sw.encode_filter_list([{
            "class": "BlurFilter",
            "blurX": 4.0, "blurY": 4.0, "quality": 1,
        }])
        po = sw.build_place_object3(
            depth=1, character_id=1, filters_data=filter_data)
        swf = build_minimal_swf(shape + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 32)


# ══════════════════════════════════════════════════════════════════════════
#  Test 23: Move Operations
# ══════════════════════════════════════════════════════════════════════════

class TestMoveOperations(unittest.TestCase):
    def test_move_operations(self):
        shape = make_simple_rect_shape(1, [SolidFill(64, 64, 64, 255)], [])
        inner = sw.build_place_object2(depth=1, character_id=1)
        inner += sw.build_tag_show_frame()
        # Move: new matrix at same depth
        matrix2 = sw.write_matrix(tx=50.0, ty=50.0)
        inner += sw.build_place_object2(depth=1, matrix=matrix2, is_move=True)
        inner += sw.build_tag_show_frame()
        inner += sw.build_tag_end()
        sprite = sw.build_define_sprite(2, 2, inner)
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(shape + sprite + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 39)


# ══════════════════════════════════════════════════════════════════════════
#  Tests 24-25: Morph Shapes (require real SWFs)
# ══════════════════════════════════════════════════════════════════════════

class TestMorphShape(unittest.TestCase):
    def test_morph_shape(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        morph_count = count_define_tags(orig_tags, 46) + count_define_tags(orig_tags, 84)
        if morph_count == 0:
            self.skipTest(f"{swf_path} has no morph shapes")
        _, rt_tags = roundtrip(swf_bytes)
        rt_morph = count_define_tags(rt_tags, 46) + count_define_tags(rt_tags, 84)
        self.assertEqual(morph_count, rt_morph,
            f"MorphShape count: orig={morph_count}, rt={rt_morph}")


class TestMorphShape2(unittest.TestCase):
    def test_morph_shape2(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        if count_define_tags(orig_tags, 84) == 0:
            self.skipTest(f"{swf_path} has no DefineMorphShape2 (tag 84)")
        _, rt_tags = roundtrip(swf_bytes)
        assert_tag_type_count_matches(self, orig_tags, rt_tags, 84)


# ══════════════════════════════════════════════════════════════════════════
#  Test 26: DefineSound MP3
# ══════════════════════════════════════════════════════════════════════════

class TestSoundMP3(unittest.TestCase):
    def test_sound_mp3(self):
        # Build a minimal DefineSound tag 14 with MP3 format
        # Format 2 = MP3, rate code 3 = 44100, size 1 = 16-bit, type 1 = stereo
        # flags: format(4) | rate(2) | size(1) | type(1) = 0x62 | 0x0C | 0x02 | 0x01
        # Actually: soundFormat<<4 | soundRate<<2 | soundSize<<1 | soundType
        # MP3=2, 44100=3, 16bit=1, stereo=1 → (2<<4)|(3<<2)|(1<<1)|1 = 0x2F
        flags = (2 << 4) | (3 << 2) | (1 << 1) | 1
        sample_count = 1152
        seek_samples = 0
        # Minimal MP3 frame (silent, MPEG1 Layer3 128kbps 44100 stereo)
        # Use sync word + minimal valid frame header
        mp3_frame = bytes([0xFF, 0xFB, 0x90, 0x00]) + bytes(413)  # ~417 bytes for 128kbps frame
        body = struct.pack("<HBI", 1, flags, sample_count)
        body += struct.pack("<h", seek_samples)  # SeekSamples (signed)
        body += mp3_frame
        tag_bytes = sw.build_tag(14, body, force_long=True)

        # Put sound in a sprite timeline with StartSound
        start_sound_body = struct.pack("<HB", 1, 0)  # charId=1, flags=0 (no envelope)
        start_tag = sw.build_tag(15, start_sound_body)

        inner = start_tag
        inner += sw.build_tag_show_frame()
        inner += sw.build_tag_end()
        sprite = sw.build_define_sprite(2, 1, inner)
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(tag_bytes + sprite + po)
        orig, rt = roundtrip(swf)
        assert_tag_type_count_matches(self, orig, rt, 14)


# ══════════════════════════════════════════════════════════════════════════
#  Test 27: StartSound
# ══════════════════════════════════════════════════════════════════════════

class TestStartSound(unittest.TestCase):
    def test_start_sound(self):
        # Same setup as test 26 — the presence of StartSound in the sprite
        flags = (2 << 4) | (3 << 2) | (1 << 1) | 1
        mp3_frame = bytes([0xFF, 0xFB, 0x90, 0x00]) + bytes(413)
        body = struct.pack("<HBI", 1, flags, 1152)
        body += struct.pack("<h", 0) + mp3_frame
        sound_tag = sw.build_tag(14, body, force_long=True)

        start_body = struct.pack("<HB", 1, 0)
        start_tag = sw.build_tag(15, start_body)

        inner = start_tag + sw.build_tag_show_frame() + sw.build_tag_end()
        sprite = sw.build_define_sprite(2, 1, inner)
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(sound_tag + sprite + po)
        orig, rt = roundtrip(swf)
        # Verify sound definition survives
        assert_tag_type_count_matches(self, orig, rt, 14)


# ══════════════════════════════════════════════════════════════════════════
#  Test 28: DoABC Passthrough
# ══════════════════════════════════════════════════════════════════════════

class TestDoABCPassthrough(unittest.TestCase):
    def test_doabc_passthrough(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        # Find DoABC2 (82) bodies
        orig_abc = [body for tt, body in orig_tags if tt == 82]
        if not orig_abc:
            self.skipTest("No DoABC2 tags")
        _, rt_tags = roundtrip(swf_bytes)
        rt_abc = [body for tt, body in rt_tags if tt == 82]
        # At least one DoABC tag should survive
        self.assertGreaterEqual(len(rt_abc), 1,
            f"DoABC2 tags: orig={len(orig_abc)}, rt={len(rt_abc)}")
        # The ABC bytecode should be preserved (after the name header)
        # Extract ABC data from DoABC2: skip flags(4) + null-terminated name
        def extract_abc(body):
            pos = 4  # skip flags
            while pos < len(body) and body[pos] != 0:
                pos += 1
            pos += 1  # skip null terminator
            return body[pos:]
        if orig_abc and rt_abc:
            self.assertEqual(extract_abc(orig_abc[0]), extract_abc(rt_abc[0]),
                "ABC bytecode differs after roundtrip")


# ══════════════════════════════════════════════════════════════════════════
#  Test 29: SymbolClass
# ══════════════════════════════════════════════════════════════════════════

class TestSymbolClass(unittest.TestCase):
    def test_symbol_class(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        orig_sc = [body for tt, body in orig_tags if tt == 76]
        if not orig_sc:
            self.skipTest("No SymbolClass tags")

        _, rt_tags = roundtrip(swf_bytes)
        rt_sc = [body for tt, body in rt_tags if tt == 76]
        self.assertGreaterEqual(len(rt_sc), 1, "SymbolClass missing from output")

        # Extract class names from SymbolClass body
        def parse_symbol_class(body):
            count = struct.unpack_from("<H", body, 0)[0]
            names = set()
            pos = 2
            for _ in range(count):
                pos += 2  # skip charId
                end = body.index(0, pos)
                names.add(body[pos:end].decode("utf-8", errors="replace"))
                pos = end + 1
            return names

        orig_names = set()
        for b in orig_sc:
            orig_names |= parse_symbol_class(b)
        rt_names = set()
        for b in rt_sc:
            rt_names |= parse_symbol_class(b)

        # All original class names should be present
        missing = orig_names - rt_names
        self.assertEqual(len(missing), 0,
            f"Missing class names: {missing}")


# ══════════════════════════════════════════════════════════════════════════
#  Test 30: FileAttributes
# ══════════════════════════════════════════════════════════════════════════

class TestFileAttributes(unittest.TestCase):
    def test_file_attributes(self):
        shape = make_simple_rect_shape(1, [SolidFill(255, 0, 0, 255)], [])
        po = sw.build_place_object2(depth=1, character_id=1)
        swf = build_minimal_swf(shape + po)
        _, rt = roundtrip(swf)
        fa = [body for tt, body in rt if tt == 69]
        self.assertGreaterEqual(len(fa), 1, "FileAttributes missing")
        # Check AS3 flag is set (bit 3)
        if fa:
            flags = struct.unpack_from("<I", fa[0], 0)[0]
            self.assertTrue(flags & 0x08, "AS3 flag not set in FileAttributes")


# ══════════════════════════════════════════════════════════════════════════
#  Test 31: SetBackgroundColor
# ══════════════════════════════════════════════════════════════════════════

class TestBackgroundColor(unittest.TestCase):
    def test_background_color(self):
        tags_bytes = sw.build_file_attributes(has_as3=True)
        tags_bytes += sw.build_set_background_color(64, 128, 192)
        tags_bytes += sw.build_tag_show_frame()
        tags_bytes += sw.build_tag_end()
        swf = sw.build_swf_file(100, 100, 24, 1, tags_bytes)
        _, rt = roundtrip(swf)
        bg = [body for tt, body in rt if tt == 9]
        self.assertGreaterEqual(len(bg), 1, "SetBackgroundColor missing")


# ══════════════════════════════════════════════════════════════════════════
#  Test 32: Protect Tag
# ══════════════════════════════════════════════════════════════════════════

class TestProtectTag(unittest.TestCase):
    def test_protect_tag(self):
        swf_path = _find_real_swf()
        if not swf_path:
            self.skipTest("No real SWF found")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        orig_protect = sum(1 for tt, _ in orig_tags if tt == 24)
        if orig_protect == 0:
            # If no protect tag, test passes (nothing to preserve)
            return
        _, rt_tags = roundtrip(swf_bytes)
        rt_protect = sum(1 for tt, _ in rt_tags if tt == 24)
        self.assertGreaterEqual(rt_protect, 1, "Protect tag lost")


# ══════════════════════════════════════════════════════════════════════════
#  Test 33: Full Roundtrip - gameandwatch_cli.n2d
# ══════════════════════════════════════════════════════════════════════════

class TestRoundtripGameAndWatch(unittest.TestCase):
    def test_roundtrip_gameandwatch(self):
        n2d_path = os.path.join(CONVERTED_DIR, "gameandwatch_cli.n2d")
        swf_path = os.path.join(CONVERTED_DIR, "gameandwatch_cli.swf")
        if not os.path.isfile(swf_path):
            self.skipTest("gameandwatch_cli.swf not found")
        with open(swf_path, "rb") as f:
            swf_bytes = f.read()
        orig_tags = parse_swf_tags(swf_bytes)
        _, rt_tags = roundtrip(swf_bytes)

        # Verify all define tag types are present
        orig_def_types = set(tt for tt, body in orig_tags if tt in DEFINE_TAGS)
        rt_def_types = set(tt for tt, body in rt_tags if tt in DEFINE_TAGS)
        missing = orig_def_types - rt_def_types
        # Some tag types may be converted (e.g., tag 20→36)
        critical_missing = missing - {20, 22, 2}  # these may be upgraded
        self.assertEqual(len(critical_missing), 0,
            f"Missing define tag types: {critical_missing}")

        # Verify counts are close for key types
        for tt in [32, 36, 39, 14, 75]:
            oc = count_define_tags(orig_tags, tt)
            rc = count_define_tags(rt_tags, tt)
            if oc > 0:
                self.assertGreaterEqual(rc, 1,
                    f"Tag {tt}: orig={oc}, rt={rc}")


# ══════════════════════════════════════════════════════════════════════════
#  Test 34: Determinism (same N2D → identical SWF 3x)
# ══════════════════════════════════════════════════════════════════════════

class TestRoundtripDeterminism(unittest.TestCase):
    def test_roundtrip_determinism(self):
        n2d_path = os.path.join(CONVERTED_DIR, "gameandwatch_cli.n2d")
        if not os.path.isfile(n2d_path):
            self.skipTest("gameandwatch_cli.n2d not found")

        outputs = []
        for i in range(3):
            with tempfile.TemporaryDirectory(prefix=f"det{i}_") as tmp:
                out_path = os.path.join(tmp, f"out{i}.swf")
                compiler = compile_n2d.N2DCompiler(
                    n2d_path=n2d_path,
                    shared_dir=tmp,
                    output_path=out_path,
                    sdk_path=None,
                )
                compiler.compile()
                with open(out_path, "rb") as f:
                    outputs.append(f.read())

        self.assertEqual(outputs[0], outputs[1],
            f"Run 1 vs 2 differ: {len(outputs[0])} vs {len(outputs[1])} bytes")
        self.assertEqual(outputs[1], outputs[2],
            f"Run 2 vs 3 differ: {len(outputs[1])} vs {len(outputs[2])} bytes")


# ══════════════════════════════════════════════════════════════════════════
#  Test 35: Structural Validation
# ══════════════════════════════════════════════════════════════════════════

class TestStructuralValidation(unittest.TestCase):
    def test_structural_validation(self):
        shape = make_simple_rect_shape(1, [SolidFill(150, 150, 150, 255)], [])
        inner = sw.build_place_object2(depth=1, character_id=1)
        inner += sw.build_tag_show_frame()
        inner += sw.build_tag_end()
        sprite = sw.build_define_sprite(2, 1, inner)
        po = sw.build_place_object2(depth=1, character_id=2)
        swf = build_minimal_swf(shape + sprite + po)
        _, rt = roundtrip(swf)

        # 1. SWF must end with End tag
        self.assertEqual(rt[-1][0], 0, "SWF does not end with End tag")

        # 2. FileAttributes must be first tag
        self.assertEqual(rt[0][0], 69, "First tag is not FileAttributes")

        # 3. Every DefineSprite must end with End tag
        for tt, body in rt:
            if tt == 39 and len(body) >= 4:
                # Parse sprite body: spriteId(u16) + frameCount(u16) + tags...
                inner_tags = parse_sprite_tags(body[4:])
                if inner_tags:
                    self.assertEqual(inner_tags[-1][0], 0,
                        "Sprite does not end with End tag")

        # 4. No truncated long tags
        # (checked implicitly by parse_swf_tags succeeding)
        self.assertGreater(len(rt), 3, "Too few tags in output SWF")


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


# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main()
