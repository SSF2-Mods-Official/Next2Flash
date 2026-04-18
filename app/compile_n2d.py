#!/usr/bin/env python3
"""
Compile a next2D .n2D file into an AS3 SWF.

Usage:
    python compile_n2d.py <input.n2D> -o <output.swf> --shared <shared_dir>

This script:
  1. Loads the .n2D file (zlib-compressed, URI-encoded JSON)
  2. Converts all libraries → SWF tags (bitmaps, shapes, sounds, movieclips)
  3. Compiles AS3 code from the shared directory with mxmlc
  4. Assembles the final SWF
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import logging
import msgpack
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import unquote

log = logging.getLogger(__name__)

from swf_binary_io import BitReader, BitWriter
from swf_constants import (
    SWFTag, TAG_DEFINE_SHAPE3, TAG_DO_ABC, TAG_DEFINE_SOUND
)
from swf_writer import (
    NEXT2D_BLEND_MAP,
    _nbits_signed_list,
    build_define_sprite,
    build_file_attributes,
    build_frame_label,
    build_place_object2,
    build_place_object3,
    build_remove_object2,
    build_set_background_color,
    build_swf_file,
    build_symbol_class,
    build_export_assets,
    build_tag,
    build_tag_end,
    build_tag_show_frame,
    encode_filter_list,
    twips,
    write_cxform_alpha,
    write_matrix,
    write_rect,
)
from bitmap_converter import build_define_bits_lossless2
from shape_converter import (
    build_define_shape3,
    build_define_shape4,
    build_define_morph_shape,
    parse_next2d_shape_buffer,
)
from text_converter import build_define_edit_text


def _decode_raw_body(s) -> bytes:
    """Decode a raw binary body — supports bytes, base64 strings, and latin-1 encoding.

    If *s* is already bytes (e.g. from msgpack), return as-is.
    Strings with 'b64:' prefix are base64-decoded after stripping the prefix.
    Other strings are tried as raw base64 first.
    Falls back to latin-1 for backward compatibility with older N2D files.
    """
    if not s:
        return b''
    if isinstance(s, (bytes, bytearray)):
        return bytes(s)
    # Strip 'b64:' prefix if present
    if isinstance(s, str) and s.startswith('b64:'):
        s = s[4:]
    try:
        return base64.b64decode(s)
    except Exception:
        # Fallback: legacy latin-1 encoding
        return bytes(ord(c) for c in s)

def _remap_sprite_raw_body(raw_body: bytes, id_map: Dict[int, int]) -> bytes:
    """Remap charID references inside a DefineSprite raw body.

    raw_body = frameCount(2) + sub-tags.  Sub-tags containing charID refs:
      PlaceObject2 (26): flags(1) + depth(2) [+ charId(2) if flags & 0x02]
      PlaceObject3 (70): flags(2) + depth(2) [+ charId(2) if flags & 0x02]
      RemoveObject (5):  charId(2) + depth(2)

    All other sub-tags are passed through unchanged.
    """
    if not id_map or len(raw_body) < 4:
        return raw_body

    out = bytearray(raw_body[:2])  # frameCount
    offset = 2
    while offset < len(raw_body):
        if offset + 2 > len(raw_body):
            out.extend(raw_body[offset:])
            break
        tag_code_and_length = struct.unpack_from('<H', raw_body, offset)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3f
        header_size = 2
        if length == 0x3f:
            if offset + 6 > len(raw_body):
                out.extend(raw_body[offset:])
                break
            length = struct.unpack_from('<I', raw_body, offset + 2)[0]
            header_size = 6

        tag_start = offset
        tag_end = offset + header_size + length
        tag_data_start = offset + header_size

        if tag_type == 26 and length >= 3:  # PlaceObject2
            flags = raw_body[tag_data_start]
            if flags & 0x02 and length >= 5:
                old_cid = struct.unpack_from('<H', raw_body, tag_data_start + 3)[0]
                new_cid = id_map.get(old_cid, old_cid)
                if new_cid != old_cid:
                    chunk = bytearray(raw_body[tag_start:tag_end])
                    cid_offset = header_size + 3
                    struct.pack_into('<H', chunk, cid_offset, new_cid)
                    out.extend(chunk)
                    offset = tag_end
                    continue
        elif tag_type == 70 and length >= 4:  # PlaceObject3
            flags = struct.unpack_from('<H', raw_body, tag_data_start)[0]
            if flags & 0x02 and length >= 6:
                old_cid = struct.unpack_from('<H', raw_body, tag_data_start + 4)[0]
                new_cid = id_map.get(old_cid, old_cid)
                if new_cid != old_cid:
                    chunk = bytearray(raw_body[tag_start:tag_end])
                    cid_offset = header_size + 4
                    struct.pack_into('<H', chunk, cid_offset, new_cid)
                    out.extend(chunk)
                    offset = tag_end
                    continue
        elif tag_type == 5 and length >= 4:  # RemoveObject (has charId)
            old_cid = struct.unpack_from('<H', raw_body, tag_data_start)[0]
            new_cid = id_map.get(old_cid, old_cid)
            if new_cid != old_cid:
                chunk = bytearray(raw_body[tag_start:tag_end])
                struct.pack_into('<H', chunk, header_size, new_cid)
                out.extend(chunk)
                offset = tag_end
                continue

        # Pass through unchanged
        out.extend(raw_body[tag_start:tag_end])
        offset = tag_end

        if tag_type == 0:  # End
            break

    return bytes(out)


# ── Bit-level helpers for skipping byte-aligned SWF structures ──────────

def _skip_swf_matrix(buf: bytes, off: int) -> int:
    """Skip a byte-aligned MATRIX record starting at buf[off].
    Returns the byte offset after the complete (byte-aligned) matrix."""
    bit_pos = off * 8

    def read_ub(n_bits):
        nonlocal bit_pos
        val = 0
        for _ in range(n_bits):
            byte_idx = bit_pos >> 3
            bit_idx = 7 - (bit_pos & 7)
            val = (val << 1) | ((buf[byte_idx] >> bit_idx) & 1)
            bit_pos += 1
        return val

    has_scale = read_ub(1)
    if has_scale:
        n = read_ub(5)
        read_ub(n)  # ScaleX
        read_ub(n)  # ScaleY
    has_rotate = read_ub(1)
    if has_rotate:
        n = read_ub(5)
        read_ub(n)  # RotateSkew0
        read_ub(n)  # RotateSkew1
    n = read_ub(5)
    read_ub(n)  # TranslateX
    read_ub(n)  # TranslateY
    return (bit_pos + 7) >> 3  # byte-align


def _skip_swf_cxform_alpha(buf: bytes, off: int) -> int:
    """Skip a byte-aligned CXFORMWITHALPHA record starting at buf[off].
    Returns the byte offset after the complete (byte-aligned) record."""
    bit_pos = off * 8

    def read_ub(n_bits):
        nonlocal bit_pos
        val = 0
        for _ in range(n_bits):
            byte_idx = bit_pos >> 3
            bit_idx = 7 - (bit_pos & 7)
            val = (val << 1) | ((buf[byte_idx] >> bit_idx) & 1)
            bit_pos += 1
        return val

    has_add = read_ub(1)
    has_mult = read_ub(1)
    nbits = read_ub(4)
    if has_mult:
        for _ in range(4):
            read_ub(nbits)  # R, G, B, A mult
    if has_add:
        for _ in range(4):
            read_ub(nbits)  # R, G, B, A add
    return (bit_pos + 7) >> 3  # byte-align


def _skip_swf_filter_list(buf: bytes, off: int) -> int:
    """Skip a FILTERLIST starting at buf[off].
    Returns the byte offset after the complete filter list."""
    count = buf[off]; off += 1
    for _ in range(count):
        fid = buf[off]; off += 1
        if fid == 0:    # DropShadowFilter
            off += 23
        elif fid == 1:  # BlurFilter
            off += 9
        elif fid == 2:  # GlowFilter
            off += 15
        elif fid == 3:  # BevelFilter
            off += 27
        elif fid == 4:  # GradientGlowFilter
            n = buf[off]; off += 1
            off += 5 * n + 19
        elif fid == 5:  # ConvolutionFilter
            mx = buf[off]; my = buf[off + 1]; off += 2
            off += 4 + 4 + 4 * mx * my + 4 + 1
        elif fid == 6:  # ColorMatrixFilter
            off += 80
        elif fid == 7:  # GradientBevelFilter
            n = buf[off]; off += 1
            off += 5 * n + 19
        else:
            raise ValueError(f"Unknown filter ID: {fid}")
    return off


def _remap_button_raw_body(raw_body: bytes, id_map: Dict[int, int]) -> bytes:
    """Remap charID references inside a DefineButton2 raw body.

    raw_body = tag data AFTER the 2-byte charID.  Layout:
      UI8  Flags
      UI16 ActionOffset
      BUTTONRECORD[] terminated by 0x00:
        UI8  ButtonStates (bit5=HasBlendMode, bit4=HasFilterList)
        UI16 CharacterId   << remapped
        UI16 PlaceDepth
        MATRIX PlaceMatrix
        CXFORMWITHALPHA ColorTransform
        [FILTERLIST if HasFilterList]
        [UI8 BlendMode if HasBlendMode]
      [BUTTONCONDACTION[] if ActionOffset > 0]
    """
    if not id_map or len(raw_body) < 4:
        return raw_body

    try:
        buf = bytearray(raw_body)
        off = 3  # skip Flags(1) + ActionOffset(2)

        while off < len(buf):
            state_flags = buf[off]
            if state_flags == 0:
                break  # end of ButtonRecords
            has_blend = bool(state_flags & 0x20)
            has_filter = bool(state_flags & 0x10)

            off += 1  # past state flags
            if off + 4 > len(buf):
                break

            # CharacterId (UI16 LE) — remap
            old_cid = buf[off] | (buf[off + 1] << 8)
            new_cid = id_map.get(old_cid, old_cid)
            buf[off] = new_cid & 0xFF
            buf[off + 1] = (new_cid >> 8) & 0xFF
            off += 2

            # PlaceDepth (UI16)
            off += 2

            # MATRIX (bit-packed, byte-aligned)
            off = _skip_swf_matrix(buf, off)

            # CXFORMWITHALPHA (bit-packed, byte-aligned)
            off = _skip_swf_cxform_alpha(buf, off)

            # Optional FilterList
            if has_filter:
                off = _skip_swf_filter_list(buf, off)

            # Optional BlendMode
            if has_blend:
                off += 1

        return bytes(buf)
    except (IndexError, ValueError):
        return raw_body  # safe fallback — un-remapped is better than dropped


def _remap_shape_raw_body(raw_body: bytes, tag_type: int,
                          id_map: Dict[int, int]) -> bytes:
    """Remap bitmap charID references inside a DefineShape raw body.

    raw_body = tag data AFTER the 2-byte charID.  Fill styles of type
    0x40–0x43 (bitmap fills) contain a UI16 bitmapId that must be remapped.

    This parses just enough of the shape structure to find fill style
    bitmapId fields and patch them.  All other bytes are unchanged.
    """
    if not id_map or len(raw_body) < 6:
        return raw_body

    buf = bytearray(raw_body)

    try:
        # ── Skip shape bounds RECT (bit-packed) ──
        bit_offset = 0
        nbits = (buf[0] >> 3) & 0x1f
        total_bits = 5 + nbits * 4
        byte_offset = (total_bits + 7) // 8

        # DefineShape4 (tag 83): extra edge-bounds RECT + 1 byte flags
        if tag_type == 83:
            nbits2 = (buf[byte_offset] >> 3) & 0x1f
            total_bits2 = 5 + nbits2 * 4
            byte_offset += (total_bits2 + 7) // 8
            byte_offset += 1  # flags byte

        # ── Parse fill style array ──
        def _remap_fill_styles(off: int) -> int:
            """Parse fill style array starting at off, remap bitmap IDs.
            Returns offset after the array."""
            count = buf[off]; off += 1
            if tag_type not in (2,) and count == 0xff:
                count = buf[off] | (buf[off+1] << 8); off += 2
            for _ in range(count):
                ft = buf[off]; off += 1
                if ft == 0:
                    # Solid fill: RGB (tags 2,22) or RGBA (tags 32,83)
                    off += 4 if tag_type in (32, 83) else 3
                elif ft in (0x10, 0x12):
                    # Gradient fill: MATRIX + GRADIENT
                    off = _skip_matrix(off)
                    off = _skip_gradient(off)
                elif ft == 0x13:
                    # Focal gradient: MATRIX + FOCALGRADIENT
                    off = _skip_matrix(off)
                    off = _skip_focal_gradient(off)
                elif ft in (0x40, 0x41, 0x42, 0x43):
                    # Bitmap fill: UI16 bitmapId + MATRIX
                    old_cid = buf[off] | (buf[off+1] << 8)
                    new_cid = id_map.get(old_cid, old_cid)
                    buf[off] = new_cid & 0xff
                    buf[off+1] = (new_cid >> 8) & 0xff
                    off += 2
                    off = _skip_matrix(off)
                else:
                    # Unknown fill type — abort to avoid corruption
                    return off
            return off

        def _skip_matrix(off: int) -> int:
            """Skip a byte-aligned MATRIX record."""
            byte_val = buf[off]
            bit_pos = 0
            def read_bits(n):
                nonlocal off, byte_val, bit_pos
                result = 0
                for _ in range(n):
                    result = (result << 1) | ((byte_val >> (7 - bit_pos)) & 1)
                    bit_pos += 1
                    if bit_pos >= 8:
                        bit_pos = 0
                        off += 1
                        if off < len(buf):
                            byte_val = buf[off]
                return result

            has_scale = read_bits(1)
            if has_scale:
                nbits_s = read_bits(5)
                read_bits(nbits_s)  # scaleX
                read_bits(nbits_s)  # scaleY
            has_rotate = read_bits(1)
            if has_rotate:
                nbits_r = read_bits(5)
                read_bits(nbits_r)  # rotateSkew0
                read_bits(nbits_r)  # rotateSkew1
            nbits_t = read_bits(5)
            read_bits(nbits_t)  # translateX
            read_bits(nbits_t)  # translateY
            # Align to byte boundary
            if bit_pos > 0:
                off += 1
            return off

        def _skip_gradient(off: int) -> int:
            """Skip a GRADIENT record (byte-aligned at start)."""
            byte_val = buf[off]
            bit_pos = 0
            def read_bits(n):
                nonlocal off, byte_val, bit_pos
                result = 0
                for _ in range(n):
                    result = (result << 1) | ((byte_val >> (7 - bit_pos)) & 1)
                    bit_pos += 1
                    if bit_pos >= 8:
                        bit_pos = 0
                        off += 1
                        if off < len(buf):
                            byte_val = buf[off]
                return result
            spread = read_bits(2)
            interp = read_bits(2)
            num_grads = read_bits(4)
            # Align
            if bit_pos > 0:
                off += 1
            # Each gradient record: UI8 ratio + color
            color_size = 4 if tag_type in (32, 83) else 3
            off += num_grads * (1 + color_size)
            return off

        def _skip_focal_gradient(off: int) -> int:
            """Skip a FOCALGRADIENT record."""
            byte_val = buf[off]
            bit_pos = 0
            def read_bits(n):
                nonlocal off, byte_val, bit_pos
                result = 0
                for _ in range(n):
                    result = (result << 1) | ((byte_val >> (7 - bit_pos)) & 1)
                    bit_pos += 1
                    if bit_pos >= 8:
                        bit_pos = 0
                        off += 1
                        if off < len(buf):
                            byte_val = buf[off]
                return result
            spread = read_bits(2)
            interp = read_bits(2)
            num_grads = read_bits(4)
            if bit_pos > 0:
                off += 1
            color_size = 4 if tag_type in (32, 83) else 3
            off += num_grads * (1 + color_size)
            off += 2  # FIXED8 focalPoint
            return off

        _remap_fill_styles(byte_offset)
    except (IndexError, KeyError):
        # If parsing fails, return original body unchanged to avoid corruption
        return raw_body

    return bytes(buf)


def _remap_morph_shape_raw_body(raw_body: bytes, tag_type: int,
                                id_map: Dict[int, int]) -> bytes:
    """Remap bitmap charID references inside a DefineMorphShape raw body.

    MorphShape has start fill styles and end fill styles, both may contain
    bitmap fills.  The structure after charID:
      StartBounds RECT + EndBounds RECT
      [MorphShape2: StartEdgeBounds RECT + EndEdgeBounds RECT + UI8 flags]
      Offset UI32 (points to end edges)
      FillStyleCount + MorphFillStyles[]
    """
    if not id_map or len(raw_body) < 10:
        return raw_body

    buf = bytearray(raw_body)
    try:
        off = 0

        def _skip_rect(o: int) -> int:
            nbits = (buf[o] >> 3) & 0x1f
            total = 5 + nbits * 4
            return o + (total + 7) // 8

        # StartBounds + EndBounds
        off = _skip_rect(off)
        off = _skip_rect(off)

        # MorphShape2 (tag 84): extra edge bounds + flags
        if tag_type == 84:
            off = _skip_rect(off)
            off = _skip_rect(off)
            off += 1  # flags

        off += 4  # Offset (UI32)

        # MorphFillStyleCount
        count = buf[off]; off += 1
        if count == 0xff:
            count = buf[off] | (buf[off+1] << 8); off += 2

        # MorphFillStyles — each has start+end fill data
        for _ in range(count):
            ft = buf[off]; off += 1
            if ft == 0:
                # Solid: StartColor RGBA + EndColor RGBA
                off += 8  # 4+4
            elif ft in (0x10, 0x12):
                # Gradient: StartMatrix + EndMatrix + start gradient + end gradient
                off = _skip_morph_matrix(buf, off)
                off = _skip_morph_matrix(buf, off)
                off = _skip_morph_gradient(buf, off)
            elif ft == 0x13:
                off = _skip_morph_matrix(buf, off)
                off = _skip_morph_matrix(buf, off)
                off = _skip_morph_gradient(buf, off)
            elif ft in (0x40, 0x41, 0x42, 0x43):
                # Bitmap: bitmapId (UI16) + StartMatrix + EndMatrix
                old_cid = buf[off] | (buf[off+1] << 8)
                new_cid = id_map.get(old_cid, old_cid)
                buf[off] = new_cid & 0xff
                buf[off+1] = (new_cid >> 8) & 0xff
                off += 2
                off = _skip_morph_matrix(buf, off)
                off = _skip_morph_matrix(buf, off)
            else:
                break  # unknown type — stop
    except (IndexError, KeyError):
        return raw_body

    return bytes(buf)


def _skip_morph_matrix(buf: bytearray, off: int) -> int:
    """Skip a byte-aligned MATRIX in a buffer."""
    byte_val = buf[off]
    bit_pos = 0

    def read_bits(n):
        nonlocal off, byte_val, bit_pos
        result = 0
        for _ in range(n):
            result = (result << 1) | ((byte_val >> (7 - bit_pos)) & 1)
            bit_pos += 1
            if bit_pos >= 8:
                bit_pos = 0
                off += 1
                if off < len(buf):
                    byte_val = buf[off]
        return result

    has_scale = read_bits(1)
    if has_scale:
        nb = read_bits(5)
        read_bits(nb); read_bits(nb)
    has_rotate = read_bits(1)
    if has_rotate:
        nb = read_bits(5)
        read_bits(nb); read_bits(nb)
    nb = read_bits(5)
    read_bits(nb); read_bits(nb)
    if bit_pos > 0:
        off += 1
    return off


def _skip_morph_gradient(buf: bytearray, off: int) -> int:
    """Skip a morph gradient record (spread+interp+numGrads, then RGBA pairs)."""
    byte_val = buf[off]
    bit_pos = 0

    def read_bits(n):
        nonlocal off, byte_val, bit_pos
        result = 0
        for _ in range(n):
            result = (result << 1) | ((byte_val >> (7 - bit_pos)) & 1)
            bit_pos += 1
            if bit_pos >= 8:
                bit_pos = 0
                off += 1
                if off < len(buf):
                    byte_val = buf[off]
        return result

    spread = read_bits(2)
    interp = read_bits(2)
    num_grads = read_bits(4)
    if bit_pos > 0:
        off += 1
    # Each morph gradient entry: ratio(1) + startColor(4) + ratio(1) + endColor(4) = 10
    off += num_grads * 10
    return off


def _remap_text_raw_body(raw_body: bytes, tag_type: int,
                         id_map: Dict[int, int]) -> bytes:
    """Remap font charID references inside a DefineText/DefineText2 raw body.

    raw_body = tag data AFTER the 2-byte charID.  Text records contain
    font ID references (UI16) that must be remapped.

    Layout: RECT bounds + MATRIX + UI8 glyphBits + UI8 advanceBits + TextRecords
    """
    if not id_map or len(raw_body) < 8:
        return raw_body

    buf = bytearray(raw_body)
    try:
        # Skip RECT bounds
        off = 0
        nbits = (buf[0] >> 3) & 0x1f
        total_bits = 5 + nbits * 4
        off = (total_bits + 7) // 8

        # Skip MATRIX
        off = _skip_morph_matrix(buf, off)

        glyph_bits = buf[off]; off += 1
        advance_bits = buf[off]; off += 1

        # Parse text records
        while off < len(buf):
            flags = buf[off]; off += 1
            if flags == 0:
                break

            has_font = bool(flags & 0x08)
            has_color = bool(flags & 0x04)
            has_y_off = bool(flags & 0x02)
            has_x_off = bool(flags & 0x01)

            if has_font:
                old_fid = buf[off] | (buf[off+1] << 8)
                new_fid = id_map.get(old_fid, old_fid)
                buf[off] = new_fid & 0xff
                buf[off+1] = (new_fid >> 8) & 0xff
                off += 2
            if has_color:
                off += 3  # RGB
                if tag_type == 33:  # DefineText2 has RGBA
                    off += 1
            if has_y_off:
                off += 2
            if has_x_off:
                off += 2
            if has_font:
                off += 2  # textHeight

            glyph_count = buf[off]; off += 1
            # Glyph entries are bit-packed: glyphBits + advanceBits per entry
            total_glyph_bits = glyph_count * (glyph_bits + advance_bits)
            off += (total_glyph_bits + 7) // 8

    except (IndexError, KeyError):
        return raw_body

    return bytes(buf)


def _remap_edit_text_raw_body(raw_body: bytes,
                              id_map: Dict[int, int]) -> bytes:
    """Remap font charID reference inside a DefineEditText raw body.

    Layout after charID: RECT bounds + UI8 flags1 + UI8 flags2 + [UI16 fontID]
    """
    if not id_map or len(raw_body) < 4:
        return raw_body

    buf = bytearray(raw_body)
    try:
        # Skip RECT bounds
        nbits = (buf[0] >> 3) & 0x1f
        total_bits = 5 + nbits * 4
        off = (total_bits + 7) // 8

        flags1 = buf[off]; off += 1
        flags2 = buf[off]; off += 1
        has_font = bool(flags1 & 0x01)

        if has_font:
            old_fid = buf[off] | (buf[off+1] << 8)
            new_fid = id_map.get(old_fid, old_fid)
            buf[off] = new_fid & 0xff
            buf[off+1] = (new_fid >> 8) & 0xff
    except (IndexError, KeyError):
        return raw_body

    return bytes(buf)


# ── SDK detection ────────────────────────────────────────────────────────
SDK_SEARCH_PATHS = [
    r"C:\aflex_sdk",
    r"C:\flex_sdk",
    r"C:\apache-flex-sdk",
]


def find_sdk() -> Optional[str]:
    env = os.environ.get("FLEX_HOME") or os.environ.get("AIR_SDK_HOME")
    if env and os.path.isdir(env):
        return env
    for p in SDK_SEARCH_PATHS:
        if os.path.isdir(p):
            return p
    return None


# ── n2D file loading ─────────────────────────────────────────────────────

def _overlay_external_scripts(data: dict, project_dir: str) -> None:
    """Read .as files from the project folder and overlay them onto the
    embedded scripts in *data*.  If any script source differs from what is
    embedded, set ``data['scriptsModified'] = True`` so the compiler will
    recompile from source instead of using the raw DoABC passthrough."""
    scripts = data.get('scripts')
    if not scripts:
        return
    modified = False
    for script in scripts:
        ext = script.get('externalFile', '')
        if not ext:
            continue
        ext_path = os.path.join(project_dir, ext)
        if not os.path.isfile(ext_path):
            continue
        with open(ext_path, 'r', encoding='utf-8') as f:
            new_source = f.read()
        old_source = script.get('source', '')
        if new_source != old_source:
            script['source'] = new_source
            modified = True
            log.info('_overlay_external_scripts: updated %s', ext)
    if modified:
        data['scriptsModified'] = True
        log.info('_overlay_external_scripts: marked scriptsModified=True')


def load_n2d(path: str) -> Tuple[dict, Optional[str]]:
    """Load an .n2D file → (parsed dict, project_dir or None).

    Supports:
      - Project folder: path is a directory containing project.n2d
      - ZIP format (PK magic): 
          * project.msgpack (MessagePack binary - preferred)
          * project.json (legacy JSON format)
      - Legacy zlib format (full URI-encoded or minimal % escaping)

    Returns the parsed dict and the project directory path (if the
    source is a folder with external assets) or None.
    """
    log.info('load_n2d: loading %s', path)

    # Project folder mode: path is a directory containing project.n2d
    if os.path.isdir(path):
        project_dir = path
        n2d_path = os.path.join(path, 'project.n2d')
        if not os.path.isfile(n2d_path):
            raise FileNotFoundError(f"No project.n2d in {path}")
        # Read the ZIP-format .n2d
        with open(n2d_path, 'rb') as f:
            raw = f.read()
        import zipfile as _zipfile
        import io as _io
        with _zipfile.ZipFile(_io.BytesIO(raw)) as zf:
            # Try MessagePack first, fall back to JSON
            if 'project.msgpack' in zf.namelist():
                log.info('load_n2d: loading MessagePack format')
                data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
            else:
                log.info('load_n2d: loading JSON format (legacy)')
                data = json.loads(zf.read('project.json'))
        _overlay_external_scripts(data, project_dir)
        return data, project_dir

    with open(path, "rb") as f:
        raw = f.read()

    # Check if this file sits inside a project folder (has bitmaps/ sibling)
    parent_dir = os.path.dirname(os.path.abspath(path))
    is_project = os.path.isdir(os.path.join(parent_dir, 'bitmaps'))
    project_dir = parent_dir if is_project else None

    # Detect ZIP format by magic bytes
    if raw[:2] == b'PK':
        import zipfile as _zipfile
        import io as _io
        with _zipfile.ZipFile(_io.BytesIO(raw)) as zf:
            # Try MessagePack first, fall back to JSON
            if 'project.msgpack' in zf.namelist():
                log.info('load_n2d: loading MessagePack format')
                data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
            else:
                log.info('load_n2d: loading JSON format (legacy)')
                data = json.loads(zf.read('project.json'))
            if project_dir:
                _overlay_external_scripts(data, project_dir)
            return data, project_dir

    decompressed = zlib.decompress(raw)
    text = decompressed.decode("utf-8")
    try:
        data = json.loads(unquote(text))
    except (json.JSONDecodeError, ValueError):
        data = json.loads(text)
    if project_dir:
        _overlay_external_scripts(data, project_dir)
    return data, project_dir


# ── WAV → DefineSound ────────────────────────────────────────────────────

def build_define_sound(char_id: int, wav_bytes: bytes) -> bytes:
    """Convert raw WAV bytes to a DefineSound tag (uncompressed little-endian PCM)."""
    log.debug("build_define_sound: char_id=%d, wav_bytes=%d", char_id, len(wav_bytes))
    assert wav_bytes[:4] == b"RIFF", "Not a WAV file"
    assert wav_bytes[8:12] == b"WAVE", "Not a WAV file"

    audio_format = 1
    num_channels = 1
    sample_rate = 22050
    bits_per_sample = 16
    pcm_data = b""

    pos = 12
    while pos < len(wav_bytes) - 8:
        chunk_id = wav_bytes[pos:pos + 4]
        chunk_size = struct.unpack_from("<I", wav_bytes, pos + 4)[0]
        if chunk_id == b"fmt ":
            audio_format = struct.unpack_from("<H", wav_bytes, pos + 8)[0]
            num_channels = struct.unpack_from("<H", wav_bytes, pos + 10)[0]
            sample_rate = struct.unpack_from("<I", wav_bytes, pos + 12)[0]
            bits_per_sample = struct.unpack_from("<H", wav_bytes, pos + 22)[0]
        elif chunk_id == b"data":
            pcm_data = wav_bytes[pos + 8:pos + 8 + chunk_size]
            break
        pos += 8 + chunk_size

    # Map sample rate to SWF rate code
    rate_map = {5512: 0, 11025: 1, 22050: 2, 44100: 3}
    swf_rate = 3  # default 44100
    for sr, code in sorted(rate_map.items()):
        if sample_rate <= sr:
            swf_rate = code
            break

    is_16bit = 1 if bits_per_sample == 16 else 0
    is_stereo = 1 if num_channels >= 2 else 0
    # Format 3 = uncompressed little-endian
    flags = (3 << 4) | (swf_rate << 2) | (is_16bit << 1) | is_stereo

    bytes_per_sample = (bits_per_sample // 8) * num_channels
    sample_count = len(pcm_data) // bytes_per_sample if bytes_per_sample > 0 else 0

    body = io.BytesIO()
    body.write(struct.pack("<H", char_id))
    body.write(struct.pack("<B", flags))
    body.write(struct.pack("<I", sample_count))
    body.write(pcm_data)
    return build_tag(TAG_DEFINE_SOUND, body.getvalue())


# ── External asset loading (project folder mode) ─────────────────────────

def _load_external_bitmap(project_dir: str, lib: dict, swf_id: int) -> Optional[bytes]:
    """Load an external PNG/JPG and return the raw SWF bitmap tag bytes.

    Returns DefineBitsJPEG3 (tag 35) for bitmaps that were originally JPEG-family,
    DefineBitsLossless2 (tag 36) otherwise.
    Returns None if no external file found or PIL unavailable.
    """
    ext_file = lib.get('externalFile', '')
    if not ext_file:
        return None
    fpath = os.path.join(project_dir, ext_file)
    if not os.path.isfile(fpath):
        return None

    try:
        from PIL import Image
    except ImportError:
        log.warning('PIL unavailable — cannot load external bitmap %s', fpath)
        return None

    img = Image.open(fpath).convert('RGBA')
    w, h = img.size
    rgba = img.tobytes()

    _JPEG_TAG_TYPES = (6, 21, 35, 90)
    raw_tag_type = lib.get('rawTagType', 36)
    if raw_tag_type in _JPEG_TAG_TYPES:
        from bitmap_converter import build_define_bits_jpeg3
        return build_define_bits_jpeg3(swf_id, w, h, rgba)
    # Preserve the original LL2 format (3=indexed, 5=ARGB).
    # Converting between formats can trigger Flash Player Error #2015.
    raw_fmt = lib.get('rawBitmapFormat', 5)
    if raw_fmt == 3:
        from bitmap_converter import build_define_bits_lossless2_indexed
        return build_define_bits_lossless2_indexed(swf_id, w, h, rgba)
    return build_define_bits_lossless2(swf_id, w, h, rgba)


def _build_define_sound_from_mp3(char_id: int, mp3_bytes: bytes) -> bytes:
    """Build a DefineSound tag from raw MP3 frame data.

    MP3 in SWF uses sound format 2 with a 2-byte SeekSamples prefix.
    We parse the first MP3 frame header to detect sample rate and channels.
    """
    if len(mp3_bytes) < 4:
        return b''

    # Parse first MP3 frame header for rate/stereo info
    sample_rate = 44100
    num_channels = 2
    hdr = struct.unpack_from('>I', mp3_bytes, 0)[0]
    if (hdr >> 21) & 0x7FF == 0x7FF:  # sync word
        version = (hdr >> 19) & 0x3
        layer = (hdr >> 17) & 0x3
        rate_idx = (hdr >> 10) & 0x3
        mode = (hdr >> 6) & 0x3
        # MPEG1 rates
        rate_table = {0: 44100, 1: 48000, 2: 32000}
        if version == 3:  # MPEG1
            sample_rate = rate_table.get(rate_idx, 44100)
        elif version == 2:  # MPEG2
            rate_table2 = {0: 22050, 1: 24000, 2: 16000}
            sample_rate = rate_table2.get(rate_idx, 22050)
        num_channels = 1 if mode == 3 else 2

    # SWF rate code
    rate_map = {5512: 0, 11025: 1, 22050: 2, 44100: 3}
    swf_rate = 3
    for sr, code in sorted(rate_map.items()):
        if sample_rate <= sr:
            swf_rate = code
            break

    is_stereo = 1 if num_channels >= 2 else 0
    # SWF format 2 = MP3, always 16-bit
    flags = (2 << 4) | (swf_rate << 2) | (1 << 1) | is_stereo

    # Estimate sample count (rough: MP3 frame = 1152 samples for MPEG1 Layer3)
    samples_per_frame = 1152
    # Count sync words roughly
    frame_count = 0
    pos = 0
    while pos < len(mp3_bytes) - 1:
        if mp3_bytes[pos] == 0xFF and (mp3_bytes[pos + 1] & 0xE0) == 0xE0:
            frame_count += 1
            pos += 4  # skip at least header
        else:
            pos += 1
    sample_count = frame_count * samples_per_frame

    body = io.BytesIO()
    body.write(struct.pack("<H", char_id))
    body.write(struct.pack("<B", flags))
    body.write(struct.pack("<I", sample_count))
    # MP3 sound data: 2-byte SeekSamples (0) + MP3 frames
    body.write(struct.pack("<H", 0))  # SeekSamples
    body.write(mp3_bytes)
    return build_tag(TAG_DEFINE_SOUND, body.getvalue())


def _build_mp3_sound_body(mp3_bytes: bytes) -> Optional[bytes]:
    """Build a DefineSound body (without charId) from raw MP3 data.

    Returns the flags + sampleCount + seekSamples + mp3Data bytes,
    suitable for embedding in a DefineSound tag.
    """
    if len(mp3_bytes) < 4:
        return None

    sample_rate = 44100
    num_channels = 2
    hdr = struct.unpack_from('>I', mp3_bytes, 0)[0]
    if (hdr >> 21) & 0x7FF == 0x7FF:
        version = (hdr >> 19) & 0x3
        rate_idx = (hdr >> 10) & 0x3
        mode = (hdr >> 6) & 0x3
        if version == 3:
            rate_table = {0: 44100, 1: 48000, 2: 32000}
            sample_rate = rate_table.get(rate_idx, 44100)
        elif version == 2:
            rate_table2 = {0: 22050, 1: 24000, 2: 16000}
            sample_rate = rate_table2.get(rate_idx, 22050)
        num_channels = 1 if mode == 3 else 2

    rate_map = {5512: 0, 11025: 1, 22050: 2, 44100: 3}
    swf_rate = 3
    for sr, code in sorted(rate_map.items()):
        if sample_rate <= sr:
            swf_rate = code
            break

    is_stereo = 1 if num_channels >= 2 else 0
    flags = (2 << 4) | (swf_rate << 2) | (1 << 1) | is_stereo

    samples_per_frame = 1152
    frame_count = 0
    pos = 0
    while pos < len(mp3_bytes) - 1:
        if mp3_bytes[pos] == 0xFF and (mp3_bytes[pos + 1] & 0xE0) == 0xE0:
            frame_count += 1
            pos += 4
        else:
            pos += 1
    sample_count = frame_count * samples_per_frame

    body = io.BytesIO()
    body.write(struct.pack("<B", flags))
    body.write(struct.pack("<I", sample_count))
    body.write(struct.pack("<H", 0))  # SeekSamples
    body.write(mp3_bytes)
    return body.getvalue()


def _build_wav_sound_body(wav_bytes: bytes) -> Optional[bytes]:
    """Build a DefineSound body (without charId) from WAV data.

    Returns the flags + sampleCount + pcmData bytes,
    suitable for embedding in a DefineSound tag.
    """
    if len(wav_bytes) < 44:
        return None

    # Parse WAV header
    if wav_bytes[:4] != b'RIFF' or wav_bytes[8:12] != b'WAVE':
        return None

    # Find fmt chunk
    pos = 12
    fmt_data = None
    data_bytes = None
    while pos < len(wav_bytes) - 8:
        chunk_id = wav_bytes[pos:pos+4]
        chunk_size = struct.unpack_from('<I', wav_bytes, pos+4)[0]
        if chunk_id == b'fmt ':
            fmt_data = wav_bytes[pos+8:pos+8+chunk_size]
        elif chunk_id == b'data':
            data_bytes = wav_bytes[pos+8:pos+8+chunk_size]
        pos += 8 + chunk_size
        if fmt_data and data_bytes:
            break

    if not fmt_data or not data_bytes:
        return None

    audio_format = struct.unpack_from('<H', fmt_data, 0)[0]
    num_channels = struct.unpack_from('<H', fmt_data, 2)[0]
    sample_rate = struct.unpack_from('<I', fmt_data, 4)[0]
    bits_per_sample = struct.unpack_from('<H', fmt_data, 14)[0]

    if audio_format != 1:  # PCM only
        return None

    rate_map = {5512: 0, 11025: 1, 22050: 2, 44100: 3}
    swf_rate = 3
    for sr, code in sorted(rate_map.items()):
        if sample_rate <= sr:
            swf_rate = code
            break

    is_16bit = 1 if bits_per_sample == 16 else 0
    is_stereo = 1 if num_channels >= 2 else 0
    # format 3 = uncompressed little-endian
    flags = (3 << 4) | (swf_rate << 2) | (is_16bit << 1) | is_stereo

    bytes_per_sample = (bits_per_sample // 8) * num_channels
    sample_count = len(data_bytes) // bytes_per_sample if bytes_per_sample else 0

    body = io.BytesIO()
    body.write(struct.pack("<B", flags))
    body.write(struct.pack("<I", sample_count))
    body.write(data_bytes)
    return body.getvalue()


def _load_external_sound(project_dir: str, lib: dict, swf_id: int) -> Optional[bytes]:
    """Load an external MP3/WAV and return the raw SWF DefineSound tag bytes.

    Returns None if no external file found.
    """
    ext_file = lib.get('externalFile', '')
    if not ext_file:
        return None
    fpath = os.path.join(project_dir, ext_file)
    if not os.path.isfile(fpath):
        return None

    with open(fpath, 'rb') as f:
        audio_bytes = f.read()

    if not audio_bytes:
        return None

    ext_lower = ext_file.lower()
    if ext_lower.endswith('.mp3'):
        return _build_define_sound_from_mp3(swf_id, audio_bytes)
    elif ext_lower.endswith('.wav'):
        return build_define_sound(swf_id, audio_bytes)

    return None


# ── toPublish equivalent ─────────────────────────────────────────────────

def _compute_total_frames(lib: dict) -> int:
    """Compute the total frame count from layer character spans.

    MovieClip.totalFrame in Next2D is a computed getter (max endFrame − 1).
    It is NOT serialised by toObject(), so after _merge_editor_into_disk the
    'totalFrame' key is absent and must be re-derived from the layer data.

    endFrame values in N2D are *exclusive* (character on frames 1-10 has
    endFrame=11), so the correct count is  max(endFrame) − 1.
    """
    max_end = 2  # sentinel: endFrame=2 → 1 frame (the minimum useful clip)
    for layer in lib.get('layers', []):
        for char in layer.get('characters', []):
            ef = char.get('endFrame', 2)
            if ef > max_end:
                max_end = ef
        for char in layer.get('emptyCharacters', []):
            ef = char.get('endFrame', 2)
            if ef > max_end:
                max_end = ef
    return max(1, max_end - 1)


def _get_place(places_list: List[dict], frame: int) -> Optional[dict]:
    """Return the place data for `frame` (nearest earlier keyframe)."""
    best = None
    for pl in places_list:
        if pl["frame"] <= frame:
            if best is None or pl["frame"] > best["frame"]:
                best = pl
    return best


def _has_exact_place(places_list: List[dict], frame: int) -> bool:
    return any(pl["frame"] == frame for pl in places_list)


def to_publish(container: dict, lib_to_char_idx: Dict[int, int],
               id_to_lib: Optional[Dict[int, dict]] = None) -> dict:
    """
    Python port of the tool's toPublish() method.

    Converts layers/characters/places → controller/dictionary/placeMap/placeObjects
    that the SWF timeline builder expects.
    """
    log.debug("to_publish: container id=%s layers=%d", container.get('id'), len(container.get('layers', [])))
    # Build set of morphShape lib IDs for ratio computation
    morph_lib_ids: Set[int] = set()
    if id_to_lib:
        for lid, lib in id_to_lib.items():
            if lib.get("isMorphShape"):
                morph_lib_ids.add(lid)
    layers = container.get("layers", [])
    dictionary: List[dict] = []

    # ── Pre-compute clip_depth for MASK layers ──
    # N2D stores mode=1 (MASK) for masking layers and mode=2 (MASK_IN) for
    # masked layers.  SWF uses clipDepth on the mask PlaceObject to specify
    # the depth range it clips.  Walk layers (in N2D order, top-to-bottom)
    # to find MASK→MASK_IN groups and compute the SWF clipDepth.
    mask_clip_depth: Dict[int, int] = {}  # swfDepth → clipDepth
    i_layer = 0
    while i_layer < len(layers):
        layer = layers[i_layer]
        if layer.get("mode") == 1:  # MASK
            mask_depth = layer.get("swfDepth")
            # Find consecutive MASK_IN layers following this MASK
            last_masked_depth = mask_depth  # fallback to own depth
            j = i_layer + 1
            while j < len(layers) and layers[j].get("mode") == 2:
                d = layers[j].get("swfDepth")
                if d is not None and d > last_masked_depth:
                    last_masked_depth = d
                j += 1
            if mask_depth is not None:
                # SWF clipDepth is typically last_masked_depth + 1 to form
                # an exclusive range, but original SWFs use the exact depth
                # of the last masked layer + gap.  From the OG data:
                #   mask depth=1, MASK_IN depth=2 → clipDepth=3
                #   mask depth=4, MASK_IN depth=5 → clipDepth=6
                # Pattern: clipDepth = last_masked_depth + 1
                mask_clip_depth[mask_depth] = last_masked_depth + 1
        i_layer += 1
    # Use dicts keyed by frame to build sparse arrays
    ctrl: Dict[int, Dict[int, int]] = {}   # frame → {depth: dict_idx}
    pmap: Dict[int, Dict[int, int]] = {}   # frame → {depth: po_idx}
    place_objects: List[dict] = []

    p = 0  # accumulated depth offset across layers

    # Iterate layers bottom-to-top (reversed)
    for layer in reversed(layers):
        if layer.get("disable", False):
            p += 1
            continue
        if layer.get("mode") == 3:  # GUIDE
            p += 1
            continue

        # Use original SWF depth if preserved, else sequential fallback
        swf_depth_val = layer.get('swfDepth')
        if swf_depth_val is not None:
            layer_depth = swf_depth_val - 1  # convert 1-based SWF depth to 0-based key
        else:
            layer_depth = p

        characters = layer.get("characters", [])

        for char in characters:
            dict_idx = len(dictionary)
            lib_id = char["libraryId"]
            char_idx = lib_to_char_idx.get(lib_id)
            if char_idx is None:
                # Referenced library not in character map — skip
                continue

            sf = char["startFrame"]
            ef = char["endFrame"]

            # Compute SWF clipDepth from MASK layer analysis
            clip_depth_val = 0
            if layer.get("mode") == 1:  # MASK layer
                swf_d = layer.get("swfDepth")
                if swf_d is not None and swf_d in mask_clip_depth:
                    clip_depth_val = mask_clip_depth[swf_d]

            dictionary.append({
                "name": char.get("name", ""),
                "characterId": char_idx,
                "startFrame": sf,
                "endFrame": ef,
                "clipDepth": clip_depth_val,
                "reinstated": char.get("reinstated", False),
            })

            places_list = char.get("places", [])
            last_po_idx = 0

            # Check if this character is a morph shape
            is_morph = lib_id in morph_lib_ids
            morph_tween_start = sf  # frame where this morph tween begins

            for frame in range(sf, ef):
                place = _get_place(places_list, frame)
                if place is None:
                    continue

                if frame not in ctrl:
                    ctrl[frame] = {}
                if frame not in pmap:
                    pmap[frame] = {}

                # If exact keyframe, create new placeObject
                if _has_exact_place(places_list, frame):
                    last_po_idx = len(place_objects)
                    # Only strip identity colorTransform on the FIRST
                    # keyframe (initial placement).  On later keyframes the
                    # identity CXFORM may be deliberately resetting a
                    # non-identity CXFORM from an earlier frame.
                    raw_ct = place.get("colorTransform")
                    if frame == sf and (
                        raw_ct == [1, 1, 1, 1, 0, 0, 0, 0]
                        or raw_ct == [1.0, 1.0, 1.0, 1.0, 0, 0, 0, 0]
                    ):
                        raw_ct = None
                    po_entry = {
                        "matrix": place.get("matrix", [1, 0, 0, 1, 0, 0]),
                        "colorTransform": raw_ct,
                        "blendMode": place.get("blendMode", "normal"),
                        "surfaceFilterList": place.get("filter") or None,
                    }
                    # Pass through ratio from OG PlaceObject if stored
                    if place.get("ratio") is not None:
                        po_entry["ratio"] = place["ratio"]
                    # For morph shapes, compute ratio based on frame
                    # within the tween span
                    elif is_morph:
                        morph_dur = ef - sf
                        if morph_dur > 1:
                            frame_in_tween = frame - morph_tween_start
                            po_entry["ratio"] = int(65536 * frame_in_tween / morph_dur)
                        else:
                            po_entry["ratio"] = 0
                    place_objects.append(po_entry)
                elif is_morph:
                    # Non-keyframe in morph tween: emit a new placeObject
                    # with updated ratio
                    morph_dur = ef - sf
                    frame_in_tween = frame - morph_tween_start
                    ratio_val = int(65536 * frame_in_tween / morph_dur)
                    last_po_idx = len(place_objects)
                    raw_ct_m = place.get("colorTransform")
                    if frame == sf and (
                        raw_ct_m == [1, 1, 1, 1, 0, 0, 0, 0]
                        or raw_ct_m == [1.0, 1.0, 1.0, 1.0, 0, 0, 0, 0]
                    ):
                        raw_ct_m = None
                    place_objects.append({
                        "matrix": place.get("matrix", [1, 0, 0, 1, 0, 0]),
                        "colorTransform": raw_ct_m,
                        "blendMode": place.get("blendMode", "normal"),
                        "surfaceFilterList": place.get("filter") or None,
                        "ratio": ratio_val,
                    })

                depth = layer_depth + place.get("depth", 0)
                ctrl[frame][depth] = dict_idx
                pmap[frame][depth] = last_po_idx

        p += 1

    # Build compacted arrays
    if not ctrl:
        return {
            "dictionary": [], "controller": [],
            "placeMap": [], "placeObjects": [],
        }

    max_frame = max(ctrl.keys())
    controller_out: List[Optional[List]] = [None] * (max_frame + 1)
    placemap_out: List[Optional[List]] = [None] * (max_frame + 1)
    depthkeys_out: List[Optional[List]] = [None] * (max_frame + 1)

    for frame in range(1, max_frame + 1):
        if frame in ctrl:
            # Sort by depth to maintain consistent ordering
            depths = sorted(ctrl[frame].keys())
            controller_out[frame] = [ctrl[frame][d] for d in depths]
            placemap_out[frame] = [pmap[frame][d] for d in depths]
            depthkeys_out[frame] = list(depths)

    return {
        "dictionary": dictionary,
        "controller": controller_out,
        "placeMap": placemap_out,
        "placeObjects": place_objects,
        "depthKeys": depthkeys_out,
    }


# ── Bitmap → DefineShape3 with bitmap fill ───────────────────────────────

def build_bitmap_fill_shape(
    shape_id: int, bitmap_id: int,
    w: int, h: int,
) -> bytes:
    """Build a DefineShape3 that renders a bitmap fill covering w×h pixels."""
    log.debug("build_bitmap_fill_shape: shape_id=%d bitmap_id=%d %dx%d", shape_id, bitmap_id, w, h)
    xmin_tw = 0
    ymin_tw = 0
    xmax_tw = twips(w)
    ymax_tw = twips(h)

    body = io.BytesIO()
    body.write(struct.pack("<H", shape_id))
    body.write(write_rect(xmin_tw, xmax_tw, ymin_tw, ymax_tw))

    # Fill style array: 1 clipped bitmap fill
    body.write(struct.pack("<B", 1))       # count = 1
    body.write(struct.pack("<B", 0x41))    # type = clipped bitmap (non-smoothed)
    body.write(struct.pack("<H", bitmap_id))
    # Bitmap fill matrix: identity at 20 twips/pixel
    body.write(write_matrix(20.0, 0, 0, 20.0, 0, 0))

    # Line style array: empty
    body.write(struct.pack("<B", 0))

    # Shape records: rectangle
    bw = BitWriter()
    num_fill_bits = 1
    num_line_bits = 0
    bw.write_ub(4, num_fill_bits)
    bw.write_ub(4, num_line_bits)

    # StyleChange: move to (0, 0), set FillStyle0 = 1
    bw.write_ub(1, 0)  # non-edge
    bw.write_ub(5, 0x03)  # StateMoveTo + StateFillStyle0
    bw.write_ub(5, 1)  # MoveBits = 1
    bw.write_sb(1, 0)
    bw.write_sb(1, 0)
    bw.write_ub(num_fill_bits, 1)  # FillStyle0 = 1

    # Line right (dx = xmax_tw)
    dx = xmax_tw
    bw.write_ub(1, 1); bw.write_ub(1, 1)  # edge, straight
    nb = max(_nbits_signed_list([dx]), 2) - 2
    bw.write_ub(4, nb)
    bw.write_ub(1, 0); bw.write_ub(1, 0)  # horiz
    bw.write_sb(nb + 2, dx)

    # Line down (dy = ymax_tw)
    dy = ymax_tw
    bw.write_ub(1, 1); bw.write_ub(1, 1)
    nb = max(_nbits_signed_list([dy]), 2) - 2
    bw.write_ub(4, nb)
    bw.write_ub(1, 0); bw.write_ub(1, 1)  # vert
    bw.write_sb(nb + 2, dy)

    # Line left (dx = -xmax_tw)
    bw.write_ub(1, 1); bw.write_ub(1, 1)
    nb = max(_nbits_signed_list([-dx]), 2) - 2
    bw.write_ub(4, nb)
    bw.write_ub(1, 0); bw.write_ub(1, 0)  # horiz
    bw.write_sb(nb + 2, -dx)

    # Line up (dy = -ymax_tw)
    bw.write_ub(1, 1); bw.write_ub(1, 1)
    nb = max(_nbits_signed_list([-dy]), 2) - 2
    bw.write_ub(4, nb)
    bw.write_ub(1, 0); bw.write_ub(1, 1)  # vert
    bw.write_sb(nb + 2, -dy)

    # End shape
    bw.write_ub(6, 0)
    body.write(bw.get_bytes())

    return build_tag(TAG_DEFINE_SHAPE3, body.getvalue())


# ── Timeline builder ─────────────────────────────────────────────────────

def build_timeline_tags(
    total_frames: int,
    tp: dict,
    labels: List[dict],
    actions: List[dict],
    char_id_map: Dict[int, int],
    bitmap_char_ids: Optional[Set[int]] = None,
) -> bytes:
    """
    Build SWF timeline tags (PlaceObject2/3, RemoveObject2, ShowFrame, etc.)
    from toPublish() output.

    char_id_map: character_array_index → SWF character ID
    """
    log.debug("build_timeline_tags: total_frames=%d labels=%d actions=%d", total_frames, len(labels or []), len(actions or []))
    controller = tp["controller"]
    dictionary = tp["dictionary"]
    place_map = tp["placeMap"]
    place_objects = tp["placeObjects"]
    depth_keys = tp.get("depthKeys")

    labels_by_frame: Dict[int, str] = {}
    for lbl in (labels or []):
        labels_by_frame[lbl["frame"]] = lbl["name"]

    actions_by_frame: Dict[int, str] = {}
    for act in (actions or []):
        actions_by_frame[act["frame"]] = act.get("action", "")

    out = bytearray()
    prev_display: Dict[int, Tuple[int, int, int]] = {}  # swf_depth → (dict_idx, swf_char_id, po_idx)

    for frame in range(1, total_frames + 1):
        # Current display list
        frame_ctrl = controller[frame] if frame < len(controller) and controller[frame] is not None else None
        frame_pm = place_map[frame] if frame < len(place_map) and place_map[frame] is not None else None
        frame_dk = None
        if depth_keys and frame < len(depth_keys):
            frame_dk = depth_keys[frame]

        cur_display: Dict[int, Tuple[int, int, int]] = {}

        # ----- Two-pass emission: collect removes + places separately -----
        # OG SWF emits: RemoveObject2 ... FrameLabel ... PlaceObject2 ...
        # We need to collect all removes first, then emit them before the label.

        remove_buf = bytearray()
        place_buf = bytearray()

        if frame_ctrl and frame_pm:
            for slot_idx, dict_idx in enumerate(frame_ctrl):
                if dict_idx is None:
                    continue
                if dict_idx < 0 or dict_idx >= len(dictionary):
                    continue

                tag_info = dictionary[dict_idx]
                char_array_idx = tag_info.get("characterId", 0)
                swf_char_id = char_id_map.get(char_array_idx, 1)
                # Use stable depth key if available, otherwise fall back to slot index
                if frame_dk and slot_idx < len(frame_dk):
                    swf_depth = frame_dk[slot_idx] + 1  # depth keys are 0-based, SWF depths are 1-based
                else:
                    swf_depth = slot_idx + 1

                # Place object data
                po_idx = frame_pm[slot_idx] if slot_idx < len(frame_pm) else None

                cur_display[swf_depth] = (dict_idx, swf_char_id, po_idx)

                # Skip PlaceObject emission if this depth is unchanged from
                # the previous frame (same character AND same placeObject)
                if swf_depth in prev_display:
                    prev_dict, prev_char, prev_po = prev_display[swf_depth]
                    if prev_char == swf_char_id and prev_po == po_idx:
                        continue  # nothing changed — character persists via ShowFrame

                po = place_objects[po_idx] if (
                    po_idx is not None and 0 <= po_idx < len(place_objects)
                ) else {}

                # Matrix
                mat_data = po.get("matrix")
                if mat_data and len(mat_data) >= 6:
                    mat_bytes = write_matrix(
                        mat_data[0], mat_data[1], mat_data[2],
                        mat_data[3], mat_data[4], mat_data[5],
                    )
                else:
                    mat_bytes = write_matrix()

                # Color transform
                ct_data = po.get("colorTransform")
                ct_bytes = None
                if ct_data and len(ct_data) >= 8:
                    ct_bytes = write_cxform_alpha(
                        ct_data[0], ct_data[1], ct_data[2], ct_data[3],
                        ct_data[4], ct_data[5], ct_data[6], ct_data[7],
                    )

                # Blend mode
                blend_str = po.get("blendMode")
                blend_mode = NEXT2D_BLEND_MAP.get(blend_str) if blend_str else None
                # Blend mode 1 (normal) doesn't need PO3 — treat as None
                if blend_mode == 1:
                    blend_mode = None
                # "normal" (1) is the default — no need to upgrade to PO3
                if blend_mode == 1:
                    blend_mode = None

                # Filters
                filters = po.get("surfaceFilterList")
                filter_bytes = encode_filter_list(filters) if filters else None

                # Morph ratio
                po_ratio = po.get("ratio")

                # Move vs place
                was_present = swf_depth in prev_display

                if was_present:
                    prev_dict, prev_char, prev_po = prev_display[swf_depth]
                    # The 'reinstated' flag means the OG SWF used
                    # RemoveObject2 + PlaceObject (new instance) at this span start.
                    # Only trigger remove+place on the FIRST frame of a reinstated
                    # span (when dict_idx changes), not on every frame within it.
                    is_reinstated = tag_info.get("reinstated", False)
                    dict_changed = (prev_dict != dict_idx)

                    if is_reinstated and dict_changed:
                        # OG pattern: remove old then place fresh (new instance)
                        remove_buf.extend(build_remove_object2(swf_depth))
                        is_move = False
                        place_char_id = swf_char_id
                    elif prev_char != swf_char_id:
                        # Different character at same depth — swap in-place
                        # using PlaceObject with MOVE + character_id.
                        is_move = True
                        place_char_id = swf_char_id
                    else:
                        # Same instance, same char — just update transform
                        is_move = True
                        place_char_id = None
                else:
                    is_move = False
                    place_char_id = swf_char_id

                instance_name = tag_info.get("name") or None

                # clipDepth: only set on initial placement (not move updates)
                po_clip_depth = tag_info.get("clipDepth", 0) if not is_move else None
                if po_clip_depth == 0:
                    po_clip_depth = None

                # Only use PO3+has_image when actually placing/changing a bitmap character,
                # not for move-only updates (same character, different transform)
                is_bitmap_place = (bitmap_char_ids is not None
                                   and swf_char_id in bitmap_char_ids
                                   and place_char_id is not None)
                needs_po3 = (blend_mode is not None) or (filter_bytes is not None) or is_bitmap_place

                if needs_po3:
                    tag_bytes = build_place_object3(
                        depth=swf_depth,
                        character_id=place_char_id,
                        matrix=mat_bytes,
                        color_transform=ct_bytes,
                        name=instance_name if not is_move else None,
                        blend_mode=blend_mode,
                        filters_data=filter_bytes,
                        is_move=is_move,
                        ratio=po_ratio,
                        has_image=is_bitmap_place,
                        clip_depth=po_clip_depth,
                    )
                else:
                    tag_bytes = build_place_object2(
                        depth=swf_depth,
                        character_id=place_char_id,
                        matrix=mat_bytes,
                        color_transform=ct_bytes,
                        name=instance_name if not is_move else None,
                        is_move=is_move,
                        ratio=po_ratio,
                        clip_depth=po_clip_depth,
                    )
                place_buf.extend(tag_bytes)

        # Emit "no longer present" removes
        for depth in sorted(prev_display):
            if depth not in cur_display:
                remove_buf.extend(build_remove_object2(depth))

        # Final emission order: removes → frame label → places → ShowFrame
        out.extend(remove_buf)
        if frame in labels_by_frame:
            out.extend(build_frame_label(labels_by_frame[frame]))
        out.extend(place_buf)

        # ShowFrame
        out.extend(build_tag_show_frame())
        prev_display = cur_display

    return bytes(out)


# ── AS3 compilation ──────────────────────────────────────────────────────

def _sanitize_class_name(sym: str) -> str:
    """Convert a symbol export name to a valid AS3 class identifier.
    Preserves dots (package separators in fully-qualified AS3 names)."""
    name = re.sub(r'[^a-zA-Z0-9_.]', '_', sym)
    if name and name[0].isdigit():
        name = '_' + name
    return name or '_unnamed'


def _escape_as3_string(s: str) -> str:
    """Escape a string for embedding in AS3 source code."""
    return (s.replace('\\', '\\\\')
             .replace('"', '\\"')
             .replace('\n', '\\n')
             .replace('\r', '\\r')
             .replace('\t', '\\t'))


def _strip_block_comments(code: str) -> str:
    """Remove all block comments (/* ... */) from code, handling unbalanced ones."""
    result = []
    i = 0
    in_line_comment = False
    in_string_sq = False
    in_string_dq = False

    while i < len(code):
        c = code[i]

        # Handle string literals (don't strip comments inside strings)
        if not in_line_comment and c == '"' and not in_string_sq:
            in_string_dq = not in_string_dq
            result.append(c)
            i += 1
            continue
        if not in_line_comment and c == "'" and not in_string_dq:
            in_string_sq = not in_string_sq
            result.append(c)
            i += 1
            continue
        if in_string_dq or in_string_sq:
            if c == '\\':
                result.append(c)
                i += 1
                if i < len(code):
                    result.append(code[i])
                    i += 1
                continue
            result.append(c)
            i += 1
            continue

        # Block comment open
        if code[i:i+2] == '/*':
            # Skip until */ or end of string
            i += 2
            while i < len(code) - 1:
                if code[i:i+2] == '*/':
                    i += 2
                    break
                i += 1
            else:
                # Reached end without closing — just skip remaining
                i = len(code)
            continue

        # Line comment — keep it (they're harmless)
        result.append(c)
        i += 1

    return ''.join(result)


def _extract_toplevel_functions(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    Extract top-level function declarations from code lines.

    Returns (remaining_lines, extracted_function_texts).
    Only extracts functions at indent level 0 (no leading whitespace or tab).
    Handles opening brace on same line or next line.
    """
    remaining = []
    functions = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        # Match: function name(...) at the start of the line (no indentation)
        if re.match(r'^function\s+\w+\s*\(', stripped):
            # Collect the function signature + body
            func_lines = [lines[i]]
            brace_count = lines[i].count('{') - lines[i].count('}')
            i += 1

            if brace_count == 0:
                # Opening brace might be on next line
                while i < len(lines):
                    func_lines.append(lines[i])
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    i += 1
                    if brace_count > 0:
                        break
                if brace_count == 0:
                    # Never found opening brace — not a real function decl,
                    # put back into remaining
                    remaining.extend(func_lines)
                    continue

            # Now collect until braces balance
            while i < len(lines) and brace_count > 0:
                func_lines.append(lines[i])
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1

            functions.append('\n'.join(func_lines))
            continue

        remaining.append(lines[i])
        i += 1

    return remaining, functions


def _extract_toplevel_vars(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    Extract top-level var declarations from code lines.

    Only extracts `var name...;` at indent level 0 (starts at column 0).
    Returns (remaining_lines, extracted_var_declarations).
    """
    remaining = []
    var_decls = []
    seen_vars: Set[str] = set()

    for line in lines:
        stripped = line.strip()
        # Must start at indent 0 (or just whitespace prefix ≤ 0)
        # and be a var declaration ending with ;
        if stripped.startswith('var ') and stripped.endswith(';'):
            var_match = re.match(r'^var\s+(\w+)', stripped)
            if var_match:
                var_name = var_match.group(1)
                if var_name not in seen_vars:
                    seen_vars.add(var_name)
                    var_decls.append(stripped)
                remaining.append(line)  # keep in body too for initialization
                continue
        remaining.append(line)

    return remaining, var_decls


def _extract_imports(lines: List[str]) -> Tuple[List[str], Set[str]]:
    """Extract import statements from code lines."""
    remaining = []
    imports: Set[str] = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import '):
            imports.add(stripped)
        else:
            remaining.append(line)

    return remaining, imports


def generate_symbol_stubs(
    libs: List[dict],
    stub_dir: str,
    project_name: str = "",
) -> Dict[str, str]:
    """
    Generate AS3 class stub files for all exported symbols.

    For containers with explicit linkageClassName (symbol set), use that name
    in the default package.

    For containers without linkage but WITH frame scripts, generate a
    class in the projectname_fla package (e.g. gameandwatch_fla.Idle_3),
    matching Flash IDE behavior.

    Returns: dict mapping lib_id_str → AS3 fully-qualified class name
             (e.g. "5" → "gameandwatch_fla.Idle_3" or "gnw_idle0")
    """
    log.debug("generate_symbol_stubs: %d libs, project=%s", len(libs), project_name)
    sym_to_class: Dict[str, str] = {}  # symbol_name → class_name (default pkg)
    fla_classes: Dict[int, str] = {}   # lib_id → fla class name (for containers w/ scripts)
    used_classes: Set[str] = set()
    # Track lowercase versions to avoid case-insensitive filesystem collisions
    used_classes_lower: Set[str] = set()

    # Determine _fla package name from project
    fla_pkg = f"{project_name}_fla" if project_name else ""

    for lib in libs:
        sym = lib.get('symbol', '')
        lib_type = lib['type']
        lib_id = lib['id']

        # Containers without explicit linkage but with frame scripts
        # get auto-generated _fla package classes (like Flash IDE does)
        if not sym and lib_type == 'container' and lib_id != 0 and fla_pkg:
            actions = [a for a in lib.get('actions', []) if a.get('action', '').strip()]
            if actions:
                # Generate class name: ProjectName_fla.SymbolName_N
                display = lib.get('name', '')
                # Clean display name: Flash IDE converts hyphens, periods
                # and ampersands to underscores, then removes spaces and
                # any remaining non-alphanumeric/underscore characters.
                clean = display.replace('-', '_').replace('.', '_').replace('&', '_').replace(' ', '')
                clean = re.sub(r'[^a-zA-Z0-9_]', '', clean)
                if clean and clean[0].isdigit():
                    clean = '_' + clean
                fla_class = f"{clean}_{lib_id}"
                fla_fqn = f"{fla_pkg}.{fla_class}"
                fla_classes[lib_id] = fla_fqn
                # We'll generate these stubs below
            continue

        if not sym:
            continue
        if sym == 'Main':  # Document class — handled separately
            continue

        class_name = _sanitize_class_name(sym)
        # De-duplicate class names (case-insensitive for Windows FS)
        orig = class_name
        counter = 2
        while class_name in used_classes or class_name.lower() in used_classes_lower:
            class_name = f"{orig}_{counter}"
            counter += 1
        used_classes.add(class_name)
        used_classes_lower.add(class_name.lower())
        sym_to_class[sym] = class_name

        if lib_type == 'bitmap':
            default_w = int(lib.get('width', 0) or 0)
            default_h = int(lib.get('height', 0) or 0)
            # Extend BitmapData
            code = (
                f'package {{\n'
                f'    import flash.display.BitmapData;\n'
                f'    public class {class_name} extends BitmapData {{\n'
                f'        public function {class_name}(w:int={default_w}, h:int={default_h}) {{\n'
                f'            super(w, h);\n'
                f'        }}\n'
                f'    }}\n'
                f'}}\n'
            )
        elif lib_type == 'sound':
            # Extend Sound
            code = (
                f'package {{\n'
                f'    import flash.media.Sound;\n'
                f'    public class {class_name} extends Sound {{\n'
                f'        public function {class_name}() {{\n'
                f'            super();\n'
                f'        }}\n'
                f'    }}\n'
                f'}}\n'
            )
        elif lib_type == 'container':
            # Extend MovieClip, with addFrameScript for frame actions
            actions = [a for a in lib.get('actions', []) if a.get('action')]

            if actions:
                # Merge duplicate frame numbers (multiple layers can have
                # scripts on the same frame)
                frame_scripts_map: Dict[int, List[str]] = {}
                for act in actions:
                    f = act['frame']
                    if f not in frame_scripts_map:
                        frame_scripts_map[f] = []
                    frame_scripts_map[f].append(act['action'])

                # Pre-process all frame scripts:
                # 1. Strip block comments (handles unbalanced /* without */)
                # 2. Extract import statements → class-level
                # 3. Extract top-level function declarations → class methods
                # 4. Extract top-level var declarations → class members
                # 5. Remaining code → frame function bodies
                all_imports: Set[str] = set()
                all_imports.add('import flash.display.MovieClip;')
                all_imports.add('import flash.events.Event;')
                all_imports.add('import flash.display.DisplayObject;')
                all_var_decls: List[str] = []
                all_func_texts: List[str] = []
                frame_bodies: Dict[int, str] = {}
                seen_var_names: Set[str] = set()
                seen_func_names: Set[str] = set()

                for frame_num in sorted(frame_scripts_map.keys()):
                    merged = '\n'.join(frame_scripts_map[frame_num])

                    # Step 1: strip block comments
                    cleaned = _strip_block_comments(merged)

                    lines = cleaned.split('\n')

                    # Step 2: extract imports
                    lines, frame_imports = _extract_imports(lines)
                    all_imports.update(frame_imports)

                    # Step 3: extract top-level functions
                    lines, funcs = _extract_toplevel_functions(lines)
                    for func_text in funcs:
                        # Get function name to avoid duplicates
                        m = re.match(r'function\s+(\w+)', func_text.strip())
                        if m and m.group(1) not in seen_func_names:
                            seen_func_names.add(m.group(1))
                            all_func_texts.append(func_text)

                    # Step 4: extract top-level var declarations
                    lines, var_decls = _extract_toplevel_vars(lines)
                    for vd in var_decls:
                        vm = re.match(r'var\s+(\w+)', vd)
                        if vm and vm.group(1) not in seen_var_names:
                            seen_var_names.add(vm.group(1))
                            all_var_decls.append(vd)

                    # Step 5: remaining lines become frame body
                    frame_bodies[frame_num] = '\n'.join(lines)

                # Build addFrameScript calls and frame functions
                afs_lines = []
                frame_func_list = []
                for frame_num in sorted(frame_bodies.keys()):
                    frame_0based = frame_num - 1
                    func_name = 'frame_' + str(frame_num)
                    body = frame_bodies[frame_num].strip()
                    if not body:
                        body = '// (empty)'
                    afs_lines.append(
                        '            addFrameScript('
                        + str(frame_0based) + ', ' + func_name + ');'
                    )
                    body_indented = '\n'.join(
                        '            ' + bl for bl in body.split('\n')
                    )
                    frame_func_list.append(
                        '        internal function ' + func_name + '():* {\n'
                        + body_indented + '\n'
                        + '        }'
                    )

                # Build the class file
                imports_block = '\n'.join(
                    '    ' + imp for imp in sorted(all_imports)
                )
                vars_block = ''
                if all_var_decls:
                    vars_block = '\n'.join(
                        '        public ' + vd for vd in all_var_decls
                    )
                funcs_block = ''
                if all_func_texts:
                    formatted_funcs = []
                    for ft in all_func_texts:
                        # Indent function to class level
                        indented = '\n'.join(
                            '        ' + fline for fline in ft.split('\n')
                        )
                        formatted_funcs.append(indented)
                    funcs_block = '\n'.join(formatted_funcs)
                afs_block = '\n'.join(afs_lines)
                frame_funcs_block = '\n'.join(frame_func_list)

                parts = []
                parts.append('package {')
                parts.append(imports_block)
                parts.append('    public dynamic class '
                             + class_name + ' extends MovieClip {')
                if vars_block:
                    parts.append(vars_block)
                parts.append(
                    '        public function ' + class_name + '() {\n'
                    '            super();\n'
                    + afs_block + '\n'
                    '        }'
                )
                if funcs_block:
                    parts.append(funcs_block)
                parts.append(frame_funcs_block)
                parts.append('    }')
                parts.append('}')
                code = '\n'.join(parts) + '\n'
            else:
                code = (
                    'package {\n'
                    '    import flash.display.MovieClip;\n'
                    '    public dynamic class ' + class_name
                    + ' extends MovieClip {\n'
                    '        public function ' + class_name + '() {\n'
                    '            super();\n'
                    '        }\n'
                    '    }\n'
                    '}\n'
                )
        else:
            # Shape / text / other — generic Sprite
            code = (
                f'package {{\n'
                f'    import flash.display.Sprite;\n'
                f'    public class {class_name} extends Sprite {{\n'
                f'        public function {class_name}() {{\n'
                f'            super();\n'
                f'        }}\n'
                f'    }}\n'
                f'}}\n'
            )

        filepath = os.path.join(stub_dir, class_name + '.as')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

    # ── Generate _fla package stubs for containers with frame scripts ──
    if fla_pkg and fla_classes:
        fla_dir = os.path.join(stub_dir, fla_pkg)
        os.makedirs(fla_dir, exist_ok=True)

        id_to_lib = {lib['id']: lib for lib in libs}
        for lib_id, fla_fqn in fla_classes.items():
            lib = id_to_lib[lib_id]
            # fla_fqn = "gameandwatch_fla.Idle_3"
            fla_class = fla_fqn.split('.')[-1]  # "Idle_3"

            actions = [a for a in lib.get('actions', []) if a.get('action', '').strip()]

            if actions:
                # Same frame-script processing as above for containers w/ actions
                frame_scripts_map: Dict[int, List[str]] = {}
                for act in actions:
                    f = act['frame']
                    if f not in frame_scripts_map:
                        frame_scripts_map[f] = []
                    frame_scripts_map[f].append(act['action'])

                all_imports_fla: Set[str] = set()
                all_imports_fla.add('import flash.display.MovieClip;')
                all_imports_fla.add('import flash.events.Event;')
                all_imports_fla.add('import flash.display.DisplayObject;')
                all_var_decls_fla: List[str] = []
                all_func_texts_fla: List[str] = []
                frame_bodies_fla: Dict[int, str] = {}
                seen_var_names_fla: Set[str] = set()
                seen_func_names_fla: Set[str] = set()

                for frame_num in sorted(frame_scripts_map.keys()):
                    merged = '\n'.join(frame_scripts_map[frame_num])
                    cleaned = _strip_block_comments(merged)
                    lines = cleaned.split('\n')
                    lines, frame_imports = _extract_imports(lines)
                    all_imports_fla.update(frame_imports)
                    lines, funcs = _extract_toplevel_functions(lines)
                    for func_text in funcs:
                        m = re.match(r'function\s+(\w+)', func_text.strip())
                        if m and m.group(1) not in seen_func_names_fla:
                            seen_func_names_fla.add(m.group(1))
                            all_func_texts_fla.append(func_text)
                    lines, var_decls = _extract_toplevel_vars(lines)
                    for vd in var_decls:
                        vm = re.match(r'var\s+(\w+)', vd)
                        if vm and vm.group(1) not in seen_var_names_fla:
                            seen_var_names_fla.add(vm.group(1))
                            all_var_decls_fla.append(vd)
                    frame_bodies_fla[frame_num] = '\n'.join(lines)

                afs_lines_fla = []
                frame_func_list_fla = []
                for frame_num in sorted(frame_bodies_fla.keys()):
                    frame_0based = frame_num - 1
                    func_name = 'frame_' + str(frame_num)
                    body = frame_bodies_fla[frame_num].strip()
                    if not body:
                        body = '// (empty)'
                    afs_lines_fla.append(
                        '            addFrameScript('
                        + str(frame_0based) + ', ' + func_name + ');'
                    )
                    body_indented = '\n'.join(
                        '            ' + bl for bl in body.split('\n')
                    )
                    frame_func_list_fla.append(
                        '        internal function ' + func_name + '():* {\n'
                        + body_indented + '\n'
                        + '        }'
                    )

                imports_block_fla = '\n'.join(
                    '    ' + imp for imp in sorted(all_imports_fla)
                )
                vars_block_fla = ''
                if all_var_decls_fla:
                    vars_block_fla = '\n'.join(
                        '        public ' + vd for vd in all_var_decls_fla
                    )
                funcs_block_fla = ''
                if all_func_texts_fla:
                    formatted = []
                    for ft in all_func_texts_fla:
                        indented = '\n'.join(
                            '        ' + fline for fline in ft.split('\n')
                        )
                        formatted.append(indented)
                    funcs_block_fla = '\n'.join(formatted)
                afs_block_fla = '\n'.join(afs_lines_fla)
                frame_funcs_block_fla = '\n'.join(frame_func_list_fla)

                parts = []
                parts.append(f'package {fla_pkg} {{')
                parts.append(imports_block_fla)
                parts.append('    public dynamic class '
                             + fla_class + ' extends MovieClip {')
                if vars_block_fla:
                    parts.append(vars_block_fla)
                parts.append(
                    '        public function ' + fla_class + '() {\n'
                    '            super();\n'
                    + afs_block_fla + '\n'
                    '        }'
                )
                if funcs_block_fla:
                    parts.append(funcs_block_fla)
                parts.append(frame_funcs_block_fla)
                parts.append('    }')
                parts.append('}')
                code = '\n'.join(parts) + '\n'
            else:
                code = (
                    f'package {fla_pkg} {{\n'
                    f'    import flash.display.MovieClip;\n'
                    f'    public dynamic class {fla_class}'
                    f' extends MovieClip {{\n'
                    f'        public function {fla_class}() {{\n'
                    f'            super();\n'
                    f'        }}\n'
                    f'    }}\n'
                    f'}}\n'
                )

            filepath = os.path.join(fla_dir, fla_class + '.as')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)

    return sym_to_class, fla_classes


def compile_as3(
    shared_dir: str,
    swc_path: str,
    sdk_path: str,
    libs: List[dict],
    main_class: str = "Main",
    project_name: str = "",
    embedded_scripts: Optional[List[dict]] = None,
) -> Tuple[bytes, Dict[str, str], Dict[int, str]]:
    """
    Generate AS3 class stubs for all exported symbols, then compile
    everything together with mxmlc.

    Returns: (doabc_tag_bytes, symbol_to_classname_map, fla_classes_map)
    """
    log.info("compile_as3: main_class=%s project=%s sdk=%s", main_class, project_name, sdk_path)
    mxmlc = os.path.join(sdk_path, "bin", "mxmlc.bat")
    if not os.path.isfile(mxmlc):
        mxmlc = os.path.join(sdk_path, "bin", "mxmlc")
    if not os.path.isfile(mxmlc):
        raise RuntimeError(f"mxmlc not found in {sdk_path}/bin/")

    with tempfile.TemporaryDirectory(prefix="n2d_as3_") as tmp_dir:
        # Generate class stubs in a subdirectory
        stub_dir = os.path.join(tmp_dir, "stubs")
        os.makedirs(stub_dir, exist_ok=True)

        print("  Generating AS3 class stubs...")
        sym_to_class, fla_classes = generate_symbol_stubs(libs, stub_dir, project_name)
        print(f"  Generated {len(sym_to_class)} class stubs + {len(fla_classes)} _fla classes")

        # Detect classes provided by the SWC so we don't override them
        # with decompiled source (which can produce incompatible bytecode).
        swc_classes: Set[str] = set()
        if os.path.isfile(swc_path):
            try:
                import zipfile as _zf
                with _zf.ZipFile(swc_path) as zswc:
                    if 'catalog.xml' in zswc.namelist():
                        cat_xml = zswc.read('catalog.xml').decode('utf-8')
                        swc_classes = set(re.findall(r'<def id="([^"]+)"', cat_xml))
                if swc_classes:
                    print(f"  SWC provides {len(swc_classes)} classes (will skip from embedded)")
            except Exception as e:
                print(f"  WARNING: Could not parse SWC catalog: {e}")

        # Write embedded scripts from N2D project to temp dir
        embedded_dir = os.path.join(tmp_dir, "embedded")
        os.makedirs(embedded_dir, exist_ok=True)
        skipped_swc = 0
        if embedded_scripts:
            for script in embedded_scripts:
                spath = script.get('path', '')
                source = script.get('source', '')
                if not spath or not source:
                    continue
                # Skip top-level scripts that the SWC already provides.
                # Sub-package scripts (e.g. gameandwatch_fla/Idle_3.as) are
                # never in the SWC so they're always written.
                if '/' not in spath and spath.endswith('.as'):
                    class_name = spath[:-3]
                    if class_name in swc_classes:
                        skipped_swc += 1
                        continue
                fpath = os.path.join(embedded_dir, spath)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                with open(fpath, 'w', encoding='utf-8') as sf:
                    sf.write(source)
            written = len(embedded_scripts) - skipped_swc
            msg = f"  Wrote {written} embedded scripts to temp dir"
            if skipped_swc:
                msg += f" (skipped {skipped_swc} SWC-provided)"
            print(msg)

        temp_swf = os.path.join(tmp_dir, "output.swf")

        env = os.environ.copy()
        env["FLEX_HOME"] = sdk_path
        player_home = os.path.join(sdk_path, "frameworks", "libs", "player")
        env["PLAYERGLOBAL_HOME"] = player_home

        # Prefer embedded Main.as (user-edited) over shared/ original
        main_as = os.path.join(embedded_dir, main_class + ".as")
        if not os.path.isfile(main_as):
            main_as = os.path.join(shared_dir, main_class + ".as")
        if not os.path.isfile(main_as):
            raise RuntimeError(f"Main class not found: {main_as}")

        cmd = [
            mxmlc,
            f"-source-path+={embedded_dir}",
            f"-source-path+={shared_dir}",
            f"-source-path+={stub_dir}",
            f"-target-player=25.0",
            "-static-link-runtime-shared-libraries",
            "-strict=false",
            f"-output={temp_swf}",
        ]

        # Add SWC as library
        if os.path.isfile(swc_path):
            cmd.append(f"-library-path+={swc_path}")
        else:
            print(f"  WARNING: SWC not found: {swc_path}", file=sys.stderr)

        # Use a config file for includes to avoid command-line-too-long
        # Auto-discover framework-style AS3 packages in shared_dir
        # (e.g. fl/motion/*.as -> fl.motion.AdjustColor)
        # These are classes not provided by the Flex SDK but needed at runtime.
        framework_classes = []
        for dirpath, _dirnames, filenames in os.walk(shared_dir):
            rel = os.path.relpath(dirpath, shared_dir)
            if rel == '.':
                continue  # skip top-level shared .as files (handled as stubs/main)
            pkg = rel.replace(os.sep, '.')
            for fn in filenames:
                if fn.endswith('.as'):
                    cls_name = fn[:-3]
                    fqn = f"{pkg}.{cls_name}"
                    framework_classes.append(fqn)
        if framework_classes:
            print(f"  Found {len(framework_classes)} framework classes: {', '.join(framework_classes)}")

        # Discover sub-package classes in embedded scripts dir
        # (e.g. gameandwatch_fla/*.as → gameandwatch_fla.Idle_3)
        embedded_classes = []
        if os.path.isdir(embedded_dir):
            for dirpath, _dn, filenames in os.walk(embedded_dir):
                rel = os.path.relpath(dirpath, embedded_dir)
                if rel == '.':
                    continue  # top-level .as handled as main / direct sources
                pkg = rel.replace(os.sep, '.')
                for fn in filenames:
                    if fn.endswith('.as'):
                        fqn = f"{pkg}.{fn[:-3]}"
                        embedded_classes.append(fqn)
        if embedded_classes:
            print(f"  Found {len(embedded_classes)} embedded sub-package classes")

        config_path = os.path.join(tmp_dir, "includes.cfg")
        with open(config_path, 'w', encoding='utf-8') as cfg:
            cfg.write('<flex-config>\n')
            cfg.write('  <includes append="true">\n')
            for class_name in sym_to_class.values():
                cfg.write(f'    <symbol>{class_name}</symbol>\n')
            # Include _fla package classes (from stub generation)
            for fla_fqn in fla_classes.values():
                cfg.write(f'    <symbol>{fla_fqn}</symbol>\n')
            # Include framework classes found in shared dir sub-packages
            for fw_fqn in framework_classes:
                cfg.write(f'    <symbol>{fw_fqn}</symbol>\n')
            # Include embedded sub-package classes (e.g. gameandwatch_fla)
            for emb_fqn in embedded_classes:
                cfg.write(f'    <symbol>{emb_fqn}</symbol>\n')
            cfg.write('  </includes>\n')
            cfg.write('</flex-config>\n')
        cmd.append(f"-load-config+={config_path}")

        cmd.append(main_as)

        total_stubs = len(sym_to_class) + len(fla_classes)
        total_includes = total_stubs + len(framework_classes) + len(embedded_classes)
        print(f"  Compiling {main_class}.as + {total_stubs} stubs + {len(framework_classes)} framework + {len(embedded_classes)} embedded classes with mxmlc...")
        result = subprocess.run(
            cmd, capture_output=True, text=True, env=env, shell=True,
        )

        if result.returncode != 0:
            print(f"  mxmlc stdout: {result.stdout}", file=sys.stderr)
            print(f"  mxmlc stderr: {result.stderr}", file=sys.stderr)
            # Show which stubs had errors
            for line in result.stderr.split('\n'):
                if 'Error' in line:
                    print(f"    {line}", file=sys.stderr)
            raise RuntimeError(
                f"mxmlc compilation failed (exit code {result.returncode})"
            )

        if not os.path.isfile(temp_swf):
            raise RuntimeError("mxmlc did not produce output SWF")

        print(f"  Compiled -> {os.path.getsize(temp_swf)} bytes")
        return extract_doabc_tags(temp_swf), sym_to_class, fla_classes


def extract_doabc_tags(swf_path: str) -> bytes:
    """Extract all DoABC/DoABC2 tags from a compiled SWF."""
    log.debug("extract_doabc_tags: %s", swf_path)
    TAG_DO_ABC_ID = 82
    TAG_DO_ABC_OLD = 72

    with open(swf_path, "rb") as f:
        sig = f.read(3)
        f.read(1)  # version
        f.read(4)  # file length
        rest = f.read()

    if sig == b"CWS":
        rest = zlib.decompress(rest)
    elif sig != b"FWS":
        raise ValueError(f"Not a SWF: {swf_path}")

    # Skip RECT header
    pos = 0
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4  # + frame rate + frame count

    doabc = bytearray()
    while pos < len(rest):
        tag_code_and_len = struct.unpack_from("<H", rest, pos)[0]
        tag_type = tag_code_and_len >> 6
        tag_len = tag_code_and_len & 0x3F
        pos += 2
        if tag_len == 0x3F:
            tag_len = struct.unpack_from("<I", rest, pos)[0]
            pos += 4

        if tag_type in (TAG_DO_ABC_ID, TAG_DO_ABC_OLD):
            tag_body = rest[pos:pos + tag_len]
            doabc.extend(build_tag(tag_type, bytes(tag_body)))

        if tag_type == 0:
            break
        pos += tag_len

    if not doabc:
        raise RuntimeError(f"No DoABC tags found in {swf_path}")

    return bytes(doabc)


# ── Main compiler class ──────────────────────────────────────────────────

class N2DCompiler:
    def __init__(self, n2d_path: str, shared_dir: str,
                 output_path: str, sdk_path: Optional[str] = None):
        log.debug('N2DCompiler.__init__: n2d=%s, shared=%s, output=%s', n2d_path, shared_dir, output_path)
        self.n2d_path = n2d_path
        self.shared_dir = os.path.abspath(shared_dir)
        self.output_path = output_path
        self.sdk_path = sdk_path or find_sdk()

        self.data: dict = {}
        self.stage: dict = {}
        self.libs: List[dict] = []
        self.id_to_lib: Dict[int, dict] = {}

        # SWF character ID allocation
        self._next_id = 1
        self._lib_to_swf_id: Dict[int, int] = {}     # n2d lib id → SWF char ID

        # Character array index mapping (for toPublish dictionary references)
        self._lib_to_char_idx: Dict[int, int] = {}   # n2d lib id → char array index
        self._char_idx_to_swf_id: Dict[int, int] = {}  # char array index → SWF char ID

        self._definition_tags = bytearray()
        self._project_dir: Optional[str] = None  # set if loading from project folder

    def _alloc_id(self) -> int:
        cid = self._next_id
        self._next_id += 1
        return cid

    def compile(self):
        """
        Compile N2D to SWF using the pipeline architecture.

        This method now delegates all work to the CompilationPipeline,
        which breaks the monolithic compilation process into discrete,
        testable stages.
        """
        from compilation_pipeline import create_default_pipeline, CompilationContext

        log.info('compile: starting compilation of %s (pipeline mode)', self.n2d_path)

        # Create compilation context
        ctx = CompilationContext(
            n2d_path=self.n2d_path,
            shared_dir=self.shared_dir,
            output_path=self.output_path,
            sdk_path=self.sdk_path
        )

        # Execute pipeline
        pipeline = create_default_pipeline()
        pipeline.execute(ctx)

    # ── ID assignment ────────────────────────────────────────────────────

    def _assign_ids(self):
        """
        Assign SWF character IDs and character array indices to all libraries.

        Adobe Animate emits tags in dependency order:
          1. All sounds first (chIDs 1..N_sounds)
          2. Walk the container dependency tree (leaves first); for each
             container, emit any not-yet-emitted bitmaps / shapes / text
             it references, then the container itself.
          3. Remaining unreferenced assets last.

        Bitmaps get two IDs (DefineBitsLossless2 + DefineShape3).
        Everything else gets one ID.  Main timeline (id=0) is the root
        and gets no SWF character ID.
        """
        log.debug("_assign_ids: %d libs total", len(self.libs))
        # ── 1. Assign character array indices (sequential, main=0) ──
        char_idx = 0
        self._lib_to_char_idx[0] = char_idx
        char_idx += 1

        for lib in self.libs:
            if lib["id"] == 0:
                continue
            if lib["type"] == "folder":
                continue
            self._lib_to_char_idx[lib["id"]] = char_idx
            char_idx += 1

        # ── 2. Determine the dependency-ordered emission sequence ──
        #    This list will hold lib ids in the order they should get
        #    SWF character IDs and be emitted as tags.
        self._emission_order: List[int] = []
        emitted: Set[int] = set()

        # Collect by type for quick lookup
        containers: Set[int] = set()
        all_non_folder: Dict[int, dict] = {}
        for lib in self.libs:
            if lib["type"] == "folder" or lib["id"] == 0:
                continue
            all_non_folder[lib["id"]] = lib
            if lib["type"] == "container":
                containers.add(lib["id"])

        # 2a. Sounds first
        for lib in self.libs:
            if lib["type"] == "sound" and lib["id"] != 0:
                self._emission_order.append(lib["id"])
                emitted.add(lib["id"])

        # 2b. Build full dependency graph for containers (what each
        #     container references — both container and non-container deps)
        container_all_deps: Dict[int, List[int]] = {}
        for lib in self.libs:
            if lib["type"] != "container" or lib["id"] == 0:
                continue
            deps: List[int] = []
            for layer in lib.get("layers", []):
                for char in layer.get("characters", []):
                    ref = char["libraryId"]
                    if ref in all_non_folder and ref != lib["id"]:
                        deps.append(ref)
            container_all_deps[lib["id"]] = deps

        # Also gather main timeline (id=0) deps — it references containers
        # that need to be emitted too
        main_lib = self.id_to_lib.get(0)
        main_deps: List[int] = []
        if main_lib:
            for layer in main_lib.get("layers", []):
                for char in layer.get("characters", []):
                    ref = char["libraryId"]
                    if ref in all_non_folder:
                        main_deps.append(ref)

        # 2c. Walk containers in dependency order (topological, leaves first)
        #     For each container, first emit its non-container deps that
        #     haven't been emitted yet, then the container.
        topo_order = self._container_order()  # leaves-first

        def _emit_deps(lib_id: int, _visiting: set = None):
            """Recursively emit all dependencies of a container."""
            if lib_id in emitted:
                return
            if _visiting is None:
                _visiting = set()
            if lib_id in _visiting:
                return  # cycle detected — break recursion
            _visiting.add(lib_id)
            if lib_id in containers:
                # It's a container — first emit ITS deps
                for dep in container_all_deps.get(lib_id, []):
                    _emit_deps(dep, _visiting)
                # Now emit this container
                self._emission_order.append(lib_id)
                emitted.add(lib_id)
            else:
                # Non-container asset (bitmap, shape, text)
                if lib_id not in emitted:
                    self._emission_order.append(lib_id)
                    emitted.add(lib_id)
            _visiting.discard(lib_id)

        for cid in topo_order:
            _emit_deps(cid)

        # Also walk main timeline deps (for assets directly on root stage)
        for dep in main_deps:
            _emit_deps(dep)

        # 2d. Any remaining unreferenced assets
        for lib_id in all_non_folder:
            if lib_id not in emitted:
                self._emission_order.append(lib_id)
                emitted.add(lib_id)

        # 2e. Keep the topological (leaves-first) emission order intact.
        #     Previous code reversed the non-sound portion to bring charIDs
        #     closer to the OG ordering, but that reversal put parents before
        #     children.  When IDs were then assigned sequentially and re-sorted
        #     ascending, parents ended up with LOWER IDs than their children,
        #     creating thousands of forward references (PlaceObject tags that
        #     reference sprites that haven't been defined yet).  Flash Player
        #     silently fails to instantiate such sprites, which breaks all
        #     MovieClip frame scripts and causes animation looping.
        #     Removing the reversal keeps children defined before parents,
        #     eliminating forward references.

        # ── 3. Assign SWF character IDs in emission order ──
        #    Preserve original OG swfCharId values where available.  The
        #    DoABC bytecode (raw passthrough from OG) may encode original
        #    charIDs in class metadata or embedded-asset annotations. Using
        #    the same charIDs ensures Flash Player can resolve those references
        #    against the RT SWF's character dictionary, preventing #2015
        #    "Invalid BitmapData" errors on BitmapData.threshold().
        max_swf_id = self._next_id - 1
        assigned_cids: Set[int] = set(self._lib_to_swf_id.values())
        for lib_id in self._emission_order:
            if lib_id not in self._lib_to_swf_id:
                lib = self.id_to_lib.get(lib_id, {})
                orig_cid = lib.get('swfCharId')
                if orig_cid and orig_cid > 0 and orig_cid not in assigned_cids:
                    self._lib_to_swf_id[lib_id] = orig_cid
                    assigned_cids.add(orig_cid)
                    if orig_cid > max_swf_id:
                        max_swf_id = orig_cid
                else:
                    new_id = self._alloc_id()
                    while new_id in assigned_cids:
                        new_id = self._alloc_id()
                    self._lib_to_swf_id[lib_id] = new_id
                    assigned_cids.add(new_id)
                    if new_id > max_swf_id:
                        max_swf_id = new_id
        # Advance _next_id past all assigned swfCharId values so that IDs
        # allocated at emit-time (e.g., companion DefineShape3 tags) do not
        # collide with any character definition already in the SWF.
        if max_swf_id >= self._next_id:
            self._next_id = max_swf_id + 1
        if max_swf_id >= self._next_id:
            self._next_id = max_swf_id + 1

        # ── 3b. Re-sort emission order by SWF character ID ascending ──
        #    The original SWF emits definition tags in strictly ascending
        #    char_id order. This ensures no forward references (a sprite
        #    never references a char_id that hasn't been defined yet).
        self._emission_order.sort(
            key=lambda lid: self._lib_to_swf_id.get(lid, 0)
        )

        # ── 3c. Defer root-timeline definitions (optional) ──
        #    If rootTimelineDefIds is available, defer those definitions
        #    to the root timeline section to match the original SWF layout.
        #    Without this hint, all definitions go in the definition section
        #    which is functionally equivalent.
        root_def_ids = set(self.data.get('rootTimelineDefIds', []))
        self._deferred_lib_ids: List[int] = []
        self._deferred_swf_ids: Set[int] = set()
        if root_def_ids:
            # Map original swfCharIds to deferred lib IDs
            deferred = []
            remaining = []
            for lid in self._emission_order:
                lib = self.id_to_lib.get(lid, {})
                orig_cid = lib.get("swfCharId")
                if orig_cid is not None and orig_cid in root_def_ids:
                    deferred.append(lid)
                    self._deferred_swf_ids.add(self._lib_to_swf_id.get(lid, 0))
                else:
                    remaining.append(lid)
            self._deferred_lib_ids = deferred
            self._emission_order = remaining

        # ── 4. Build char_idx → swf_id mapping ──
        for lib_id, swf_id in self._lib_to_swf_id.items():
            ci = self._lib_to_char_idx.get(lib_id)
            if ci is not None:
                self._char_idx_to_swf_id[ci] = swf_id

        # ── 5. Build original swfCharId → new swf_id mapping ──
        #    Used to remap charID references inside button data and font aux tags.
        self._orig_to_new_id: Dict[int, int] = {}
        for lib in self.libs:
            orig_cid = lib.get("swfCharId")
            lid = lib["id"]
            new_id = self._lib_to_swf_id.get(lid)
            if orig_cid is not None and new_id is not None:
                self._orig_to_new_id[orig_cid] = new_id

    # ── Unified asset emission ──────────────────────────────────────────

    def _build_font_name_map(self) -> Dict[str, int]:
        """Build a mapping of font name → new SWF character ID.

        Scans all font libraries (isFont=True) and extracts the font name
        from the DefineFont3 raw data, mapping it to the newly assigned
        SWF char ID.  Used by text_converter to write the correct FontID.
        """
        if hasattr(self, '_font_name_map_cache'):
            return self._font_name_map_cache
        fmap: Dict[str, int] = {}
        for lib in self.libs:
            if not lib.get('isFont'):
                continue
            lid = lib['id']
            swf_id = self._lib_to_swf_id.get(lid)
            if swf_id is None:
                continue
            # Try to extract font name from fontData (raw DefineFont3 body)
            font_data_b64 = lib.get('fontData')
            if font_data_b64:
                try:
                    raw = _decode_raw_body(font_data_b64)
                    # DefineFont3 body (after charID): flags(1) + langCode(1) +
                    # nameLen(1) + name(nameLen) + ...
                    if len(raw) >= 3:
                        name_len = raw[2]
                        if name_len > 0 and len(raw) >= 3 + name_len:
                            font_name = raw[3:3 + name_len].rstrip(b'\x00').decode('utf-8', errors='replace')
                            fmap[font_name] = swf_id
                except Exception:
                    pass
            # Also try the lib 'name' field as fallback (often "Font_123" but
            # parse_define_font3_name stores the real name there via import)
            lib_name = lib.get('name', '')
            if lib_name and lib_name not in fmap:
                fmap[lib_name] = swf_id
            # Also try fontFaceName (set during SWF import for face-name matching)
            face_name = lib.get('fontFaceName', '')
            if face_name and face_name not in fmap:
                fmap[face_name] = swf_id
        self._font_name_map_cache = fmap
        return fmap

    def _build_font_id_map(self) -> Dict[int, int]:
        """Build a mapping of original SWF font charID → new SWF charID.

        Used by _remap_text_raw_body to update font references inside
        DefineText/DefineText2 raw binary passthrough bodies.
        """
        if hasattr(self, '_font_id_map_cache'):
            return self._font_id_map_cache
        id_map: Dict[int, int] = {}
        for lib in self.libs:
            if not lib.get('isFont'):
                continue
            orig_cid = lib.get('swfCharId')
            lid = lib['id']
            new_swf_id = self._lib_to_swf_id.get(lid)
            if orig_cid is not None and new_swf_id is not None:
                id_map[orig_cid] = new_swf_id
        self._font_id_map_cache = id_map
        return id_map

    def _validate_library_entry(self, lib: dict):
        """Validate a library entry has the minimum required fields for emission.

        Returns None if valid, or a warning string if the entry should be skipped.
        """
        lib_id = lib.get("id")
        ltype = lib.get("type", "")
        name = lib.get("name", "?")

        if lib_id is None:
            return f"Library entry '{name}' has no id"
        if not ltype:
            return f"Library entry id={lib_id} '{name}' has no type"
        if lib_id not in self._lib_to_swf_id:
            return f"Library entry id={lib_id} '{name}' has no SWF charID mapping"

        if ltype == "bitmap":
            if not (lib.get("buffer") or
                    (self._project_dir and lib.get("externalFile"))):
                return (f"Bitmap '{name}' (id={lib_id}) has no"
                        " buffer or externalFile -- skipping")

        elif ltype == "sound":
            if not (lib.get("buffer") or
                    (self._project_dir and lib.get("externalFile"))):
                return (f"Sound '{name}' (id={lib_id}) has no"
                        " buffer or externalFile -- skipping")

        elif ltype == "text":
            # Rebuild path needs at least a text or font field
            pass  # text_converter handles defaults for missing fields

        elif ltype == "shape":
            # Font shapes need fontData
            if lib.get("isFont") and not lib.get("fontData"):
                return (f"Font '{name}' (id={lib_id}) has no"
                        " fontData -- skipping")
            # Legacy button shapes (pre-container) need buttonData
            if lib.get("isButton") and not lib.get("buttonData"):
                return (f"Button '{name}' (id={lib_id}) has no"
                        " buttonData -- skipping")
            # Binary data shapes need binaryDataBody
            if lib.get("isBinaryData") and not lib.get("binaryDataBody"):
                return (f"BinaryData '{name}' (id={lib_id}) has no"
                        " binaryDataBody -- skipping")

        elif ltype == "container":
            # Button containers use layers, not buttonData — no extra requirement
            pass

        return None

    def _emit_font_aux_for(self, swf_id: int):
        """Emit any pending font/text auxiliary tags (73, 74, 88) that
        reference *swf_id*. Must be called right after the definition tag
        for that character, matching the original SWF ordering."""
        pending = self._font_aux_tags.get(swf_id)
        if pending:
            for tag_type, body in pending:
                self._definition_tags.extend(
                    build_tag(tag_type, body, force_long=True)
                )

    def _embed_system_fonts(self):
        """Auto-embed system fonts referenced by text fields.

        Scans all text library entries for font names not already present
        in the embedded font library.  For each missing font, looks up the
        TTF on the system, converts it to DefineFont3, and creates a
        synthetic font library entry so it gets compiled into the SWF.
        """
        # Collect font names already embedded
        existing = set()
        for lib in self.libs:
            if not lib.get('isFont'):
                continue
            fd = lib.get('fontData')
            if not fd:
                continue
            # Extract font face name from raw DefineFont3 body
            try:
                raw = _decode_raw_body(fd)
                if len(raw) >= 3:
                    nl = raw[2]
                    if nl > 0 and len(raw) >= 3 + nl:
                        existing.add(raw[3:3 + nl].rstrip(b'\x00').decode('utf-8', errors='replace'))
            except Exception:
                pass
            # Also register library name
            n = lib.get('name', '')
            if n:
                existing.add(n)
            fn = lib.get('fontFaceName', '')
            if fn:
                existing.add(fn)

        # Collect font names used by text fields
        needed: set = set()
        for lib in self.libs:
            if lib.get('type') != 'text':
                continue
            fname = lib.get('font', '')
            if fname and fname not in existing and fname != 'sans-serif':
                needed.add(fname)

        if not needed:
            return

        log.info('_embed_system_fonts: need system fonts: %s', needed)

        # Enumerate system fonts
        from server import _enumerate_system_fonts
        sys_fonts = _enumerate_system_fonts()
        sys_map = {f['name']: f['path'] for f in sys_fonts}

        import base64
        from ttf_to_swf_font import ttf_to_define_font3

        added = 0
        for font_name in sorted(needed):
            ttf_path = sys_map.get(font_name)
            if not ttf_path or not os.path.isfile(ttf_path):
                log.warning('_embed_system_fonts: system font not found: %s', font_name)
                continue

            try:
                with open(ttf_path, 'rb') as fh:
                    ttf_data = fh.read()
                body = ttf_to_define_font3(ttf_data, font_name)
                if not body:
                    log.warning('_embed_system_fonts: conversion failed for %s', font_name)
                    continue
            except Exception as e:
                log.warning('_embed_system_fonts: error converting %s: %s', font_name, e)
                continue

            # Create synthetic library entry
            syn_id = max((lib['id'] for lib in self.libs), default=0) + 1 + added
            entry = {
                'id': syn_id,
                'name': font_name,
                'type': 'shape',
                'isFont': True,
                'fontFaceName': font_name,
                'symbol': '',
                'folderId': 0,
                'bitmapId': 0,
                'inBitmap': False,
                'recodes': [],
                'bounds': {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20},
                'fontData': base64.b64encode(body).decode('ascii'),
                'fontTagType': 75,  # DefineFont3
            }

            self.libs.append(entry)
            self.id_to_lib[syn_id] = entry

            # Allocate SWF character ID and add to emission order
            swf_id = self._alloc_id()
            self._lib_to_swf_id[syn_id] = swf_id
            self._emission_order.insert(0, syn_id)  # fonts first

            added += 1
            print(f"  [FONT] Embedded system font: {font_name} (lib {syn_id} -> SWF {swf_id}, {len(body):,} bytes)")

        if added:
            log.info('_embed_system_fonts: embedded %d system fonts', added)
            # Invalidate font name map cache
            if hasattr(self, '_font_name_map_cache'):
                del self._font_name_map_cache

    def _define_all_assets(self):
        """Emit all definition tags in dependency order (sounds first, then
        bitmaps/shapes/text/containers interleaved by dependency)."""
        log.debug('_define_all_assets: emitting %d assets', len(self._emission_order))
        counts = {"sound": 0, "bitmap": 0, "shape": 0, "container": 0, "text": 0}

        for lib_id in self._emission_order:
            lib = self.id_to_lib[lib_id]
            ltype = lib["type"]

            # ── Phase 5: Validate required fields before emission ──
            warning = self._validate_library_entry(lib)
            if warning:
                print(f"  SKIP: {warning}")
                continue

            if ltype == "sound":
                self._emit_sound(lib)
                counts["sound"] += 1

            elif ltype == "bitmap":
                self._emit_bitmap(lib)
                counts["bitmap"] += 1

            elif ltype == "shape":
                self._emit_shape(lib)
                counts["shape"] += 1

            elif ltype == "text":
                self._emit_text(lib)
                counts["text"] += 1

            elif ltype == "container":
                self._emit_container(lib)
                counts["container"] += 1

            # After each definition, emit its auxiliary tags (FontAlignZones,
            # CSMTextSettings, DefineFontName) if any exist for this charId.
            swf_id = self._lib_to_swf_id.get(lib_id)
            if swf_id is not None:
                self._emit_font_aux_for(swf_id)

        print(f"  {counts['sound']} sounds, {counts['bitmap']} bitmaps, "
              f"{counts['shape']} shapes, {counts['text']} texts, "
              f"{counts['container']} movieclips defined")

    def _emit_bitmap(self, lib: dict):
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_bitmap: lib_id=%d, swf_id=%d', lib['id'], swf_id)
        # Try external file (project folder mode)
        if self._project_dir and lib.get("externalFile"):
            tag_bytes = _load_external_bitmap(self._project_dir, lib, swf_id)
            if tag_bytes:
                self._definition_tags.extend(tag_bytes)
                return

        # ── Re-encode from pixel buffer ─────────────────────────────────
        w = lib.get("width", 1)
        h = lib.get("height", 1)
        buf_str = lib.get("buffer", "")
        pixel_data = _decode_raw_body(buf_str)
        # Bitmaps originally encoded as JPEG family (tags 6/21/35/90) are
        # re-encoded as DefineBitsJPEG3 (tag 35) rather than LL2.  This keeps
        # the RT SWF LL2 count equal to OG (735 vs 785), preventing Flash
        # Player's internal bitmap pool from overflowing and disposing pixel
        # data — which would cause Error #2015 on BitmapData.threshold().
        _JPEG_TAG_TYPES = (6, 21, 35, 90)  # DefineBits, JPEG2, JPEG3, JPEG4
        raw_tag_type = lib.get("rawTagType", 36)
        if raw_tag_type in _JPEG_TAG_TYPES and pixel_data:
            from bitmap_converter import build_define_bits_jpeg3
            bmp_tag = build_define_bits_jpeg3(swf_id, w, h, pixel_data)
        elif pixel_data:
            # Preserve the original LL2 format (3=indexed, 5=ARGB).
            # Converting between formats can trigger Flash Player Error #2015
            # even though the decompressed pixel data is byte-identical.
            raw_fmt = lib.get('rawBitmapFormat', 5)
            if raw_fmt == 3:
                from bitmap_converter import build_define_bits_lossless2_indexed
                bmp_tag = build_define_bits_lossless2_indexed(swf_id, w, h, pixel_data)
            else:
                bmp_tag = build_define_bits_lossless2(swf_id, w, h, pixel_data)
        else:
            bmp_tag = build_define_bits_lossless2(swf_id, w, h, pixel_data)
        self._definition_tags.extend(bmp_tag)

    def _emit_shape(self, lib: dict):
        # If this is a morph shape, dispatch to morph emitter
        if lib.get("isMorphShape"):
            self._emit_morph_shape(lib)
            return
        # If this is a button (DefineButton2), dispatch to button emitter
        if lib.get("isButton"):
            self._emit_button(lib)
            return
        # If this is binary data (DefineBinaryData), dispatch to binary emitter
        if lib.get("isBinaryData"):
            self._emit_binary_data(lib)
            return
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_shape: lib_id=%d, swf_id=%d, name=%s', lib['id'], swf_id, lib.get('name', '?'))
        # Font data: emit DefineFont tag from fontData
        if lib.get("isFont") and lib.get("fontData"):
            raw_body = _decode_raw_body(lib["fontData"])
            tag_type = lib.get("fontTagType", 75)  # DefineFont3
            tag_data = struct.pack('<H', swf_id) + raw_body
            self._definition_tags.extend(build_tag(tag_type, tag_data, force_long=True))
            return
        # Rebuild shape from recodes
        recodes = lib.get("recodes", [])
        bounds = lib.get("bounds")
        if not recodes:
            tag = build_define_shape3(swf_id, [], [], [], bounds)
        else:
            try:
                fill_styles, line_styles, sub_paths = parse_next2d_shape_buffer(recodes)
            except (IndexError, Exception) as e:
                print(f"  WARNING: Shape '{lib.get('name','?')}' (id={lib['id']}, swfId={swf_id}) "
                      f"recode parse error: {e}  — emitting empty shape")
                tag = build_define_shape3(swf_id, [], [], [], bounds)
                self._definition_tags.extend(tag)
                return
            # Resolve bitmap fill character IDs
            self._resolve_bitmap_fills(fill_styles)
            # Always emit DefineShape3 (tag 32) — full colour/alpha support
            tag = build_define_shape3(swf_id, fill_styles, line_styles, sub_paths, bounds)
        self._definition_tags.extend(tag)

    def _resolve_bitmap_fills(self, fill_styles: list):
        """For each BitmapFill, resolve its bitmap_char_id.

        If the fill carries a bitmap_lib_id (N2D library reference), map it
        to the already-emitted SWF character ID.  Only allocate a NEW bitmap
        tag when no library reference exists AND the pixel content doesn't
        match any known bitmap library entry (deduplication).
        """
        from shape_converter import BitmapFill
        for fs in fill_styles:
            if not isinstance(fs, BitmapFill):
                continue
            if fs.bitmap_char_id:
                continue  # already resolved
            # Try to resolve via N2D library ID → existing SWF charID
            if fs.bitmap_lib_id and fs.bitmap_lib_id in self._lib_to_swf_id:
                fs.bitmap_char_id = self._lib_to_swf_id[fs.bitmap_lib_id]
                continue
            if not fs.pixel_data or len(fs.pixel_data) <= 4:
                continue  # placeholder, nothing to emit
            # Try to match against known bitmap libraries by content hash
            # (handles bitmapId=0 from JS roundtrip losing the reference)
            matched = self._match_bitmap_by_content(fs.width, fs.height, fs.pixel_data)
            if matched:
                fs.bitmap_char_id = matched
                continue
            # Fallback: allocate a new SWF character ID for this embedded bitmap
            new_id = self._alloc_id()
            fs.bitmap_char_id = new_id
            self._bitmap_char_ids.add(new_id)
            # Emit the bitmap definition tag
            from bitmap_converter import build_define_bits_lossless2_indexed
            bmp_tag = build_define_bits_lossless2_indexed(new_id, fs.width, fs.height, fs.pixel_data)
            self._definition_tags.extend(bmp_tag)
            # Cache for future dedup
            import hashlib
            key = (fs.width, fs.height, hashlib.md5(fs.pixel_data).digest())
            self._bitmap_content_cache[key] = new_id

    def _match_bitmap_by_content(self, width: int, height: int, pixel_data: bytes) -> int:
        """Try to find a matching bitmap SWF char ID by pixel content hash.

        Lazily builds a cache mapping (width, height, md5) → SWF char ID
        from all bitmap library entries on first call.
        Returns the SWF char ID if found, else 0.
        """
        import hashlib
        if not hasattr(self, '_bitmap_content_cache'):
            self._bitmap_content_cache = {}
            for lib in self.libs:
                if lib.get('type') != 'bitmap':
                    continue
                lid = lib['id']
                swf_id = self._lib_to_swf_id.get(lid)
                if not swf_id:
                    continue
                w = lib.get('width', 0)
                h = lib.get('height', 0)
                buf = lib.get('buffer', '')
                if not buf:
                    continue
                rgba = _decode_raw_body(buf)
                if not rgba:
                    continue
                key = (w, h, hashlib.md5(rgba).digest())
                self._bitmap_content_cache[key] = swf_id

        key = (width, height, hashlib.md5(pixel_data).digest())
        return self._bitmap_content_cache.get(key, 0)

    def _emit_morph_shape(self, lib: dict):
        swf_id = self._lib_to_swf_id[lib["id"]]
        # Always rebuild morph shape from recodes
        start_recodes = lib.get("recodes") or lib.get("startRecodes") or []
        start_bounds = lib.get("bounds") or lib.get("startBounds")
        end_recodes = lib.get("endRecodes", [])
        end_bounds = lib.get("endBounds")
        try:
            if start_recodes:
                s_fills, s_lines, s_paths = parse_next2d_shape_buffer(start_recodes)
            else:
                s_fills, s_lines, s_paths = [], [], []
            if end_recodes:
                e_fills, e_lines, e_paths = parse_next2d_shape_buffer(end_recodes)
            else:
                e_fills, e_lines, e_paths = [], [], []
        except (IndexError, Exception) as e:
            print(f"  WARNING: MorphShape '{lib.get('name','?')}' (id={lib['id']}, swfId={swf_id}) "
                  f"recode parse error: {e}  — emitting empty morph")
            s_fills, s_lines, s_paths = [], [], []
            e_fills, e_lines, e_paths = [], [], []
        # Always emit DefineMorphShape2 (tag 84) — supports DefineShape4 fill/line styles
        from shape_converter import build_define_morph_shape2
        tag = build_define_morph_shape2(
            swf_id,
            s_fills, s_lines, s_paths, start_bounds,
            e_fills, e_lines, e_paths, end_bounds,
        )
        self._definition_tags.extend(tag)

    def _emit_text(self, lib: dict):
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_text: lib_id=%d, swf_id=%d', lib['id'], swf_id)

        # Always rebuild text from structured editable properties so that
        # any text edits the user makes in the canvas tool are reflected
        # in the exported SWF.  The old raw-passthrough path (rawTagBody +
        # rawTagType 11/33) is intentionally removed: it silently ignored
        # every text edit because it replayed the original import bytes.
        font_map = self._build_font_name_map()
        tag = build_define_edit_text(swf_id, lib, font_map=font_map)
        self._definition_tags.extend(tag)

    def _emit_sound(self, lib: dict):
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_sound: lib_id=%d, swf_id=%d', lib['id'], swf_id)
        # Try external file first (project folder mode)
        if self._project_dir and lib.get("externalFile"):
            tag_bytes = _load_external_sound(self._project_dir, lib, swf_id)
            if tag_bytes:
                self._definition_tags.extend(tag_bytes)
                return
        # Rebuild from buffer (WAV or MP3)
        buf_str = lib.get("buffer", "")
        if not buf_str:
            print(f"  WARNING: Sound '{lib.get('name','?')}' has no audio buffer — skipping")
            return
        audio_bytes = _decode_raw_body(buf_str)
        if not audio_bytes:
            return
        # Detect format and build appropriate DefineSound tag
        if audio_bytes[:4] == b"RIFF":
            # WAV — uncompressed PCM
            tag = build_define_sound(swf_id, audio_bytes)
            self._definition_tags.extend(tag)
        elif len(audio_bytes) >= 2 and (audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0):
            # MP3 sync word detected
            tag = _build_define_sound_from_mp3(swf_id, audio_bytes)
            if tag:
                self._definition_tags.extend(tag)
            else:
                print(f"  WARNING: Failed to build MP3 sound tag for: {lib.get('name', '?')}")
        elif lib.get("soundFormat") == "mp3":
            # Explicitly tagged as MP3
            tag = _build_define_sound_from_mp3(swf_id, audio_bytes)
            if tag:
                self._definition_tags.extend(tag)
            else:
                print(f"  WARNING: Failed to build MP3 sound tag for: {lib.get('name', '?')}")
        else:
            print(f"  WARNING: Unknown sound format for: {lib.get('name', '?')} — skipping")

    def _emit_binary_data(self, lib: dict):
        """Emit DefineBinaryData (tag 87) from binaryDataBody field."""
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_binary_data: lib_id=%d, swf_id=%d', lib['id'], swf_id)
        body_data = lib.get("binaryDataBody")
        if body_data:
            raw_body = _decode_raw_body(body_data)
            tag_data = struct.pack('<H', swf_id) + raw_body
            self._definition_tags.extend(build_tag(87, tag_data, force_long=True))

    def _emit_button_from_container(self, lib: dict):
        """Emit DefineButton2 from a button stored as an editable 4-frame container.

        Frame 1=up, 2=over, 3=down, 4=hit.  Each layer in the container
        represents one SWF button depth; characters placed on those frames
        map back to ButtonRecords with the appropriate state-bit masks.
        """
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_button_from_container: lib_id=%d, swf_id=%d', lib['id'], swf_id)

        # Fall back to raw buttonData if layers are missing (old-format N2D file)
        if not lib.get("layers") and lib.get("buttonData"):
            self._emit_button(lib)
            return

        track_as_menu = lib.get('buttonTrackAsMenu', False)

        # Build frame→state_bit from labels (works for both 4-frame and 12-frame formats)
        _state_name_to_bit = {'up': 0x01, 'over': 0x02, 'down': 0x04, 'hit': 0x08}
        _total = lib.get('totalFrame', 4)
        _labels = sorted(lib.get('labels', []), key=lambda l: l['frame'])
        if _labels:
            frame_to_bit: Dict[int, int] = {}
            for _i, _lbl in enumerate(_labels):
                _bit = _state_name_to_bit.get(_lbl['name'].lower(), 0)
                if not _bit:
                    continue
                _end = _labels[_i + 1]['frame'] if _i + 1 < len(_labels) else _total + 1
                for _f in range(_lbl['frame'], _end):
                    frame_to_bit[_f] = _bit
        else:
            frame_to_bit = {1: 0x01, 2: 0x02, 3: 0x04, 4: 0x08}  # legacy fallback

        # Collect what character+transform is placed at each (depth, frame)
        depth_frame: Dict[int, Dict[int, dict]] = {}
        for layer in lib.get("layers", []):
            depth = layer.get("swfDepth", 0)
            if depth not in depth_frame:
                depth_frame[depth] = {}
            for char in layer.get("characters", []):
                lib_id = char.get("libraryId", 0)
                char_swf_id = self._lib_to_swf_id.get(lib_id)
                if char_swf_id is None:
                    continue
                for frame in range(1, _total + 1):
                    if char["startFrame"] <= frame < char["endFrame"]:
                        if frame in depth_frame[depth]:
                            continue  # first (topmost) character wins at this frame+depth
                        # Find active place at this frame (last keyframe <= frame)
                        places = sorted(char.get("places", []), key=lambda p: p["frame"])
                        active = None
                        for p in places:
                            if p["frame"] <= frame:
                                active = p
                            else:
                                break
                        if active is None and places:
                            active = places[0]
                        if active is not None:
                            depth_frame[depth][frame] = {
                                'char_swf_id': char_swf_id,
                                'matrix': active.get('matrix', [1, 0, 0, 1, 0, 0]),
                                'cxform': active.get('colorTransform', [1, 1, 1, 1, 0, 0, 0, 0]),
                                'filters': active.get('filter', []),
                                'blend': active.get('blendMode', 'normal'),
                            }

        # Build merged ButtonRecords per depth: merge state bits for identical placements
        button_records: List[dict] = []
        for depth in sorted(depth_frame.keys()):
            merged: List[dict] = []
            for frame in sorted(frame_to_bit.keys()):
                if frame not in depth_frame[depth]:
                    continue
                rec = depth_frame[depth][frame]
                bit = frame_to_bit[frame]
                found = False
                for m in merged:
                    if (m['char_swf_id'] == rec['char_swf_id']
                            and m['matrix'] == rec['matrix']
                            and m['cxform'] == rec['cxform']):
                        m['state_bits'] |= bit
                        found = True
                        break
                if not found:
                    merged.append({
                        'state_bits': bit,
                        'char_swf_id': rec['char_swf_id'],
                        'depth': depth,
                        'matrix': list(rec['matrix']),
                        'cxform': list(rec['cxform']),
                        'filters': list(rec.get('filters', [])),
                        'blend': rec.get('blend', 'normal'),
                    })
            button_records.extend(merged)

        # Serialize ButtonRecord structs
        records_buf = bytearray()
        for brec in button_records:
            state_flags = brec['state_bits']
            blend_name = brec.get('blend', 'normal')
            blend_code = 0
            for k, v in NEXT2D_BLEND_MAP.items():
                if v == blend_name:
                    blend_code = k
                    break
            has_filters = bool(brec.get('filters'))
            has_blend = blend_code not in (0, 1)
            if has_filters:
                state_flags |= 0x10
            if has_blend:
                state_flags |= 0x20

            a, b, c, d, tx, ty = brec['matrix']
            cx = brec['cxform']
            records_buf += bytes([state_flags])
            records_buf += struct.pack('<H', brec['char_swf_id'])
            records_buf += struct.pack('<H', brec['depth'])
            records_buf += write_matrix(a=a, b=b, c=c, d=d, tx=tx, ty=ty)
            records_buf += write_cxform_alpha(
                cx[0], cx[1], cx[2], cx[3], cx[4], cx[5], cx[6], cx[7])
            if has_filters:
                records_buf += encode_filter_list(brec['filters'])
            if has_blend:
                records_buf += bytes([blend_code])

        # Serialize ButtonCondActions (ActionScript)
        button_actions = lib.get('buttonActions', [])
        actions_buf = bytearray()
        for i, ba in enumerate(button_actions):
            action_bytes = _decode_raw_body(ba.get('actionBytes', ''))
            cond_flags = ba.get('conditions', 0)
            is_last = (i == len(button_actions) - 1)
            size_field = 0 if is_last else (4 + len(action_bytes))
            actions_buf += struct.pack('<HH', size_field, cond_flags)
            actions_buf += action_bytes

        # Build tag body: [trackFlags][actionOffset2][records][0x00][actions]
        track_flags = 0x01 if track_as_menu else 0x00
        action_offset = (2 + len(records_buf) + 1) if actions_buf else 0
        body = (bytes([track_flags])
                + struct.pack('<H', action_offset)
                + bytes(records_buf) + b'\x00'
                + bytes(actions_buf))
        tag_data = struct.pack('<H', swf_id) + body
        self._definition_tags.extend(build_tag(34, tag_data, force_long=True))

    def _emit_button(self, lib: dict):
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_button: lib_id=%d, swf_id=%d', lib['id'], swf_id)
        # Emit button from buttonData field
        body_data = lib.get("buttonData")
        if body_data:
            raw_body = _decode_raw_body(body_data)
            # Remap charID references inside ButtonRecords
            raw_body = _remap_button_raw_body(raw_body, self._orig_to_new_id)
            tag_data = struct.pack('<H', swf_id) + raw_body
            self._definition_tags.extend(build_tag(34, tag_data, force_long=True))

    def _emit_container(self, lib: dict):
        # Buttons imported from SWF are stored as 4-frame containers
        if lib.get("isButton"):
            self._emit_button_from_container(lib)
            return
        swf_id = self._lib_to_swf_id[lib["id"]]
        log.debug('_emit_container: lib_id=%d, swf_id=%d, name=%s', lib['id'], swf_id, lib.get('name', '?'))
        # Always rebuild containers from JSON so that editor placement edits
        # (position, colorTransform, filters, etc.) are compiled into the SWF.
        tp = to_publish(lib, self._lib_to_char_idx, self.id_to_lib)
        # totalFrame is NOT serialised by MovieClip.toObject() (it's a computed
        # getter), so it can be absent after _merge_editor_into_disk.  Fall back
        # to computing it from layer character endpoints.
        total_frames = lib.get("totalFrame") or _compute_total_frames(lib)
        labels = lib.get("labels", [])
        actions = lib.get("actions", [])

        # SoundStreamHead2 tag — rebuild from structured dict
        ssh_prefix = b""
        ssh_parsed = lib.get("soundStreamParsed")
        if ssh_parsed:
            from compilation_pipeline import _rebuild_sound_stream_head
            ssh_prefix = build_tag(45, _rebuild_sound_stream_head(ssh_parsed))

        inner_tags = ssh_prefix + build_timeline_tags(
            total_frames, tp, labels, actions, self._char_idx_to_swf_id,
            bitmap_char_ids=self._bitmap_char_ids,
        )
        inner_tags += build_tag_end()
        sprite_tag = build_define_sprite(swf_id, total_frames, inner_tags)
        self._definition_tags.extend(sprite_tag)

    def _container_order(self) -> List[int]:
        """Topological sort of containers (leaves first)."""
        containers: Set[int] = set()
        for lib in self.libs:
            if lib["type"] == "container" and lib["id"] != 0:
                containers.add(lib["id"])

        # Build dependency graph
        deps: Dict[int, Set[int]] = {}
        for lib in self.libs:
            if lib["type"] != "container" or lib["id"] == 0:
                continue
            lib_deps: Set[int] = set()
            for layer in lib.get("layers", []):
                for char in layer.get("characters", []):
                    ref = char["libraryId"]
                    if ref in containers:
                        lib_deps.add(ref)
            deps[lib["id"]] = lib_deps

        # Topological sort (DFS)
        order: List[int] = []
        visited: Set[int] = set()

        def visit(node: int):
            if node in visited:
                return
            visited.add(node)
            for dep in deps.get(node, set()):
                visit(dep)
            order.append(node)

        for c in containers:
            visit(c)

        return order

    # ── Root timeline ────────────────────────────────────────────────────

    def _build_deferred_def_bytes(self) -> Dict[int, bytes]:
        """Build definition + font-aux tag bytes for each deferred character,
        keyed by its SWF charId."""
        result: Dict[int, bytes] = {}
        if not self._deferred_lib_ids:
            return result
        for lib_id in self._deferred_lib_ids:
            lib = self.id_to_lib[lib_id]
            swf_id = self._lib_to_swf_id[lib_id]
            # Temporarily capture definition tags produced by the normal emit path
            saved = self._definition_tags
            self._definition_tags = bytearray()
            ltype = lib.get("type", "")
            if ltype == "sound":
                self._emit_sound(lib)
            elif ltype == "bitmap":
                self._emit_bitmap(lib)
            elif ltype == "shape":
                self._emit_shape(lib)
            elif ltype == "text":
                self._emit_text(lib)
            elif ltype == "container":
                self._emit_container(lib)
            buf = bytearray(self._definition_tags)
            self._definition_tags = saved
            # Also emit font auxiliary tags
            pending = self._font_aux_tags.get(swf_id)
            if pending:
                for tag_type, body in pending:
                    buf.extend(build_tag(tag_type, body, force_long=True))
            result[swf_id] = bytes(buf)
        return result

    def _build_root_timeline(self) -> bytes:
        """Build root timeline from main container (id=0)."""
        log.debug('_build_root_timeline: entry')
        main = self.id_to_lib.get(0)
        if not main:
            print("  WARNING: No main container (id=0) found — empty root timeline")
            return build_tag_show_frame() + build_tag_end()

        tp = to_publish(main, self._lib_to_char_idx, self.id_to_lib)
        total_frames = main.get("totalFrame") or _compute_total_frames(main)
        labels = main.get("labels", [])
        actions = main.get("actions", [])

        # Diagnostic: report root timeline stats
        n_layers = len(main.get("layers", []))
        n_chars = sum(len(l.get("characters", [])) for l in main.get("layers", []))
        n_dict = len(tp.get("dictionary", []))
        n_po = len(tp.get("placeObjects", []))
        print(f"  Root timeline: {total_frames} frames, {n_layers} layers, "
              f"{n_chars} characters, {n_dict} dict entries, {n_po} placeObjects")

        timeline_tags = build_timeline_tags(
            total_frames, tp, labels, actions, self._char_idx_to_swf_id,
            bitmap_char_ids=self._bitmap_char_ids,
        )

        # Inject deferred root-timeline definitions interleaved with
        # PlaceObject tags: each definition appears right before the
        # first PlaceObject that places a character with charId >= the
        # definition's charId.  This matches the original SWF layout.
        deferred_per_cid = self._build_deferred_def_bytes()
        if deferred_per_cid:
            timeline_tags = self._inject_deferred_into_timeline(
                timeline_tags, deferred_per_cid
            )

        return timeline_tags

    def _inject_deferred_into_timeline(self, timeline_bytes: bytes,
                                        deferred: Dict[int, bytes]) -> bytes:
        """Re-serialize *timeline_bytes* with deferred definitions injected
        right before their corresponding PlaceObject tags."""
        # Parse the flat byte stream into individual tags
        raw_tags: List[Tuple[int, bytes, int]] = []  # (tag_type, body, hdr_len)
        pos = 0
        while pos < len(timeline_bytes):
            tcl = struct.unpack_from('<H', timeline_bytes, pos)[0]
            tt = tcl >> 6
            ln = tcl & 0x3F
            hdr = 2
            pos += 2
            if ln == 0x3F:
                ln = struct.unpack_from('<I', timeline_bytes, pos)[0]
                pos += 4
                hdr = 6
            body = timeline_bytes[pos:pos + ln]
            raw_tags.append((tt, body, hdr))
            pos += ln
            if tt == 0:
                break

        emitted: Set[int] = set()
        result = bytearray()

        for tt, body, hdr in raw_tags:
            # Before each PlaceObject2/3 with HasCharacter, inject any
            # not-yet-emitted deferred defs whose charId <= placed charId.
            if tt in (26, 70) and len(body) >= 5:
                flags = body[0]
                has_char = bool(flags & 0x02)
                if has_char:
                    if tt == 26:
                        placed_cid = struct.unpack_from('<H', body, 3)[0]
                    else:  # PlaceObject3 has an extra flags byte
                        placed_cid = struct.unpack_from('<H', body, 4)[0]
                    for cid in sorted(deferred.keys()):
                        if cid not in emitted and cid <= placed_cid:
                            result.extend(deferred[cid])
                            emitted.add(cid)

            # Re-emit the tag, using forced long format for PlaceObject2/3
            # that carry a HasName flag (matching Adobe/JPEXS convention).
            use_long = (hdr == 6)
            if tt in (26, 70) and len(body) >= 1 and (body[0] & 0x20):
                use_long = True  # HasName → force long header
            if use_long or len(body) >= 0x3F:
                code_and_len = (tt << 6) | 0x3F
                result.extend(struct.pack("<HI", code_and_len, len(body)))
            else:
                code_and_len = (tt << 6) | len(body)
                result.extend(struct.pack("<H", code_and_len))
            result.extend(body)

        return bytes(result)

    def _assemble_swf(self, root_timeline_tags: bytes, doabc_tags: bytes,
                       sym_to_class: Dict[str, str] = None,
                       fla_classes: Dict[int, str] = None,
                       raw_aux_tags: bytes = b"",
                       raw_aux_map: Dict[int, bytes] = None) -> bytes:
        log.info('_assemble_swf: root_timeline=%d bytes, doabc=%d bytes',
                 len(root_timeline_tags), len(doabc_tags))
        if sym_to_class is None:
            sym_to_class = {}
        if fla_classes is None:
            fla_classes = {}
        if raw_aux_map is None:
            raw_aux_map = {}

        width = self.stage.get("width", 550)
        height = self.stage.get("height", 400)
        fps = self.stage.get("fps", 24)
        bg_color = self.stage.get("bgColor", "#ffffff")
        main = self.id_to_lib.get(0, {})
        total_frames = main.get("totalFrame") or _compute_total_frames(main)
        swf_version = self.data.get("swfVersion", 14)
        swf_compressed = self.data.get("swfCompressed", True)

        # Parse bg color
        bg = bg_color.lstrip("#")
        r = int(bg[0:2], 16) if len(bg) >= 2 else 255
        g = int(bg[2:4], 16) if len(bg) >= 4 else 255
        b = int(bg[4:6], 16) if len(bg) >= 6 else 255

        all_tags = bytearray()

        # 1. FileAttributes (AS3) — use stored OG flags if available
        file_attr_flags = self.data.get("fileAttributeFlags", 0)
        all_tags.extend(build_file_attributes(has_as3=True, raw_flags=file_attr_flags))

        # 2. SetBackgroundColor (before non-definition metadata, matching OG)
        all_tags.extend(build_set_background_color(r, g, b))

        # 3. Auxiliary tags (Protect, SceneAndFrameLabel, SoundStreamHead2)
        if raw_aux_tags:
            all_tags.extend(raw_aux_tags)
        else:
            # Generate fallback auxiliary tags when rawGlobalTags is missing
            # Protect tag (24): empty body, signals the SWF is protected
            all_tags.extend(build_tag(24, b''))
            # SceneAndFrameLabel (86): single scene "Scene 1" at offset 0
            scene_body = bytearray()
            scene_body.extend(struct.pack('<B', 1))  # scene count (encoded UB30)
            scene_body.extend(struct.pack('<B', 0))  # scene 0 offset (encoded UB30)
            scene_body.extend(b'Scene 1\x00')        # scene name
            scene_body.extend(struct.pack('<B', 0))  # frame label count
            all_tags.extend(build_tag(86, bytes(scene_body), force_long=True))

        # 4. All definition tags (bitmaps, shapes, sounds, fonts, morphShapes, texts, containers)
        #    Font/text auxiliary tags (73, 74, 88) are emitted inline by
        #    _define_all_assets right after their referenced definition.
        all_tags.extend(self._definition_tags)

        # 4. DoABC (compiled AS3 bytecode)
        if doabc_tags:
            all_tags.extend(doabc_tags)

        # 5. SymbolClass — map exported symbols + document class
        #    Always rebuild SymbolClass with new charIDs (charIDs change every
        #    compilation so raw passthrough from the original SWF is invalid).
        if True:
            #    For AS3, each symbol needs to map to its ABC class name.
            #    - Bitmaps: use DefineBitsLossless2 ID (bmp_id), class extends BitmapData
            #    - Sounds: use DefineSound ID, class extends Sound
            #    - Containers: use DefineSprite ID, class extends MovieClip
            symbol_pairs: List[Tuple[int, str]] = []

            # Document class: character ID 0 → "Main"
            symbol_pairs.append((0, "Main"))

            # All other exported symbols
            for lib in self.libs:
                if lib["id"] == 0:
                    continue
                sym = lib.get("symbol", "")
                if not sym or sym == "Main":
                    continue

                # Get the class name from the stub map
                class_name = sym_to_class.get(sym, sym)

                swf_id = self._lib_to_swf_id.get(lib["id"])
                if swf_id is not None:
                    symbol_pairs.append((swf_id, class_name))

            # Add _fla package classes for containers with frame scripts
            for lib_id, fla_fqn in fla_classes.items():
                swf_id = self._lib_to_swf_id.get(lib_id)
                if swf_id is not None:
                    symbol_pairs.append((swf_id, fla_fqn))

            # Preserve original SymbolClass entry order from the OG SWF.
            # Flash Player may depend on the order for class initialization.
            og_order = self.data.get('symbolClassOrder', [])
            if og_order:
                order_map = {name: idx for idx, name in enumerate(og_order)}
                # Sort: entries present in OG order come first (in OG order),
                # any new entries are appended at the end.
                sentinel = len(og_order)
                symbol_pairs.sort(key=lambda p: order_map.get(p[1], sentinel))

            if symbol_pairs:
                all_tags.extend(build_symbol_class(symbol_pairs))

        # 6. Root timeline
        all_tags.extend(root_timeline_tags)

        # 7. End tag
        all_tags.extend(build_tag_end())

        return build_swf_file(
            width=width,
            height=height,
            fps=fps,
            frame_count=total_frames,
            tags=bytes(all_tags),
            compressed=swf_compressed,
            version=swf_version,
        )


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    log.debug('main: entry')
    parser = argparse.ArgumentParser(
        description="Compile a next2D .n2D file into an AS3 SWF"
    )
    parser.add_argument("input", help="Path to .n2D file")
    parser.add_argument("-o", "--output", help="Output .swf path")
    parser.add_argument("--shared", required=True,
                        help="Path to shared AS3 source directory")
    parser.add_argument("--sdk", help="Path to Flex/AIR SDK")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    output = args.output
    if not output:
        output = os.path.splitext(args.input)[0] + ".swf"

    compiler = N2DCompiler(
        n2d_path=args.input,
        shared_dir=args.shared,
        output_path=output,
        sdk_path=args.sdk,
    )
    compiler.compile()
    return 0


if __name__ == "__main__":
    sys.exit(main())
