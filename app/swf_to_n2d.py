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
import msgpack
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
from swf_binary_io import BitReader
from swf_constants import (
    SWFTag, TAG_END, TAG_SHOW_FRAME, TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2,
    TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4, TAG_DEFINE_BITS, TAG_DEFINE_BITS_JPEG2,
    TAG_DEFINE_BITS_JPEG3, TAG_DEFINE_BITS_JPEG4, TAG_DEFINE_BITS_LOSSLESS,
    TAG_DEFINE_BITS_LOSSLESS2, TAG_DEFINE_SPRITE, TAG_PLACE_OBJECT2,
    TAG_PLACE_OBJECT3, TAG_REMOVE_OBJECT2, TAG_FRAME_LABEL, TAG_DEFINE_SOUND,
    TAG_DEFINE_TEXT, TAG_DEFINE_TEXT2, TAG_DEFINE_EDIT_TEXT, TAG_DEFINE_MORPH_SHAPE,
    TAG_DEFINE_MORPH_SHAPE2, TAG_SYMBOL_CLASS, TAG_DO_ABC, TAG_DO_ABC2,
    TAG_FILE_ATTRIBUTES, TAG_SET_BACKGROUND_COLOR, TAG_DEFINE_FONT3,
    TAG_DEFINE_BUTTON2, TAG_START_SOUND, TAG_START_SOUND2,
    TAG_DEFINE_SCALING_GRID,
    TAG_JPEG_TABLES, TAG_DEFINE_BUTTON_SOUND, TAG_DEFINE_BUTTON_CXFORM,
    TAG_DEFINE_FONT2, TAG_IMPORT_ASSETS, TAG_IMPORT_ASSETS2,
    TAG_DEFINE_BINARY_DATA,
)
from cycle_detector import validate_swf_sprites

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

# ── Low-level helpers for structured tag parsing ──────────────────────────

def _read_encoded_u32(data: bytes, off: int) -> Tuple[int, int]:
    """Read a SWF EncodedU32 (variable-length, 1-5 bytes)."""
    result = 0
    for i in range(5):
        b = data[off]; off += 1
        result |= (b & 0x7f) << (7 * i)
        if not (b & 0x80):
            break
    return result, off


def _read_cstring(data: bytes, off: int) -> Tuple[str, int]:
    """Read a NUL-terminated string."""
    nul = data.index(0, off) if 0 in data[off:] else len(data)
    s = data[off:nul].decode('utf-8', errors='replace')
    return s, nul + 1


def _read_swf_matrix(data: bytes, off: int) -> Tuple[dict, int]:
    """Read a SWF MATRIX record from byte data at byte offset."""
    br = BitReader(data, off)
    has_scale = br.read_ub(1)
    sx, sy = 1.0, 1.0
    if has_scale:
        nb = br.read_ub(5)
        sx = br.read_fb(nb)
        sy = br.read_fb(nb)
    has_rot = br.read_ub(1)
    r0, r1 = 0.0, 0.0
    if has_rot:
        nb = br.read_ub(5)
        r0 = br.read_fb(nb)
        r1 = br.read_fb(nb)
    nb = br.read_ub(5)
    tx = br.read_sb(nb)
    ty = br.read_sb(nb)
    new_off = (br.pos + 7) // 8
    return {'scaleX': sx, 'rotateSkew0': r0, 'rotateSkew1': r1,
            'scaleY': sy, 'translateX': tx, 'translateY': ty}, new_off


def _read_swf_cxform_alpha(data: bytes, off: int) -> Tuple[dict, int]:
    """Read CXFORMWITHALPHA from byte data."""
    br = BitReader(data, off)
    has_add = br.read_ub(1)
    has_mult = br.read_ub(1)
    nb = br.read_ub(4)
    rm, gm, bm, am = 256, 256, 256, 256
    ra, ga, ba, aa = 0, 0, 0, 0
    if has_mult:
        rm = br.read_sb(nb); gm = br.read_sb(nb)
        bm = br.read_sb(nb); am = br.read_sb(nb)
    if has_add:
        ra = br.read_sb(nb); ga = br.read_sb(nb)
        ba = br.read_sb(nb); aa = br.read_sb(nb)
    new_off = (br.pos + 7) // 8
    return {'redMultTerm': rm, 'greenMultTerm': gm, 'blueMultTerm': bm, 'alphaMultTerm': am,
            'redAddTerm': ra, 'greenAddTerm': ga, 'blueAddTerm': ba, 'alphaAddTerm': aa}, new_off


def _read_swf_filter_list(data: bytes, off: int) -> Tuple[list, int]:
    """Read FILTERLIST — returns list of filter dicts and new offset."""
    count = data[off]; off += 1
    filters = []
    for _ in range(count):
        fid = data[off]; off += 1
        # Store as base64 per-filter — full parse TBD
        # We need to know the filter size; for now, skip known sizes
        filter_sizes = {0: 23, 1: 9, 2: 15, 3: 27, 4: -1, 5: -1, 6: -1, 7: -1}
        sz = filter_sizes.get(fid, 0)
        if sz > 0:
            filters.append({'filterId': fid, 'data': base64.b64encode(data[off:off+sz]).decode('ascii')})
            off += sz
        else:
            # Variable-size filters: GradientGlow(4), GradientBevel(7), ColorMatrix(6), Convolution(5)
            if fid == 6:  # ColorMatrix: 20 floats
                filters.append({'filterId': fid, 'data': base64.b64encode(data[off:off+80]).decode('ascii')})
                off += 80
            elif fid == 5:  # Convolution
                mx = data[off]; my = data[off+1]; off += 2
                skip = 4 + mx * my * 4 + 4 + 1  # divisor, matrix, bias, clamp+preserveAlpha, defaultColor
                filters.append({'filterId': fid, 'data': base64.b64encode(data[off-2:off-2+2+skip]).decode('ascii')})
                off += skip
            elif fid in (4, 7):  # GradientGlow / GradientBevel
                num_colors = data[off]; off += 1
                skip = num_colors * 4 + num_colors + 19  # colors + ratios + rest
                filters.append({'filterId': fid, 'data': base64.b64encode(data[off-1:off-1+1+skip]).decode('ascii')})
                off += skip
            else:
                filters.append({'filterId': fid, 'data': ''})
    return filters, off


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


def _read_rgba_color(br: BitReader) -> Tuple[int, float]:
    """Read RGBA → (0xRRGGBB, alpha_0to1)."""
    r = br.read_ui8()
    g = br.read_ui8()
    b = br.read_ui8()
    a = br.read_ui8()
    return (r << 16 | g << 8 | b), a / 255.0

def _read_fixed16(br: BitReader) -> float:
    """Read FIXED (16.16) as float."""
    raw = struct.unpack_from('<i', br.data, br.byte_pos)[0]
    br.byte_pos += 4
    return raw / 65536.0

def _read_fixed8(br: BitReader) -> float:
    """Read FIXED8 (8.8) as float."""
    raw = struct.unpack_from('<H', br.data, br.byte_pos)[0]
    br.byte_pos += 2
    return raw / 256.0

def _read_float32(br: BitReader) -> float:
    """Read IEEE 754 float32."""
    val = struct.unpack_from('<f', br.data, br.byte_pos)[0]
    br.byte_pos += 4
    return val

def _parse_drop_shadow(br: BitReader) -> dict:
    color, alpha = _read_rgba_color(br)
    blur_x = _read_fixed16(br)
    blur_y = _read_fixed16(br)
    angle = _read_fixed16(br) * (180.0 / math.pi)
    distance = _read_fixed16(br)
    strength = _read_fixed8(br)
    flags = br.read_ui8()
    inner = bool(flags & 0x80)
    knockout = bool(flags & 0x40)
    # bit 5 is CompositeSource (always 1)
    hide_object = not bool(flags & 0x20)
    quality = flags & 0x1F
    return {
        'name': 'DropShadowFilter',
        'blurX': blur_x, 'blurY': blur_y, 'quality': quality, 'state': True,
        'distance': distance, 'angle': angle, 'color': color, 'alpha': alpha,
        'strength': strength, 'inner': inner, 'knockout': knockout,
        'hideObject': hide_object,
    }

def _parse_blur(br: BitReader) -> dict:
    blur_x = _read_fixed16(br)
    blur_y = _read_fixed16(br)
    flags = br.read_ui8()
    quality = (flags >> 3) & 0x1F
    return {
        'name': 'BlurFilter',
        'blurX': blur_x, 'blurY': blur_y, 'quality': quality, 'state': True,
    }

def _parse_glow(br: BitReader) -> dict:
    color, alpha = _read_rgba_color(br)
    blur_x = _read_fixed16(br)
    blur_y = _read_fixed16(br)
    strength = _read_fixed8(br)
    flags = br.read_ui8()
    inner = bool(flags & 0x80)
    knockout = bool(flags & 0x40)
    quality = flags & 0x1F
    return {
        'name': 'GlowFilter',
        'blurX': blur_x, 'blurY': blur_y, 'quality': quality, 'state': True,
        'color': color, 'alpha': alpha, 'strength': strength,
        'inner': inner, 'knockout': knockout,
    }

def _parse_bevel(br: BitReader) -> dict:
    shadow_color, shadow_alpha = _read_rgba_color(br)
    highlight_color, highlight_alpha = _read_rgba_color(br)
    blur_x = _read_fixed16(br)
    blur_y = _read_fixed16(br)
    angle = _read_fixed16(br) * (180.0 / math.pi)
    distance = _read_fixed16(br)
    strength = _read_fixed8(br)
    flags = br.read_ui8()
    inner = bool(flags & 0x80)
    knockout = bool(flags & 0x40)
    # bit 5 is CompositeSource
    on_top = bool(flags & 0x10)
    quality = flags & 0x0F
    if inner:
        btype = 'inner'
    elif on_top:
        btype = 'full'
    else:
        btype = 'outer'
    return {
        'name': 'BevelFilter',
        'blurX': blur_x, 'blurY': blur_y, 'quality': quality, 'state': True,
        'distance': distance, 'angle': angle,
        'highlightColor': highlight_color, 'highlightAlpha': highlight_alpha,
        'shadowColor': shadow_color, 'shadowAlpha': shadow_alpha,
        'strength': strength, 'type': btype, 'knockout': knockout,
    }

def _parse_gradient_filter(br: BitReader, name: str) -> dict:
    """Parse GradientGlowFilter or GradientBevelFilter."""
    num_colors = br.read_ui8()
    colors = []
    alphas = []
    for _ in range(num_colors):
        c, a = _read_rgba_color(br)
        colors.append(c)
        alphas.append(a * 100)  # editor stores 0-100
    ratios = []
    for _ in range(num_colors):
        ratios.append(br.read_ui8())
    blur_x = _read_fixed16(br)
    blur_y = _read_fixed16(br)
    angle = _read_fixed16(br) * (180.0 / math.pi)
    distance = _read_fixed16(br)
    strength = _read_fixed8(br)
    flags = br.read_ui8()
    inner = bool(flags & 0x80)
    knockout = bool(flags & 0x40)
    on_top = bool(flags & 0x10)
    quality = flags & 0x0F
    if inner:
        ftype = 'inner'
    elif on_top:
        ftype = 'full'
    else:
        ftype = 'outer'
    return {
        'name': name,
        'blurX': blur_x, 'blurY': blur_y, 'quality': quality, 'state': True,
        'distance': distance, 'angle': angle,
        'colors': colors, 'alphas': alphas, 'ratios': ratios,
        'strength': strength, 'type': ftype, 'knockout': knockout,
    }

def _parse_color_matrix(br: BitReader) -> None:
    """Parse ColorMatrixFilter — skip 20 floats (not supported in editor)."""
    br.byte_pos += 20 * 4
    return None

def _parse_convolution(br: BitReader) -> None:
    """Parse ConvolutionFilter — skip (not supported in editor)."""
    mx = br.read_ui8()
    my = br.read_ui8()
    br.byte_pos += 4  # divisor float
    br.byte_pos += 4  # bias float
    br.byte_pos += mx * my * 4  # matrix floats
    br.byte_pos += 4  # default color RGBA
    br.read_ui8()  # flags
    return None

_FILTER_PARSERS = {
    0: _parse_drop_shadow,
    1: _parse_blur,
    2: _parse_glow,
    3: _parse_bevel,
    4: lambda br: _parse_gradient_filter(br, 'GradientGlowFilter'),
    5: _parse_convolution,
    6: _parse_color_matrix,
    7: lambda br: _parse_gradient_filter(br, 'GradientBevelFilter'),
}

def read_filter_list(br: BitReader) -> List[dict]:
    """Parse FILTERLIST from PlaceObject3. Returns list of filter dicts
    matching the editor's filter object format."""
    count = br.read_ui8()
    filters = []
    for _ in range(count):
        filter_id = br.read_ui8()
        parser = _FILTER_PARSERS.get(filter_id)
        if parser is None:
            log.warning('read_filter_list: unknown filter id %d, stopping', filter_id)
            break
        result = parser(br)
        if result is not None:
            filters.append(result)
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
    Returns (header_info, [SWFTag, ...]).
    
    Raises:
        ValueError: If SWF signature is invalid or data is too short
        struct.error: If binary data is malformed
    """
    # ── M1.3: Input validation ──
    if not swf_data or len(swf_data) < 8:
        raise ValueError(f"SWF data too short: {len(swf_data)} bytes (minimum 8 bytes)")
    
    log.debug('parse_swf: parsing %d bytes', len(swf_data))
    
    # ── M1.3: Signature validation ──
    sig = swf_data[0:3]
    if sig not in (b'FWS', b'CWS', b'ZWS'):
        raise ValueError(f"Not a SWF file (invalid signature: {sig!r}, expected FWS/CWS/ZWS)")

    version = swf_data[3]
    if version < 1 or version > 50:  # Sanity check
        log.warning(f"Unusual SWF version: {version} (expected 1-50)")
    
    try:
        file_length = struct.unpack_from('<I', swf_data, 4)[0]
    except struct.error as e:
        raise ValueError(f"Failed to read SWF file length: {e}")

    # ── M1.3: Decompression with error handling ──
    try:
        if sig == b'CWS':
            if len(swf_data) < 8:
                raise ValueError("CWS (zlib) SWF too short for header")
            body = zlib.decompress(swf_data[8:])
            data = swf_data[:8] + body
        elif sig == b'ZWS':
            if len(swf_data) < 12:
                raise ValueError("ZWS (LZMA) SWF too short for header")
            import lzma
            body = lzma.decompress(swf_data[12:])
            data = swf_data[:8] + body
        else:
            data = swf_data
    except (zlib.error, Exception) as e:
        raise ValueError(f"Failed to decompress SWF ({sig.decode('latin-1')}): {e}")

    # ── M1.3: Bounds checking for struct operations ──
    if len(data) < 16:
        raise ValueError(f"Decompressed SWF too short: {len(data)} bytes (minimum 16 bytes)")

    try:
        # Parse header RECT
        br = BitReader(data, 8)
        rect = read_rect(br)
        br.align()

        # Frame rate + frame count
        if br.byte_pos + 4 > len(data):
            raise ValueError("SWF header incomplete: missing frame rate/count")
        
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
    
    except (IndexError, struct.error) as e:
        raise ValueError(f"Failed to parse SWF header: {e}")


def parse_tags(data: bytes, offset: int) -> List[SWFTag]:
    """Parse a sequence of SWF tags starting at offset.
    
    Gracefully handles malformed tags by stopping at the first error.
    """
    log.debug('parse_tags: starting at offset %d, data len %d', offset, len(data))
    tags = []
    pos = offset
    
    # ── M1.3: Bounds checking in tag parsing loop ──
    while pos < len(data) - 1:
        try:
            # Need at least 2 bytes for tag code+length
            if pos + 2 > len(data):
                log.warning(f"parse_tags: incomplete tag header at offset {pos}")
                break
            
            tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
            tag_type = tag_code_and_length >> 6
            tag_length = tag_code_and_length & 0x3F
            pos += 2
            
            if tag_length == 0x3F:  # long tag
                if pos + 4 > len(data):
                    log.warning(f"parse_tags: incomplete long tag length at offset {pos}")
                    break
                tag_length = struct.unpack_from('<I', data, pos)[0]
                pos += 4
            
            # Bounds check for tag data
            if pos + tag_length > len(data):
                log.warning(f"parse_tags: tag {tag_type} claims {tag_length} bytes but only {len(data) - pos} available")
                tag_length = len(data) - pos  # Clip to available data
            
            tag_data = data[pos:pos + tag_length]
            tags.append(SWFTag(tag_type, tag_data, pos))
            pos += tag_length
            
            if tag_type == TAG_END:
                break
        
        except (struct.error, ValueError) as e:
            log.error(f"parse_tags: failed to parse tag at offset {pos}: {e}")
            break  # Stop parsing on error instead of crashing
    
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
            result['filters'] = read_filter_list(br)

        if has_blend_mode:
            result['blendMode'] = br.read_ui8()

        if has_cache_bitmap:
            result['cacheAsBitmap'] = True
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


def _merge_jpeg_tables(jpeg_table: bytes, define_bits_body: bytes) -> bytes:
    """Merge JPEGTables (tag 8) header with DefineBits (tag 6) body.

    SWF DefineBits (tag 6) relies on a separate JPEGTables for the JPEG
    header (SOI + quantization/huffman tables).  This function merges them
    into a standalone JPEG suitable for storage as DefineBitsJPEG2.

    Per SWF spec, both the table and the image data may be wrapped in
    SOI/EOI markers that need stripping to avoid duplicate markers.
    """
    # Strip erroneous SOI/EOI pairs from both streams
    # Adobe tools sometimes wrap table/data in extra SOI(FFD8)/EOI(FFD9) pairs
    tbl = jpeg_table
    img = define_bits_body
    # Strip trailing EOI from table
    if tbl[-2:] == b'\xff\xd9':
        tbl = tbl[:-2]
    # Strip leading SOI from image data
    if img[:2] == b'\xff\xd8':
        img = img[2:]
    # If table doesn't start with SOI, prepend one
    if tbl[:2] != b'\xff\xd8':
        tbl = b'\xff\xd8' + tbl
    return tbl + img


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


def parse_define_button2_char_ids(tag_data: bytes) -> List[int]:
    """Extract referenced character IDs from DefineButton2 records.

    tag_data starts AFTER the 2-byte charId (already stripped in raw_tag_data).
    Layout:
      UI8    Flags (bit0=trackAsMenu)
      UI16   ActionOffset
      BUTTONRECORD[] (terminated by 0 byte)
    """
    char_ids = []
    if len(tag_data) < 3:
        return char_ids
    br = BitReader(tag_data, 3)  # skip flags(1) + actionOffset(2)
    try:
        while br.byte_offset < len(tag_data):
            br.byte_align()
            first_byte = br.read_ui8()
            if first_byte == 0:
                break  # end of button records
            has_blend = bool(first_byte & 0x20)
            has_filter = bool(first_byte & 0x10)
            ref_char_id = br.read_ui16()
            char_ids.append(ref_char_id)
            br.read_ui16()  # PlaceDepth
            read_matrix(br)  # PlaceMatrix (variable-length)
            read_cxform_with_alpha(br)  # CXFORMWITHALPHA
            if has_filter:
                read_filter_list(br)  # skip filters
            if has_blend:
                br.read_ui8()  # BlendMode
    except Exception:
        pass  # best-effort — return whatever we got
    return char_ids


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


def parse_define_font2_name(tag_data: bytes) -> Tuple[int, str, bool, bool]:
    """Parse DefineFont2 (tag 48) → (charId, fontName, bold, italic).

    DefineFont2 has the same header layout as DefineFont3:
      UI16  FontID
      UI8   Flags
      UI8   LanguageCode
      UI8   FontNameLen
      UI8[] FontName
    """
    # DefineFont2 shares the same header structure as DefineFont3
    return parse_define_font3_name(tag_data)


def parse_define_font2_code_table(tag_data: bytes) -> Tuple[int, List[str]]:
    """Parse DefineFont2 (tag 48) → (charId, code_table).

    DefineFont2 code table has the same structure as DefineFont3, except
    codes may be UI8 (non-wide) or UI16 (wide) depending on WideCodes flag.
    """
    char_id = struct.unpack_from('<H', tag_data, 0)[0]
    flags = tag_data[2]
    wide_offsets = bool(flags & 0x08)
    wide_codes = bool(flags & 0x04)
    name_len = tag_data[4]
    offset = 5 + name_len
    num_glyphs = struct.unpack_from('<H', tag_data, offset)[0]
    offset += 2

    if num_glyphs == 0:
        return char_id, []

    # Jump past offset table + glyph shapes using code table offset
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
        if wide_codes:
            cp = struct.unpack_from('<H', tag_data, ct_start + i * 2)[0]
        else:
            cp = tag_data[ct_start + i]
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
    all_glyphs = []     # collected (char, advance) tuples

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
                all_glyphs.append((ct[glyph_idx], glyph_advance))
            else:
                all_glyphs.append(('?', glyph_advance))
        br.align()

        # Track the rightmost point reached by this text record
        record_end = current_x + total_advance
        if record_end > max_x:
            max_x = record_end

    # Convert bounds from twips to pixels, then normalize to origin (0,0)
    # so the N2D tool renders the text field at the character origin.
    # The offset is stored separately so it can be baked into placement matrices.
    font_size = current_height / 20.0 if current_height else 12.0

    # Post-process glyphs: detect inter-character spacing pattern where
    # space glyphs are inserted between every real character (common in
    # Flash-authored SWFs to achieve custom letter-spacing).
    # Uses a state machine: take each glyph as a real character, then
    # optionally consume the next glyph if it's a space (inter-char spacing).
    # This handles real word spaces naturally (they become real chars, and
    # the following non-space char just has no IC before it).
    text_str = ''
    letter_spacing_twips = 0
    if len(all_glyphs) >= 3:
        result_chars = []
        spacing_advances = []
        i = 0
        while i < len(all_glyphs):
            ch, adv = all_glyphs[i]
            result_chars.append(ch)
            i += 1
            # Check if next glyph is a spacing space
            if i < len(all_glyphs) and all_glyphs[i][0] in (' ', '\xa0'):
                spacing_advances.append(all_glyphs[i][1])
                i += 1
        # Confirm interleaved pattern: enough IC spaces relative to text length
        if (len(spacing_advances) >= 3
                and len(spacing_advances) >= (len(result_chars) - 1) * 0.7
                and len(result_chars) >= 3):
            text_str = ''.join(result_chars)
            letter_spacing_twips = sorted(spacing_advances)[len(spacing_advances) // 2]
    if not text_str:
        text_str = ''.join(ch for ch, adv in all_glyphs)

    letter_spacing_px = letter_spacing_twips / 20.0
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
    # Account for letter-spacing in width estimate
    if letter_spacing_px > 0 and len(text_str) > 1:
        char_estimate_w += letter_spacing_px * (len(text_str) - 1)
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
        'inputType': 'static',  # DefineText is always static glyph text
        'size': font_size,
        'align': 'left',
        'color': current_color,
        'leading': 0,
        'letterSpacing': letter_spacing_px,
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
        'html': False,
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
        # SWF ADPCM — decode to PCM and wrap in WAV
        try:
            pcm = _decode_swf_adpcm(sound_data, num_channels)
            if pcm:
                wav = _build_wav(pcm, sample_rate, 16, num_channels)
                return ('wav', wav, sound_rate_code)
        except Exception as e:
            log.warning("ADPCM decode failed: %s", e)
        return ('adpcm', sound_data, sound_rate_code)

    return ('unknown', b'', sound_rate_code)


# ── SWF ADPCM Decoder ──────────────────────────────────────────────────

# SWF ADPCM step table (IMA-style, 89 entries)
_ADPCM_STEP_TABLE = [
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34,
    37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143,
    157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494,
    544, 598, 658, 724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552,
    1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428,
    4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487,
    12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086,
    29794, 32767,
]

# Index adjustment table per nBits (2..5)
_ADPCM_INDEX_TABLES = {
    2: [-1, 2],
    3: [-1, -1, 2, 4],
    4: [-1, -1, -1, -1, 2, 4, 6, 8],
    5: [-1, -1, -1, -1, -1, -1, -1, -1, 1, 2, 4, 6, 8, 10, 13, 16],
}


def _decode_swf_adpcm(sound_data: bytes, num_channels: int) -> bytes:
    """Decode SWF ADPCM sound data to 16-bit signed PCM.

    SWF ADPCM format (per the SWF spec):
    - First 2 bits: AdpcmCodeSize (n_bits = value + 2, so 2..5 bits per sample)
    - Then for each 4096-sample block per channel:
        - Initial sample: SI16 (signed 16-bit)
        - Initial index: UB6 (6 bits)
        - Then (4096 - 1) ADPCM codes of n_bits each
    - Stereo interleaves left/right blocks.
    """
    if not sound_data:
        return b''

    br = BitReader(sound_data)
    n_bits = br.read_ub(2) + 2
    idx_table = _ADPCM_INDEX_TABLES[n_bits]

    samples_per_block = 4096
    output = io.BytesIO()

    try:
        while br.remaining > 0:
            # Read initial values for each channel
            predictors = []
            indices = []
            for _ch in range(num_channels):
                # Initial sample: 16-bit signed
                init_sample = br.read_sb(16)
                # Initial step index: 6 bits unsigned
                init_index = br.read_ub(6)
                init_index = max(0, min(init_index, 88))
                predictors.append(init_sample)
                indices.append(init_index)
                # Write the initial sample
                output.write(struct.pack('<h', max(-32768, min(32767, init_sample))))

            # Decode 4095 more samples per channel, interleaved
            for _s in range(1, samples_per_block):
                for ch in range(num_channels):
                    if br.remaining <= 0:
                        # Pad remaining with last known value if data ends early
                        output.write(struct.pack('<h', max(-32768, min(32767, predictors[ch]))))
                        continue

                    code = br.read_ub(n_bits)
                    step = _ADPCM_STEP_TABLE[indices[ch]]

                    # Compute difference
                    delta = 0
                    for bit in range(n_bits - 1):
                        if code & (1 << (n_bits - 2 - bit)):
                            delta += step >> bit
                    delta += step >> (n_bits - 1)

                    # Apply sign
                    if code & (1 << (n_bits - 1)):
                        predictors[ch] -= delta
                    else:
                        predictors[ch] += delta

                    # Clamp
                    predictors[ch] = max(-32768, min(32767, predictors[ch]))

                    # Update step index
                    indices[ch] += idx_table[code & ((1 << (n_bits - 1)) - 1)]
                    indices[ch] = max(0, min(88, indices[ch]))

                    output.write(struct.pack('<h', predictors[ch]))
    except (IndexError, struct.error):
        pass  # End of data — return what we have

    return output.getvalue()


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

    # Convert from twips to pixels — raw values before expansion
    raw_bounds = {
        'xMin': bounds_raw['xMin'] / 20.0,
        'xMax': bounds_raw['xMax'] / 20.0,
        'yMin': bounds_raw['yMin'] / 20.0,
        'yMax': bounds_raw['yMax'] / 20.0,
    }
    # Will be expanded after font_size is known (see below)
    bounds = dict(raw_bounds)

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
    html_text = ""
    if has_text:
        text = br.read_string()
        if html and text:
            html_text = text
            # Strip HTML tags for display, keep only visible text
            text = re.sub(r'<[^>]+>', '', text).strip()

    # Determine inputType
    if read_only:
        input_type = "static" if was_static else "dynamic"
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

    # --- Expand bounds for system-font rendering (same approach as DefineText) ---
    # Flash embeds tight glyph-metric bounds; system fonts in browsers are wider/
    # taller.  Expand so the text field is large enough for its content.
    bw = bounds['xMax'] - bounds['xMin']
    bh = bounds['yMax'] - bounds['yMin']

    # Width: at minimum fit the text at ~0.65 em per char, plus margins + padding
    if text:
        char_estimate_w = len(text) * font_size * 0.65
    else:
        char_estimate_w = 0
    padding_w = font_size * 0.5 + 8
    effective_w = max(bw, char_estimate_w) + padding_w + left_margin + right_margin

    # Height: at least font_size * 1.5 + 4 for line-height + descenders
    min_h = font_size * 1.5 + 4
    effective_h = max(bh, min_h)

    bounds = {
        'xMin': raw_bounds['xMin'],
        'xMax': raw_bounds['xMin'] + effective_w,
        'yMin': raw_bounds['yMin'],
        'yMax': raw_bounds['yMin'] + effective_h,
    }

    return {
        'text': text,
        'htmlText': html_text,
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
        'html': html,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  TIMELINE ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class FrameAction:
    """An action on a frame: place, move, or remove."""
    pass

class PlaceAction(FrameAction):
    def __init__(self, depth, char_id, matrix, color_transform, name,
                 clip_depth, blend_mode, is_move, ratio=None, filters=None):
        self.depth = depth
        self.char_id = char_id
        self.matrix = matrix
        self.color_transform = color_transform
        self.name = name
        self.clip_depth = clip_depth
        self.blend_mode = blend_mode
        self.is_move = is_move
        self.ratio = ratio
        self.filters = filters or []

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
                filters=po.get('filters', []),
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
                filters=po.get('filters', []),
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


# ─── Script normalization helpers ───────────────────────────────────────────

# Detects simple BitmapData / Sound linkage stubs.
_LINKAGE_EXTENDS_RE = re.compile(
    r'public\s+(?:dynamic\s+)?class\s+\w+\s+extends\s+(?:BitmapData|Sound)\b'
)

# Detects simple MovieClip symbol stubs generated from linkage.
_MOVIECLIP_EXTENDS_RE = re.compile(
    r'public\s+(?:dynamic\s+)?class\s+\w+\s+extends\s+MovieClip\b'
)

def _is_linkage_stub(source: str) -> bool:
    """Return True if *source* is a synthetic linkage stub.

    A stub is a class that extends BitmapData or Sound with only a
    constructor that calls super().  These are regenerated at compile
    time and must not be persisted as editable scripts.
    """
    if not _LINKAGE_EXTENDS_RE.search(source):
        return False
    # Strip comments then look for method bodies beyond the constructor
    stripped = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
    stripped = re.sub(r'//[^\n]*', '', stripped)
    # Remove known boilerplate patterns
    stripped = re.sub(r'package\s*\{[^}]*}', '', stripped)            # package
    stripped = re.sub(r'import\s+[\w.]+;', '', stripped)             # imports
    stripped = re.sub(r'public\s+(?:dynamic\s+)?class\s+\w+[^{]*\{', '', stripped)  # class decl
    stripped = re.sub(r'public\s+function\s+\w+\s*\([^)]*\)\s*\{', '', stripped)   # constructor
    stripped = re.sub(r'super\s*\([^)]*\)\s*;', '', stripped)        # super()
    stripped = re.sub(r'[{}]', '', stripped).strip()
    return not stripped


def _is_movieclip_symbol_stub(source: str) -> bool:
    """Return True if *source* is a synthetic MovieClip symbol stub.

    A synthetic MovieClip stub is constructor-only boilerplate that just calls
    ``super();`` and has no frame scripts, vars, or helper methods.
    """
    if not _MOVIECLIP_EXTENDS_RE.search(source):
        return False
    # Frame-script classes are handled separately; never classify them as stubs.
    if re.search(r'addFrameScript\s*\(', source):
        return False

    stripped = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
    stripped = re.sub(r'//[^\n]*', '', stripped)
    stripped = re.sub(r'package\s*\{', '', stripped)
    stripped = re.sub(r'import\s+[\w.]+;', '', stripped)
    stripped = re.sub(r'public\s+(?:dynamic\s+)?class\s+\w+\s+extends\s+MovieClip\s*\{', '', stripped)
    stripped = re.sub(r'public\s+function\s+\w+\s*\([^)]*\)\s*\{', '', stripped)
    stripped = re.sub(r'super\s*\(\s*\)\s*;', '', stripped)
    stripped = re.sub(r'[{}]', '', stripped).strip()
    return not stripped


def _extract_frame_methods_from_fla_class(source: str) -> Dict[int, str]:
    """Parse a MovieClip class source with addFrameScript().

        Returns a tuple:
      frame_bodies  — {1-based frame number: body string}
      var_decls     — list of raw ``var NAME:TYPE;`` declaration strings
                      (stripped of leading ``public ``/``private `` modifier)
      helper_funcs  — list of complete function source texts for methods
                      that are NOT frame-mapped (i.e. true helper methods)
            import_lines  — list of ``import ...;`` lines found in the class source

    Frame method names are discovered from addFrameScript() calls; the
    corresponding method bodies are then extracted by brace-matching.
    Class-level field declarations and helper functions are collected so
    callers can inject them into the target container's frame actions.
    """
    frame_bodies: Dict[int, str] = {}
    var_decls: List[str] = []
    helper_funcs: List[str] = []
    import_lines: List[str] = []

    # Capture class-level imports so typed declarations (e.g. Point) still
    # compile after frame extraction/injection.
    for m in re.finditer(r'^\s*import\s+[\w.]+\s*;', source, re.MULTILINE):
        imp = m.group(0).strip()
        if imp not in import_lines:
            import_lines.append(imp)

    # ── Step 1: discover frame method names from addFrameScript() ────────
    # Two formats handled:
    #   1. FLA decompiler multi-arg:  addFrameScript(0, this.frame1, 5, this.frame6, ...)
    #   2. Next2Flash re-export single-pair:  addFrameScript(0, frame_1);
    # re.DOTALL so the arg list can span multiple lines.
    all_arg_groups = re.findall(r'addFrameScript\s*\(([^)]+)\)', source, re.DOTALL)
    frame_method_names: Dict[int, str] = {}  # {1-based frame: method_name}
    for match_args in all_arg_groups:
        args = [a.strip() for a in match_args.split(',')]
        for i in range(0, len(args) - 1, 2):
            try:
                frame_0 = int(args[i])
                meth = args[i + 1].strip()
                if meth.startswith('this.'):
                    meth = meth[5:]
                frame_method_names[frame_0 + 1] = meth
            except (ValueError, IndexError):
                continue

    frame_meth_set = set(frame_method_names.values())

    # ── Step 2: extract ALL method bodies by brace-matching ─────────────
    # Pattern matches: [access] function NAME(...) [: ReturnType] {
    func_pat = re.compile(
        r'(?:internal\s+|public\s+|private\s+|protected\s+)?'
        r'function\s+(\w+)\s*\([^)]*\)\s*(?::\s*[\w.*]+\s*)?\{',
        re.DOTALL,
    )
    # Skip the constructor (same name as class, detected by having addFrameScript inside)
    constructor_names: set = set()
    for m in re.finditer(r'public\s+function\s+(\w+)\s*\([^)]*\)', source):
        # Heuristic: constructor has no return type annotation and shares name with class
        # We use a simple fallback: if the body contains addFrameScript it's the ctor
        pass  # handled below by checking for addFrameScript in body

    for mm in func_pat.finditer(source):
        meth_name = mm.group(1)
        start = mm.end()
        depth = 1
        pos = start
        while pos < len(source) and depth > 0:
            if source[pos] == '{':
                depth += 1
            elif source[pos] == '}':
                depth -= 1
            pos += 1
        body = source[start:pos - 1]

        if meth_name in frame_meth_set:
            # This is a frame action method
            for fnum, fname in frame_method_names.items():
                if fname == meth_name:
                        # Store even empty bodies — an empty frame action is intentional
                        # (e.g. a timeline stop() that the decompiler omitted)
                        frame_bodies[fnum] = body.strip()
        else:
            # Skip constructors (bodies that contain addFrameScript calls)
            if 'addFrameScript' in body:
                continue
            # Helper function — capture the full text including signature
            full_text = source[mm.start():pos].strip()
            helper_funcs.append(full_text)

    # ── Step 3: extract class-level field declarations ───────────────────
    # Collect vars only at class scope depth (inside class body, outside any
    # method body). This prevents local frame-method vars from being promoted
    # into class fields, which causes duplicate-definition compile errors.
    class_decl = re.search(r'\bclass\s+\w+\b[^\{]*\{', source)
    if class_decl:
        class_start = class_decl.end() - 1  # points at the '{' of class body
        depth = 1
        i = class_start + 1
        while i < len(source) and depth > 0:
            ch = source[i]
            if ch == '{':
                depth += 1
                i += 1
                continue
            if ch == '}':
                depth -= 1
                i += 1
                continue

            if depth == 1:
                # Read one physical line at class scope.
                line_end = source.find('\n', i)
                if line_end == -1:
                    line_end = len(source)
                line = source[i:line_end].strip()

                vm = re.match(
                    r'^(?:public\s+|private\s+|protected\s+|internal\s+)?var\s+(.+;)$',
                    line,
                )
                if vm:
                    decl = 'var ' + vm.group(1).strip()
                    if decl not in var_decls:
                        var_decls.append(decl)

                i = line_end + 1
                continue

            i += 1

    return frame_bodies, var_decls, helper_funcs, import_lines


def normalize_imported_scripts(scripts: List[dict], libs: List[dict]) -> List[dict]:
    """Normalize decompiled AS3 scripts after import.

    Three categories are identified and handled:

    1. ``linkage-generated`` — Simple BitmapData/Sound stubs.  Dropped; they
       are regenerated at compile time from current library metadata.

    2. ``frame`` — ``*_fla`` package frame-aggregate classes.  Frame bodies
       are extracted and injected into the matching container lib's
       ``actions`` list.  The script is marked ``scriptOrigin: 'frame'`` so it
       will be excluded from compilation; it persists in the N2D for reference.

    3. ``class-source`` — All remaining scripts.  Kept and marked for
       compilation from source.

    Returns the list of normalized scripts (linkage stubs removed; frame and
    class-source scripts marked with ``scriptOrigin`` field).
    """
    # Optional fidelity mode: preserve imported script text exactly.
    # Default behavior remains legacy normalization (stub/frame extraction).
    # Set N2F_PRESERVE_IMPORTED_SCRIPTS=1 to bypass normalization.
    if os.getenv('N2F_PRESERVE_IMPORTED_SCRIPTS', '').strip().lower() in ('1', 'true', 'yes', 'on'):
        preserved: List[dict] = []
        for script in scripts:
            src = script.get('source', '')
            if _is_linkage_stub(src):
                script['scriptOrigin'] = 'linkage-generated'
            else:
                script['scriptOrigin'] = 'class-source'
            preserved.append(script)
        log.info(
            'normalize_imported_scripts: preserve mode active (preserved %d scripts, normalization bypassed)',
            len(preserved),
        )
        print(f"  Script normalization: preserve mode kept {len(preserved)} scripts")
        return preserved

    log.info('normalize_imported_scripts: starting with %d scripts', len(scripts))
    
    # index containers by swfCharId AND by symbol for _fla class matching.
    # _fla class filenames use the FLA internal timeline index, NOT the SWF charId.
    # The actual container has symbol == "<pkg>.<ClassName>" (e.g. "bowser_fla.FTilt_25").
    # Symbol matching is therefore the primary strategy; charId is a fast-path fallback.
    swf_cid_to_lib: Dict[int, dict] = {}
    symbol_to_lib: Dict[str, dict] = {}
    for lib in libs:
        if lib.get('type') == 'container':
            cid = lib.get('swfCharId')
            if cid is not None:
                swf_cid_to_lib[cid] = lib
            sym = lib.get('symbol', '')
            if sym:
                symbol_to_lib[sym] = lib

    kept: List[dict] = []
    n_linkage = n_frame = 0

    for idx, script in enumerate(scripts):
        source = script.get('source', '')
        path = script.get('path', '')
        parts = path.rsplit('/', 1)
        pkg_dir = parts[0] if len(parts) == 2 else ''
        class_filename = parts[-1].replace('.as', '')

        # Precompute symbol candidates for matching scripts to library containers.
        symbol_candidates: List[str] = []
        if pkg_dir:
            symbol_candidates.append(pkg_dir.replace('/', '.') + '.' + class_filename)
        symbol_candidates.append(class_filename)

        # ── 1. Linkage stub ───────────────────────────────────────────
        if _is_linkage_stub(source):
            n_linkage += 1
            log.debug('  [%d] LINKAGE STUB: %s', idx, path)
            continue  # discard — regenerated at export

        # ── 1b. MovieClip symbol stub ─────────────────────────────────
        # Drop constructor-only MovieClip stubs when they map to a real
        # container symbol. These are export-generated and should not appear
        # in Source Scripts.
        if _is_movieclip_symbol_stub(source):
            matched_container = None
            for cand in symbol_candidates:
                matched_container = symbol_to_lib.get(cand)
                if matched_container is not None:
                    break
            if matched_container is not None:
                n_linkage += 1
                log.debug('  [%d] MOVIECLIP STUB: %s -> container %d', idx, path, matched_container.get('id'))
                continue

        # ── 2. Frame aggregate / timeline class ───────────────────────
        # Handle both classic *_fla classes and package-less MovieClip classes
        # that define timeline actions via addFrameScript().
        has_add_frame_script = bool(re.search(r'addFrameScript\s*\(', source))
        is_movieclip_class = bool(re.search(r'class\s+\w+\s+extends\s+MovieClip\b', source))
        is_frame_candidate = pkg_dir.endswith('_fla') or (has_add_frame_script and is_movieclip_class)

        if is_frame_candidate:
            # Candidate symbol names (best to worst):
            # 1) package path + filename class (e.g. bowser_fla.FTilt_25)
            # 2) filename class only (e.g. blackmage_dash_attack)
            # 3) parsed class name from source (if different from file)
            symbol_candidates = []
            if pkg_dir:
                symbol_candidates.append(pkg_dir.replace('/', '.') + '.' + class_filename)
            symbol_candidates.append(class_filename)

            class_decl = re.search(r'class\s+(\w+)\s+extends\s+MovieClip\b', source)
            if class_decl:
                declared_class = class_decl.group(1)
                if pkg_dir:
                    symbol_candidates.append(pkg_dir.replace('/', '.') + '.' + declared_class)
                symbol_candidates.append(declared_class)

            target_lib = None
            for cand in symbol_candidates:
                target_lib = symbol_to_lib.get(cand)
                if target_lib is not None:
                    break

            # Secondary fallback for some *_fla files where trailing number
            # can still coincide with SWF charId.
            if target_lib is None and pkg_dir.endswith('_fla'):
                num_match = re.search(r'_(\d+)$', class_filename)
                if num_match:
                    target_lib = swf_cid_to_lib.get(int(num_match.group(1)))

            if target_lib is not None:
                frame_bodies, var_decls, helper_funcs, import_lines = _extract_frame_methods_from_fla_class(source)
                if frame_bodies or var_decls or helper_funcs or import_lines:
                    # Build a preamble of class-level vars and helper functions.
                    # These get prepended to frame 1's body so that compile_n2d.py's
                    # _extract_toplevel_vars / _extract_toplevel_functions lifts them
                    # into the generated class.
                    preamble_parts = []
                    for imp in import_lines:
                        preamble_parts.append(imp)
                    for vd in var_decls:
                        preamble_parts.append(vd)
                    for hf in helper_funcs:
                        preamble_parts.append(hf)
                    preamble = '\n'.join(preamble_parts)

                    existing = {a['frame']: a for a in target_lib.get('actions', [])}
                    for fnum, body in frame_bodies.items():
                        if fnum not in existing:
                            inject_body = body
                            # Inject preamble into first frame only
                            if preamble and fnum == min(frame_bodies.keys()):
                                inject_body = preamble + '\n' + body
                            target_lib.setdefault('actions', []).append(
                                {'frame': fnum, 'action': inject_body}
                            )
                    # If there's a preamble but no frame bodies — inject into a new frame 1
                    if preamble and not frame_bodies and 1 not in existing:
                        target_lib.setdefault('actions', []).append(
                            {'frame': 1, 'action': preamble}
                        )
                    target_lib['actions'] = sorted(
                        target_lib.get('actions', []), key=lambda a: a['frame']
                    )
                n_frame += 1
                log.debug('  [%d] FRAME AGGREGATE: %s -> container %d', idx, path, target_lib.get('id'))
            else:
                if pkg_dir.endswith('_fla'):
                    log.debug('  [%d] FRAME AGGREGATE (no container match, dropping): %s', idx, path)
                else:
                    # Non-_fla classes can be real class-source code. If we couldn't
                    # map them to a container symbol, keep them as class-source.
                    script['scriptOrigin'] = 'class-source'
                    kept.append(script)
                    log.debug('  [%d] CLASS-SOURCE (unmapped addFrameScript class): %s', idx, path)
                    continue

            # Frame aggregate scripts are always dropped from the script list.
            # Their content has been injected into the container's lib.actions;
            # keeping them as external scripts would make them appear twice in
            # the UI (once in Source Scripts, once in the frame panels).
            continue

        # ── 3. Class-source ───────────────────────────────────────────
        script['scriptOrigin'] = 'class-source'
        kept.append(script)
        log.debug('  [%d] CLASS-SOURCE: %s', idx, path)

    log.info(
        'normalize_imported_scripts: %d linkage stubs dropped, %d frame aggregates injected, %d scripts kept',
        n_linkage, n_frame, len(kept),
    )
    print(f"  Script normalization: {n_linkage} linkage stubs dropped, "
          f"{n_frame} frame aggregates -> timeline, {len(kept)} scripts kept")
    return kept


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
        # Ordered list of class names from original SymbolClass (preserves entry order)
        self.symbol_class_order: List[str] = []
        # Shape bounds from SWF
        self.shape_bounds: Dict[int, dict] = {}
        # DefineScalingGrid: swf_char_id → {x, y, w, h} in pixels
        self.scaling_grids: Dict[int, dict] = {}
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
        # ── Structured parsed global tags (replaces raw passthrough) ──
        self.parsed_abc_blocks: List[dict] = []       # DoABC / DoABC2
        self.parsed_protect: Optional[bool] = None     # Protect (tag 24)
        self.parsed_metadata: Optional[str] = None     # Metadata XML (tag 77)
        self.parsed_scene_labels: Optional[dict] = None  # SceneAndFrameLabel (tag 86)
        self.parsed_sound_stream: Optional[dict] = None  # SoundStreamHead2 (tag 45) global
        self.parsed_import_assets: List[dict] = []     # ImportAssets / ImportAssets2
        self.parsed_bg_color: Optional[str] = None     # SetBackgroundColor (tag 9) as "#rrggbb"
        self.parsed_file_attributes: int = 0           # FileAttributes (tag 69) raw flags
        # Font aux: swf_char_id → {fontAlignZones, csmTextSettings, fontNameRecord}
        self.parsed_font_aux: Dict[int, dict] = {}
        # AS3 source scripts: [{name, path, source}]
        self.scripts: List[dict] = []
        # Bitmap RGBA buffers: n2d_lib_id → raw RGBA bytes (for ZIP packaging)
        self.bitmap_buffers: Dict[int, bytes] = {}
        # JPEGTables (tag 8) — shared JPEG header for DefineBits (tag 6)
        self.jpeg_table: Optional[bytes] = None
        # Button auxiliary tags: swf_char_id → [(tag_type, full_tag_data)]
        self.button_aux_tags: Dict[int, List[Tuple[int, bytes]]] = {}
        # ImportAssets tags: [(tag_type, full_tag_data)] for passthrough
        self.import_asset_tags: List[Tuple[int, bytes]] = []

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
            TAG_DEFINE_FONT3, TAG_DEFINE_BUTTON2, TAG_DEFINE_FONT2,
            TAG_DEFINE_BINARY_DATA,
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
                # For DefineBits (tag 6), merge shared JPEGTables header to
                # make the data standalone, then store as DefineBitsJPEG2.
                if tag.tag_type == TAG_DEFINE_BITS and self.jpeg_table is not None:
                    merged = _merge_jpeg_tables(self.jpeg_table, tag.data[2:])
                    self.raw_tag_data[char_id] = (TAG_DEFINE_BITS_JPEG2, merged)
                else:
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

            elif tag.tag_type == TAG_DEFINE_BUTTON2:
                char_id = struct.unpack_from('<H', tag.data, 0)[0]
                self.char_types[char_id] = 'button'
                # Store raw tag body for 1:1 roundtrip
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type == TAG_JPEG_TABLES:
                # Tag 8: shared JPEG header used by DefineBits (tag 6)
                self.jpeg_table = bytes(tag.data)

            elif tag.tag_type == TAG_DEFINE_FONT2:
                # Tag 48: DefineFont2 — parse like DefineFont3 (subset)
                char_id = struct.unpack_from('<H', tag.data, 0)[0]
                self.char_types[char_id] = 'font'
                self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])
                try:
                    _, fname, fbold, fitalic = parse_define_font2_name(tag.data)
                    self.font_names[char_id] = fname
                    self.font_attrs[char_id] = (fbold, fitalic)
                except Exception:
                    pass
                try:
                    _, code_table = parse_define_font2_code_table(tag.data)
                    if code_table:
                        self.font_code_tables[char_id] = code_table
                except Exception:
                    pass

            elif tag.tag_type == TAG_DEFINE_BINARY_DATA:
                # Tag 87: DefineBinaryData — store as raw passthrough
                if len(tag.data) >= 2:
                    char_id = struct.unpack_from('<H', tag.data, 0)[0]
                    self.char_types[char_id] = 'binaryData'
                    self.raw_tag_data[char_id] = (tag.tag_type, tag.data[2:])

            elif tag.tag_type in (TAG_IMPORT_ASSETS, TAG_IMPORT_ASSETS2):
                # Tags 57/71: ImportAssets — store for passthrough
                self.import_asset_tags.append((tag.tag_type, bytes(tag.data)))

            elif tag.tag_type in (TAG_DEFINE_BUTTON_SOUND,
                                  TAG_DEFINE_BUTTON_CXFORM):
                # Tags 17/23: button auxiliary — store keyed by button charID
                if len(tag.data) >= 2:
                    btn_char_id = struct.unpack_from('<H', tag.data, 0)[0]
                    self.button_aux_tags.setdefault(btn_char_id, []).append(
                        (tag.tag_type, bytes(tag.data)))

            elif tag.tag_type == TAG_SYMBOL_CLASS:
                sc = parse_symbol_class(tag.data)
                self.symbol_names.update(sc)
                # Preserve original entry order (list of class names)
                self.symbol_class_order = list(sc.values())
                past_symbol_class = True

            elif tag.tag_type == TAG_DEFINE_SCALING_GRID:
                # DefineScalingGrid: UI16 charId + RECT (9-slice grid)
                if len(tag.data) >= 4:
                    char_id = struct.unpack_from('<H', tag.data, 0)[0]
                    br = BitReader(tag.data, 2)
                    rect = read_rect(br)
                    # Convert from twips RECT {xMin,xMax,yMin,yMax} to
                    # editor grid format {x,y,w,h} in pixels
                    x = rect['xMin'] / 20.0
                    y = rect['yMin'] / 20.0
                    w = (rect['xMax'] - rect['xMin']) / 20.0
                    h = (rect['yMax'] - rect['yMin']) / 20.0
                    self.scaling_grids[char_id] = {
                        'x': x, 'y': y, 'w': w, 'h': h
                    }

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
                                76,   # SymbolClass
                                TAG_IMPORT_ASSETS,    # ImportAssets
                                TAG_IMPORT_ASSETS2):  # ImportAssets2
                self.global_raw_tags.append((tag.tag_type, bytes(tag.data)))

            # ── Structured parsing of global tags (replaces raw passthrough) ──
            if tag.tag_type == 24:  # Protect
                self.parsed_protect = True

            elif tag.tag_type == 9 and len(tag.data) >= 3:  # SetBackgroundColor
                r, g, b = tag.data[0], tag.data[1], tag.data[2]
                self.parsed_bg_color = f"#{r:02x}{g:02x}{b:02x}"

            elif tag.tag_type == 69 and len(tag.data) >= 4:  # FileAttributes
                self.parsed_file_attributes = struct.unpack_from('<I', tag.data, 0)[0]

            elif tag.tag_type == 77:  # Metadata
                try:
                    self.parsed_metadata = tag.data.decode('utf-8').rstrip('\x00')
                except Exception:
                    self.parsed_metadata = tag.data.decode('latin-1').rstrip('\x00')

            elif tag.tag_type == 86:  # DefineSceneAndFrameLabelData
                self.parsed_scene_labels = self._parse_scene_and_frame_label(bytes(tag.data))

            elif tag.tag_type == 45 and self.parsed_sound_stream is None:  # SoundStreamHead2 (global)
                self.parsed_sound_stream = self._parse_sound_stream_head(bytes(tag.data))

            elif tag.tag_type in (TAG_DO_ABC, TAG_DO_ABC2):
                self.parsed_abc_blocks.append(
                    self._parse_doabc(tag.tag_type, bytes(tag.data)))

            elif tag.tag_type in (TAG_IMPORT_ASSETS, TAG_IMPORT_ASSETS2):
                self.parsed_import_assets.append(
                    self._parse_import_assets(tag.tag_type, bytes(tag.data)))

            elif tag.tag_type in (73, 74, 88):  # Font aux tags
                body = bytes(tag.data)
                if len(body) >= 2:
                    ref_cid = struct.unpack_from('<H', body, 0)[0]
                    aux = self.parsed_font_aux.setdefault(ref_cid, {})
                    if tag.tag_type == 73:
                        aux['fontAlignZones'] = self._parse_font_align_zones(body)
                    elif tag.tag_type == 74:
                        aux['csmTextSettings'] = self._parse_csm_text_settings(body)
                    elif tag.tag_type == 88:
                        aux['fontNameRecord'] = self._parse_font_name(body)

    # ── Structured tag parsing helpers ──────────────────────────────────

    @staticmethod
    def _parse_sound_stream_head(data: bytes) -> dict:
        """Parse SoundStreamHead / SoundStreamHead2 into structured fields."""
        if len(data) < 4:
            return {}
        b0 = data[0]
        b1 = data[1]
        result = {
            'playbackRate': (b0 >> 2) & 0x03,
            'playbackSize': (b0 >> 1) & 0x01,
            'playbackType': b0 & 0x01,
            'compression': (b1 >> 4) & 0x0f,
            'streamRate': (b1 >> 2) & 0x03,
            'streamSize': (b1 >> 1) & 0x01,
            'streamType': b1 & 0x01,
            'streamSampleCount': struct.unpack_from('<H', data, 2)[0],
        }
        if result['compression'] == 2 and len(data) >= 6:  # MP3
            result['latencySeek'] = struct.unpack_from('<h', data, 4)[0]
        return result

    @staticmethod
    def _parse_scene_and_frame_label(data: bytes) -> dict:
        """Parse DefineSceneAndFrameLabelData (tag 86)."""
        off = 0
        result = {'scenes': [], 'frameLabels': []}
        if not data:
            return result
        # EncodedU32 scene count
        scene_count, off = _read_encoded_u32(data, off)
        for _ in range(scene_count):
            offset_val, off = _read_encoded_u32(data, off)
            name, off = _read_cstring(data, off)
            result['scenes'].append({'offset': offset_val, 'name': name})
        # EncodedU32 frame label count
        label_count, off = _read_encoded_u32(data, off)
        for _ in range(label_count):
            frame_num, off = _read_encoded_u32(data, off)
            name, off = _read_cstring(data, off)
            result['frameLabels'].append({'frame': frame_num, 'name': name})
        return result

    @staticmethod
    def _parse_doabc(tag_type: int, data: bytes) -> dict:
        """Parse DoABC (72) or DoABC2 (82) tag wrapper."""
        if tag_type == 82:  # DoABC2: flags(UI32) + name(NUL-terminated) + abc
            if len(data) < 5:
                return {'tagVersion': 2, 'flags': 0, 'name': '', 'bytecode': base64.b64encode(data).decode('ascii')}
            flags = struct.unpack_from('<I', data, 0)[0]
            nul_pos = data.index(0, 4) if 0 in data[4:] else len(data)
            name = data[4:nul_pos].decode('utf-8', errors='replace')
            abc_bytes = data[nul_pos + 1:]
            return {
                'tagVersion': 2,
                'flags': flags,
                'name': name,
                'bytecode': base64.b64encode(abc_bytes).decode('ascii'),
            }
        else:  # DoABC (72): raw ABC bytecode only
            return {
                'tagVersion': 1,
                'flags': 0,
                'name': '',
                'bytecode': base64.b64encode(data).decode('ascii'),
            }

    @staticmethod
    def _parse_import_assets(tag_type: int, data: bytes) -> dict:
        """Parse ImportAssets (57) or ImportAssets2 (71)."""
        off = 0
        url, off = _read_cstring(data, off)
        version = 2 if tag_type == 71 else 1
        if tag_type == 71 and off + 2 <= len(data):
            off += 2  # skip reserved UI8 + UI8
        count = struct.unpack_from('<H', data, off)[0] if off + 2 <= len(data) else 0
        off += 2
        assets = []
        for _ in range(count):
            if off + 2 > len(data):
                break
            _char_id = struct.unpack_from('<H', data, off)[0]
            off += 2
            name, off = _read_cstring(data, off)
            assets.append({'name': name})
        return {'version': version, 'url': url, 'assets': assets}

    @staticmethod
    def _parse_font_align_zones(data: bytes) -> dict:
        """Parse DefineFontAlignZones (tag 73) body (includes charID prefix)."""
        if len(data) < 3:
            return {'tableHint': 0, 'zones': []}
        off = 2  # skip charID
        table_hint = (data[off] >> 6) & 0x03
        off += 1
        zones = []
        while off < len(data):
            num_zones = data[off]; off += 1
            zone_data = []
            for _ in range(num_zones):
                if off + 4 > len(data):
                    break
                zd = struct.unpack_from('<HH', data, off)
                zone_data.append({'alignmentCoord': zd[0] / 256.0, 'range': zd[1] / 256.0})
                off += 4
            if off < len(data):
                off += 1  # zoneMask byte
            zones.append(zone_data)
        return {'tableHint': table_hint, 'zones': zones}

    @staticmethod
    def _parse_csm_text_settings(data: bytes) -> dict:
        """Parse CSMTextSettings (tag 74) body (includes charID prefix)."""
        if len(data) < 12:
            return {'useFlashType': 0, 'gridFit': 0, 'thickness': 0.0, 'sharpness': 0.0}
        off = 2  # skip charID
        byte3 = data[off]
        use_flash = (byte3 >> 6) & 0x03
        grid_fit = (byte3 >> 3) & 0x07
        off += 1
        thickness = struct.unpack_from('<f', data, off)[0] if off + 4 <= len(data) else 0.0
        off += 4
        sharpness = struct.unpack_from('<f', data, off)[0] if off + 4 <= len(data) else 0.0
        return {'useFlashType': use_flash, 'gridFit': grid_fit,
                'thickness': thickness, 'sharpness': sharpness}

    @staticmethod
    def _parse_font_name(data: bytes) -> dict:
        """Parse DefineFontName (tag 88) body (includes charID prefix)."""
        off = 2  # skip charID
        font_name, off = _read_cstring(data, off)
        copyright_str, off = _read_cstring(data, off)
        return {'fontName': font_name, 'copyright': copyright_str}

    @staticmethod
    def _parse_button2(data_after_cid: bytes) -> dict:
        """Parse DefineButton2 tag body (after charID) into structured fields."""
        if len(data_after_cid) < 3:
            return {'trackAsMenu': False, 'buttonStates': {}, 'buttonActions': []}
        off = 0
        flags = data_after_cid[off]; off += 1
        track_as_menu = bool(flags & 0x01)
        action_offset = struct.unpack_from('<H', data_after_cid, off)[0]; off += 2

        states = {'up': [], 'over': [], 'down': [], 'hit': []}
        while off < len(data_after_cid):
            state_flags = data_after_cid[off]
            if state_flags == 0:
                off += 1
                break
            has_blend = bool(state_flags & 0x20)
            has_filter = bool(state_flags & 0x10)
            off += 1
            if off + 4 > len(data_after_cid):
                break
            char_id = struct.unpack_from('<H', data_after_cid, off)[0]; off += 2
            depth = struct.unpack_from('<H', data_after_cid, off)[0]; off += 2

            # Parse MATRIX
            matrix, off = _read_swf_matrix(data_after_cid, off)
            # Parse CXFORMWITHALPHA
            cxform, off = _read_swf_cxform_alpha(data_after_cid, off)
            # FilterList
            filters = []
            if has_filter:
                _br_f = BitReader(data_after_cid, off)
                filters = [f for f in read_filter_list(_br_f) if f is not None]
                off = _br_f.byte_pos
            blend_mode = 0
            if has_blend and off < len(data_after_cid):
                blend_mode = data_after_cid[off]; off += 1

            record = {
                'characterId': char_id,
                'placeDepth': depth,
                'matrix': matrix,
                'colorTransform': cxform,
                'filters': filters,
                'blendMode': blend_mode,
            }
            if state_flags & 0x01:
                states['up'].append(record)
            if state_flags & 0x02:
                states['over'].append(record)
            if state_flags & 0x04:
                states['down'].append(record)
            if state_flags & 0x08:
                states['hit'].append(record)

        # Parse ButtonCondActions if present
        button_actions = []
        if action_offset > 0:
            act_off = action_offset  # relative to start of data_after_cid
            while act_off < len(data_after_cid):
                if act_off + 4 > len(data_after_cid):
                    break
                cond_action_size = struct.unpack_from('<H', data_after_cid, act_off)[0]
                cond_flags = struct.unpack_from('<H', data_after_cid, act_off + 2)[0]
                if cond_action_size == 0:
                    # Last action — rest of data
                    action_bytes = data_after_cid[act_off + 4:]
                    button_actions.append({
                        'conditions': cond_flags,
                        'actionBytes': base64.b64encode(action_bytes).decode('ascii'),
                    })
                    break
                else:
                    action_bytes = data_after_cid[act_off + 4:act_off + cond_action_size]
                    button_actions.append({
                        'conditions': cond_flags,
                        'actionBytes': base64.b64encode(action_bytes).decode('ascii'),
                    })
                    act_off += cond_action_size

        return {
            'trackAsMenu': track_as_menu,
            'buttonStates': states,
            'buttonActions': button_actions,
        }

    def build_all(self, *, fast_shapes: bool = False):
        """Build all library entries from cataloged SWF data.
        
        fast_shapes: if True, skip shape binary parsing (use gray rect placeholders).
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
            ('Buttons',     'button'),
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

        # Collect bitmap cids for parallel decode
        bitmap_cids = [cid for cid in all_char_ids if self.char_types[cid] == 'bitmap']

        def _decode_one_bitmap(cid):
            """Decode a single bitmap's RGBA — safe for ThreadPoolExecutor."""
            width, height = self.bitmap_dims.get(cid, (0, 0))
            buffer_str = ''
            rgba = b''
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
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
                    buffer_str = 'b64:' + base64.b64encode(rgba).decode('ascii')
            return cid, width, height, buffer_str

        # Parallel bitmap decode (zlib decompress + pixel conversion are CPU-bound
        # but release the GIL, so threads help)
        from concurrent.futures import ThreadPoolExecutor
        decoded_bitmaps = {}
        with ThreadPoolExecutor(max_workers=min(8, max(1, len(bitmap_cids)))) as executor:
            for cid, w, h, buf_str in executor.map(_decode_one_bitmap, bitmap_cids):
                decoded_bitmaps[cid] = (w, h, buf_str)

        for cid in bitmap_cids:
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Bitmap_{cid}"

            width, height, buffer_str = decoded_bitmaps[cid]
            if buffer_str:
                decode_ok += 1

            # Preserve original bitmap tag type and format for lossless re-encoding
            raw_tag_type = 36  # default: DefineBitsLossless2
            raw_bitmap_format = 5  # default: 32-bit ARGB
            if cid in self.raw_tag_data:
                raw_tag_type = self.raw_tag_data[cid][0]
                tag_body = self.raw_tag_data[cid][1]
                # Preserve the LL2 format byte (3=indexed, 5=ARGB) so that
                # re-encoding uses the same format as the original.  Converting
                # between formats (e.g. fmt5→fmt3) can trigger Flash Player
                # Error #2015 even though pixel data is identical.
                if raw_tag_type in (TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2) and len(tag_body) >= 1:
                    raw_bitmap_format = tag_body[0]

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
                'rawTagType': raw_tag_type,
                'rawBitmapFormat': raw_bitmap_format,
            }
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

            # Preserve original tag type for correct re-encoding
            shape_tag_type = 32  # default: DefineShape3
            if cid in self.raw_tag_data:
                shape_tag_type = self.raw_tag_data[cid][0]

            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'shape',
                'symbol': sym_name,
                'folderId': self.folder_ids.get('shape', 0),
                'bitmapId': 0,
                'grid': self.scaling_grids.get(cid),
                'inBitmap': has_bitmap_fill,
                'recodes': recodes,
                'bounds': bounds,
                'rawTagType': shape_tag_type,
            }
            self.libraries.append(entry)
            shape_count += 1

        step(f"Built {shape_count} shape entries ({shape_parsed} parsed from SWF binary)")

        # Phase 2b: Bitmap RGBA decode in shape recodes skipped for speed.
        # Shape recodes keep integer bitmap IDs (tool shows blank fills).
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
            morph_tag_type = 46  # default DefineMorphShape
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                morph_tag_type = tag_type
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
                'rawTagType': morph_tag_type,
                'symbol': sym_name,
                'folderId': self.folder_ids.get('morphShape', 0),
                'bitmapId': 0,
                'grid': self.scaling_grids.get(cid),
                'inBitmap': has_bitmap_fill,
                'recodes': recodes,
                'bounds': bounds,
                'endRecodes': end_recodes,
                'endBounds': end_bounds,
            }
            self.libraries.append(entry)
            morph_count += 1

        step(f"Built {morph_count} morph shape entries ({morph_parsed} parsed start-state)")

        # Phase 4: Build sound entries
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

            buffer_data = b''
            sound_fmt = 'unknown'
            if cid in sound_data_cache:
                fmt_name, audio_bytes, swf_rate = sound_data_cache[cid]
                sound_fmt = fmt_name
                # Use parallel-converted MP3 if available (Nellymoser → MP3)
                if cid in nelly_results:
                    audio_bytes = nelly_results[cid]
                    sound_fmt = 'mp3'
                if audio_bytes:
                    buffer_data = audio_bytes if isinstance(audio_bytes, (bytes, bytearray)) else bytes(audio_bytes)

            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'sound',
                'symbol': sym_name,
                'folderId': self.folder_ids.get('sound', 0),
                'buffer': buffer_data,
                'soundFormat': sound_fmt,
                'volume': 100,
                'loopCount': 0,
            }
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
                        # rawTagBody intentionally NOT stored — _emit_text always
                        # rebuilds from structured fields as DefineEditText.
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
            else:
                # Fallback: store as text with defaults
                entry = {
                    'id': lid,
                    'swfCharId': cid,
                    'name': display_name,
                    'type': 'text',
                    'symbol': sym_name,
                    'folderId': self.folder_ids.get('text', 0),
                    'text': '',
                    'font': 'Arial',
                    'size': 12,
                    'color': 0,
                    'bounds': {'xMin': 0, 'xMax': 200, 'yMin': 0, 'yMax': 30},
                }

            self.libraries.append(entry)
            text_count += 1

        step(f"Built {text_count} text entries ({text_parsed} parsed as editable)")

        # Phase 6: Build font entries — store as shapes for tool compatibility
        # The Next2D tool has no "font" library type; fonts are stored as
        # shapes with fontData field so compile_n2d.py can emit DefineFont3 tags.
        # fontAuxTags (auxiliary tags like DefineFontAlignZones, CSMTextSettings,
        # DefineFontName) are stored directly on the font entry.
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
            face_name = self.font_names.get(cid, display_name)
            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'shape',
                'isFont': True,
                'fontFaceName': face_name,
                'symbol': sym_name,
                'folderId': self.folder_ids.get('font', 0),
                'bitmapId': 0,
                'grid': self.scaling_grids.get(cid),
                'inBitmap': False,
                'recodes': [],
                'bounds': {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20},
            }
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                # Store font body as fontData for compilation
                entry['fontData'] = base64.b64encode(body).decode('ascii')
                entry['fontTagType'] = tag_type
            # Attach font auxiliary tags as structured fields only
            if cid in self.parsed_font_aux:
                entry['fontAuxParsed'] = self.parsed_font_aux[cid]
            self.libraries.append(entry)
            font_count += 1

        step(f"Built {font_count} font entries")

        # Phase 7a: Build button entries (DefineButton2) — editable 4-frame containers
        button_count = 0
        for cid in all_char_ids:
            if self.char_types[cid] != 'button':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"Button_{cid}"
            bounds = self._compute_button_bounds(cid)

            # Parse button data into structured form
            button_parsed = {}
            button_data_b64 = None
            if cid in self.raw_tag_data:
                _, body = self.raw_tag_data[cid]
                button_data_b64 = base64.b64encode(body).decode('ascii')
                try:
                    button_parsed = self._parse_button2(body)
                except Exception as e:
                    log.warning("Could not parse button %d: %s", cid, e)

            # Store as editable container (4 frames: up/over/down/hit)
            entry = self._button_as_container(
                lid, cid, display_name, sym_name, bounds, button_parsed)
            # Persist button actions (ActionScript) separately — editor won't touch them
            entry['buttonActions'] = button_parsed.get('buttonActions', [])
            self.libraries.append(entry)
            button_count += 1

        if button_count:
            step(f"Built {button_count} button entries (editable containers)")

        # Phase 7a.5: Build binary data entries (DefineBinaryData, tag 87)
        bindata_count = 0
        for cid in all_char_ids:
            if self.char_types[cid] != 'binaryData':
                continue
            lid = self.swf_to_n2d[cid]
            sym_name = self.symbol_names.get(cid, '')
            display_name = sym_name.split('.')[-1] if sym_name else f"BinaryData_{cid}"
            entry = {
                'id': lid,
                'swfCharId': cid,
                'name': display_name,
                'type': 'shape',
                'isBinaryData': True,
                'symbol': sym_name,
                'folderId': self.folder_ids.get('binaryData', 0),
                'bitmapId': 0,
                'grid': None,
                'inBitmap': False,
                'recodes': [],
                'bounds': {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20},
            }
            if cid in self.raw_tag_data:
                tag_type, body = self.raw_tag_data[cid]
                entry['binaryDataBody'] = base64.b64encode(body).decode('ascii')
            self.libraries.append(entry)
            bindata_count += 1

        if bindata_count:
            step(f"Built {bindata_count} binary data entries")

        # Phase 7b: Build MovieClip (container) entries from DefineSprite data
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
            # Capture SoundStreamHead (tag 18/45) as structured fields only
            for ntag in nested_tags:
                if ntag.tag_type in (18, 45):
                    container['soundStreamParsed'] = self._parse_sound_stream_head(bytes(ntag.data))
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
                        if action.filters:
                            existing['filters'] = action.filters
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
                            'filters': action.filters or [],
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
        all_depths_asc = sorted(depth_events.keys())

        # Reverse: highest depth first (front-to-back)
        all_depths = list(reversed(all_depths_asc))

        layers = []
        for depth_idx, depth in enumerate(all_depths):
            events = depth_events[depth]
            layer = self._build_layer_from_events(
                depth, depth_idx, events, actual_frame_count)
            layers.append(layer)

        # ── Split mixed clip_depth layers ──
        # A depth may act as a mask (has clip_depth) on some frames and
        # as normal content on others (SWF reuses depths).  N2D layer
        # modes are static, so we split into separate MASK and NORMAL
        # layers.  Character spans already carry _clip_depth metadata.
        split_layers = []
        for layer in layers:
            mask_chars = [c for c in layer['characters'] if c.get('_clip_depth')]
            normal_chars = [c for c in layer['characters'] if not c.get('_clip_depth')]
            if mask_chars and normal_chars:
                # Mixed — create two layers from this depth
                normal_layer = dict(layer)
                normal_layer['characters'] = normal_chars
                normal_layer['emptyCharacters'] = self._compute_empty_ranges(
                    normal_chars, actual_frame_count)
                split_layers.append(normal_layer)

                mask_layer = dict(layer)
                mask_layer['name'] = f"mask_{layer['swfDepth']}"
                mask_layer['characters'] = mask_chars
                mask_layer['emptyCharacters'] = self._compute_empty_ranges(
                    mask_chars, actual_frame_count)
                mask_layer['_is_mask_split'] = True
                split_layers.append(mask_layer)
            else:
                split_layers.append(layer)
        layers = split_layers

        # ── Build clip_depth_map from character-level _clip_depth ──
        # Maps layer index → clip_depth value for layers that contain
        # mask characters.  Also collects active frame ranges per mask
        # for frame-aware MASK_IN assignment.
        clip_depth_map = {}   # layer_idx → clip_depth_value
        mask_frame_ranges = {}  # layer_idx → [(start, end), ...]
        for li, layer in enumerate(layers):
            for ch in layer['characters']:
                cd = ch.get('_clip_depth', 0)
                if cd:
                    clip_depth_map[li] = cd
                    mask_frame_ranges.setdefault(li, []).append(
                        (ch['startFrame'], ch['endFrame']))

        # ── Frame-aware mask assignment ──
        if clip_depth_map:
            # Helper: check if a character's frame range overlaps any
            # of a mask's active frame ranges.
            def _overlaps(char, mask_ranges):
                cs, ce = char['startFrame'], char['endFrame']
                return any(cs < me and ms < ce for ms, me in mask_ranges)

            # Process each mask and apply splits immediately so that
            # subsequent masks see already-modified character lists.
            # range(len(layers)) is evaluated once, so appended layers
            # won't be re-iterated.
            for mi, clip_val in clip_depth_map.items():
                mask_depth = layers[mi]['swfDepth']
                layers[mi]['mode'] = 1  # MASK
                layers[mi]['lock'] = True  # Lock makes mask shape invisible
                layers[mi]['maskId'] = None

                m_ranges = mask_frame_ranges[mi]

                n_orig = len(layers)
                for li in range(n_orig):
                    layer = layers[li]
                    if li == mi:
                        continue
                    # Skip layers already assigned as MASK
                    if layer['mode'] == 1:
                        continue
                    d = layer['swfDepth']
                    if d > mask_depth and d <= clip_val:
                        overlapping = [c for c in layer['characters']
                                       if _overlaps(c, m_ranges)]
                        non_overlapping = [c for c in layer['characters']
                                          if not _overlaps(c, m_ranges)]

                        if overlapping and non_overlapping:
                            # Apply split immediately
                            layer['characters'] = non_overlapping
                            layer['emptyCharacters'] = self._compute_empty_ranges(
                                non_overlapping, actual_frame_count)

                            mi_layer = dict(layer)
                            mi_layer['name'] = f"maskin_{d}"
                            mi_layer['characters'] = overlapping
                            mi_layer['emptyCharacters'] = self._compute_empty_ranges(
                                overlapping, actual_frame_count)
                            mi_layer['mode'] = 2  # MASK_IN
                            mi_layer['maskId'] = mi
                            layers.append(mi_layer)
                        elif overlapping:
                            layer['mode'] = 2
                            layer['maskId'] = mi

            # ── Reorganize for contiguity ──
            # toPublish() requires each MASK layer to be immediately
            # followed by its MASK_IN layers (contiguous group).
            layer_old_idx = {id(l): i for i, l in enumerate(layers)}
            mask_in_indices = {i for i, l in enumerate(layers)
                               if l.get('mode') == 2}
            visited = set()
            new_layers = []
            for i, layer in enumerate(layers):
                if i in visited:
                    continue
                if i in mask_in_indices:
                    continue  # Will be pulled in by its MASK
                new_layers.append(layer)
                visited.add(i)
                if layer['mode'] == 1:  # MASK
                    for j, l2 in enumerate(layers):
                        if (j not in visited
                                and j in mask_in_indices
                                and l2.get('maskId') == i):
                            new_layers.append(l2)
                            visited.add(j)

            # Orphaned MASK_IN layers
            for i in sorted(mask_in_indices - visited):
                new_layers.append(layers[i])
                visited.add(i)

            # Remap maskId from old → new layer indices
            old_to_new = {}
            for new_idx, layer in enumerate(new_layers):
                old_idx = layer_old_idx[id(layer)]
                old_to_new[old_idx] = new_idx
            for layer in new_layers:
                if layer.get('mode') == 2 and layer.get('maskId') is not None:
                    layer['maskId'] = old_to_new.get(
                        layer['maskId'], layer['maskId'])

            layers = new_layers

        # Strip internal metadata from characters
        for layer in layers:
            for ch in layer.get('characters', []):
                ch.pop('_clip_depth', None)
            layer.pop('_is_mask_split', None)

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
                        entry.get('filters') != prev_entry.get('filters') or
                        entry.get('name') != prev_entry.get('name') or
                        entry.get('ratio') != prev_entry.get('ratio')):
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
        span_clip_depth = 0

        for frame_num, state, is_reinstated in events:
            if state is None:
                # Remove event — close current span
                if span_start is not None:
                    ch = self._build_character_span(
                        span_char_id, span_start, frame_num, span_places,
                        reinstated=span_reinstated)
                    ch['_clip_depth'] = span_clip_depth
                    characters.append(ch)
                    span_start = None
                    span_char_id = None
                    span_places = []
                    span_reinstated = False
                    span_clip_depth = 0
            else:
                # Place or move event — depth is present
                cur_char_id = state.get('char_id')

                if span_start is None:
                    # Start new span
                    span_start = frame_num
                    span_char_id = cur_char_id
                    span_places = [(frame_num, state)]
                    span_reinstated = is_reinstated
                    span_clip_depth = state.get('clip_depth', 0) or 0
                elif cur_char_id != span_char_id or is_reinstated:
                    # Character changed or reinstated — close old, start new
                    ch = self._build_character_span(
                        span_char_id, span_start, frame_num, span_places,
                        reinstated=span_reinstated)
                    ch['_clip_depth'] = span_clip_depth
                    characters.append(ch)
                    span_start = frame_num
                    span_char_id = cur_char_id
                    span_places = [(frame_num, state)]
                    span_reinstated = is_reinstated
                    span_clip_depth = state.get('clip_depth', 0) or 0
                else:
                    # Same character — add keyframe if properties changed
                    _, prev_entry = span_places[-1]
                    if (state.get('matrix') != prev_entry.get('matrix') or
                        state.get('cxform') != prev_entry.get('cxform') or
                        state.get('blend_mode') != prev_entry.get('blend_mode') or
                        state.get('filters') != prev_entry.get('filters') or
                        state.get('name') != prev_entry.get('name') or
                        state.get('ratio') != prev_entry.get('ratio')):
                        span_places.append((frame_num, state))

        # Close final span
        if span_start is not None:
            ch = self._build_character_span(
                span_char_id, span_start, total_frames + 1, span_places,
                reinstated=span_reinstated)
            ch['_clip_depth'] = span_clip_depth
            characters.append(ch)

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

            # Convert parsed SWF filters to n2d filter format
            raw_filters = entry.get('filters', [])
            n2d_filters = []
            for f in raw_filters:
                n2d_filters.append(f)

            place = {
                'frame': frame_num,
                'depth': 0,
                'blendMode': blend_name,
                'filter': n2d_filters,
                'matrix': [a, b, c, d, tx, ty],
                'colorTransform': list(cxform),
            }
            # Preserve ratio from OG PlaceObject for 1:1 roundtrip
            if entry.get('ratio') is not None:
                place['ratio'] = entry['ratio']
            places.append(place)

        # --- Motion tween detection ---
        # Mirrors the native Next2D algorithm (Util.js lines 2642-2706):
        # Consecutive single-frame keyframes spanning >2 frames → linear tween.
        # Editor expects [{frame: N, value: {method, curve, custom, startFrame, endFrame}}, ...]
        tweens = []
        if len(places) > 2:
            DEFAULT_EASING = [
                {"type": "pointer", "fixed": True, "x": 0, "y": 0},
                {"type": "curve", "x": 0, "y": 0},
                {"type": "curve", "x": 100, "y": 100},
                {"type": "pointer", "fixed": True, "x": 100, "y": 100},
            ]
            i = 0
            while i < len(places) - 1:
                # Find a run of consecutive-frame keyframes
                run_start = i
                while (i + 1 < len(places)
                       and places[i + 1]['frame'] == places[i]['frame'] + 1):
                    i += 1
                run_len = i - run_start + 1  # number of keyframes in run
                if run_len > 2:
                    sf = places[run_start]['frame']
                    ef = places[i]['frame']
                    tweens.append({
                        "frame": sf,
                        "value": {
                            "method": "linear",
                            "curve": [],
                            "custom": list(DEFAULT_EASING),
                            "startFrame": sf,
                            "endFrame": ef,
                        }
                    })
                    # Mark intermediate places with tweenFrame
                    for j in range(run_start, i):
                        places[j]['tweenFrame'] = sf
                i += 1

        self.next_char_id += 1

        result = {
            'id': self.next_char_id,
            'name': instance_name,
            'libraryId': lib_id,
            'startFrame': start_frame,
            'endFrame': end_frame,
            'tween': tweens,
            'places': places,
        }
        if reinstated:
            result['reinstated'] = True
        return result

    def _button_as_container(self, lid: int, cid: int, display_name: str,
                             sym_name: str, bounds: dict,
                             button_parsed: dict) -> dict:
        """Convert parsed DefineButton2 data into an editable 4-frame N2D container.

        Frame mapping: 1=up, 2=over, 3=down, 4=hit.
        Each SWF depth becomes one layer; characters are placed on the frames
        corresponding to the button states they appear in.
        """
        # 3 frames per state → labels are wide enough to read in the timeline
        _FPS = 3  # frames per state
        state_to_frame_start = {'up': 1, 'over': 1 + _FPS, 'down': 1 + 2 * _FPS, 'hit': 1 + 3 * _FPS}
        _TOTAL = 4 * _FPS  # 12 total frames

        # Collect per-depth, per-frame placements.
        # depth → {frame_no: {char_swf_id, matrix, cxform, filters, blend}}
        depth_frames: dict = {}
        for state_name, frame_start in state_to_frame_start.items():
            for rec in button_parsed.get('buttonStates', {}).get(state_name, []):
                depth = rec['placeDepth']
                if depth not in depth_frames:
                    depth_frames[depth] = {}
                m = rec['matrix']
                cx = rec['colorTransform']
                # _read_swf_matrix returns dict with tx/ty in twips → convert to pixels
                matrix_list = [
                    m.get('scaleX', 1.0),
                    m.get('rotateSkew0', 0.0),
                    m.get('rotateSkew1', 0.0),
                    m.get('scaleY', 1.0),
                    m.get('translateX', 0) / 20.0,
                    m.get('translateY', 0) / 20.0,
                ]
                # _read_swf_cxform_alpha returns raw integers → normalize to N2D format
                cxform_list = [
                    cx.get('redMultTerm', 256) / 256.0,
                    cx.get('greenMultTerm', 256) / 256.0,
                    cx.get('blueMultTerm', 256) / 256.0,
                    cx.get('alphaMultTerm', 256) / 256.0,
                    float(cx.get('redAddTerm', 0)),
                    float(cx.get('greenAddTerm', 0)),
                    float(cx.get('blueAddTerm', 0)),
                    float(cx.get('alphaAddTerm', 0)),
                ]
                fd = {
                    'char_swf_id': rec['characterId'],
                    'matrix': matrix_list,
                    'cxform': cxform_list,
                    'filters': rec.get('filters', []),
                    'blend': rec.get('blendMode', 0),
                }
                # Fill all frames in this state's range with the same placement
                for f in range(frame_start, frame_start + _FPS):
                    if f not in depth_frames[depth]:  # first state wins for shared frames
                        depth_frames[depth][f] = fd

        # Build one layer per depth — highest depth first (N2D renders layers[0] on top)
        layers = []
        for depth_idx, depth in enumerate(sorted(depth_frames.keys(), reverse=True)):
            frames_at_depth = depth_frames[depth]
            all_frame_nos = sorted(frames_at_depth.keys())

            # Group frames into contiguous spans of the same characterId
            characters = []
            i = 0
            while i < len(all_frame_nos):
                span_f0 = all_frame_nos[i]
                span_cid_swf = frames_at_depth[span_f0]['char_swf_id']
                span_lib_id = self.swf_to_n2d.get(span_cid_swf, 0)
                # Extend span while contiguous frames and same characterId
                j = i + 1
                while (j < len(all_frame_nos)
                       and all_frame_nos[j] == all_frame_nos[j - 1] + 1
                       and frames_at_depth[all_frame_nos[j]]['char_swf_id'] == span_cid_swf):
                    j += 1
                span_frames = all_frame_nos[i:j]

                # Build place entries (only emit a new keyframe when transform changes)
                places = []
                prev_key = None
                for f in span_frames:
                    fd = frames_at_depth[f]
                    blend_name = BLEND_MODE_MAP.get(fd['blend'], 'normal') if fd['blend'] else 'normal'
                    key = (tuple(fd['matrix']), tuple(fd['cxform']),
                           blend_name, str(fd.get('filters', [])))
                    if key != prev_key:
                        places.append({
                            'frame': f,
                            'depth': 0,
                            'blendMode': blend_name,
                            'filter': fd.get('filters', []),
                            'matrix': fd['matrix'],
                            'colorTransform': fd['cxform'],
                        })
                        prev_key = key

                reinstated = (i > 0)
                self.next_char_id += 1
                char_entry = {
                    'id': self.next_char_id,
                    'name': '',
                    'libraryId': span_lib_id,
                    'startFrame': span_frames[0],
                    'endFrame': span_frames[-1] + 1,
                    'tween': [],
                    'places': places,
                }
                if reinstated:
                    char_entry['reinstated'] = True
                characters.append(char_entry)
                i = j

            # Compute empty frame ranges (gaps in the _TOTAL-frame window)
            occupied = set()
            for ch in characters:
                for f in range(ch['startFrame'], ch['endFrame']):
                    occupied.add(f)
            empty = []
            gap_start = None
            for f in range(1, _TOTAL + 2):  # sentinel = _TOTAL+1
                if f not in occupied:
                    if gap_start is None:
                        gap_start = f
                else:
                    if gap_start is not None:
                        empty.append({'startFrame': gap_start, 'endFrame': f})
                        gap_start = None
            if gap_start is not None:
                empty.append({'startFrame': gap_start, 'endFrame': _TOTAL + 1})

            layer_color = LAYER_COLORS[depth_idx % len(LAYER_COLORS)]
            layers.append({
                'name': f"depth_{depth}",
                'swfDepth': depth,
                'light': False,
                'disable': False,
                'lock': False,
                'mode': 0,
                'maskId': None,
                'guideId': None,
                'color': layer_color,
                'characters': characters,
                'emptyCharacters': empty,
            })

        return {
            'id': lid,
            'swfCharId': cid,
            'name': display_name,
            'type': 'container',
            'isButton': True,
            'buttonTrackAsMenu': button_parsed.get('trackAsMenu', False),
            'symbol': sym_name,
            'folderId': self.folder_ids.get('button', 0),
            'bounds': bounds,
            'totalFrame': _TOTAL,
            'currentFrame': 1,
            'leftFrame': 1,
            'labels': [
                {'frame': 1,            'name': 'up'},
                {'frame': 1 + _FPS,     'name': 'over'},
                {'frame': 1 + 2 * _FPS, 'name': 'down'},
                {'frame': 1 + 3 * _FPS, 'name': 'hit'},
            ],
            'actions': [],
            'sounds': [],
            'layers': layers,
        }

    def _compute_button_bounds(self, cid: int) -> dict:
        """Compute bounds for a DefineButton2 by unioning referenced character bounds."""
        fallback = {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20}
        if cid not in self.raw_tag_data:
            return fallback
        _, body = self.raw_tag_data[cid]
        try:
            ref_ids = parse_define_button2_char_ids(body)
        except Exception:
            return fallback
        if not ref_ids:
            return fallback
        x_min = float('inf')
        y_min = float('inf')
        x_max = float('-inf')
        y_max = float('-inf')
        found = False
        for ref_id in ref_ids:
            b = self.shape_bounds.get(ref_id)
            if b:
                x_min = min(x_min, b['xMin'])
                y_min = min(y_min, b['yMin'])
                x_max = max(x_max, b['xMax'])
                y_max = max(y_max, b['yMax'])
                found = True
        if not found:
            return fallback
        return {'xMin': x_min, 'xMax': x_max, 'yMin': y_min, 'yMax': y_max}

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

        Decodes bitmap RGBA from the buffer field on demand — only bitmaps
        actually referenced in shape fills are decoded.
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
                    'buffer': rgba_bytes,
                    'width': w,
                    'height': h,
                }
                continue

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
        # Clamp stage dimensions to WebGL MAX_RENDERBUFFER_SIZE safe limit.
        # Exceeding this causes GL_INVALID_VALUE in glRenderbufferStorageMultisample.
        _MAX_RB = 4096
        stage_w = self.header['width']
        stage_h = self.header['height']
        if stage_w > _MAX_RB or stage_h > _MAX_RB:
            scale = min(_MAX_RB / stage_w, _MAX_RB / stage_h)
            stage_w = max(1, int(stage_w * scale))
            stage_h = max(1, int(stage_h * scale))
            print(f"  [STAGE] clamped to {stage_w}x{stage_h} (was {self.header['width']}x{self.header['height']})", flush=True)
        result = {
            'version': 1,
            'name': self.name,
            'characterId': max_id + 1,
            'stage': {
                'width': stage_w,
                'height': stage_h,
                'fps': self.header['fps'],
                'bgColor': self.parsed_bg_color or '#333333',
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
        # ── Structured global tag fields (no rawGlobalTags passthrough) ──
        if self.parsed_abc_blocks:
            result['abcBlocks'] = self.parsed_abc_blocks
        if self.parsed_protect:
            result['protectFromImport'] = True
        if self.parsed_metadata:
            result['metadata'] = self.parsed_metadata
        if self.parsed_scene_labels:
            result['sceneAndFrameLabels'] = self.parsed_scene_labels
        if self.parsed_sound_stream:
            result['soundStream'] = self.parsed_sound_stream
        if self.parsed_import_assets:
            result['importAssets'] = self.parsed_import_assets
        # Include SWF version and compression format for matching
        result['swfVersion'] = self.header.get('version', 14)
        result['swfCompressed'] = self.header.get('compressed', True)
        # Include FileAttributes flags for roundtrip
        if self.parsed_file_attributes:
            result['fileAttributeFlags'] = self.parsed_file_attributes
        # Store which charIds are defined inline in the root timeline section
        # (after SymbolClass). These must NOT be emitted in the definition
        # section during compilation — they go in the root timeline instead.
        if self.root_timeline_def_ids:
            result['rootTimelineDefIds'] = self.root_timeline_def_ids
        if self.symbol_class_order:
            result['symbolClassOrder'] = self.symbol_class_order
        # Include AS3 source scripts if any were loaded
        if self.scripts:
            result['scripts'] = self.scripts
        return result


# ═══════════════════════════════════════════════════════════════════════════
#  SAVE .n2d FILE
# ═══════════════════════════════════════════════════════════════════════════

def save_n2d(data: dict, output_path: str, bitmap_buffers: dict = None, use_msgpack: bool = True):
    """Save dict as .n2d ZIP archive with MessagePack or JSON format.

    Format: ZIP file containing:
      - project.msgpack: the main N2D data in MessagePack binary format (default)
      - project.json: the main N2D JSON (legacy format, if use_msgpack=False)

    MessagePack format benefits:
      - 50-70% smaller files
      - No string conversion (direct binary parsing)
      - Handles unlimited file sizes (bypasses JavaScript string length limit)
      - Faster parsing

    Bitmap data is stored inline in each library entry's buffer field
    (base64-encoded RGBA pixel data). No separate bitmap files are
    written — this keeps memory usage minimal.

    bitmap_buffers parameter is accepted for backwards compatibility but
    is no longer used (ignored). All bitmap data comes from the buffer field.
    """
    log.info('save_n2d: writing to %s (format: %s)', output_path, 'MessagePack' if use_msgpack else 'JSON')
    import zipfile
    t0 = time.time()
    step = lambda msg: print(f"  [{time.time()-t0:6.1f}s] {msg}", flush=True)

    if use_msgpack:
        step("Serializing MessagePack binary...")
        msgpack_data = msgpack.packb(data, use_bin_type=True)
        step(f"MessagePack: {len(msgpack_data):,} bytes")

        step("Writing ZIP (project.msgpack)...")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
            zf.writestr('project.msgpack', msgpack_data)
    else:
        step("Serializing JSON...")
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=True)
        step(f"JSON: {len(json_str):,} chars")

        step("Writing ZIP (project.json — legacy format)...")
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
    The human-readable files can be edited and will be preferred during
    compilation when they are newer.
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

        # Decode from pre-decoded RGBA buffer
        buf = lib.get('buffer', '')
        w = lib.get('width', 0)
        h = lib.get('height', 0)
        if not buf or not w or not h:
            return 0

        fname = f"{cid}_{name}.png"
        fpath = os.path.join(bitmaps_dir, fname)

        # Skip re-encoding if the file already exists (unchanged bitmap)
        if os.path.isfile(fpath):
            lib['externalFile'] = f'bitmaps/{fname}'
            return 1

        if buf.startswith('b64:'):
            rgba = base64.b64decode(buf[4:])
        else:
            rgba = buf.encode('latin-1')
        if rgba and len(rgba) == w * h * 4:
            try:
                from PIL import Image
                img = Image.frombytes('RGBA', (w, h), rgba)
                _MAX_TEX = 4096
                if w > _MAX_TEX or h > _MAX_TEX:
                    scale = min(_MAX_TEX / w, _MAX_TEX / h)
                    img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
                img.save(fpath)
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

        buf = lib.get('buffer', b'')
        if not buf:
            return 0
        audio_bytes = buf if isinstance(buf, (bytes, bytearray)) else base64.b64decode(buf)
        ext = _detect_audio_ext(audio_bytes)
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

    # 1a. Validate sprite dependencies (Bug Fix #2: detect circular references)
    try:
        validate_swf_sprites(tags)
        step("Sprite dependency validation passed (no circular references)")
    except ValueError as e:
        log.error(f"Sprite validation failed: {e}")
        raise ValueError(f"Invalid SWF structure: {e}") from e

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

    # 3a. Normalize imported scripts: drop linkage stubs, inject _fla frame
    #     aggregates into timeline actions, keep only class-source scripts.
    if n2d.get('scripts'):
        step("Normalizing imported AS3 scripts...")
        n2d['scripts'] = normalize_imported_scripts(n2d['scripts'], n2d['libraries'])

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