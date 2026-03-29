#!/usr/bin/env python3
"""
swf_to_n2d.py — Convert a SWF file into a complete .n2d project for the
Next2D Animation Tool using only pure-Python parsing (no JPEXS).

This script:
  1. Parses the SWF binary for timeline structure (DefineSprite, PlaceObject,
     ShowFrame, RemoveObject, FrameLabel)
  2. Decodes bitmaps directly from SWF tags (DefineBitsLossless/JPEG)
  3. Parses shapes from raw DefineShape binary data
  4. Extracts SymbolClass names from SWF tags
  5. Decompiles AS3 source from DoABC bytecode via as3_decompiler
  6. Builds a complete .n2d JSON with all library entries, layers, and frames
  7. Saves as .n2d file (JSON → URI-encode → zlib compress)

Usage:
    python swf_to_n2d.py <swf_file> [output.n2d]

Example:
    python swf_to_n2d.py gameandwatch.swf gameandwatch.n2d
"""

from __future__ import annotations

import base64
import io
import json
import logging
import math
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote

log = logging.getLogger(__name__)

# NumPy optional — used for fast palette-indexed bitmap decoding (fmt==3)
try:
    import numpy as _np
    _HAS_NUMPY = True
except ImportError:
    _np = None
    _HAS_NUMPY = False

from swf_shape_to_recodes import parse_define_shape_to_recodes, parse_define_morph_shape_to_recodes

# AS3 Weaver — pure-Python AVM2/ABC decompiler
# Locate the as3_decompiler package:
#   1. Workspace root (parent of Next2Flash/) has as3_decompiler/
#   2. Sibling repo: ../../AS3-Weaver-Github/as3_decompiler
_this_dir = os.path.dirname(os.path.abspath(__file__))
_workspace_root = os.path.normpath(os.path.join(_this_dir, '..'))
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)
_as3_weaver_dir = os.path.normpath(os.path.join(_this_dir, '..', '..', 'AS3-Weaver-Github'))
if os.path.isdir(_as3_weaver_dir) and _as3_weaver_dir not in sys.path:
    sys.path.insert(0, _as3_weaver_dir)

try:
    from as3_decompiler import ABCFile, AS3Decompiler
    from as3_decompiler.swf_reader import extract_abc_blocks
    HAS_AS3_DECOMPILER = True
except ImportError:
    HAS_AS3_DECOMPILER = False

# ═══════════════════════════════════════════════════════════════════════════
#  SWF BINARY PARSER
# ═══════════════════════════════════════════════════════════════════════════

# SWF tag type constants
TAG_END                     = 0
TAG_SHOW_FRAME              = 1
TAG_DEFINE_SHAPE            = 2
TAG_DEFINE_SHAPE2           = 22
TAG_DEFINE_SHAPE3           = 32
TAG_DEFINE_SHAPE4           = 83
TAG_DEFINE_BITS             = 6
TAG_DEFINE_BITS_JPEG2       = 21
TAG_DEFINE_BITS_JPEG3       = 35
TAG_DEFINE_BITS_JPEG4       = 90
TAG_DEFINE_BITS_LOSSLESS    = 20
TAG_DEFINE_BITS_LOSSLESS2   = 36
TAG_DEFINE_SPRITE           = 39
TAG_PLACE_OBJECT2           = 26
TAG_PLACE_OBJECT3           = 70
TAG_REMOVE_OBJECT2          = 28
TAG_FRAME_LABEL             = 43
TAG_DEFINE_SOUND            = 14
TAG_DEFINE_TEXT              = 11
TAG_DEFINE_TEXT2             = 33
TAG_DEFINE_EDIT_TEXT         = 37
TAG_DEFINE_MORPH_SHAPE      = 46
TAG_DEFINE_MORPH_SHAPE2     = 84
TAG_SYMBOL_CLASS            = 76
TAG_DO_ABC                  = 72
TAG_DO_ABC2                 = 82
TAG_FILE_ATTRIBUTES         = 69
TAG_SET_BACKGROUND_COLOR    = 9
TAG_DEFINE_FONT3            = 75
TAG_START_SOUND             = 15
TAG_START_SOUND2            = 89


class BitReader:
    """Read individual bits from a byte buffer."""

    def __init__(self, data: bytes, byte_offset: int = 0):
        self.data = data
        self.byte_pos = byte_offset
        self.bit_pos = 0

    @property
    def pos(self):
        return self.byte_pos * 8 + self.bit_pos

    def align(self):
        """Align to next byte boundary."""
        if self.bit_pos > 0:
            self.byte_pos += 1
            self.bit_pos = 0

    def read_ub(self, n: int) -> int:
        """Read n unsigned bits."""
        if n == 0:
            return 0
        result = 0
        for _ in range(n):
            byte_val = self.data[self.byte_pos]
            bit = (byte_val >> (7 - self.bit_pos)) & 1
            result = (result << 1) | bit
            self.bit_pos += 1
            if self.bit_pos >= 8:
                self.bit_pos = 0
                self.byte_pos += 1
        return result

    def read_sb(self, n: int) -> int:
        """Read n signed bits (two's complement)."""
        if n == 0:
            return 0
        val = self.read_ub(n)
        if val & (1 << (n - 1)):  # sign bit set
            val -= (1 << n)
        return val

    def read_fb(self, n: int) -> float:
        """Read n-bit fixed-point 16.16 value."""
        return self.read_sb(n) / 65536.0

    def read_ui8(self) -> int:
        self.align()
        val = self.data[self.byte_pos]
        self.byte_pos += 1
        return val

    def read_ui16(self) -> int:
        self.align()
        val = struct.unpack_from('<H', self.data, self.byte_pos)[0]
        self.byte_pos += 2
        return val

    def read_ui32(self) -> int:
        self.align()
        val = struct.unpack_from('<I', self.data, self.byte_pos)[0]
        self.byte_pos += 4
        return val

    def read_si16(self) -> int:
        self.align()
        val = struct.unpack_from('<h', self.data, self.byte_pos)[0]
        self.byte_pos += 2
        return val

    def read_string(self) -> str:
        self.align()
        end = self.data.index(0, self.byte_pos)
        s = self.data[self.byte_pos:end].decode('utf-8', errors='replace')
        self.byte_pos = end + 1
        return s


def read_rect(br: BitReader) -> dict:
    """Parse a RECT record."""
    nbits = br.read_ub(5)
    xmin = br.read_sb(nbits)
    xmax = br.read_sb(nbits)
    ymin = br.read_sb(nbits)
    ymax = br.read_sb(nbits)
    return {'xMin': xmin, 'xMax': xmax, 'yMin': ymin, 'yMax': ymax}


def read_matrix(br: BitReader) -> List[float]:
    """Parse a MATRIX record → [scaleX, rotSkew0, rotSkew1, scaleY, tx, ty].
    tx/ty are in twips."""
    scale_x = 1.0
    scale_y = 1.0
    rot_skew0 = 0.0
    rot_skew1 = 0.0

    has_scale = br.read_ub(1)
    if has_scale:
        nbits = br.read_ub(5)
        scale_x = br.read_fb(nbits)
        scale_y = br.read_fb(nbits)

    has_rotate = br.read_ub(1)
    if has_rotate:
        nbits = br.read_ub(5)
        rot_skew0 = br.read_fb(nbits)
        rot_skew1 = br.read_fb(nbits)

    nbits_translate = br.read_ub(5)
    tx = br.read_sb(nbits_translate)  # twips
    ty = br.read_sb(nbits_translate)  # twips

    # Convert twips to pixels for tx/ty
    return [scale_x, rot_skew0, rot_skew1, scale_y, tx / 20.0, ty / 20.0]


def read_cxform_with_alpha(br: BitReader) -> List[float]:
    """Parse CXFORMWITHALPHA → [rMul, gMul, bMul, aMul, rAdd, gAdd, bAdd, aAdd].
    Multipliers are 0..1 range (SWF stores as 8.8 fixed), adds are -255..255."""
    has_add = br.read_ub(1)
    has_mul = br.read_ub(1)
    nbits = br.read_ub(4)

    if has_mul:
        r_mul = br.read_sb(nbits) / 256.0
        g_mul = br.read_sb(nbits) / 256.0
        b_mul = br.read_sb(nbits) / 256.0
        a_mul = br.read_sb(nbits) / 256.0
    else:
        r_mul = g_mul = b_mul = a_mul = 1.0

    if has_add:
        r_add = br.read_sb(nbits)
        g_add = br.read_sb(nbits)
        b_add = br.read_sb(nbits)
        a_add = br.read_sb(nbits)
    else:
        r_add = g_add = b_add = a_add = 0

    return [r_mul, g_mul, b_mul, a_mul, r_add, g_add, b_add, a_add]


def read_filter_list(br: BitReader) -> List[dict]:
    """Parse FILTERLIST (for PlaceObject3). Returns simplified filter list."""
    count = br.read_ui8()
    filters = []
    for _ in range(count):
        filter_id = br.read_ui8()
        # Skip filter data — we just need to advance the reader past it.
        # This is complex; for now return empty and skip remaining filters.
        # TODO: implement full filter parsing if needed
        break  # bail out — filters are complex to parse
    return filters


class SWFTag:
    """Represents a parsed SWF tag."""
    __slots__ = ('tag_type', 'data', 'offset')

    def __init__(self, tag_type: int, data: bytes, offset: int):
        self.tag_type = tag_type
        self.data = data
        self.offset = offset


def parse_swf(swf_data: bytes) -> Tuple[dict, List[SWFTag]]:
    """Parse SWF header and all top-level tags.
    Returns (header_info, [SWFTag, ...])."""
    log.debug('parse_swf: parsing %d bytes', len(swf_data))
    sig = swf_data[0:3]
    if sig not in (b'FWS', b'CWS', b'ZWS'):
        raise ValueError(f"Not a SWF file (signature: {sig!r})")

    version = swf_data[3]
    file_length = struct.unpack_from('<I', swf_data, 4)[0]

    # Decompress
    if sig == b'CWS':
        body = zlib.decompress(swf_data[8:])
        data = swf_data[:8] + body
    elif sig == b'ZWS':
        import lzma
        body = lzma.decompress(swf_data[12:])
        data = swf_data[:8] + body
    else:
        data = swf_data

    # Parse header RECT
    br = BitReader(data, 8)
    rect = read_rect(br)
    br.align()

    # Frame rate + frame count
    fps_raw = struct.unpack_from('<H', data, br.byte_pos)[0]
    fps = fps_raw >> 8
    if fps == 0:
        fps = fps_raw & 0xFF or 24
    frame_count = struct.unpack_from('<H', data, br.byte_pos + 2)[0]

    header = {
        'version': version,
        'compressed': (sig == b'CWS' or sig == b'ZWS'),
        'width': max((rect['xMax'] - rect['xMin']) // 20, 1),
        'height': max((rect['yMax'] - rect['yMin']) // 20, 1),
        'fps': fps,
        'frameCount': max(frame_count, 1),
    }

    # Parse tags
    tag_offset = br.byte_pos + 4
    tags = parse_tags(data, tag_offset)

    return header, tags


def parse_tags(data: bytes, offset: int) -> List[SWFTag]:
    """Parse a sequence of SWF tags starting at offset."""
    log.debug('parse_tags: starting at offset %d, data len %d', offset, len(data))
    tags = []
    pos = offset
    while pos < len(data) - 1:
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        pos += 2
        if tag_length == 0x3F:  # long tag
            tag_length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        tag_data = data[pos:pos + tag_length]
        tags.append(SWFTag(tag_type, tag_data, pos))
        pos += tag_length
        if tag_type == TAG_END:
            break
    return tags


# ── Tag-specific parsers ─────────────────────────────────────────────────

def parse_define_sprite(tag: SWFTag) -> Tuple[int, int, List[SWFTag]]:
    """Parse DefineSprite → (charId, frameCount, [nested tags])."""
    char_id = struct.unpack_from('<H', tag.data, 0)[0]
    frame_count = struct.unpack_from('<H', tag.data, 2)[0]
    nested = parse_tags(tag.data, 4)
    return char_id, frame_count, nested


def parse_place_object2(tag_data: bytes, swf_version: int = 10) -> dict:
    """Parse PlaceObject2 tag data → placement dict."""
    flags = tag_data[0]
    has_clip_actions = bool(flags & 0x80)
    has_clip_depth = bool(flags & 0x40)
    has_name = bool(flags & 0x20)
    has_ratio = bool(flags & 0x10)
    has_color_transform = bool(flags & 0x08)
    has_matrix = bool(flags & 0x04)
    has_character = bool(flags & 0x02)
    is_move = bool(flags & 0x01)

    depth = struct.unpack_from('<H', tag_data, 1)[0]
    result = {
        'depth': depth,
        'move': is_move,
        'charId': None,
        'matrix': None,
        'colorTransform': None,
        'name': None,
        'ratio': None,
        'clipDepth': None,
        'blendMode': None,
        'filters': [],
    }

    try:
        br = BitReader(tag_data, 3)

        if has_character:
            result['charId'] = br.read_ui16()

        if has_matrix:
            result['matrix'] = read_matrix(br)
            br.align()

        if has_color_transform:
            result['colorTransform'] = read_cxform_with_alpha(br)
            br.align()

        if has_ratio:
            result['ratio'] = br.read_ui16()

        if has_name:
            result['name'] = br.read_string()

        if has_clip_depth:
            result['clipDepth'] = br.read_ui16()
    except (IndexError, struct.error):
        pass  # return what we have

    return result


def parse_place_object3(tag_data: bytes) -> dict:
    """Parse PlaceObject3 tag data → placement dict.
    PlaceObject3 has extra flags byte for filters, blend mode, cache bitmap."""
    flags1 = tag_data[0]
    flags2 = tag_data[1]

    has_clip_actions = bool(flags1 & 0x80)
    has_clip_depth = bool(flags1 & 0x40)
    has_name = bool(flags1 & 0x20)
    has_ratio = bool(flags1 & 0x10)
    has_color_transform = bool(flags1 & 0x08)
    has_matrix = bool(flags1 & 0x04)
    has_character = bool(flags1 & 0x02)
    is_move = bool(flags1 & 0x01)

    # flags2 (PlaceObject3 extended)
    has_opaque_bg = bool(flags2 & 0x40)    # PlaceFlagOpaqueBackground
    has_visible = bool(flags2 & 0x20)      # PlaceFlagHasVisible
    has_image = bool(flags2 & 0x10)        # PlaceFlagHasImage
    has_class_name = bool(flags2 & 0x08)   # PlaceFlagHasClassName
    has_cache_bitmap = bool(flags2 & 0x04) # PlaceFlagHasCacheAsBitmap
    has_blend_mode = bool(flags2 & 0x02)   # PlaceFlagHasBlendMode
    has_filter_list = bool(flags2 & 0x01)  # PlaceFlagHasFilterList

    depth = struct.unpack_from('<H', tag_data, 2)[0]
    result = {
        'depth': depth,
        'move': is_move,
        'charId': None,
        'matrix': None,
        'colorTransform': None,
        'name': None,
        'ratio': None,
        'clipDepth': None,
        'blendMode': None,
        'filters': [],
    }

    try:
        br = BitReader(tag_data, 4)

        # Only read className when HasClassName flag is explicitly set.
        # The SWF spec condition (HasImage && HasCharacter) is unreliable
        # in practice — many SWFs set HasImage as a caching hint only.
        if has_class_name:
            result['className'] = br.read_string()

        if has_character:
            result['charId'] = br.read_ui16()

        if has_matrix:
            result['matrix'] = read_matrix(br)
            br.align()

        if has_color_transform:
            result['colorTransform'] = read_cxform_with_alpha(br)
            br.align()

        if has_ratio:
            result['ratio'] = br.read_ui16()

        if has_name:
            result['name'] = br.read_string()

        if has_clip_depth:
            result['clipDepth'] = br.read_ui16()

        if has_filter_list:
            # Skip filter list — too complex to parse generically.
            # Can't read blend_mode or cache_bitmap after this.
            pass
        elif has_blend_mode:
            result['blendMode'] = br.read_ui8()
    except (IndexError, struct.error):
        # Gracefully handle parse errors — return what we have so far
        pass

    return result


def parse_frame_label(tag_data: bytes) -> str:
    """Parse FrameLabel tag → label name string."""
    end = tag_data.index(0)
    return tag_data[:end].decode('utf-8', errors='replace')


def parse_symbol_class(tag_data: bytes) -> Dict[int, str]:
    """Parse SymbolClass tag → {charId: className}."""
    num = struct.unpack_from('<H', tag_data, 0)[0]
    result = {}
    pos = 2
    for _ in range(num):
        char_id = struct.unpack_from('<H', tag_data, pos)[0]
        pos += 2
        end = tag_data.index(0, pos)
        name = tag_data[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
        result[char_id] = name
    return result


def parse_define_shape_bounds(tag_data: bytes) -> Tuple[int, dict]:
    """Parse DefineShape (any version) → (charId, bounds_in_pixels)."""
    char_id = struct.unpack_from('<H', tag_data, 0)[0]
    br = BitReader(tag_data, 2)
    rect = read_rect(br)
    bounds = {
        'xMin': rect['xMin'] / 20.0,
        'xMax': rect['xMax'] / 20.0,
        'yMin': rect['yMin'] / 20.0,
        'yMax': rect['yMax'] / 20.0,
    }
    return char_id, bounds


def _parse_image_dimensions(data: bytes) -> Tuple[int, int]:
    """Extract (width, height) from JPEG / PNG / GIF image data."""
    if len(data) < 4:
        return (0, 0)
    # PNG
    if data[:4] == b'\x89PNG':
        if len(data) >= 24:
            w = struct.unpack_from('>I', data, 16)[0]
            h = struct.unpack_from('>I', data, 20)[0]
            return (w, h)
        return (0, 0)
    # GIF
    if data[:3] == b'GIF':
        if len(data) >= 10:
            w = struct.unpack_from('<H', data, 6)[0]
            h = struct.unpack_from('<H', data, 8)[0]
            return (w, h)
        return (0, 0)
    # JPEG – scan for SOF marker
    i = 0
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker == 0xD8:       # SOI
            i += 2; continue
        if marker == 0xD9:       # EOI
            break
        if marker == 0x00 or (0xD0 <= marker <= 0xD7):
            i += 2; continue
        if i + 3 >= len(data):
            break
        seg_len = struct.unpack_from('>H', data, i + 2)[0]
        # SOF markers: C0-CF except C4 (DHT), C8, CC (DAC)
        if (0xC0 <= marker <= 0xCF) and marker not in (0xC4, 0xC8, 0xCC):
            if i + 9 <= len(data):
                h = struct.unpack_from('>H', data, i + 5)[0]
                w = struct.unpack_from('>H', data, i + 7)[0]
                return (w, h)
        i += 2 + seg_len
    return (0, 0)


def parse_define_bits_jpeg_info(tag_type: int, tag_data: bytes) -> Tuple[int, int, int]:
    """Parse DefineBitsJPEG2/3/4 → (charId, width, height)."""
    char_id = struct.unpack_from('<H', tag_data, 0)[0]
    if tag_type == 21:        # DefineBitsJPEG2
        img_data = tag_data[2:]
    elif tag_type == 35:      # DefineBitsJPEG3
        alpha_off = struct.unpack_from('<I', tag_data, 2)[0]
        img_data = tag_data[6:6 + alpha_off]
    elif tag_type == 90:      # DefineBitsJPEG4
        alpha_off = struct.unpack_from('<I', tag_data, 2)[0]
        img_data = tag_data[8:8 + alpha_off]
    else:                     # DefineBits (tag 6)
        img_data = tag_data[2:]
    w, h = _parse_image_dimensions(img_data)
    return char_id, w, h


def parse_define_bits_char_id(tag_data: bytes) -> int:
    """Get character ID from any DefineBits tag."""
    return struct.unpack_from('<H', tag_data, 0)[0]


def parse_define_bits_lossless_info(tag_data: bytes) -> Tuple[int, int, int]:
    """Parse DefineBitsLossless/2 → (charId, width, height)."""
    char_id = struct.unpack_from('<H', tag_data, 0)[0]
    fmt = tag_data[2]
    width = struct.unpack_from('<H', tag_data, 3)[0]
    height = struct.unpack_from('<H', tag_data, 5)[0]
    return char_id, width, height


def parse_define_sound_id(tag_data: bytes) -> int:
    """Get character ID from DefineSound."""
    return struct.unpack_from('<H', tag_data, 0)[0]


def parse_define_font3_name(tag_data: bytes) -> Tuple[int, str, bool, bool]:
    """Parse DefineFont3 (tag 75) → (charId, fontName, bold, italic).

    DefineFont3 layout (SWF spec §p.178):
      UI16  FontID
      UI8   Flags: HasLayout(7) ShiftJIS(6) SmallText(5) ANSI(4)
                   WideOffsets(3) WideCodes(2) Italic(1) Bold(0)
      UI8   LanguageCode
      UI8   FontNameLen
      UI8[FontNameLen] FontName (null-terminated inside len)
      ...
    """
    char_id = struct.unpack_from('<H', tag_data, 0)[0]
    flags = tag_data[2]
    italic = bool(flags & 0x02)
    bold = bool(flags & 0x01)
    # lang_code = tag_data[3]
    name_len = tag_data[4]
    if name_len > 0:
        raw_name = tag_data[5:5 + name_len]
        # Strip trailing null bytes
        font_name = raw_name.rstrip(b'\x00').decode('utf-8', errors='replace')
    else:
        font_name = f"Font_{char_id}"
    return char_id, font_name, bold, italic


def parse_define_font3_code_table(tag_data: bytes) -> Tuple[int, List[str]]:
    """Parse DefineFont3 (tag 75) → (charId, code_table).

    The code table maps glyph index → Unicode character. This is needed
    to convert DefineText glyph indices back to readable text.

    DefineFont3 layout after charId:
      UI8   Flags
      UI8   LanguageCode
      UI8   FontNameLen
      UI8[] FontName
      UI16  NumGlyphs
      UI16/UI32[] OffsetTable (NumGlyphs entries)
      UI16/UI32   CodeTableOffset
      SHAPE[]     GlyphShapeTable (skipped via offsets)
      UI16[]      CodeTable (NumGlyphs entries — Unicode code points)
    """
    char_id = struct.unpack_from('<H', tag_data, 0)[0]
    flags = tag_data[2]
    wide_offsets = bool(flags & 0x08)
    # lang_code = tag_data[3]
    name_len = tag_data[4]
    offset = 5 + name_len
    num_glyphs = struct.unpack_from('<H', tag_data, offset)[0]
    offset += 2

    if num_glyphs == 0:
        return char_id, []

    # Read code table offset to jump past glyph shapes
    ot_start = offset
    if wide_offsets:
        code_table_offset = struct.unpack_from('<I', tag_data,
                                               offset + num_glyphs * 4)[0]
    else:
        code_table_offset = struct.unpack_from('<H', tag_data,
                                               offset + num_glyphs * 2)[0]

    ct_start = ot_start + code_table_offset
    code_table = []
    for i in range(num_glyphs):
        cp = struct.unpack_from('<H', tag_data, ct_start + i * 2)[0]
        code_table.append(chr(cp))

    return char_id, code_table


def parse_define_text(tag_data: bytes, tag_type: int,
                      font_names: Dict[int, str],
                      font_attrs: Dict[int, Tuple[bool, bool]],
                      font_code_tables: Dict[int, List[str]]) -> dict:
    """Parse DefineText/DefineText2 (tag 11/33) binary data → text properties.

    Extracts glyph records, resolves them to Unicode via the font code table,
    and returns properties suitable for a Next2D `type: "text"` library entry.
    """
    br = BitReader(tag_data, 0)
    char_id = br.read_ui16()

    # Bounds RECT
    bounds_raw = read_rect(br)
    br.align()

    # Text matrix (usually identity for simple text)
    _matrix = read_matrix(br)
    br.align()

    glyph_bits = br.read_ui8()
    advance_bits = br.read_ui8()

    text_str = ''
    current_font_id = None
    current_height = 0
    current_color = 0

    # Track glyph advances to compute actual text width (in twips)
    total_advance = 0   # running x advance within current text record
    max_x = 0           # rightmost x position across all records
    current_x = 0       # x origin of current text record

    while True:
        flags = br.read_ui8()
        if flags == 0:
            break

        has_font = bool(flags & 0x08)
        has_color = bool(flags & 0x04)
        has_y_off = bool(flags & 0x02)
        has_x_off = bool(flags & 0x01)

        if has_font:
            current_font_id = br.read_ui16()
        if has_color:
            r = br.read_ui8()
            g = br.read_ui8()
            b = br.read_ui8()
            if tag_type == TAG_DEFINE_TEXT2:
                _a = br.read_ui8()
            current_color = (r << 16) | (g << 8) | b
        if has_y_off:
            _y_off = br.read_si16()
        if has_x_off:
            current_x = br.read_si16()
            total_advance = 0
        if has_font:
            current_height = br.read_ui16()

        glyph_count = br.read_ui8()
        for _ in range(glyph_count):
            glyph_idx = br.read_ub(glyph_bits)
            glyph_advance = br.read_sb(advance_bits)
            total_advance += glyph_advance
            ct = font_code_tables.get(current_font_id, [])
            if glyph_idx < len(ct):
                text_str += ct[glyph_idx]
            else:
                text_str += '?'
        br.align()

        # Track the rightmost point reached by this text record
        record_end = current_x + total_advance
        if record_end > max_x:
            max_x = record_end

    # Convert bounds from twips to pixels, then normalize to origin (0,0)
    # so the N2D tool renders the text field at the character origin.
    # The offset is stored separately so it can be baked into placement matrices.
    font_size = current_height / 20.0 if current_height else 12.0
    bx = bounds_raw['xMin'] / 20.0
    by = bounds_raw['yMin'] / 20.0
    bw = (bounds_raw['xMax'] - bounds_raw['xMin']) / 20.0
    bh = (bounds_raw['yMax'] - bounds_raw['yMin']) / 20.0

    # Compute advance-based width (sum of glyph advances in twips → pixels).
    # This represents how wide Flash actually rendered the text.
    advance_width_px = max_x / 20.0 if max_x > 0 else 0

    # DefineText bounds are tight glyph bounding boxes.  The N2D tool renders
    # with system fonts which are often wider/taller than the original embedded
    # Flash glyphs.  Compute generous bounds so text never overflows the field.
    #
    # Width: use the largest of SWF bounds, glyph advance total, or a rough
    # estimate from character count × font size – then add padding.
    char_estimate_w = len(text_str) * font_size * 0.65   # rough system-font width
    padding_w = font_size * 0.5 + 8   # horizontal breathing room
    effective_w = max(bw, advance_width_px, char_estimate_w) + padding_w

    # Height: use at least fontSize * 1.5 + 4 for line-height + descenders
    min_h = font_size * 1.5 + 4
    effective_h = max(bh, min_h)

    bounds = {
        'xMin': 0,
        'xMax': effective_w,
        'yMin': 0,
        'yMax': effective_h,
    }

    font_name = font_names.get(current_font_id, "sans-serif")
    is_bold = False
    is_italic = False
    if current_font_id in font_attrs:
        is_bold, is_italic = font_attrs[current_font_id]

    # Tool mapping: fontType 1=bold, 2=italic, 3=both
    font_type = 0
    if is_bold and is_italic:
        font_type = 3
    elif is_bold:
        font_type = 1
    elif is_italic:
        font_type = 2

    return {
        'text': text_str,
        'font': font_name,
        'fontType': font_type,
        'inputType': 'dynamic',  # static text → read-only dynamic
        'size': font_size,
        'align': 'left',
        'color': current_color,
        'leading': 0,
        'letterSpacing': 0,
        'leftMargin': 0,
        'rightMargin': 0,
        'multiline': False,
        'wordWrap': False,
        'border': False,
        'autoSize': 1,  # auto-size to fit text
        'scroll': True,
        'bounds': bounds,
        'originBounds': dict(bounds),
        'thickness': 0,
        'thicknessColor': 0,
        # Internal: bounds offset to bake into placement matrices
        '_boundsOffset': [bx, by],
    }


def extract_sound_buffer(raw_tag_body: bytes) -> Tuple[str, bytes, int]:
    """Extract playable sound data from a DefineSound raw tag body.

    The raw_tag_body starts AFTER the 2-byte character ID:
      UI8   Flags (SoundFormat:4 | SoundRate:2 | SoundSize:1 | SoundType:1)
      UI32  SoundSampleCount
      UI8[] SoundData

    For MP3 (format 2): SoundData starts with 2-byte SeekSamples, then MP3 frames.
    For raw PCM (format 0/3): SoundData is raw samples.
    For Nellymoser (format 5/6): SoundData is Nellymoser-encoded.

    Returns (format_name, playable_bytes, swf_rate_code) where:
      - playable_bytes is MP3/WAV/raw audio data
      - swf_rate_code is the SWF SoundRate (0=5.5kHz, 1=11kHz, 2=22kHz, 3=44kHz)
    """
    if len(raw_tag_body) < 5:
        return ('unknown', b'', 0)

    flags = raw_tag_body[0]
    sound_format = (flags >> 4) & 0xF
    sound_rate_code = (flags >> 2) & 0x3
    sound_size = (flags >> 1) & 0x1  # 0=8-bit, 1=16-bit
    sound_type = flags & 0x1          # 0=mono, 1=stereo

    sample_count = struct.unpack_from('<I', raw_tag_body, 1)[0]
    sound_data = raw_tag_body[5:]

    rate_map = {0: 5512, 1: 11025, 2: 22050, 3: 44100}
    sample_rate = rate_map.get(sound_rate_code, 44100)
    bits_per_sample = 16 if sound_size else 8
    num_channels = 2 if sound_type else 1

    if sound_format == 2:
        # MP3: skip 2-byte SeekSamples prefix, rest is MP3 frames
        if len(sound_data) > 2:
            return ('mp3', sound_data[2:], sound_rate_code)
        return ('mp3', b'', sound_rate_code)

    elif sound_format in (0, 3):
        # Uncompressed PCM (0=native endian, 3=little-endian)
        # Wrap in WAV header so the browser can decode it
        wav = _build_wav(sound_data, sample_rate, bits_per_sample, num_channels)
        return ('wav', wav, sound_rate_code)

    elif sound_format in (5, 6):
        # Nellymoser — not directly playable in browsers.
        # Format 5 = Nellymoser 8kHz mono, Format 6 = Nellymoser at flags rate.
        # Return the raw data; we'll try ffmpeg conversion in build_all.
        return ('nellymoser', sound_data, sound_rate_code)

    elif sound_format == 1:
        # ADPCM — not directly playable
        return ('adpcm', sound_data, sound_rate_code)

    return ('unknown', b'', sound_rate_code)


def _build_wav(pcm_data: bytes, sample_rate: int, bits_per_sample: int,
               num_channels: int) -> bytes:
    """Build a minimal WAV file from raw PCM data."""
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_data)
    file_size = 36 + data_size

    wav = io.BytesIO()
    wav.write(b'RIFF')
    wav.write(struct.pack('<I', file_size))
    wav.write(b'WAVE')
    wav.write(b'fmt ')
    wav.write(struct.pack('<I', 16))               # fmt chunk size
    wav.write(struct.pack('<H', 1))                # PCM format
    wav.write(struct.pack('<H', num_channels))
    wav.write(struct.pack('<I', sample_rate))
    wav.write(struct.pack('<I', byte_rate))
    wav.write(struct.pack('<H', block_align))
    wav.write(struct.pack('<H', bits_per_sample))
    wav.write(b'data')
    wav.write(struct.pack('<I', data_size))
    wav.write(pcm_data)
    return wav.getvalue()


def _build_nellymoser_flv(sound_data: bytes, swf_rate_code: int = 0) -> bytes:
    """Build a minimal FLV file containing Nellymoser audio.

    Uses the correct FLV audio format based on the SWF rate code:
    - rate_code 0 (5512 Hz): FLV SoundFormat 5 (Nellymoser 8kHz mono)
    - rate_code 1-3 (11025/22050/44100): FLV SoundFormat 6 (Nellymoser)

    All raw Nellymoser data is placed in a single FLV audio tag at ts=0
    and ffmpeg handles internal codec framing.
    """
    if not sound_data:
        return b''

    # Build FLV audio tag header byte
    # Bits 7-4: SoundFormat, Bits 3-2: SoundRate, Bit 1: SoundSize, Bit 0: SoundType
    if swf_rate_code == 0:
        # Nellymoser 8kHz mono — FLV format 5 (rate/size/type ignored)
        audio_hdr = (5 << 4) | (0 << 2) | (1 << 1) | 0  # 0x52
    else:
        # General Nellymoser — FLV format 6 with actual rate
        audio_hdr = (6 << 4) | (swf_rate_code << 2) | (1 << 1) | 0

    flv = io.BytesIO()

    # --- FLV header ---
    flv.write(b'FLV')
    flv.write(struct.pack('>B', 1))       # version
    flv.write(struct.pack('>B', 0x04))    # flags: has audio
    flv.write(struct.pack('>I', 9))       # header size
    flv.write(struct.pack('>I', 0))       # PreviousTagSize0

    # Single audio tag containing all sound data
    data_size = 1 + len(sound_data)  # audio header byte + payload

    # FLV tag header (11 bytes)
    flv.write(struct.pack('>B', 8))                          # TagType = audio
    flv.write(struct.pack('>I', data_size)[1:])              # DataSize (UI24)
    flv.write(b'\x00\x00\x00')                               # Timestamp (UI24) = 0
    flv.write(b'\x00')                                       # TimestampExtended = 0
    flv.write(b'\x00\x00\x00')                               # StreamID = 0

    # Audio tag body
    flv.write(struct.pack('>B', audio_hdr))
    flv.write(sound_data)

    # PreviousTagSize
    flv.write(struct.pack('>I', 11 + data_size))

    return flv.getvalue()


# Cache ffmpeg path on first call
_ffmpeg_path: str | None = None
_ffmpeg_checked = False


def _find_ffmpeg() -> str | None:
    """Return the path to ffmpeg, or None if not available."""
    global _ffmpeg_path, _ffmpeg_checked
    if _ffmpeg_checked:
        return _ffmpeg_path
    _ffmpeg_checked = True
    import shutil
    _ffmpeg_path = shutil.which('ffmpeg')
    return _ffmpeg_path


def convert_nellymoser_to_mp3(sound_data: bytes, swf_rate_code: int = 0) -> bytes:
    """Convert Nellymoser audio to MP3 via ffmpeg.

    Builds a temporary FLV file containing the Nellymoser audio at the
    correct sample rate, runs ffmpeg to transcode to MP3, and returns the
    MP3 bytes.  Returns empty bytes if ffmpeg is not available or fails.
    """
    ffmpeg = _find_ffmpeg()
    if ffmpeg is None:
        return b''

    flv_data = _build_nellymoser_flv(sound_data, swf_rate_code)
    if not flv_data:
        return b''

    try:
        with tempfile.NamedTemporaryFile(suffix='.flv', delete=False) as f_in:
            f_in.write(flv_data)
            in_path = f_in.name
        out_path = in_path.replace('.flv', '.mp3')

        result = subprocess.run(
            [ffmpeg, '-hide_banner', '-loglevel', 'error',
             '-i', in_path, '-y', '-f', 'mp3', out_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )

        if result.returncode == 0 and os.path.isfile(out_path):
            with open(out_path, 'rb') as f_out:
                return f_out.read()
        return b''
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return b''
    finally:
        for p in (in_path, out_path):
            try:
                os.remove(p)
            except OSError:
                pass


def parse_define_edit_text(tag_data: bytes, font_names: Dict[int, str],
                           font_attrs: Dict[int, Tuple[bool, bool]]) -> dict:
    """Parse DefineEditText (tag 37) binary data → dict of text properties.

    Returns a dict suitable for a Next2D `type: "text"` library entry with
    fields: text, font, fontType, inputType, size, align, color, leading,
    letterSpacing, leftMargin, rightMargin, multiline, wordWrap, border,
    autoSize, scroll, bounds, originBounds, thickness, thicknessColor.
    """
    br = BitReader(tag_data, 0)
    char_id = br.read_ui16()

    # Bounds RECT
    bounds_raw = read_rect(br)
    br.align()

    # Convert from twips to pixels
    bounds = {
        'xMin': bounds_raw['xMin'] / 20.0,
        'xMax': bounds_raw['xMax'] / 20.0,
        'yMin': bounds_raw['yMin'] / 20.0,
        'yMax': bounds_raw['yMax'] / 20.0,
    }

    # Flags byte 1
    f1 = br.read_ui8()
    has_text      = bool(f1 & 0x80)
    word_wrap     = bool(f1 & 0x40)
    multiline     = bool(f1 & 0x20)
    password      = bool(f1 & 0x10)
    read_only     = bool(f1 & 0x08)
    has_color     = bool(f1 & 0x04)
    has_max_len   = bool(f1 & 0x02)
    has_font      = bool(f1 & 0x01)

    # Flags byte 2
    f2 = br.read_ui8()
    has_font_class = bool(f2 & 0x80)
    auto_size      = bool(f2 & 0x40)
    has_layout     = bool(f2 & 0x20)
    no_select      = bool(f2 & 0x10)
    border         = bool(f2 & 0x08)
    was_static     = bool(f2 & 0x04)
    html           = bool(f2 & 0x02)
    use_outlines   = bool(f2 & 0x01)

    font_name = "sans-serif"
    font_size = 12.0
    is_bold = False
    is_italic = False

    if has_font:
        font_id = br.read_ui16()
        if has_font_class:
            # FontClass string — rare, skip
            font_name = br.read_string()
        else:
            font_name = font_names.get(font_id, f"Font_{font_id}")
            if font_id in font_attrs:
                is_bold, is_italic = font_attrs[font_id]
        font_size = br.read_ui16() / 20.0

    color = 0  # default black
    if has_color:
        r = br.read_ui8()
        g = br.read_ui8()
        b = br.read_ui8()
        a = br.read_ui8()
        color = (r << 16) | (g << 8) | b

    if has_max_len:
        _max_len = br.read_ui16()

    align = "left"
    left_margin = 0.0
    right_margin = 0.0
    indent = 0.0
    leading = 0.0

    if has_layout:
        align_val = br.read_ui8()
        align = {0: "left", 1: "right", 2: "center", 3: "justify"}.get(align_val, "left")
        left_margin = br.read_ui16() / 20.0
        right_margin = br.read_ui16() / 20.0
        indent_raw = br.read_si16()
        indent = indent_raw / 20.0
        leading_raw = br.read_si16()
        leading = leading_raw / 20.0

    # Variable name (null-terminated string)
    _var_name = br.read_string()

    text = ""
    if has_text:
        text = br.read_string()

    # Determine inputType
    if read_only:
        input_type = "dynamic"
    else:
        input_type = "input"

    # fontType: 0=normal, 1=bold, 2=italic, 3=bold+italic (matches tool)
    font_type = 0
    if is_bold and is_italic:
        font_type = 3
    elif is_bold:
        font_type = 1
    elif is_italic:
        font_type = 2

    return {
        'text': text,
        'font': font_name,
        'fontType': font_type,
        'inputType': input_type,
        'size': font_size,
        'align': align,
        'color': color,
        'leading': leading,
        'letterSpacing': 0,
        'leftMargin': left_margin,
        'rightMargin': right_margin,
        'multiline': multiline,
        'wordWrap': word_wrap,
        'border': border,
        'autoSize': 1 if auto_size else 0,
        'scroll': True,
        'bounds': bounds,
        'originBounds': dict(bounds),
        'thickness': 0,
        'thicknessColor': 0,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  TIMELINE ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class FrameAction:
    """An action on a frame: place, move, or remove."""
    pass

class PlaceAction(FrameAction):
    def __init__(self, depth, char_id, matrix, color_transform, name,
                 clip_depth, blend_mode, is_move, ratio=None):
        self.depth = depth
        self.char_id = char_id
        self.matrix = matrix
        self.color_transform = color_transform
        self.name = name
        self.clip_depth = clip_depth
        self.blend_mode = blend_mode
        self.is_move = is_move
        self.ratio = ratio

class RemoveAction(FrameAction):
    def __init__(self, depth):
        self.depth = depth

class SoundAction(FrameAction):
    """StartSound action: trigger a sound on this frame."""
    def __init__(self, sound_id: int, loop_count: int = 0, has_loops: bool = False):
        self.sound_id = sound_id       # SWF character ID of DefineSound
        self.loop_count = loop_count
        self.has_loops = has_loops


class TimelineFrame:
    """One frame of a timeline."""
    def __init__(self, frame_num: int):
        self.frame_num = frame_num
        self.actions: List[FrameAction] = []
        self.sounds: List[SoundAction] = []
        self.label: Optional[str] = None


def analyze_timeline(nested_tags: List[SWFTag], swf_version: int = 10) -> List[TimelineFrame]:
    """Analyze a sequence of tags (from DefineSprite or main timeline)
    and produce a list of TimelineFrame objects."""
    log.debug('analyze_timeline: %d nested tags, swf_version=%d', len(nested_tags), swf_version)
    frames = []
    current_frame = TimelineFrame(1)

    for tag in nested_tags:
        if tag.tag_type == TAG_SHOW_FRAME:
            frames.append(current_frame)
            current_frame = TimelineFrame(len(frames) + 1)

        elif tag.tag_type == TAG_FRAME_LABEL:
            current_frame.label = parse_frame_label(tag.data)

        elif tag.tag_type == TAG_PLACE_OBJECT2:
            po = parse_place_object2(tag.data, swf_version)
            action = PlaceAction(
                depth=po['depth'],
                char_id=po['charId'],
                matrix=po['matrix'],
                color_transform=po['colorTransform'],
                name=po['name'],
                clip_depth=po['clipDepth'],
                blend_mode=po['blendMode'],
                is_move=po['move'],
                ratio=po['ratio'],
            )
            current_frame.actions.append(action)

        elif tag.tag_type == TAG_PLACE_OBJECT3:
            po = parse_place_object3(tag.data)
            action = PlaceAction(
                depth=po['depth'],
                char_id=po['charId'],
                matrix=po['matrix'],
                color_transform=po['colorTransform'],
                name=po['name'],
                clip_depth=po['clipDepth'],
                blend_mode=po['blendMode'],
                is_move=po['move'],
                ratio=po['ratio'],
            )
            current_frame.actions.append(action)

        elif tag.tag_type == TAG_REMOVE_OBJECT2:
            depth = struct.unpack_from('<H', tag.data, 0)[0]
            current_frame.actions.append(RemoveAction(depth))

        elif tag.tag_type in (TAG_START_SOUND, TAG_START_SOUND2):
            sa = parse_start_sound(tag.tag_type, tag.data)
            if sa is not None:
                current_frame.sounds.append(sa)

    return frames


def parse_start_sound(tag_type: int, data: bytes) -> Optional[SoundAction]:
    """Parse StartSound (tag 15) or StartSound2 (tag 89) tag data."""
    try:
        off = 0
        sound_id = struct.unpack_from('<H', data, off)[0]
        off += 2
        if tag_type == TAG_START_SOUND2:
            # Skip SoundClassName (null-terminated string)
            while off < len(data) and data[off] != 0:
                off += 1
            off += 1  # skip null

        # Parse SOUNDINFO
        if off >= len(data):
            return SoundAction(sound_id)
        flags = data[off]
        off += 1
        sync_stop = bool(flags & 0x20)
        sync_no_multiple = bool(flags & 0x10)
        has_envelope = bool(flags & 0x08)
        has_loops = bool(flags & 0x04)
        has_out_point = bool(flags & 0x02)
        has_in_point = bool(flags & 0x01)

        if has_in_point:
            off += 4  # UI32 InPoint
        if has_out_point:
            off += 4  # UI32 OutPoint

        loop_count = 0
        if has_loops and off + 2 <= len(data):
            loop_count = struct.unpack_from('<H', data, off)[0]
            off += 2

        # Skip envelope records (we don't need them for the n2d format)
        return SoundAction(sound_id, loop_count=loop_count, has_loops=has_loops)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def bytes_to_binstr(data: bytes) -> str:
    """Convert raw bytes to latin-1 string (one char per byte) matching
    Next2D's String.fromCharCode() encoding."""
    return data.decode('latin-1')


def extract_frame_scripts_from_abc(global_raw_tags: list) -> Dict[str, Dict[int, str]]:
    """Extract frame scripts from DoABC/DoABC2 tags using as3_decompiler.

    Parses the ABC bytecode, decompiles every class, and looks for
    addFrameScript() calls to extract per-frame script bodies.

    Returns: {fully.qualified.ClassName: {1: "script_body", 2: "..."}}
    """
    log.debug('extract_frame_scripts_from_abc: %d raw tags', len(global_raw_tags))
    if not HAS_AS3_DECOMPILER:
        print("  [WARN] as3_decompiler not available — skipping frame script extraction")
        return {}

    result: Dict[str, Dict[int, str]] = {}

    # Extract ABC blocks from the raw tags
    abc_tags = [(ttype, data) for ttype, data in global_raw_tags if ttype in (72, 82)]
    if not abc_tags:
        return result

    for tag_type, tag_data in abc_tags:
        try:
            # DoABC2 (tag 82) has flags(UI32) + name(string) before ABC data
            if tag_type == 82:
                off = 4  # skip flags
                # skip null-terminated name string
                while off < len(tag_data) and tag_data[off] != 0:
                    off += 1
                off += 1  # skip null terminator
                abc_data = tag_data[off:]
            else:
                # DoABC (tag 72) is raw ABC data
                abc_data = tag_data

            abc = ABCFile(abc_data)
            decompiler = AS3Decompiler(abc)

            # Decompile each class and look for addFrameScript calls
            for cls_info in decompiler.list_classes():
                cls_idx = cls_info['index']
                try:
                    source = decompiler.decompile_class(cls_idx)
                except Exception:
                    continue

                class_name = cls_info.get('name', '')
                pkg = cls_info.get('package', '')
                if pkg:
                    full_name = f"{pkg}.{class_name}"
                else:
                    full_name = class_name

                # Look for addFrameScript(N, methodRef) patterns
                frame_methods = {}
                for m in re.finditer(r'addFrameScript\s*\(\s*(\d+)\s*,\s*(\w+)', source):
                    frame_0based = int(m.group(1))
                    method_name = m.group(2)
                    frame_1based = frame_0based + 1
                    frame_methods[frame_1based] = method_name

                if not frame_methods:
                    continue

                # Extract method bodies
                frame_scripts: Dict[int, str] = {}
                for frame_num, method_name in frame_methods.items():
                    pattern = (r'(?:internal\s+|public\s+|private\s+|protected\s+)?'
                               r'function\s+' + re.escape(method_name) +
                               r'\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{')
                    mmatch = re.search(pattern, source)
                    if mmatch:
                        start = mmatch.end()
                        depth = 1
                        pos = start
                        while pos < len(source) and depth > 0:
                            if source[pos] == '{':
                                depth += 1
                            elif source[pos] == '}':
                                depth -= 1
                            pos += 1
                        body = source[start:pos - 1].strip()
                        if body:
                            frame_scripts[frame_num] = body

                if frame_scripts:
                    result[full_name] = frame_scripts

        except Exception as e:
            print(f"  [WARN] Failed to parse ABC block: {e}")
            continue

    return result


def decompile_all_scripts(global_raw_tags: list) -> Tuple[List[Dict[str, str]], Dict[str, Dict[int, str]]]:
    """Decompile all AS3 classes from DoABC/DoABC2 tags.

    Single-pass: produces both script sources and frame-script mappings.
    Returns: (scripts_list, frame_scripts_dict)
      scripts_list:  [{name, path, source}, ...]
      frame_scripts: {fully.qualified.ClassName: {1: "body", ...}}
    """
    log.debug('decompile_all_scripts: entry with %d raw tags', len(global_raw_tags))
    if not HAS_AS3_DECOMPILER:
        log.warning('decompile_all_scripts: as3_decompiler not available')
        print("  [WARN] as3_decompiler not available — skipping AS3 decompilation")
        return [], {}

    scripts: List[Dict[str, str]] = []
    frame_scripts: Dict[str, Dict[int, str]] = {}
    abc_tags = [(ttype, data) for ttype, data in global_raw_tags if ttype in (72, 82)]
    if not abc_tags:
        return scripts, frame_scripts

    for tag_type, tag_data in abc_tags:
        try:
            if tag_type == 82:
                off = 4
                while off < len(tag_data) and tag_data[off] != 0:
                    off += 1
                off += 1
                abc_data = tag_data[off:]
            else:
                abc_data = tag_data

            abc = ABCFile(abc_data)
            decompiler = AS3Decompiler(abc)

            for cls_info in decompiler.list_classes():
                cls_idx = cls_info['index']
                try:
                    source = decompiler.decompile_class(cls_idx)
                except Exception:
                    continue

                class_name = cls_info.get('name', '')
                pkg = cls_info.get('package', '')
                if pkg:
                    path = pkg.replace('.', '/') + '/' + class_name + '.as'
                    full_name = f"{pkg}.{class_name}"
                else:
                    path = class_name + '.as'
                    full_name = class_name

                scripts.append({
                    'name': class_name + '.as',
                    'path': path,
                    'source': source,
                })

                # --- frame script extraction (was a separate 13s pass) ---
                frame_methods = {}
                for m in re.finditer(r'addFrameScript\s*\(\s*(\d+)\s*,\s*(\w+)', source):
                    frame_0based = int(m.group(1))
                    method_name = m.group(2)
                    frame_methods[frame_0based + 1] = method_name

                if frame_methods:
                    class_fs: Dict[int, str] = {}
                    for frame_num, method_name in frame_methods.items():
                        pattern = (r'(?:internal\s+|public\s+|private\s+|protected\s+)?'
                                   r'function\s+' + re.escape(method_name) +
                                   r'\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{')
                        mmatch = re.search(pattern, source)
                        if mmatch:
                            start = mmatch.end()
                            depth = 1
                            pos = start
                            while pos < len(source) and depth > 0:
                                if source[pos] == '{':
                                    depth += 1
                                elif source[pos] == '}':
                                    depth -= 1
                                pos += 1
                            body = source[start:pos - 1].strip()
                            if body:
                                class_fs[frame_num] = body
                    if class_fs:
                        frame_scripts[full_name] = class_fs

        except Exception as e:
            print(f"  [WARN] Failed to decompile ABC block: {e}")
            continue

    return scripts, frame_scripts


# ═══════════════════════════════════════════════════════════════════════════
#  BITMAP DECODING — SWF raw tag data → RGBA pixel buffer
# ═══════════════════════════════════════════════════════════════════════════

def decode_lossless_to_rgba(tag_type: int, body_after_char_id: bytes) -> Tuple[int, int, bytes]:
    """Decode DefineBitsLossless/2 raw body (after charId) → (width, height, rgba_bytes).

    Supports:
      - Tag 36 (DefineBitsLossless2): formats 3 (palette+alpha), 5 (32-bit ARGB)
      - Tag 20 (DefineBitsLossless):  formats 3 (palette), 4 (15-bit), 5 (24-bit)
    """
    log.debug('decode_lossless_to_rgba: tag_type=%d, body_len=%d', tag_type, len(body_after_char_id))
    if len(body_after_char_id) < 5:
        return 0, 0, b''

    fmt = body_after_char_id[0]
    width = struct.unpack_from('<H', body_after_char_id, 1)[0]
    height = struct.unpack_from('<H', body_after_char_id, 3)[0]

    if width == 0 or height == 0:
        return width, height, b''

    is_lossless2 = (tag_type == TAG_DEFINE_BITS_LOSSLESS2)

    if fmt == 3:
        # Palette format: ColorTableSize(1 byte) + compressed data
        if len(body_after_char_id) < 6:
            return width, height, b''
        color_table_size = body_after_char_id[5] + 1  # stored as size-1
        compressed = body_after_char_id[6:]
        try:
            decompressed = zlib.decompress(compressed)
        except zlib.error:
            return width, height, b''

        if is_lossless2:
            # DefineBitsLossless2: palette entries are RGBA (4 bytes each)
            palette_bytes = 4 * color_table_size
            palette = decompressed[:palette_bytes]
            pixel_data = decompressed[palette_bytes:]
            # Each row is padded to 4-byte boundary
            row_stride = (width + 3) & ~3
            if _HAS_NUMPY:
                pal = _np.frombuffer(palette, dtype=_np.uint8).reshape(-1, 4)
                n_full = min(height, len(pixel_data) // row_stride) if row_stride else 0
                rows = _np.frombuffer(pixel_data[:n_full * row_stride], dtype=_np.uint8).reshape(n_full, row_stride)
                indices = _np.clip(rows[:, :width], 0, len(pal) - 1)
                rgba_arr = _np.zeros((height, width, 4), dtype=_np.uint8)
                rgba_arr[:n_full] = pal[indices]
                return width, height, rgba_arr.tobytes()
            rgba = bytearray(width * height * 4)
            for y in range(height):
                row_off = y * row_stride
                for x in range(width):
                    if row_off + x >= len(pixel_data):
                        break
                    idx = pixel_data[row_off + x]
                    p_off = idx * 4
                    if p_off + 3 < len(palette):
                        out_off = (y * width + x) * 4
                        rgba[out_off]     = palette[p_off]     # R
                        rgba[out_off + 1] = palette[p_off + 1] # G
                        rgba[out_off + 2] = palette[p_off + 2] # B
                        rgba[out_off + 3] = palette[p_off + 3] # A
            return width, height, bytes(rgba)
        else:
            # DefineBitsLossless: palette entries are RGB (3 bytes each)
            palette_bytes = 3 * color_table_size
            palette = decompressed[:palette_bytes]
            pixel_data = decompressed[palette_bytes:]
            row_stride = (width + 3) & ~3
            if _HAS_NUMPY:
                pal_rgb = _np.frombuffer(palette, dtype=_np.uint8).reshape(-1, 3)
                pal = _np.empty((color_table_size, 4), dtype=_np.uint8)
                pal[:, :3] = pal_rgb
                pal[:, 3] = 255
                n_full = min(height, len(pixel_data) // row_stride) if row_stride else 0
                rows = _np.frombuffer(pixel_data[:n_full * row_stride], dtype=_np.uint8).reshape(n_full, row_stride)
                indices = _np.clip(rows[:, :width], 0, len(pal) - 1)
                rgba_arr = _np.zeros((height, width, 4), dtype=_np.uint8)
                rgba_arr[:n_full] = pal[indices]
                return width, height, rgba_arr.tobytes()
            rgba = bytearray(width * height * 4)
            for y in range(height):
                row_off = y * row_stride
                for x in range(width):
                    if row_off + x >= len(pixel_data):
                        break
                    idx = pixel_data[row_off + x]
                    p_off = idx * 3
                    if p_off + 2 < len(palette):
                        out_off = (y * width + x) * 4
                        rgba[out_off]     = palette[p_off]     # R
                        rgba[out_off + 1] = palette[p_off + 1] # G
                        rgba[out_off + 2] = palette[p_off + 2] # B
                        rgba[out_off + 3] = 255                 # A
            return width, height, bytes(rgba)

    elif fmt == 5:
        # 32-bit ARGB (Lossless2) or 24-bit xRGB (Lossless)
        compressed = body_after_char_id[5:]
        try:
            decompressed = zlib.decompress(compressed)
        except zlib.error:
            return width, height, b''

        pixel_count = width * height
        needed = pixel_count * 4

        if is_lossless2:
            # DefineBitsLossless2 format 5: premultiplied ARGB
            # Fast path: use bytearray slice operations (C-level) for reorder
            if len(decompressed) < needed:
                decompressed = decompressed + b'\x00' * (needed - len(decompressed))
            src = decompressed[:needed]
            rgba = bytearray(needed)
            # ARGB → RGBA reorder via slice assignment (runs in C)
            rgba[0::4] = src[1::4]  # R
            rgba[1::4] = src[2::4]  # G
            rgba[2::4] = src[3::4]  # B
            rgba[3::4] = src[0::4]  # A
            # Un-premultiply only pixels with partial alpha (0 < a < 255)
            # Most game bitmaps are fully opaque so this loop is rarely entered
            alpha_channel = src[0::4]
            if any(0 < a < 255 for a in alpha_channel):
                for i in range(pixel_count):
                    a = rgba[i * 4 + 3]
                    if 0 < a < 255:
                        off = i * 4
                        rgba[off]     = min(255, (rgba[off]     * 255 + a // 2) // a)
                        rgba[off + 1] = min(255, (rgba[off + 1] * 255 + a // 2) // a)
                        rgba[off + 2] = min(255, (rgba[off + 2] * 255 + a // 2) // a)
        else:
            # DefineBitsLossless format 5: 0xRGB (24-bit, x is padding)
            # Fast path: slice assignment
            if len(decompressed) < needed:
                decompressed = decompressed + b'\x00' * (needed - len(decompressed))
            src = decompressed[:needed]
            rgba = bytearray(needed)
            rgba[0::4] = src[1::4]  # R (skip padding byte at offset 0)
            rgba[1::4] = src[2::4]  # G
            rgba[2::4] = src[3::4]  # B
            rgba[3::4] = b'\xff' * pixel_count  # A = 255

        return width, height, bytes(rgba)

    elif fmt == 4:
        # 15-bit RGB (DefineBitsLossless only, rare)
        compressed = body_after_char_id[5:]
        try:
            decompressed = zlib.decompress(compressed)
        except zlib.error:
            return width, height, b''

        # Each row padded to 4-byte boundary, 2 bytes/pixel
        row_stride = ((width * 2) + 3) & ~3
        rgba = bytearray(width * height * 4)
        for y in range(height):
            for x in range(width):
                src_off = y * row_stride + x * 2
                if src_off + 1 >= len(decompressed):
                    break
                val = struct.unpack_from('>H', decompressed, src_off)[0]
                # piiiiigggggbbbbb (1-5-5-5)
                r = ((val >> 10) & 0x1F) * 255 // 31
                g = ((val >> 5) & 0x1F) * 255 // 31
                b = (val & 0x1F) * 255 // 31
                out_off = (y * width + x) * 4
                rgba[out_off]     = r
                rgba[out_off + 1] = g
                rgba[out_off + 2] = b
                rgba[out_off + 3] = 255

        return width, height, bytes(rgba)

    return width, height, b''


def decode_jpeg_to_rgba(tag_type: int, full_tag_data: bytes) -> Tuple[int, int, bytes]:
    """Decode DefineBitsJPEG2/3/4 full tag data → (width, height, rgba_bytes).

    Uses PIL/Pillow for JPEG decoding.
    Falls back to empty buffer if PIL is not available.
    """
    log.debug('decode_jpeg_to_rgba: tag_type=%d, data_len=%d', tag_type, len(full_tag_data))
    if len(full_tag_data) < 4:
        return 0, 0, b''

    char_id = struct.unpack_from('<H', full_tag_data, 0)[0]

    if tag_type == TAG_DEFINE_BITS_JPEG2:  # tag 21
        img_data = full_tag_data[2:]
        alpha_data = None
    elif tag_type == TAG_DEFINE_BITS_JPEG3:  # tag 35
        alpha_off = struct.unpack_from('<I', full_tag_data, 2)[0]
        img_data = full_tag_data[6:6 + alpha_off]
        alpha_compressed = full_tag_data[6 + alpha_off:]
        try:
            alpha_data = zlib.decompress(alpha_compressed) if alpha_compressed else None
        except zlib.error:
            alpha_data = None
    elif tag_type == TAG_DEFINE_BITS_JPEG4:  # tag 90
        alpha_off = struct.unpack_from('<I', full_tag_data, 2)[0]
        # deblock = struct.unpack_from('<H', full_tag_data, 6)[0]  # not needed
        img_data = full_tag_data[8:8 + alpha_off]
        alpha_compressed = full_tag_data[8 + alpha_off:]
        try:
            alpha_data = zlib.decompress(alpha_compressed) if alpha_compressed else None
        except zlib.error:
            alpha_data = None
    elif tag_type == TAG_DEFINE_BITS:  # tag 6
        img_data = full_tag_data[2:]
        alpha_data = None
    else:
        return 0, 0, b''

    # Strip erroneous JPEG data: SWF sometimes prefixes with FF D9 FF D8
    if len(img_data) >= 4 and img_data[:4] == b'\xff\xd9\xff\xd8':
        img_data = img_data[4:]

    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_data))
        img = img.convert('RGBA')
        w, h = img.size
        rgba = bytearray(img.tobytes())

        # Apply alpha channel from JPEG3/4
        if alpha_data and len(alpha_data) >= w * h:
            for i in range(w * h):
                rgba[i * 4 + 3] = alpha_data[i]

        return w, h, bytes(rgba)
    except ImportError:
        # PIL not available — extract dimensions only
        w, h = _parse_image_dimensions(img_data)
        return w, h, b''
    except Exception as e:
        w, h = _parse_image_dimensions(img_data)
        return w, h, b''


# ═══════════════════════════════════════════════════════════════════════════
#  NEXT2D RECODE COMMAND CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# Next2D recode command codes (used for gray rectangle placeholder shapes)
CMD_MOVE_TO         = 0
CMD_CURVE_TO        = 1
CMD_LINE_TO         = 2
CMD_CUBIC           = 3
CMD_FILL_STYLE      = 5
CMD_END_FILL        = 7
CMD_STROKE_STYLE    = 6
CMD_END_STROKE      = 8
CMD_BEGIN_PATH      = 9
CMD_CLOSE_PATH      = 12


# ═══════════════════════════════════════════════════════════════════════════
#  N2D BUILDER
# ═══════════════════════════════════════════════════════════════════════════

# SWF blend mode values → Next2D blend mode names
BLEND_MODE_MAP = {
    0: "normal", 1: "normal", 2: "layer", 3: "multiply",
    4: "screen", 5: "lighten", 6: "darken", 7: "difference",
    8: "add", 9: "subtract", 10: "invert", 11: "alpha",
    12: "erase", 13: "overlay", 14: "hardlight",
}

# Layer colors — cycle through for visual distinction
LAYER_COLORS = [
    "#0000ff", "#ff0000", "#00ff00", "#ff00ff",
    "#00ffff", "#ffff00", "#ff8800", "#8800ff",
]


class N2DBuilder:
    """Build a complete .n2d JSON from parsed SWF data and JPEXS assets."""

    def __init__(self, header: dict, name: str = "imported"):
        log.debug('N2DBuilder.__init__: name=%s, header=%s', name, header)
        self.header = header
        self.name = name
        self.libraries: List[dict] = []
        self.next_lib_id = 0
        self.next_char_id = 1

        # Mapping: SWF character ID → n2d library ID
        self.swf_to_n2d: Dict[int, int] = {}
        # SWF character ID → tag type name
        self.char_types: Dict[int, str] = {}
        # Symbol names from SymbolClass or CSV
        self.symbol_names: Dict[int, str] = {}
        # Shape bounds from SWF
        self.shape_bounds: Dict[int, dict] = {}
        # Bitmap dimensions from SWF
        self.bitmap_dims: Dict[int, Tuple[int, int]] = {}
        # DefineSprite data: swf_char_id → (frame_count, [nested_tags])
        self.sprite_data: Dict[int, Tuple[int, List[SWFTag]]] = {}
        # Raw SWF tag data for passthrough: swf_char_id → (tag_type, body_bytes_after_char_id)
        self.raw_tag_data: Dict[int, Tuple[int, bytes]] = {}
        # Font name mapping: swf_char_id → font name string
        self.font_names: Dict[int, str] = {}
        # Font attributes: swf_char_id → (bold, italic)
        self.font_attrs: Dict[int, Tuple[bool, bool]] = {}
        # Font code tables: swf_char_id → [Unicode chars] (glyph index → character)
        self.font_code_tables: Dict[int, List[str]] = {}
        # Text bounds offsets: n2d_lib_id → (dx, dy) for DefineText normalization
        self.text_bounds_offsets: Dict[int, Tuple[float, float]] = {}
        # Global raw tags (DoABC, fonts, auxiliary) for 1:1 roundtrip
        # List of (tag_type, full_tag_body_bytes)
        self.global_raw_tags: List[Tuple[int, bytes]] = []
        # AS3 source scripts: [{name, path, source}]
        self.scripts: List[dict] = []
        # Bitmap RGBA buffers: n2d_lib_id → raw RGBA bytes (for ZIP packaging)
        self.bitmap_buffers: Dict[int, bytes] = {}

    def _alloc_id(self) -> int:
        """Allocate a new library ID."""
        lid = self.next_lib_id
        self.next_lib_id += 1
        return lid

    def catalog_swf_tags(self, tags: List[SWFTag]):
        """First pass: catalog all definition tags (types, IDs, dimensions)."""
        log.info('catalog_swf_tags: processing %d tags', len(tags))
        DEF_TYPES = {
            TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2,
            TAG_DEFINE_BITS, TAG_DEFINE_BITS_JPEG2, TAG_DEFINE_BITS_JPEG3,
            TAG_DEFINE_BITS_JPEG4, TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2,
            TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4, TAG_DEFINE_SPRITE,
            TAG_DEFINE_SOUND, TAG_DEFINE_TEXT, TAG_DEFINE_TEXT2,
            TAG_DEFINE_EDIT_TEXT, TAG_DEFINE_MORPH_SHAPE, TAG_DEFINE_MORPH_SHAPE2,
            TAG_DEFINE_FONT3,
        }
        past_symbol_class = False
        self.root_timeline_def_ids: List[int] = []  # charIds defined inside root timeline
        for tag in tags:
            if tag.tag_type in (TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2):
                char_id, w, h = parse_define_bits_lossless_info(tag.data)
                self.char_types[char_id] = 'bitmap'
                self.bitmap_dims[char_id] = (w, h)
                # Store raw tag body for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type in (TAG_DEFINE_BITS, TAG_DEFINE_BITS_JPEG2,
                                  TAG_DEFINE_BITS_JPEG3, TAG_DEFINE_BITS_JPEG4):
                char_id, w, h = parse_define_bits_jpeg_info(tag.tag_type, tag.data)
                self.char_types[char_id] = 'bitmap'
                if w > 0 and h > 0:
                    self.bitmap_dims[char_id] = (w, h)
                # Store raw tag body for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type in (TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2,
                                  TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4):
                char_id, bounds = parse_define_shape_bounds(tag.data)
                self.char_types[char_id] = 'shape'
                self.shape_bounds[char_id] = bounds
                # Store raw tag body for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type == TAG_DEFINE_SPRITE:
                char_id, fc, nested = parse_define_sprite(tag)
                self.char_types[char_id] = 'container'
                self.sprite_data[char_id] = (fc, nested)
                # Store raw tag body (minus 2-byte char ID) for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])
                # Recurse — catalog definitions inside the sprite too
                # (SWF allows nested definitions, though rarely used)

            elif tag.tag_type == TAG_DEFINE_SOUND:
                char_id = parse_define_sound_id(tag.data)
                self.char_types[char_id] = 'sound'
                # Store raw tag body (minus 2-byte char ID) for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type in (TAG_DEFINE_TEXT, TAG_DEFINE_TEXT2,
                                  TAG_DEFINE_EDIT_TEXT):
                char_id = struct.unpack_from('<H', tag.data, 0)[0]
                self.char_types[char_id] = 'text'
                # Store raw tag body for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type in (TAG_DEFINE_MORPH_SHAPE, TAG_DEFINE_MORPH_SHAPE2):
                char_id = struct.unpack_from('<H', tag.data, 0)[0]
                self.char_types[char_id] = 'morphShape'
                # Store raw tag body for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type == TAG_DEFINE_FONT3:
                char_id = struct.unpack_from('<H', tag.data, 0)[0]
                self.char_types[char_id] = 'font'
                # Store raw tag body for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])
                # Parse font name and attributes for text entry resolution
                try:
                    _, fname, fbold, fitalic = parse_define_font3_name(tag.data)
                    self.font_names[char_id] = fname
                    self.font_attrs[char_id] = (fbold, fitalic)
                except Exception:
                    pass  # font name extraction is best-effort
                # Parse code table for DefineText glyph→Unicode resolution
                try:
                    _, code_table = parse_define_font3_code_table(tag.data)
                    if code_table:
                        self.font_code_tables[char_id] = code_table
                except Exception:
                    pass  # code table extraction is best-effort

            elif tag.tag_type == TAG_SYMBOL_CLASS:
                sc = parse_symbol_class(tag.data)
                self.symbol_names.update(sc)
                past_symbol_class = True

            # Track definition tags that appear after SymbolClass
            # (i.e., inline definitions in the root timeline section).
            if past_symbol_class and tag.tag_type in DEF_TYPES and len(tag.data) >= 2:
                cid = struct.unpack_from('<H', tag.data, 0)[0]
                self.root_timeline_def_ids.append(cid)

            # Store DoABC and auxiliary tags for 1:1 roundtrip passthrough
            if tag.tag_type in (TAG_DO_ABC, TAG_DO_ABC2,
                                73,   # DefineFontAlignZones
                                74,   # CSMTextSettings
                                88,   # DefineFontName
                                24,   # Protect
                                45,   # SoundStreamHead2
                                86,   # DefineSceneAndFrameLabelData
                                76):  # SymbolClass
                self.global_raw_tags.append((tag.tag_type, bytes(tag.data)))

    def build_all(self, *, fast_shapes: bool = False):
        """Build all library entries from cataloged SWF data.
        
        fast_shapes: if True, skip shape binary parsing (use gray rect placeholders).
                     SWF export still works 1:1 via rawTagBody passthrough.
        """
        log.info('build_all: building library entries (fast_shapes=%s)', fast_shapes)
        t0 = time.time()
        step = lambda msg: print(f"  [{time.time()-t0:6.1f}s] {msg}", flush=True)

        # frame_scripts should be pre-populated before calling build_all()
        if self.frame_scripts:
            total_scripts = sum(len(v) for v in self.frame_scripts.values())
            step(f"Using {len(self.frame_scripts)} pre-extracted frame script classes "
                 f"({total_scripts} total scripts)")
        else:
            step("No frame scripts available")

        # Allocate n2d library IDs for all SWF characters
        # Library id 0 is always reserved for the main timeline
        self.swf_to_n2d[0] = 0  # main timeline / root class
        self.next_lib_id = 1

        # Sort character IDs for deterministic output
        all_char_ids = sorted(self.char_types.keys())

        for cid in all_char_ids:
            lid = self._alloc_id()
            self.swf_to_n2d[cid] = lid

        step(f"Allocated {len(self.swf_to_n2d)} library IDs")

        # Create library folders to organize assets by type
        self.folder_ids: Dict[str, int] = {}
        folder_defs = [
            ('Bitmaps',     'bitmap'),
            ('Shapes',      'shape'),
            ('MorphShapes', 'morphShape'),
            ('Sounds',      'sound'),
            ('Texts',       'text'),
            ('Fonts',       'font'),
            ('MovieClips',  'container'),
        ]
        for fname, ctype in folder_defs:
            # Only create folder if there are assets of this type
            if any(self.char_types.get(cid) == ctype for cid in all_char_ids):
                fid = self._alloc_id()
                self.folder_ids[ctype] = fid
                self.libraries.append({
                    'id': fid,
                    'name': fname,
                    'type': 'folder',
                    'symbol': '',
                    'folderId': 0,
                    'mode': 'close',
                })
        step(f"Created {len(self.folder_ids)} library folders")

        # Phase 1: Build bitmap library entries with decoded RGBA buffers.
        # Buffer is stored as base64 with "b64:" prefix — ~3-4x smaller than
        # latin-1 after json.dumps(ensure_ascii=True) + quote() encoding.
        # The JS Bitmap setter detects the prefix and decodes via atob().
        bitmap_count = 0
        decode_ok = 0

        for cid in all_char_ids:
            if self.char_types[cid] != 'bitmap':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Bitmap_{cid}"

            width, height = self.bitmap_dims.get(cid, (0, 0))

            # Decode RGBA from raw SWF tag data (once — cached in buffer_str)
            buffer_str = ''
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                rgba = b''
                if tag_type in (TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2):
                    dw, dh, rgba = decode_lossless_to_rgba(tag_type, body)
                    if dw and dh:
                        width, height = dw, dh
                elif tag_type in (TAG_DEFINE_BITS, TAG_DEFINE_BITS_JPEG2,
                                  TAG_DEFINE_BITS_JPEG3, TAG_DEFINE_BITS_JPEG4):
                    dw, dh, rgba = decode_jpeg_to_rgba(tag_type, b'\x00\x00' + body)
                    if dw and dh:
                        width, height = dw, dh
                if rgba:
                    # Store as "b64:<base64>" — JS setter handles the prefix
                    buffer_str = 'b64:' + base64.b64encode(rgba).decode('ascii')
                    decode_ok += 1

            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'bitmap',
                'symbol': sym_name,
                'folderId': self.folder_ids.get('bitmap', 0),
                'width': width,
                'height': height,
                'imageType': 'image/png',
                'buffer': buffer_str,
            }
            # Include raw SWF tag body as base64 for 1:1 roundtrip
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                entry['rawTagType'] = tag_type
                entry['rawTagBody'] = base64.b64encode(body).decode('ascii')
            self.libraries.append(entry)
            bitmap_count += 1

        step(f"Built {bitmap_count} bitmap entries ({decode_ok} decoded)")

        # Build bitmap ID mapping for shape parser (SWF bitmap charId → N2D lib id)
        bitmap_id_map: Dict[int, int] = {}
        for cid in all_char_ids:
            if self.char_types.get(cid) == 'bitmap':
                bitmap_id_map[cid] = self.swf_to_n2d.get(cid, 0)

        # Phase 2: Build shape library entries
        shape_count = 0
        shape_parsed = 0
        for cid in all_char_ids:
            if self.char_types[cid] != 'shape':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Shape_{cid}"
            bounds = self.shape_bounds.get(cid, {'xMin': 0, 'xMax': 100, 'yMin': 0, 'yMax': 100})

            recodes = []
            has_bitmap_fill = False

            # Strategy 1: Parse raw SWF DefineShape binary → recodes  (best quality)
            if not fast_shapes and cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                if tag_type in (TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2,
                                TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4):
                    try:
                        recodes, parsed_bounds, has_bitmap_fill = \
                            parse_define_shape_to_recodes(tag_type, bytes(body), bitmap_id_map)
                        # Strip trailing boolean (has_bitmap flag) — the tool's
                        # SWF importer pops it, but JSON loading reads inBitmap
                        # from the entry directly. Leaving it corrupts commands.
                        if recodes and isinstance(recodes[-1], bool):
                            recodes.pop()
                        # Check if recodes has actual draw commands
                        has_draw_cmds = len(recodes) > 0 and any(
                            not isinstance(v, bool) and isinstance(v, (int, float))
                            for v in recodes[:5]
                        )
                        if not has_draw_cmds:
                            recodes = []
                        elif parsed_bounds and parsed_bounds.get('xMin', 0) != float('inf'):
                            bounds = parsed_bounds
                        if recodes:
                            shape_parsed += 1
                    except Exception as e:
                        print(f"  [WARN] Shape {cid}: binary parse failed ({e})")
                        recodes = []

            # Strategy 2: Gray rectangle placeholder
            if not recodes:
                x0 = bounds.get('xMin', 0)
                y0 = bounds.get('yMin', 0)
                x1 = bounds.get('xMax', 100)
                y1 = bounds.get('yMax', 100)
                recodes = [
                    CMD_BEGIN_PATH,
                    CMD_MOVE_TO, x0, y0,
                    CMD_LINE_TO, x1, y0,
                    CMD_LINE_TO, x1, y1,
                    CMD_LINE_TO, x0, y1,
                    CMD_LINE_TO, x0, y0,
                    CMD_FILL_STYLE, 200, 200, 200, 128,
                    CMD_END_FILL,
                ]

            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'shape',
                'symbol': sym_name,
                'folderId': self.folder_ids.get('shape', 0),
                'bitmapId': 0,
                'grid': None,
                'inBitmap': has_bitmap_fill,
                'recodes': recodes,
                'bounds': bounds,
            }
            # Include raw SWF tag body as base64 for 1:1 roundtrip
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                entry['rawTagType'] = tag_type
                entry['rawTagBody'] = base64.b64encode(body).decode('ascii')
            self.libraries.append(entry)
            shape_count += 1

        step(f"Built {shape_count} shape entries ({shape_parsed} parsed from SWF binary)")

        # Phase 2b: SKIPPED — Bitmap RGBA decode is skipped for speed.
        # Shape recodes keep integer bitmap IDs (tool shows blank fills).
        # rawTagBody passthrough ensures SWF export still works perfectly.
        step("Bitmap embed in shape recodes skipped (speed optimization)")

        # Phase 3: Build morph shape entries — parse start-state into visual recodes
        morph_count = 0
        morph_parsed = 0
        for cid in all_char_ids:
            if self.char_types[cid] != 'morphShape':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"MorphShape_{cid}"

            # Parse start-state and end-state shapes from DefineMorphShape binary
            recodes = []
            end_recodes = []
            bounds = {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20}
            end_bounds = {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20}
            has_bitmap_fill = False
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                try:
                    recodes, bounds, end_recodes, end_bounds, has_bitmap_fill = \
                        parse_define_morph_shape_to_recodes(
                            tag_type, body, self.swf_to_n2d)
                    if recodes:
                        morph_parsed += 1
                except Exception as e:
                    print(f"    Warning: Could not parse MorphShape {cid}: {e}")

            # Strip trailing boolean (tool pops it in SWF path but not N2D path)
            if recodes and isinstance(recodes[-1], bool):
                recodes.pop()
            if end_recodes and isinstance(end_recodes[-1], bool):
                end_recodes.pop()

            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'shape',
                'isMorphShape': True,
                'symbol': sym_name,
                'folderId': self.folder_ids.get('morphShape', 0),
                'bitmapId': 0,
                'grid': None,
                'inBitmap': has_bitmap_fill,
                'recodes': recodes,
                'bounds': bounds,
                'endRecodes': end_recodes,
                'endBounds': end_bounds,
            }
            # Include raw SWF tag body as base64 for 1:1 roundtrip
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                entry['rawTagType'] = tag_type
                entry['rawTagBody'] = base64.b64encode(body).decode('ascii')
            self.libraries.append(entry)
            morph_count += 1

        step(f"Built {morph_count} morph shape entries ({morph_parsed} parsed start-state)")

        # Phase 4: Build sound entries with raw tag data for 1:1 roundtrip
        # Pre-pass: identify Nellymoser sounds and convert in parallel via ffmpeg
        sound_count = 0
        sound_formats = {}
        nelly_converted = 0
        nelly_total = 0

        # Collect Nellymoser conversion jobs for parallel execution
        sound_data_cache = {}  # cid → (fmt_name, audio_bytes, swf_rate)
        nelly_jobs = []  # (cid, audio_bytes, swf_rate)
        for cid in all_char_ids:
            if self.char_types[cid] != 'sound':
                continue
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                fmt_name, audio_bytes, swf_rate = extract_sound_buffer(body)
                sound_data_cache[cid] = (fmt_name, audio_bytes, swf_rate)
                sound_formats[fmt_name] = sound_formats.get(fmt_name, 0) + 1
                if fmt_name == 'nellymoser' and audio_bytes:
                    nelly_total += 1
                    nelly_jobs.append((cid, audio_bytes, swf_rate))

        # Run all Nellymoser→MP3 conversions in parallel (ffmpeg subprocess I/O)
        nelly_results = {}  # cid → mp3_bytes
        if nelly_jobs and _find_ffmpeg():
            max_workers = min(8, len(nelly_jobs))
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {
                    pool.submit(convert_nellymoser_to_mp3, audio, rate): cid
                    for cid, audio, rate in nelly_jobs
                }
                for future in futures:
                    cid = futures[future]
                    try:
                        mp3 = future.result()
                        if mp3:
                            nelly_results[cid] = mp3
                            nelly_converted += 1
                    except Exception:
                        pass

        for cid in all_char_ids:
            if self.char_types[cid] != 'sound':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Sound_{cid}"

            buffer_str = ''
            if cid in sound_data_cache:
                fmt_name, audio_bytes, swf_rate = sound_data_cache[cid]
                # Use parallel-converted MP3 if available
                if cid in nelly_results:
                    audio_bytes = nelly_results[cid]
                if audio_bytes:
                    buffer_str = base64.b64encode(audio_bytes if isinstance(audio_bytes, (bytes, bytearray)) else bytes(audio_bytes)).decode('ascii')

            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'sound',
                'symbol': sym_name,
                'folderId': self.folder_ids.get('sound', 0),
                'buffer': buffer_str,
                'volume': 100,
                'loopCount': 0,
            }
            # Include raw SWF tag body as base64 for 1:1 roundtrip
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                entry['rawTagType'] = tag_type
                entry['rawTagBody'] = base64.b64encode(body).decode('ascii')
            self.libraries.append(entry)
            sound_count += 1

        fmt_summary = ', '.join(f"{v} {k}" for k, v in sorted(sound_formats.items()))
        nelly_msg = ''
        if nelly_total > 0:
            if nelly_converted == nelly_total:
                nelly_msg = f'; all {nelly_converted} Nellymoser converted to MP3'
            elif nelly_converted > 0:
                nelly_msg = (f'; {nelly_converted}/{nelly_total} Nellymoser '
                             f'converted to MP3')
            else:
                nelly_msg = (f'; {nelly_total} Nellymoser sounds NOT playable '
                             f'(install ffmpeg to convert)')
        step(f"Built {sound_count} sound entries ({fmt_summary}{nelly_msg})")

        # Phase 5: Build text entries — parse into editable text fields
        text_count = 0
        text_parsed = 0
        for cid in all_char_ids:
            if self.char_types[cid] != 'text':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Text_{cid}"

            # Try to parse text tag binary for editable text fields
            parsed_props = None
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                full_data = struct.pack('<H', cid) + body

                if tag_type == TAG_DEFINE_EDIT_TEXT:
                    try:
                        parsed_props = parse_define_edit_text(
                            full_data, self.font_names, self.font_attrs
                        )
                        text_parsed += 1
                    except Exception as e:
                        print(f"    Warning: Could not parse DefineEditText {cid}: {e}")

                elif tag_type in (TAG_DEFINE_TEXT, TAG_DEFINE_TEXT2):
                    try:
                        parsed_props = parse_define_text(
                            full_data, tag_type,
                            self.font_names, self.font_attrs,
                            self.font_code_tables
                        )
                        text_parsed += 1
                    except Exception as e:
                        print(f"    Warning: Could not parse DefineText {cid}: {e}")

            if parsed_props is not None:
                # Store text bounds offset for placement matrix adjustment
                if '_boundsOffset' in parsed_props:
                    offset = parsed_props.pop('_boundsOffset')
                    self.text_bounds_offsets[lid] = tuple(offset)

                # Create a proper type:"text" entry the tool can edit
                entry = {
                    'id': lid,
                    'swfCharId': cid,
                    'name': display_name,
                    'type': 'text',
                    'symbol': sym_name,
                    'folderId': self.folder_ids.get('text', 0),
                }
                entry.update(parsed_props)
                # Include raw tag body as base64 for roundtrip
                if cid in self.raw_tag_data:
                    tag_type, body = self.raw_tag_data[cid]
                    entry['rawTagType'] = tag_type
                    entry['rawTagBody'] = base64.b64encode(body).decode('ascii')
            else:
                # Fallback: store as shape placeholder
                entry = {
                    'id': lid,
                    'swfCharId': cid,
                    'name': display_name,
                    'type': 'shape',
                    'symbol': sym_name,
                    'folderId': self.folder_ids.get('text', 0),
                    'bitmapId': 0,
                    'grid': None,
                    'inBitmap': False,
                    'recodes': [],
                    'bounds': {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20},
                }
                if cid in self.raw_tag_data:
                    tag_type, body = self.raw_tag_data[cid]
                    entry['rawTagType'] = tag_type
                    entry['rawTagBody'] = base64.b64encode(body).decode('ascii')

            self.libraries.append(entry)
            text_count += 1

        step(f"Built {text_count} text entries ({text_parsed} parsed as editable)")

        # Phase 6: Build font entries — store as shapes for tool compatibility
        # The Next2D tool has no "font" library type; fonts are transient SWF
        # import data.  We store them as shapes with raw tag passthrough so
        # compile_n2d.py can reconstruct the DefineFont3 tags.  Font raw data
        # is also preserved in rawGlobalTags for auxiliary tag ordering.
        #
        # We also store fontData (the raw tag body as a latin-1 string) and
        # fontAuxTags (auxiliary tags like DefineFontAlignZones, CSMTextSettings,
        # DefineFontName) directly on the font entry so the sidecar is not needed.
        font_count = 0
        # Pre-collect font aux tags keyed by char ID for attachment below
        _font_aux_by_cid: Dict[int, List[Tuple[int, bytes]]] = {}
        for tt, body in self.global_raw_tags:
            if tt in (73, 74, 88) and len(body) >= 2:
                ref_cid = struct.unpack_from('<H', body, 0)[0]
                _font_aux_by_cid.setdefault(ref_cid, []).append((tt, body))
        for cid in all_char_ids:
            if self.char_types[cid] != 'font':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Font_{cid}"
            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'shape',
                'isFont': True,
                'symbol': sym_name,
                'folderId': self.folder_ids.get('font', 0),
                'bitmapId': 0,
                'grid': None,
                'inBitmap': False,
                'recodes': [],
                'bounds': {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20},
            }
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                entry['rawTagType'] = tag_type
                entry['rawTagBody'] = base64.b64encode(body).decode('ascii')
                # Store font body separately so it survives without sidecar
                entry['fontData'] = base64.b64encode(body).decode('ascii')
                entry['fontTagType'] = tag_type
            # Attach font auxiliary tags (DefineFontAlignZones, CSMTextSettings,
            # DefineFontName) to the entry so they survive without rawGlobalTags
            if cid in _font_aux_by_cid:
                entry['fontAuxTags'] = [
                    {'tagType': tt, 'body': base64.b64encode(body).decode('ascii')}
                    for tt, body in _font_aux_by_cid[cid]
                ]
            self.libraries.append(entry)
            font_count += 1

        step(f"Built {font_count} font entries")

        # Phase 7: Build MovieClip (container) entries from DefineSprite data
        sprite_count = 0
        for cid in all_char_ids:
            if self.char_types[cid] != 'container':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Sprite_{cid}"

            frame_count, nested_tags = self.sprite_data[cid]
            frames = analyze_timeline(nested_tags, self.header['version'])

            container = self._build_container(lid, display_name, sym_name,
                                              frame_count, frames)
            container['swfCharId'] = cid
            # Include raw DefineSprite body as base64 for 1:1 roundtrip
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                container['rawTagType'] = tag_type
                container['rawTagBody'] = base64.b64encode(body).decode('ascii')
            # Capture SoundStreamHead2 (tag 45) for roundtrip
            for ntag in nested_tags:
                if ntag.tag_type == 45:
                    container['rawSoundStreamHead'] = base64.b64encode(ntag.data).decode('ascii')
                    break
            self.libraries.append(container)
            sprite_count += 1

        step(f"Built {sprite_count} MovieClip (container) entries")

    def _build_container(self, lib_id: int, name: str, symbol: str,
                         frame_count: int, frames: List[TimelineFrame]) -> dict:
        """Build a container (MovieClip) library entry from analyzed timeline frames.

        Uses event-based per-depth tracking instead of full display list snapshots
        to avoid O(frames × depths) memory copies.
        """

        labels = []

        actual_frame_count = max(len(frames), frame_count, 1)

        # Per-depth event tracking (avoids O(frames×depths) full-copy snapshots)
        # depth → list of (frame_num, state_dict_or_None, is_reinstated)
        # state_dict_or_None is None for 'remove' events
        depth_events: Dict[int, list] = {}

        # Collect sounds triggered on each frame
        sounds_per_frame: Dict[int, List[SoundAction]] = {}

        # Track live display_list state for cumulative move updates
        display_list: Dict[int, dict] = {}

        for frame_idx, frame in enumerate(frames):
            frame_num = frame_idx + 1

            # Record label
            if frame.label:
                labels.append({'frame': frame_num, 'name': frame.label})

            removed_this_frame: Set[int] = set()

            for action in frame.actions:
                if isinstance(action, PlaceAction):
                    depth = action.depth
                    if action.is_move and depth in display_list:
                        # Move: update existing entry in-place
                        existing = display_list[depth]
                        if action.char_id is not None:
                            existing['char_id'] = action.char_id
                        if action.matrix is not None:
                            existing['matrix'] = action.matrix
                        if action.color_transform is not None:
                            existing['cxform'] = action.color_transform
                        if action.name is not None:
                            existing['name'] = action.name
                        if action.blend_mode is not None:
                            existing['blend_mode'] = action.blend_mode
                        if action.ratio is not None:
                            existing['ratio'] = action.ratio
                        # Record snapshot of current state as event
                        depth_events.setdefault(depth, []).append(
                            (frame_num, dict(existing), False))
                    else:
                        # New placement
                        is_reinstated = depth in removed_this_frame
                        state = {
                            'char_id': action.char_id,
                            'matrix': action.matrix or [1, 0, 0, 1, 0, 0],
                            'cxform': action.color_transform or [1, 1, 1, 1, 0, 0, 0, 0],
                            'name': action.name or '',
                            'clip_depth': action.clip_depth,
                            'blend_mode': action.blend_mode,
                            'ratio': action.ratio,
                        }
                        display_list[depth] = state
                        depth_events.setdefault(depth, []).append(
                            (frame_num, dict(state), is_reinstated))
                elif isinstance(action, RemoveAction):
                    display_list.pop(action.depth, None)
                    removed_this_frame.add(action.depth)
                    depth_events.setdefault(action.depth, []).append(
                        (action.depth, None, False))
                    # Store frame_num instead of depth for 'remove' events
                    depth_events[action.depth][-1] = (frame_num, None, False)

            # Collect sound triggers for this frame
            if frame.sounds:
                sounds_per_frame[frame_num] = list(frame.sounds)

        # Convert per-depth events → n2d layers
        all_depths = sorted(depth_events.keys(), reverse=True)

        layers = []
        for depth_idx, depth in enumerate(all_depths):
            events = depth_events[depth]
            layer = self._build_layer_from_events(
                depth, depth_idx, events, actual_frame_count)
            layers.append(layer)

        # If no layers, create one empty layer
        if not layers:
            layers = [{
                'name': 'layer_0',
                'light': False,
                'disable': False,
                'lock': False,
                'mode': 0,
                'maskId': None,
                'guideId': None,
                'color': LAYER_COLORS[0],
                'characters': [],
                'emptyCharacters': [{'startFrame': 1, 'endFrame': actual_frame_count + 1}],
            }]

        # Build sounds array from collected StartSound entries
        sounds = []
        for fnum in sorted(sounds_per_frame.keys()):
            sound_entries = []
            for sa in sounds_per_frame[fnum]:
                n2d_id = self.swf_to_n2d.get(sa.sound_id, 0)
                if n2d_id:
                    sound_entries.append({
                        'characterId': n2d_id,
                        'volume': 100,
                        'loopCount': sa.loop_count,
                        'autoPlay': sa.has_loops,
                    })
            if sound_entries:
                sounds.append({'frame': fnum, 'sound': sound_entries})

        # Build actions array from JPEXS-decompiled frame scripts
        actions = []
        if symbol and hasattr(self, 'frame_scripts') and self.frame_scripts:
            fs = self.frame_scripts.get(symbol, {})
            for frame_num in sorted(fs.keys()):
                if 1 <= frame_num <= actual_frame_count:
                    actions.append({
                        'frame': frame_num,
                        'action': fs[frame_num],
                    })

        return {
            'id': lib_id,
            'name': name,
            'type': 'container',
            'symbol': symbol,
            'folderId': self.folder_ids.get('container', 0),
            'totalFrame': actual_frame_count,
            'currentFrame': 1,
            'leftFrame': 1,
            'layers': layers,
            'labels': labels,
            'sounds': sounds,
            'actions': actions,
        }

    def _build_layer_for_depth(self, depth: int, depth_idx: int,
                               frame_states: List[dict],
                               total_frames: int,
                               reinstated_per_frame: Optional[List[Set[int]]] = None) -> dict:
        """Build one n2d layer from the frame history of a single SWF depth."""
        layer_name = f"layer_{depth}"
        layer_color = LAYER_COLORS[depth_idx % len(LAYER_COLORS)]

        characters = []
        empty_chars = []

        # Walk through frames and find character spans
        # A span is a contiguous range of frames where the same character
        # is placed at this depth
        span_start = None
        span_char_id = None
        span_places = []  # (frame_num, state_dict) for each frame in span

        for frame_idx in range(total_frames):
            frame_num = frame_idx + 1
            state = frame_states[frame_idx] if frame_idx < len(frame_states) else {}

            # Check if this depth was reinstated (removed then re-placed) this frame
            is_reinstated = (reinstated_per_frame is not None
                             and frame_idx < len(reinstated_per_frame)
                             and depth in reinstated_per_frame[frame_idx])

            if depth in state:
                entry = state[depth]
                cur_char_id = entry['char_id']

                if span_start is None:
                    # Start new span
                    span_start = frame_num
                    span_char_id = cur_char_id
                    span_places = [(frame_num, entry)]
                    span_reinstated = is_reinstated
                elif cur_char_id != span_char_id or is_reinstated:
                    # Character changed OR depth was removed+re-placed (new instance)
                    # — close old span, start new
                    characters.append(self._build_character_span(
                        span_char_id, span_start, frame_num, span_places,
                        reinstated=span_reinstated))
                    span_start = frame_num
                    span_char_id = cur_char_id
                    span_places = [(frame_num, entry)]
                    span_reinstated = is_reinstated
                else:
                    # Same character — only add if properties changed (keyframe)
                    _, prev_entry = span_places[-1]
                    if (entry.get('matrix') != prev_entry.get('matrix') or
                        entry.get('cxform') != prev_entry.get('cxform') or
                        entry.get('blend_mode') != prev_entry.get('blend_mode') or
                        entry.get('name') != prev_entry.get('name')):
                        span_places.append((frame_num, entry))
            else:
                if span_start is not None:
                    # Close span
                    characters.append(self._build_character_span(
                        span_char_id, span_start, frame_num, span_places,
                        reinstated=span_reinstated))
                    span_start = None
                    span_char_id = None
                    span_places = []
                    span_reinstated = False

        # Close final span
        if span_start is not None:
            characters.append(self._build_character_span(
                span_char_id, span_start, total_frames + 1, span_places,
                reinstated=span_reinstated))

        # Build empty character ranges (gaps)
        empty_chars = self._compute_empty_ranges(characters, total_frames)

        return {
            'name': layer_name,
            'swfDepth': depth,
            'light': False,
            'disable': False,
            'lock': False,
            'mode': 0,
            'maskId': None,
            'guideId': None,
            'color': layer_color,
            'characters': characters,
            'emptyCharacters': empty_chars,
        }

    def _build_layer_from_events(self, depth: int, depth_idx: int,
                                events: list, total_frames: int) -> dict:
        """Build one n2d layer from per-depth events (optimized, no frame_states).

        Each event is (frame_num, state_dict_or_None, is_reinstated).
        state_dict is None for remove events.
        """
        layer_name = f"layer_{depth}"
        layer_color = LAYER_COLORS[depth_idx % len(LAYER_COLORS)]

        characters = []
        span_start = None
        span_char_id = None
        span_places = []
        span_reinstated = False

        for frame_num, state, is_reinstated in events:
            if state is None:
                # Remove event — close current span
                if span_start is not None:
                    characters.append(self._build_character_span(
                        span_char_id, span_start, frame_num, span_places,
                        reinstated=span_reinstated))
                    span_start = None
                    span_char_id = None
                    span_places = []
                    span_reinstated = False
            else:
                # Place or move event — depth is present
                cur_char_id = state.get('char_id')

                if span_start is None:
                    # Start new span
                    span_start = frame_num
                    span_char_id = cur_char_id
                    span_places = [(frame_num, state)]
                    span_reinstated = is_reinstated
                elif cur_char_id != span_char_id or is_reinstated:
                    # Character changed or reinstated — close old, start new
                    characters.append(self._build_character_span(
                        span_char_id, span_start, frame_num, span_places,
                        reinstated=span_reinstated))
                    span_start = frame_num
                    span_char_id = cur_char_id
                    span_places = [(frame_num, state)]
                    span_reinstated = is_reinstated
                else:
                    # Same character — add keyframe if properties changed
                    _, prev_entry = span_places[-1]
                    if (state.get('matrix') != prev_entry.get('matrix') or
                        state.get('cxform') != prev_entry.get('cxform') or
                        state.get('blend_mode') != prev_entry.get('blend_mode') or
                        state.get('name') != prev_entry.get('name')):
                        span_places.append((frame_num, state))

        # Close final span
        if span_start is not None:
            characters.append(self._build_character_span(
                span_char_id, span_start, total_frames + 1, span_places,
                reinstated=span_reinstated))

        # Build empty character ranges (gaps)
        empty_chars = self._compute_empty_ranges(characters, total_frames)

        return {
            'name': layer_name,
            'swfDepth': depth,
            'light': False,
            'disable': False,
            'lock': False,
            'mode': 0,
            'maskId': None,
            'guideId': None,
            'color': layer_color,
            'characters': characters,
            'emptyCharacters': empty_chars,
        }

    def _build_character_span(self, swf_char_id: int, start_frame: int,
                              end_frame: int,
                              frame_entries: List[Tuple[int, dict]],
                              reinstated: bool = False) -> dict:
        """Build an n2d character object for a span of frames at one depth."""
        lib_id = self.swf_to_n2d.get(swf_char_id, 0) if swf_char_id is not None else 0
        instance_name = ''

        # Build places array
        places = []
        for frame_num, entry in frame_entries:
            matrix = entry.get('matrix', [1, 0, 0, 1, 0, 0])
            cxform = entry.get('cxform', [1, 1, 1, 1, 0, 0, 0, 0])
            blend_raw = entry.get('blend_mode')
            blend_name = BLEND_MODE_MAP.get(blend_raw, 'normal') if blend_raw else 'normal'

            if entry.get('name') and not instance_name:
                instance_name = entry['name']

            # matrix: [scaleX, rotSkew0, rotSkew1, scaleY, tx, ty]
            # n2d expects [a, b, c, d, tx, ty] — same order
            a, b, c, d, tx, ty = matrix

            # For DefineText converted to type:"text", the original SWF
            # bounds had an offset that we normalized to (0,0).  Bake that
            # offset into the placement matrix so the text appears in the
            # correct position.  Tool computes x = matrix.tx + bounds.xMin,
            # so with bounds.xMin = 0 we need tx to include the offset.
            if lib_id in self.text_bounds_offsets:
                dx, dy = self.text_bounds_offsets[lib_id]
                tx += dx
                ty += dy

            place = {
                'frame': frame_num,
                'depth': 0,
                'blendMode': blend_name,
                'filter': [],
                'matrix': [a, b, c, d, tx, ty],
                'colorTransform': list(cxform),
            }
            # Preserve ratio from OG PlaceObject for 1:1 roundtrip
            if entry.get('ratio') is not None:
                place['ratio'] = entry['ratio']
            places.append(place)

        self.next_char_id += 1

        result = {
            'id': self.next_char_id,
            'name': instance_name,
            'libraryId': lib_id,
            'startFrame': start_frame,
            'endFrame': end_frame,
            'tween': [],
            'places': places,
        }
        if reinstated:
            result['reinstated'] = True
        return result

    def _compute_empty_ranges(self, characters: List[dict],
                              total_frames: int) -> List[dict]:
        """Compute empty frame ranges (gaps between characters)."""
        occupied = set()
        for char in characters:
            for f in range(char['startFrame'], char['endFrame']):
                occupied.add(f)

        empty = []
        gap_start = None
        for f in range(1, total_frames + 2):
            if f not in occupied:
                if gap_start is None:
                    gap_start = f
            else:
                if gap_start is not None:
                    empty.append({'startFrame': gap_start, 'endFrame': f})
                    gap_start = None
        if gap_start is not None:
            empty.append({'startFrame': gap_start, 'endFrame': total_frames + 1})

        return empty

    def build_main_timeline(self, tags: List[SWFTag]):
        """Build the main timeline (library id=0) from top-level SWF tags."""
        log.info('build_main_timeline: building from %d top-level tags', len(tags))
        # The main timeline's structural tags are those at the top level
        # that are PlaceObject/RemoveObject/ShowFrame/FrameLabel
        # (Definition tags are already cataloged)
        frames = analyze_timeline(tags, self.header['version'])

        main = self._build_container(
            0, 'main', self.symbol_names.get(0, ''),
            self.header['frameCount'], frames)

        # Set currentFrame to the first frame that actually has content
        # (SSF2 characters often leave frame 1 blank)
        first_content_frame = 1
        for layer in main.get('layers', []):
            for ch in layer.get('characters', []):
                sf = ch.get('startFrame', 1)
                if first_content_frame == 1 and sf > 1:
                    first_content_frame = sf
                elif sf < first_content_frame:
                    first_content_frame = sf
        if first_content_frame > 1:
            main['currentFrame'] = first_content_frame

        # Main timeline stays at root (not inside MovieClips folder)
        main['folderId'] = 0

        # Insert main timeline at position 0
        self.libraries.insert(0, main)

    def _embed_bitmap_data_in_recodes(self):
        """Replace integer bitmap IDs in shape recodes with embedded BitmapData
        objects ({buffer, width, height}).  The tool's Shape class expects actual
        pixel data at the BITMAP_FILL / BITMAP_STROKE positions, not library IDs.

        Decodes bitmap RGBA from rawTagBody (base64-encoded SWF tag data) on
        demand — only bitmaps actually referenced in shape fills are decoded.
        """
        BITMAP_FILL = 13
        BITMAP_STROKE = 14

        # Phase 1: Find which bitmap IDs are referenced in shape recodes
        referenced_ids = set()
        for lib in self.libraries:
            if lib.get('type') != 'shape' or not lib.get('inBitmap'):
                continue
            recodes = lib.get('recodes', [])
            i = 0
            while i < len(recodes):
                cmd = recodes[i]
                if cmd == BITMAP_FILL and i + 1 < len(recodes):
                    val = recodes[i + 1]
                    if isinstance(val, int):
                        referenced_ids.add(val)
                    i += 5
                elif cmd == BITMAP_STROKE and i + 5 < len(recodes):
                    val = recodes[i + 5]
                    if isinstance(val, int):
                        referenced_ids.add(val)
                    i += 9
                else:
                    i += 1

        if not referenced_ids:
            return

        # Phase 2: Decode only the referenced bitmaps
        bitmap_map = {}
        for lib in self.libraries:
            if lib.get('type') != 'bitmap':
                continue
            lid = lib['id']
            if lid not in referenced_ids:
                continue
            w = lib.get('width', 0)
            h = lib.get('height', 0)
            if not w or not h:
                continue

            # Try pre-decoded buffer first
            buf = lib.get('buffer', '')
            if buf:
                if buf.startswith('b64:'):
                    rgba_bytes = base64.b64decode(buf[4:])
                else:
                    rgba_bytes = buf.encode('latin-1')
                bitmap_map[lid] = {
                    'buffer': list(rgba_bytes),
                    'width': w,
                    'height': h,
                }
                continue

            # Decode from rawTagBody (base64 of SWF tag body, charId stripped)
            raw_b64 = lib.get('rawTagBody', '')
            raw_tag_type = lib.get('rawTagType', 0)
            if not raw_b64 or not raw_tag_type:
                continue

            try:
                raw_bytes = base64.b64decode(raw_b64)
            except Exception:
                continue

            rgba = b''
            if raw_tag_type in (TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2):
                # decode_lossless expects body after charId — matches our storage
                _, _, rgba = decode_lossless_to_rgba(raw_tag_type, raw_bytes)
            elif raw_tag_type in (TAG_DEFINE_BITS, TAG_DEFINE_BITS_JPEG2,
                                  TAG_DEFINE_BITS_JPEG3, TAG_DEFINE_BITS_JPEG4):
                # decode_jpeg expects full body including charId — prepend dummy
                _, _, rgba = decode_jpeg_to_rgba(raw_tag_type, b'\x00\x00' + raw_bytes)

            if rgba:
                bitmap_map[lid] = {
                    'buffer': list(rgba),
                    'width': w,
                    'height': h,
                }

        if not bitmap_map:
            print(f"  Warning: {len(referenced_ids)} bitmap fills but 0 decoded")
            return

        # Phase 3: Replace numeric IDs with decoded bitmap data
        replaced = 0
        for lib in self.libraries:
            if lib.get('type') != 'shape' or not lib.get('inBitmap'):
                continue
            recodes = lib.get('recodes', [])
            if not recodes:
                continue

            i = 0
            while i < len(recodes):
                cmd = recodes[i]
                if cmd == BITMAP_FILL and i + 1 < len(recodes):
                    bmp_id = recodes[i + 1]
                    if isinstance(bmp_id, int) and bmp_id in bitmap_map:
                        recodes[i + 1] = dict(bitmap_map[bmp_id], bitmapId=bmp_id)
                        replaced += 1
                    i += 5  # BITMAP_FILL + bitmapData + matrix + repeat + smooth
                elif cmd == BITMAP_STROKE and i + 5 < len(recodes):
                    bmp_id = recodes[i + 5]
                    if isinstance(bmp_id, int) and bmp_id in bitmap_map:
                        recodes[i + 5] = dict(bitmap_map[bmp_id], bitmapId=bmp_id)
                        replaced += 1
                    i += 9  # BITMAP_STROKE + w,c,j,m + bitmapData + matrix + repeat + smooth
                else:
                    i += 1

        print(f"  Embedded bitmap data in {replaced} fill/stroke commands "
              f"({len(bitmap_map)} bitmaps decoded)")

    def to_n2d_json(self) -> dict:
        """Produce the complete .n2d JSON."""
        log.info('to_n2d_json: %d libraries', len(self.libraries))
        # characterId must exceed all existing library and placement IDs
        # so the tool can allocate new IDs without collision.
        max_id = max(self.next_lib_id, self.next_char_id)
        result = {
            'version': 1,
            'name': self.name,
            'characterId': max_id + 1,
            'stage': {
                'width': self.header['width'],
                'height': self.header['height'],
                'fps': self.header['fps'],
                'bgColor': '#333333',
                'lock': False,
            },
            'libraries': self.libraries,
            'plugins': [],
            'setting': {
                'timelineHeight': 280,
                'controllerWidth': 360,
                'ruler': False,
                'rulerX': [],
                'rulerY': [],
            },
        }
        # Include raw SWF global tags as base64 for 1:1 roundtrip passthrough
        if self.global_raw_tags:
            result['rawGlobalTags'] = [
                {'tagType': tt, 'body': base64.b64encode(body).decode('ascii')}
                for tt, body in self.global_raw_tags
            ]
        # Include SWF version and compression format for matching
        result['swfVersion'] = self.header.get('version', 14)
        result['swfCompressed'] = self.header.get('compressed', True)
        # Store which charIds are defined inline in the root timeline section
        # (after SymbolClass). These must NOT be emitted in the definition
        # section during compilation — they go in the root timeline instead.
        if self.root_timeline_def_ids:
            result['rootTimelineDefIds'] = self.root_timeline_def_ids
        # Include AS3 source scripts if any were loaded
        if self.scripts:
            result['scripts'] = self.scripts
        return result


# ═══════════════════════════════════════════════════════════════════════════
#  SAVE .n2d FILE
# ═══════════════════════════════════════════════════════════════════════════

def save_n2d(data: dict, output_path: str, bitmap_buffers: dict = None):
    """Save dict as .n2d ZIP archive.

    Format: ZIP file containing:
      - project.json: the main N2D JSON

    Bitmap data is stored inline in each library entry's rawTagBody field
    (base64-encoded original SWF tag data). No separate bitmap files are
    written — this keeps memory usage minimal and avoids the 500 MB+ RAM
    spike from decoding all bitmaps to raw RGBA.

    bitmap_buffers parameter is accepted for backwards compatibility but
    is no longer used (ignored). All bitmap data comes from rawTagBody.
    """
    log.info('save_n2d: writing to %s', output_path)
    import zipfile
    t0 = time.time()
    step = lambda msg: print(f"  [{time.time()-t0:6.1f}s] {msg}", flush=True)

    step("Serializing JSON...")
    json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=True)
    step(f"JSON: {len(json_str):,} chars")

    step("Writing ZIP (project.json only — bitmaps stored as rawTagBody)...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        zf.writestr('project.json', json_str)
    step(f"ZIP written: {os.path.getsize(output_path):,} bytes")
    step(f"Written to {output_path}")


# ═══════════════════════════════════════════════════════════════════════════
#  SAVE PROJECT FOLDER (external assets: PNG / WAV / MP3 / AS)
# ═══════════════════════════════════════════════════════════════════════════

def _safe_filename(name: str) -> str:
    """Sanitise a library/script name for use as a filesystem filename."""
    # Replace path separators and other problematic characters
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    return name.strip('. ') or 'unnamed'


def save_project_folder(data: dict, folder_path: str):
    """Save an N2D project as an editable folder with external asset files.

    Creates:
      {folder_path}/
        project.n2d           — N2D ZIP archive
        bitmaps/              — PNG / JPG images
        sounds/               — MP3 / WAV audio
        scripts/              — .as ActionScript source files

    Libraries gain an ``externalFile`` field pointing to their asset.
    The rawTagBody is still preserved in project.n2d for lossless
    roundtrip, but the human-readable files can be edited and will be
    preferred during compilation when they are newer.
    """
    log.info('save_project_folder: writing to %s', folder_path)
    t0 = time.time()
    step = lambda msg: print(f"  [{time.time()-t0:6.1f}s] {msg}", flush=True)

    os.makedirs(folder_path, exist_ok=True)
    bitmaps_dir = os.path.join(folder_path, 'bitmaps')
    sounds_dir = os.path.join(folder_path, 'sounds')
    scripts_dir = os.path.join(folder_path, 'scripts')
    os.makedirs(bitmaps_dir, exist_ok=True)
    os.makedirs(sounds_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    bitmap_count = 0
    sound_count = 0

    # ── Extract bitmaps ──────────────────────────────────────────────
    step("Extracting bitmaps...")

    def _extract_bitmap(lib):
        """Decode one bitmap entry and write PNG/JPG to bitmaps_dir.
        Returns 1 if saved, 0 otherwise.  Modifies lib['externalFile'] in place.
        """
        cid = lib.get('swfCharId', lib.get('id', 0))
        name = _safe_filename(lib.get('name', f'bitmap_{cid}'))
        raw_b64 = lib.get('rawTagBody', '')
        tag_type = lib.get('rawTagType', 36)

        if not raw_b64:
            return 0

        raw_body = base64.b64decode(raw_b64)

        # JPEG2 → write raw JPEG bytes directly (already efficient, no decode)
        if tag_type == TAG_DEFINE_BITS_JPEG2:
            img_data = raw_body
            if len(img_data) >= 4 and img_data[:4] == b'\xff\xd9\xff\xd8':
                img_data = img_data[4:]
            fname = f"{cid}_{name}.jpg"
            with open(os.path.join(bitmaps_dir, fname), 'wb') as f:
                f.write(img_data)
            lib['externalFile'] = f'bitmaps/{fname}'
            return 1

        # All other types → save as PNG
        fname = f"{cid}_{name}.png"
        fpath = os.path.join(bitmaps_dir, fname)

        # Fast path: reuse pre-decoded RGBA from build_all() — avoids third decode
        buf = lib.get('buffer', '')
        w = lib.get('width', 0)
        h = lib.get('height', 0)
        if buf and w and h:
            if buf.startswith('b64:'):
                rgba = base64.b64decode(buf[4:])
            else:
                rgba = buf.encode('latin-1')
            if rgba and len(rgba) == w * h * 4:
                try:
                    from PIL import Image
                    Image.frombytes('RGBA', (w, h), rgba).save(fpath)
                    lib['externalFile'] = f'bitmaps/{fname}'
                    return 1
                except ImportError:
                    pass  # fall through to raw-decode path

        # Fallback: decode from raw SWF tag body
        rgba = w = h = b''
        if tag_type in (TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2):
            w, h, rgba = decode_lossless_to_rgba(tag_type, raw_body)
        elif tag_type in (TAG_DEFINE_BITS, TAG_DEFINE_BITS_JPEG3, TAG_DEFINE_BITS_JPEG4):
            full_tag_data = struct.pack('<H', cid) + raw_body
            w, h, rgba = decode_jpeg_to_rgba(tag_type, full_tag_data)

        if w and h and rgba:
            try:
                from PIL import Image
                Image.frombytes('RGBA', (w, h), rgba).save(fpath)
                lib['externalFile'] = f'bitmaps/{fname}'
                return 1
            except ImportError:
                step(f"  [WARN] PIL unavailable, cannot save PNG for bitmap {cid}")
        return 0

    bitmap_libs = [lib for lib in data.get('libraries', [])
                   if lib and lib.get('type') == 'bitmap']
    if bitmap_libs:
        with ThreadPoolExecutor(max_workers=min(8, len(bitmap_libs))) as ex:
            bitmap_count = sum(ex.map(_extract_bitmap, bitmap_libs))

    step(f"Extracted {bitmap_count} bitmaps")

    # ── Extract sounds ───────────────────────────────────────────────
    step("Extracting sounds...")

    def _detect_audio_ext(data: bytes) -> str:
        """Detect audio format from magic bytes."""
        if data[:3] == b'ID3' or (len(data) >= 2 and data[0] == 0xff and data[1] & 0xe0 == 0xe0):
            return 'mp3'
        if data[:4] == b'RIFF':
            return 'wav'
        if data[:4] == b'OggS':
            return 'ogg'
        return 'bin'

    def _extract_sound(lib):
        """Write one sound entry to sounds_dir. Returns 1 if saved, 0 otherwise."""
        cid = lib.get('swfCharId', lib.get('id', 0))
        name = _safe_filename(lib.get('name', f'sound_{cid}'))

        # Fast path: reuse pre-decoded/pre-converted buffer from build_all()
        buf = lib.get('buffer', '')
        if buf:
            audio_bytes = base64.b64decode(buf)
            ext = _detect_audio_ext(audio_bytes)
            fname = f"{cid}_{name}.{ext}"
            fpath = os.path.join(sounds_dir, fname)
            with open(fpath, 'wb') as f:
                f.write(audio_bytes)
            lib['externalFile'] = f'sounds/{fname}'
            return 1

        # Fallback: decode from raw SWF tag body
        raw_b64 = lib.get('rawTagBody', '')
        if not raw_b64:
            return 0
        raw_body = base64.b64decode(raw_b64)
        fmt_name, audio_bytes, _rate = extract_sound_buffer(raw_body)
        if not audio_bytes:
            return 0
        ext = 'mp3' if fmt_name == 'mp3' else 'wav' if fmt_name == 'wav' else 'bin'
        fname = f"{cid}_{name}.{ext}"
        fpath = os.path.join(sounds_dir, fname)
        with open(fpath, 'wb') as f:
            f.write(audio_bytes)
        lib['externalFile'] = f'sounds/{fname}'
        return 1

    sound_libs = [lib for lib in data.get('libraries', [])
                  if lib and lib.get('type') == 'sound']
    if sound_libs:
        with ThreadPoolExecutor(max_workers=min(8, len(sound_libs))) as ex:
            sound_count = sum(ex.map(_extract_sound, sound_libs))

    step(f"Extracted {sound_count} sounds")

    # ── Extract scripts ──────────────────────────────────────────────
    script_count = 0
    step("Extracting scripts...")
    for script in data.get('scripts', []):
        source = script.get('source', '')
        if not source:
            continue
        spath = script.get('path', script.get('name', 'unknown.as'))
        # Create subdirectories matching package paths
        full_path = os.path.join(scripts_dir, spath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(source)
        script['externalFile'] = f'scripts/{spath}'
        script_count += 1

    step(f"Extracted {script_count} scripts")

    # ── Write project.n2d ────────────────────────────────────────────
    step("Writing project.n2d...")
    n2d_path = os.path.join(folder_path, 'project.n2d')
    save_n2d(data, n2d_path)

    total = bitmap_count + sound_count + script_count
    step(f"DONE: {total} assets extracted to {folder_path}")
    step(f"  {bitmap_count} bitmaps, {sound_count} sounds, {script_count} scripts")
    return folder_path


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    log.debug('main: entry')
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    swf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.isfile(swf_path):
        print(f"Error: SWF file not found: {swf_path}")
        return 1

    name = os.path.splitext(os.path.basename(swf_path))[0]
    if not output_path:
        output_path = name + '.n2d'

    t0 = time.time()
    step = lambda msg: print(f"[{time.time()-t0:6.1f}s] {msg}", flush=True)

    # 1. Parse SWF
    step("Parsing SWF binary...")
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    header, tags = parse_swf(swf_data)
    step(f"SWF: {header['width']}x{header['height']} @ {header['fps']}fps, "
         f"{header['frameCount']} frames, {len(tags)} top-level tags")

    # 2. Build n2d
    step("Building n2d project...")
    builder = N2DBuilder(header, name=name)

    step("Cataloging SWF tags...")
    builder.catalog_swf_tags(tags)
    step(f"Found: {sum(1 for t in builder.char_types.values() if t=='bitmap')} bitmaps, "
         f"{sum(1 for t in builder.char_types.values() if t=='shape')} shapes, "
         f"{sum(1 for t in builder.char_types.values() if t=='container')} sprites, "
         f"{sum(1 for t in builder.char_types.values() if t=='sound')} sounds, "
         f"{sum(1 for t in builder.char_types.values() if t=='text')} texts, "
         f"{sum(1 for t in builder.char_types.values() if t=='morphShape')} morphShapes, "
         f"{len(builder.symbol_names)} symbol names")

    # 2a. Single-pass ABC decompilation: scripts + frame scripts
    step("Decompiling AS3 scripts + extracting frame scripts (single pass)...")
    scripts, frame_scripts = decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
    if scripts:
        builder.scripts.extend(scripts)
        step(f"Decompiled {len(scripts)} AS3 scripts, "
             f"{len(frame_scripts)} classes with frame scripts")
    else:
        step("No AS3 scripts decompiled (no DoABC tags or as3_decompiler not available)")

    step("Building library entries...")
    builder.build_all()

    step("Building main timeline...")
    builder.build_main_timeline(tags)

    step("Embedding bitmap data in shape recodes...")
    builder._embed_bitmap_data_in_recodes()

    # 3. Save
    step("Generating .n2d output...")
    n2d = builder.to_n2d_json()

    lib_summary = {}
    for lib in n2d['libraries']:
        t = lib.get('type', 'unknown')
        lib_summary[t] = lib_summary.get(t, 0) + 1
    step(f"Total libraries: {len(n2d['libraries'])} — {dict(lib_summary)}")

    save_n2d(n2d, output_path)

    step(f"DONE! Output: {output_path} ({os.path.getsize(output_path):,} bytes)")
    return 0


if __name__ == '__main__':
    sys.exit(main())