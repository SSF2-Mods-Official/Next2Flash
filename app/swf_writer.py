"""
SWF Binary Writer — Low-level primitives for SWF file generation.

Implements the SWF file format specification (version 10+):
  - Bit-packed I/O (RECT, MATRIX, CXFORM)
  - Tag serialisation
  - File header (uncompressed)
"""

from __future__ import annotations

import io
import logging
import math
import struct
import zlib
from typing import List, Optional, Tuple

log = logging.getLogger(__name__)

from swf_binary_io import BitWriter
from swf_constants import (
    SWFTag, BlendMode,
    TAG_END, TAG_SHOW_FRAME, TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2, TAG_DEFINE_SHAPE3,
    TAG_DEFINE_SHAPE4, TAG_PLACE_OBJECT, TAG_PLACE_OBJECT2, TAG_PLACE_OBJECT3,
    TAG_REMOVE_OBJECT2, TAG_DEFINE_SPRITE, TAG_DEFINE_EDIT_TEXT, TAG_FRAME_LABEL,
    TAG_DO_ACTION, TAG_DO_INIT_ACTION, TAG_SET_BACKGROUND_COLOR, TAG_FILE_ATTRIBUTES,
    TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2, TAG_DEFINE_FONT3,
    TAG_DEFINE_TEXT2, TAG_SYMBOL_CLASS, TAG_DO_ABC, TAG_EXPORT_ASSETS, TAG_DEFINE_MORPH_SHAPE,
    # Blend mode mappings
    SWF_BLEND_NORMAL, SWF_BLEND_LAYER, SWF_BLEND_MULTIPLY, SWF_BLEND_SCREEN,
    SWF_BLEND_LIGHTEN, SWF_BLEND_DARKEN, SWF_BLEND_DIFFERENCE, SWF_BLEND_ADD,
    SWF_BLEND_SUBTRACT, SWF_BLEND_INVERT, SWF_BLEND_ALPHA, SWF_BLEND_ERASE,
    SWF_BLEND_OVERLAY, SWF_BLEND_HARDLIGHT,
    NEXT2D_BLEND_MAP
)


# ── Filter IDs (SWF spec) ───────────────────────────────────────────────
SWF_FILTER_DROPSHADOW      = 0
SWF_FILTER_BLUR            = 1
SWF_FILTER_GLOW            = 2
SWF_FILTER_BEVEL           = 3
SWF_FILTER_GRADIENT_GLOW   = 4
SWF_FILTER_CONVOLUTION     = 5
SWF_FILTER_COLORMATRIX     = 6
SWF_FILTER_GRADIENT_BEVEL  = 7


# ── Helpers ──────────────────────────────────────────────────────────────

def _nbits_unsigned(value: int) -> int:
    if value <= 0:
        return 0        # 0 styles → 0 index bits (was incorrectly 1)
    return value.bit_length()


def _nbits_signed(value: int) -> int:
    if value == 0:
        return 1
    if value > 0:
        return value.bit_length() + 1
    return (value + 1).bit_length() + 1  # extra sign bit


def _nbits_signed_list(values: List[int]) -> int:
    return max(_nbits_signed(v) for v in values) if values else 0


def _nbits_fixed(value: float) -> int:
    return _nbits_signed(int(round(value * 65536)))


def _nbits_fixed_list(values: List[float]) -> int:
    return max(_nbits_fixed(v) for v in values) if values else 0


def twips(value: float) -> int:
    """Convert pixels → twips (1 px = 20 twips)."""
    return int(round(value * 20))


# ── RECT ─────────────────────────────────────────────────────────────────

def write_rect(xmin: int, xmax: int, ymin: int, ymax: int) -> bytes:
    """Encode a RECT structure in twips (values should already be twips)."""
    nbits = _nbits_signed_list([xmin, xmax, ymin, ymax])
    nbits = max(nbits, 1)
    bw = BitWriter()
    bw.write_ub(5, nbits)
    bw.write_sb(nbits, xmin)
    bw.write_sb(nbits, xmax)
    bw.write_sb(nbits, ymin)
    bw.write_sb(nbits, ymax)
    return bw.get_bytes()


# ── MATRIX ───────────────────────────────────────────────────────────────

def write_matrix(
    a: float = 1.0, b: float = 0.0,
    c: float = 0.0, d: float = 1.0,
    tx: float = 0.0, ty: float = 0.0,
) -> bytes:
    """
    Encode a MATRIX structure.
    - Scale values (a, d) are 16.16 fixed-point.
    - Rotate values (b, c) are 16.16 fixed-point.
    - Translate values (tx, ty) are in twips (signed bits).
    """
    bw = BitWriter()

    # HasScale
    has_scale = not (a == 1.0 and d == 1.0)
    bw.write_ub(1, int(has_scale))
    if has_scale:
        nbits = _nbits_fixed_list([a, d])
        nbits = max(nbits, 1)
        bw.write_ub(5, nbits)
        bw.write_fb(nbits, a)
        bw.write_fb(nbits, d)

    # HasRotate
    has_rotate = not (b == 0.0 and c == 0.0)
    bw.write_ub(1, int(has_rotate))
    if has_rotate:
        nbits = _nbits_fixed_list([b, c])
        nbits = max(nbits, 1)
        bw.write_ub(5, nbits)
        bw.write_fb(nbits, b)
        bw.write_fb(nbits, c)

    # Translate (always present)
    tx_tw = twips(tx)
    ty_tw = twips(ty)
    if tx_tw == 0 and ty_tw == 0:
        nbits_t = 0
    else:
        nbits_t = _nbits_signed_list([tx_tw, ty_tw])
    bw.write_ub(5, nbits_t)
    bw.write_sb(nbits_t, tx_tw)
    bw.write_sb(nbits_t, ty_tw)

    return bw.get_bytes()


# ── CXFORM with Alpha ───────────────────────────────────────────────────

def write_cxform_alpha(
    r_mul: float = 1.0, g_mul: float = 1.0, b_mul: float = 1.0, a_mul: float = 1.0,
    r_off: float = 0.0, g_off: float = 0.0, b_off: float = 0.0, a_off: float = 0.0,
) -> bytes:
    """
    Encode a CXFORMWITHALPHA.
    Multiplier values are 8.8 fixed (we use *256).
    Offsets are signed integers (-32768..32767).
    """
    bw = BitWriter()

    muls = [int(round(r_mul * 256)), int(round(g_mul * 256)),
            int(round(b_mul * 256)), int(round(a_mul * 256))]
    offs = [int(round(r_off)), int(round(g_off)),
            int(round(b_off)), int(round(a_off))]

    has_add = any(o != 0 for o in offs)
    has_mul = any(m != 256 for m in muls)

    bw.write_ub(1, int(has_add))
    bw.write_ub(1, int(has_mul))

    all_vals = []
    if has_mul:
        all_vals.extend(muls)
    if has_add:
        all_vals.extend(offs)

    nbits = _nbits_signed_list(all_vals) if all_vals else 1
    nbits = max(nbits, 1)
    bw.write_ub(4, nbits)

    if has_mul:
        for m in muls:
            bw.write_sb(nbits, m)
    if has_add:
        for o in offs:
            bw.write_sb(nbits, o)

    return bw.get_bytes()


# ── SWF Tag building ────────────────────────────────────────────────────

def build_tag(tag_id: int, data: bytes = b"", force_long: bool = False) -> bytes:
    """
    Build a complete SWF tag (tag header + data).
    Uses short header for data ≤ 62 bytes, long header otherwise.
    When *force_long* is True, always use the 6-byte long header (matches
    Adobe/JPEXS behaviour for definition tags).
    """
    length = len(data)
    log.debug("build_tag: id=%d len=%d force_long=%s", tag_id, length, force_long)
    if length < 0x3F and not force_long:
        code_and_len = (tag_id << 6) | length
        return struct.pack("<H", code_and_len) + data
    else:
        code_and_len = (tag_id << 6) | 0x3F
        return struct.pack("<HI", code_and_len, length) + data


def build_tag_show_frame() -> bytes:
    return build_tag(TAG_SHOW_FRAME)


def build_tag_end() -> bytes:
    return build_tag(TAG_END)


# ── FileAttributes tag ──────────────────────────────────────────────────

def build_file_attributes(has_as3: bool = True) -> bytes:
    """FileAttributes (tag 69) — required as the first tag in SWF 8+."""
    flags = 0
    if has_as3:
        flags |= (1 << 3)  # UseAS3
    return build_tag(TAG_FILE_ATTRIBUTES, struct.pack("<I", flags))


# ── SetBackgroundColor ──────────────────────────────────────────────────

def build_set_background_color(r: int, g: int, b: int) -> bytes:
    return build_tag(TAG_SET_BACKGROUND_COLOR, struct.pack("BBB", r, g, b))


# ── FrameLabel ──────────────────────────────────────────────────────────

def build_frame_label(name: str) -> bytes:
    data = name.encode("utf-8") + b"\x00"
    return build_tag(TAG_FRAME_LABEL, data)


# ── SymbolClass (tag 76) ────────────────────────────────────────────────

def build_symbol_class(symbols: List[Tuple[int, str]]) -> bytes:
    """
    SymbolClass tag – maps character IDs to AS3 class names.
    `symbols` is a list of (character_id, class_name) tuples.
    """
    log.debug("build_symbol_class: %d symbols", len(symbols))
    buf = io.BytesIO()
    buf.write(struct.pack("<H", len(symbols)))
    for cid, name in symbols:
        buf.write(struct.pack("<H", cid))
        buf.write(name.encode("utf-8") + b"\x00")
    return build_tag(TAG_SYMBOL_CLASS, buf.getvalue())


# ── ExportAssets (tag 56) — AS2 equivalent of SymbolClass ────────────────

def build_export_assets(assets: List[Tuple[int, str]]) -> bytes:
    buf = io.BytesIO()
    buf.write(struct.pack("<H", len(assets)))
    for cid, name in assets:
        buf.write(struct.pack("<H", cid))
        buf.write(name.encode("utf-8") + b"\x00")
    return build_tag(TAG_EXPORT_ASSETS, buf.getvalue())


# ── PlaceObject2 (tag 26) ───────────────────────────────────────────────

def build_place_object2(
    depth: int,
    character_id: Optional[int] = None,
    matrix: Optional[bytes] = None,
    color_transform: Optional[bytes] = None,
    name: Optional[str] = None,
    blend_mode: Optional[int] = None,
    clip_depth: Optional[int] = None,
    is_move: bool = False,
    ratio: Optional[int] = None,
) -> bytes:
    """Build a PlaceObject2 tag (tag 26)."""
    log.debug("build_place_object2: depth=%d char=%s move=%s", depth, character_id, is_move)
    # SWF PlaceObject2 flags byte (MSB→LSB):
    #   bit 7: HasClipActions
    #   bit 6: HasClipDepth
    #   bit 5: HasName
    #   bit 4: HasRatio
    #   bit 3: HasColorTransform
    #   bit 2: HasMatrix
    #   bit 1: HasCharacter
    #   bit 0: Move
    flags = 0
    if is_move:
        flags |= 0x01
    if character_id is not None:
        flags |= 0x02
    if matrix is not None:
        flags |= 0x04
    if color_transform is not None:
        flags |= 0x08
    if ratio is not None:
        flags |= 0x10
    if name is not None:
        flags |= 0x20
    if clip_depth is not None and clip_depth > 0:
        flags |= 0x40

    body = io.BytesIO()
    body.write(struct.pack("<B", flags))
    body.write(struct.pack("<H", depth))

    if character_id is not None:
        body.write(struct.pack("<H", character_id))
    if matrix is not None:
        body.write(matrix)
    if color_transform is not None:
        body.write(color_transform)
    if ratio is not None:
        body.write(struct.pack("<H", ratio))
    if name is not None:
        body.write(name.encode("utf-8") + b"\x00")
    if clip_depth is not None and clip_depth > 0:
        body.write(struct.pack("<H", clip_depth))

    return build_tag(TAG_PLACE_OBJECT2, body.getvalue())


# ── PlaceObject3 (tag 70) — adds blend mode and filters ─────────────────

def build_place_object3(
    depth: int,
    character_id: Optional[int] = None,
    matrix: Optional[bytes] = None,
    color_transform: Optional[bytes] = None,
    name: Optional[str] = None,
    blend_mode: Optional[int] = None,
    filters_data: Optional[bytes] = None,
    clip_depth: Optional[int] = None,
    is_move: bool = False,
    ratio: Optional[int] = None,
    has_image: bool = False,
) -> bytes:
    """Build a PlaceObject3 tag (tag 70) — supports blend mode, filters, ratio, and bitmap placement."""
    log.debug("build_place_object3: depth=%d char=%s move=%s blend=%s filters=%s", depth, character_id, is_move, blend_mode, filters_data is not None)

    # PlaceObject3 has TWO flag bytes
    flags1 = 0
    flags2 = 0

    if is_move:
        flags1 |= 0x01
    if character_id is not None:
        flags1 |= 0x02
    if matrix is not None:
        flags1 |= 0x04
    if color_transform is not None:
        flags1 |= 0x08
    if ratio is not None:
        flags1 |= 0x10
    if name is not None:
        flags1 |= 0x20
    if clip_depth is not None and clip_depth > 0:
        flags1 |= 0x40

    has_filter_list = filters_data is not None and len(filters_data) > 0
    has_blend_mode = blend_mode is not None

    if has_filter_list:
        flags2 |= 0x01
    if has_blend_mode:
        flags2 |= 0x02
    if has_image:
        flags2 |= 0x10

    body = io.BytesIO()
    body.write(struct.pack("<BB", flags1, flags2))
    body.write(struct.pack("<H", depth))

    if character_id is not None:
        body.write(struct.pack("<H", character_id))
    if matrix is not None:
        body.write(matrix)
    if color_transform is not None:
        body.write(color_transform)
    if ratio is not None:
        body.write(struct.pack("<H", ratio))
    if name is not None:
        body.write(name.encode("utf-8") + b"\x00")
    if clip_depth is not None and clip_depth > 0:
        body.write(struct.pack("<H", clip_depth))
    if has_filter_list:
        body.write(filters_data)
    if has_blend_mode:
        body.write(struct.pack("<B", blend_mode))

    return build_tag(TAG_PLACE_OBJECT3, body.getvalue())


# ── RemoveObject2 (tag 28) ──────────────────────────────────────────────

def build_remove_object2(depth: int) -> bytes:
    return build_tag(TAG_REMOVE_OBJECT2, struct.pack("<H", depth))


# ── DefineSprite (tag 39) ───────────────────────────────────────────────

def build_define_sprite(sprite_id: int, frame_count: int, control_tags: bytes) -> bytes:
    """
    Build a DefineSprite tag.
    `control_tags` should be the concatenation of all inner tags (PlaceObject,
    ShowFrame, FrameLabel, …) terminated by an End tag.
    """
    log.debug("build_define_sprite: sprite_id=%d frames=%d tags_len=%d", sprite_id, frame_count, len(control_tags))
    header = struct.pack("<HH", sprite_id, frame_count)
    return build_tag(TAG_DEFINE_SPRITE, header + control_tags)


# ── DoAction (tag 12) — AS2 frame script stub ───────────────────────────

def build_do_action_stop() -> bytes:
    """Simple DoAction that calls stop()."""
    # ActionStop = 0x07, end = 0x00
    return build_tag(TAG_DO_ACTION, b"\x07\x00")


def build_do_action_play() -> bytes:
    """Simple DoAction that calls play()."""
    # ActionPlay = 0x06, end = 0x00
    return build_tag(TAG_DO_ACTION, b"\x06\x00")


def build_do_action_goto_and_stop(frame: int) -> bytes:
    """DoAction: gotoAndStop(frame). frame is 0-based in AVM1."""
    # ActionGotoFrame = 0x81, length = 2, frameIndex (UI16), ActionStop, end
    data = b"\x81\x02\x00" + struct.pack("<H", frame) + b"\x07\x00"
    return build_tag(TAG_DO_ACTION, data)


def build_do_action_goto_and_play(frame: int) -> bytes:
    """DoAction: gotoAndPlay(frame). frame is 0-based in AVM1."""
    data = b"\x81\x02\x00" + struct.pack("<H", frame) + b"\x06\x00"
    return build_tag(TAG_DO_ACTION, data)


# ── Filters serialization (for PlaceObject3) ────────────────────────────

def _normalize_filter(f: dict) -> dict:
    """Convert import-format filter dict (name + fields) to editor format
    (class + params) so encode_filter_list can handle both."""
    if 'class' in f:
        return f  # already in editor format
    name = f.get('name', '')
    if name == 'BlurFilter':
        return {'class': 'BlurFilter', 'params': [
            None, f.get('blurX', 4.0), f.get('blurY', 4.0),
            f.get('quality', 1),
        ]}
    elif name == 'GlowFilter':
        return {'class': 'GlowFilter', 'params': [
            None, f.get('color', 0), f.get('alpha', 1.0),
            f.get('blurX', 4.0), f.get('blurY', 4.0),
            f.get('strength', 2.0), f.get('quality', 1),
            f.get('inner', False), f.get('knockout', False),
        ]}
    elif name == 'DropShadowFilter':
        return {'class': 'DropShadowFilter', 'params': [
            None, f.get('distance', 4.0), f.get('angle', 45.0),
            f.get('color', 0), f.get('alpha', 1.0),
            f.get('blurX', 4.0), f.get('blurY', 4.0),
            f.get('strength', 1.0), f.get('quality', 1),
            f.get('inner', False), f.get('knockout', False),
            f.get('hideObject', False),
        ]}
    elif name == 'BevelFilter':
        btype = f.get('type', 'full')
        return {'class': 'BevelFilter', 'params': [
            None, f.get('distance', 4.0), f.get('angle', 45.0),
            f.get('highlightColor', 0xFFFFFF), f.get('highlightAlpha', 1.0),
            f.get('shadowColor', 0), f.get('shadowAlpha', 1.0),
            f.get('blurX', 4.0), f.get('blurY', 4.0),
            f.get('strength', 1.0), f.get('quality', 1),
            btype, f.get('knockout', False),
        ]}
    elif name in ('GradientGlowFilter', 'GradientBevelFilter'):
        gtype = f.get('type', 'full')
        return {'class': name, 'params': [
            None, f.get('distance', 4.0), f.get('angle', 45.0),
            f.get('colors', [0]), f.get('alphas', [100]),
            f.get('ratios', [0]),
            f.get('blurX', 4.0), f.get('blurY', 4.0),
            f.get('strength', 1.0), f.get('quality', 1),
            gtype, f.get('knockout', False),
        ]}
    return f  # unknown, pass through as-is


def encode_filter_list(filters: list) -> bytes:
    """
    Encode a list of Next2D ISurfaceFilter objects into SWF FilterList bytes.
    """
    log.debug("encode_filter_list: %d filters", len(filters))
    if not filters:
        return b""

    buf = io.BytesIO()
    buf.write(struct.pack("<B", len(filters)))  # NumberOfFilters

    for f in filters:
        f = _normalize_filter(f)
        cls = f.get("class", "")
        params = f.get("params", [])
        # skip leading null
        p = params[1:] if params and params[0] is None else params

        if cls == "BlurFilter":
            buf.write(struct.pack("<B", SWF_FILTER_BLUR))
            blur_x = _to_fixed16(p[0] if len(p) > 0 else 4.0)
            blur_y = _to_fixed16(p[1] if len(p) > 1 else 4.0)
            quality = p[2] if len(p) > 2 else 1
            buf.write(struct.pack("<IIB", blur_x, blur_y, (quality << 3)))

        elif cls == "GlowFilter":
            buf.write(struct.pack("<B", SWF_FILTER_GLOW))
            color = int(p[0]) if len(p) > 0 else 0xFF0000
            alpha = p[1] if len(p) > 1 else 1.0
            blur_x = _to_fixed16(p[2] if len(p) > 2 else 4.0)
            blur_y = _to_fixed16(p[3] if len(p) > 3 else 4.0)
            strength = _to_fixed8(p[4] if len(p) > 4 else 2.0)
            quality = p[5] if len(p) > 5 else 1
            inner = p[6] if len(p) > 6 else False
            knockout = p[7] if len(p) > 7 else False
            r, g, b = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
            a = int(round(alpha * 255))
            buf.write(struct.pack("<BBBB", r, g, b, a))
            buf.write(struct.pack("<II", blur_x, blur_y))
            buf.write(struct.pack("<H", strength))
            flags = (int(inner) << 7) | (int(knockout) << 6) | (quality & 0x1F)
            buf.write(struct.pack("<B", flags))

        elif cls == "DropShadowFilter":
            buf.write(struct.pack("<B", SWF_FILTER_DROPSHADOW))
            distance = p[0] if len(p) > 0 else 4.0
            angle_deg = p[1] if len(p) > 1 else 45.0
            color = int(p[2]) if len(p) > 2 else 0x000000
            alpha = p[3] if len(p) > 3 else 1.0
            blur_x = _to_fixed16(p[4] if len(p) > 4 else 4.0)
            blur_y = _to_fixed16(p[5] if len(p) > 5 else 4.0)
            strength = _to_fixed8(p[6] if len(p) > 6 else 1.0)
            quality = p[7] if len(p) > 7 else 1
            inner = p[8] if len(p) > 8 else False
            knockout = p[9] if len(p) > 9 else False
            hide_obj = p[10] if len(p) > 10 else False
            r, g, b = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
            a = int(round(alpha * 255))
            buf.write(struct.pack("<BBBB", r, g, b, a))
            buf.write(struct.pack("<II", blur_x, blur_y))
            dist_fixed = _to_fixed16(distance)
            angle_fixed = _to_fixed16(angle_deg * math.pi / 180.0)
            buf.write(struct.pack("<II", dist_fixed, angle_fixed))
            buf.write(struct.pack("<H", strength))
            flags = (int(inner) << 7) | (int(knockout) << 6) | \
                    (int(hide_obj) << 5) | (quality & 0x1F)
            buf.write(struct.pack("<B", flags))

        elif cls == "BevelFilter":
            buf.write(struct.pack("<B", SWF_FILTER_BEVEL))
            distance = p[0] if len(p) > 0 else 4.0
            angle_deg = p[1] if len(p) > 1 else 45.0
            highlight_color = int(p[2]) if len(p) > 2 else 0xFFFFFF
            highlight_alpha = p[3] if len(p) > 3 else 1.0
            shadow_color = int(p[4]) if len(p) > 4 else 0x000000
            shadow_alpha = p[5] if len(p) > 5 else 1.0
            blur_x = _to_fixed16(p[6] if len(p) > 6 else 4.0)
            blur_y = _to_fixed16(p[7] if len(p) > 7 else 4.0)
            strength = _to_fixed8(p[8] if len(p) > 8 else 1.0)
            quality = p[9] if len(p) > 9 else 1
            bevel_type = p[10] if len(p) > 10 else "full"  # "inner","outer","full"
            knockout = p[11] if len(p) > 11 else False

            hr, hg, hb = (highlight_color >> 16) & 0xFF, (highlight_color >> 8) & 0xFF, highlight_color & 0xFF
            ha = int(round(highlight_alpha * 255))
            sr, sg, sb = (shadow_color >> 16) & 0xFF, (shadow_color >> 8) & 0xFF, shadow_color & 0xFF
            sa = int(round(shadow_alpha * 255))
            buf.write(struct.pack("<BBBB", sr, sg, sb, sa))
            buf.write(struct.pack("<BBBB", hr, hg, hb, ha))
            buf.write(struct.pack("<II", blur_x, blur_y))
            buf.write(struct.pack("<II", _to_fixed16(distance), _to_fixed16(angle_deg * math.pi / 180.0)))
            buf.write(struct.pack("<H", strength))
            on_top = 0
            inner_flag = 0
            if bevel_type == "inner":
                inner_flag = 1
            elif bevel_type == "full":
                inner_flag = 1
                on_top = 1
            flags = (int(inner_flag) << 7) | (int(knockout) << 6) | \
                    (int(on_top) << 4) | (quality & 0x0F)
            buf.write(struct.pack("<B", flags))

        elif cls == "ColorMatrixFilter":
            buf.write(struct.pack("<B", SWF_FILTER_COLORMATRIX))
            matrix = p[0] if len(p) > 0 else [1,0,0,0,0, 0,1,0,0,0, 0,0,1,0,0, 0,0,0,1,0]
            for val in matrix:
                buf.write(struct.pack("<f", float(val)))

        elif cls == "ConvolutionFilter":
            buf.write(struct.pack("<B", SWF_FILTER_CONVOLUTION))
            mat_x = int(p[0]) if len(p) > 0 else 3
            mat_y = int(p[1]) if len(p) > 1 else 3
            matrix = p[2] if len(p) > 2 else [0] * (mat_x * mat_y)
            divisor = p[3] if len(p) > 3 else 1.0
            bias = p[4] if len(p) > 4 else 0.0
            preserve_alpha = p[5] if len(p) > 5 else True
            clamp = p[6] if len(p) > 6 else True
            color = int(p[7]) if len(p) > 7 else 0x000000
            alpha = p[8] if len(p) > 8 else 0.0
            buf.write(struct.pack("<BB", mat_x, mat_y))
            buf.write(struct.pack("<f", divisor))
            buf.write(struct.pack("<f", bias))
            for val in matrix:
                buf.write(struct.pack("<f", float(val)))
            r2, g2, b2 = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
            a2 = int(round(alpha * 255))
            buf.write(struct.pack("<BBBB", r2, g2, b2, a2))
            flags = (int(clamp) << 1) | int(preserve_alpha)
            buf.write(struct.pack("<B", flags))

        elif cls in ("GradientGlowFilter", "GradientBevelFilter"):
            fid = SWF_FILTER_GRADIENT_GLOW if cls == "GradientGlowFilter" else SWF_FILTER_GRADIENT_BEVEL
            buf.write(struct.pack("<B", fid))
            distance = p[0] if len(p) > 0 else 4.0
            angle_deg = p[1] if len(p) > 1 else 45.0
            colors = p[2] if len(p) > 2 else [0]
            alphas = p[3] if len(p) > 3 else [1.0]
            ratios = p[4] if len(p) > 4 else [0]
            blur_x = _to_fixed16(p[5] if len(p) > 5 else 4.0)
            blur_y = _to_fixed16(p[6] if len(p) > 6 else 4.0)
            strength = _to_fixed8(p[7] if len(p) > 7 else 1.0)
            quality = p[8] if len(p) > 8 else 1
            grad_type = p[9] if len(p) > 9 else "full"
            knockout = p[10] if len(p) > 10 else False

            num_colors = len(colors)
            buf.write(struct.pack("<B", num_colors))
            for i in range(num_colors):
                c = int(colors[i])
                alph = alphas[i] if i < len(alphas) else 1.0
                cr, cg, cb = (c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF
                ca = int(round(alph * 255))
                buf.write(struct.pack("<BBBB", cr, cg, cb, ca))
            for i in range(num_colors):
                buf.write(struct.pack("<B", int(ratios[i]) if i < len(ratios) else 0))
            buf.write(struct.pack("<II", blur_x, blur_y))
            buf.write(struct.pack("<II", _to_fixed16(distance), _to_fixed16(angle_deg * math.pi / 180.0)))
            buf.write(struct.pack("<H", strength))
            on_top = 0
            inner_flag = 0
            if grad_type == "inner":
                inner_flag = 1
            elif grad_type == "full":
                inner_flag = 1
                on_top = 1
            flags = (int(inner_flag) << 7) | (int(knockout) << 6) | \
                    (int(on_top) << 4) | (quality & 0x0F)
            buf.write(struct.pack("<B", flags))

    return buf.getvalue()


def _to_fixed16(value: float) -> int:
    """Convert float to unsigned 16.16 fixed-point stored as UI32."""
    return int(round(value * 65536)) & 0xFFFFFFFF


def _to_fixed8(value: float) -> int:
    """Convert float to unsigned 8.8 fixed-point stored as UI16."""
    return int(round(value * 256)) & 0xFFFF


# ── SWF File assembly ───────────────────────────────────────────────────

def build_swf_file(
    width: int,
    height: int,
    fps: int,
    frame_count: int,
    tags: bytes,
    compressed: bool = True,
    version: int = 14,
) -> bytes:
    """
    Assemble a complete SWF file.
    `tags` should be the concatenation of ALL tags (including End).
    """
    log.info("build_swf_file: %dx%d @%dfps frames=%d compressed=%s ver=%d tags_len=%d",
             width, height, fps, frame_count, compressed, version, len(tags))
    rect = write_rect(0, twips(width), 0, twips(height))
    # Frame rate: 8.8 fixed-point (hi byte = integer fps, lo = fraction)
    fps_bytes = struct.pack("<H", fps << 8)
    frame_count_bytes = struct.pack("<H", frame_count)

    body = rect + fps_bytes + frame_count_bytes + tags

    # File length = 8 (header) + body length
    file_length = 8 + len(body)

    if compressed:
        sig = b"CWS"
        compressed_body = zlib.compress(body, 9)
        header = sig + struct.pack("<BI", version, file_length)
        return header + compressed_body
    else:
        sig = b"FWS"
        header = sig + struct.pack("<BI", version, file_length)
        return header + body
