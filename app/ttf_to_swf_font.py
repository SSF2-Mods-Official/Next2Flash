"""
ttf_to_swf_font.py — Convert a TrueType font to DefineFont3 raw body for SWF embedding.

Reads glyph outlines from a TTF file using fontTools and produces a binary
DefineFont3 tag body (without the 2-byte charID prefix) suitable for storing
as ``fontData`` on a font library entry.

Coordinate systems:
  - TTF: Y increases upward, units in font units (unitsPerEm)
  - SWF DefineFont3: Y increases downward, EM square = 20480 units
"""

from __future__ import annotations

import io
import logging
import struct
from typing import List, Tuple

log = logging.getLogger(__name__)

_EM_SWF_FONT3 = 20480  # DefineFont3 EM square size


def ttf_to_define_font3(ttf_bytes: bytes, font_name: str | None = None) -> bytes:
    """Convert TTF file bytes to a DefineFont3 tag body (after charID).

    Args:
        ttf_bytes: Raw .ttf file content.
        font_name: Override the embedded font name. If *None*, read from the
                   TTF name table.

    Returns:
        Raw binary body for a DefineFont3 tag (tag type 75), excluding the
        leading 2-byte character ID.  Returns empty bytes on failure.
    """
    from fontTools.ttLib import TTFont

    font = TTFont(io.BytesIO(ttf_bytes))

    # ── Font metadata ────────────────────────────────────────────────
    if not font_name:
        name_table = font['name']
        font_name = name_table.getBestFamilyName() or 'Unknown'

    os2 = font.get('OS/2')
    bold = bool(os2 and os2.fsSelection & 0x20)
    italic = bool(os2 and os2.fsSelection & 0x01)

    hhea = font['hhea']
    upem = font['head'].unitsPerEm
    scale = _EM_SWF_FONT3 / upem

    ascent = int(hhea.ascent * scale)
    descent = int(abs(hhea.descent) * scale)
    leading = int(hhea.lineGap * scale)

    # ── Character map ────────────────────────────────────────────────
    cmap = font.getBestCmap()
    if not cmap:
        log.warning('ttf_to_define_font3: no usable cmap in font %s', font_name)
        return b''

    hmtx = font['hmtx']
    glyph_set = font.getGlyphSet()

    # Build sorted glyph list (skip code point 0)
    entries: List[Tuple[int, str]] = sorted(
        ((cp, gn) for cp, gn in cmap.items() if cp > 0),
        key=lambda t: t[0],
    )
    if not entries:
        return b''

    # ── Build per-glyph data ─────────────────────────────────────────
    code_table: List[int] = []
    advance_table: List[int] = []
    glyph_shape_bytes: List[bytes] = []  # raw SWF SHAPE per glyph

    from fontTools.pens.recordingPen import RecordingPen

    for cp, glyph_name in entries:
        code_table.append(cp)

        # Advance width
        adv, _lsb = hmtx[glyph_name]
        advance_table.append(max(int(adv * scale), 0))

        # Record glyph drawing commands
        pen = RecordingPen()
        try:
            glyph_set[glyph_name].draw(pen)
        except Exception:
            glyph_shape_bytes.append(_empty_glyph_shape())
            continue

        glyph_shape_bytes.append(_recording_to_swf_shape(pen.value, scale))

    num_glyphs = len(code_table)

    # ── Assemble DefineFont3 body ────────────────────────────────────
    body = io.BytesIO()

    # Flags
    flags = 0x80  # HasLayout
    flags |= 0x08  # WideOffsets (always use UI32)
    flags |= 0x04  # WideCodes  (always for Font3)
    if italic:
        flags |= 0x02
    if bold:
        flags |= 0x01
    body.write(struct.pack('B', flags))

    # Language code (1 = Latin)
    body.write(struct.pack('B', 1))

    # Font name
    name_bytes = font_name.encode('utf-8')
    body.write(struct.pack('B', len(name_bytes)))
    body.write(name_bytes)

    # NumGlyphs
    body.write(struct.pack('<H', num_glyphs))

    # ── Offset table (WideOffsets → UI32) ────────────────────────────
    # Offsets are relative to the start of the offset table itself.
    # offset_table_size = num_glyphs * 4 + 4 (for codeTableOffset)
    offset_table_size = num_glyphs * 4 + 4
    running_offset = offset_table_size
    offsets: List[int] = []
    for sb in glyph_shape_bytes:
        offsets.append(running_offset)
        running_offset += len(sb)
    code_table_offset = running_offset

    for off in offsets:
        body.write(struct.pack('<I', off))
    body.write(struct.pack('<I', code_table_offset))

    # ── Glyph shape data ─────────────────────────────────────────────
    for sb in glyph_shape_bytes:
        body.write(sb)

    # ── Code table (WideCodes → UI16) ────────────────────────────────
    for cp in code_table:
        body.write(struct.pack('<H', cp))

    # ── Layout section ───────────────────────────────────────────────
    body.write(struct.pack('<H', ascent & 0xFFFF))
    body.write(struct.pack('<H', descent & 0xFFFF))
    body.write(struct.pack('<h', leading))

    # Advance table
    for adv in advance_table:
        body.write(struct.pack('<H', adv & 0xFFFF))

    # Bounds table (one RECT per glyph) — write minimal rects
    from swf_writer import write_rect
    for sb in glyph_shape_bytes:
        body.write(write_rect(0, 0, 0, 0))

    # Kerning count = 0
    body.write(struct.pack('<H', 0))

    result = body.getvalue()
    log.info('ttf_to_define_font3: %s -> %d glyphs, %d bytes',
             font_name, num_glyphs, len(result))
    return result


# ─────────────────────────────────────────────────────────────────────────
#  SWF glyph shape helpers
# ─────────────────────────────────────────────────────────────────────────

def _empty_glyph_shape() -> bytes:
    """Return minimal SHAPE bytes for an empty glyph (space, etc.)."""
    from swf_binary_io import BitWriter
    bw = BitWriter()
    bw.write_ub(4, 1)   # NumFillBits = 1
    bw.write_ub(4, 0)   # NumLineBits = 0
    bw.write_ub(6, 0)   # EndShapeRecord (type=0, flags=0)
    return bw.get_bytes()


def _recording_to_swf_shape(operations: list, scale: float) -> bytes:
    """Convert fontTools RecordingPen operations to SWF glyph SHAPE bytes.

    Operations are tuples like:
      ('moveTo', ((x, y),))
      ('lineTo', ((x, y),))
      ('qCurveTo', ((cx, cy), (ax, ay)))
      ('curveTo', ((cx1,cy1), (cx2,cy2), (ax,ay)))  — cubic (rare in TTF)
      ('closePath', ())
      ('endPath', ())
    """
    from swf_binary_io import BitWriter, _nbits_signed

    # First, collect all contour data in SWF coordinates
    contours: List[List[Tuple]] = []
    current: List[Tuple] = []

    for op_name, args in operations:
        if op_name == 'moveTo':
            if current:
                contours.append(current)
            x = int(args[0][0] * scale)
            y = -int(args[0][1] * scale)  # flip Y for SWF
            current = [('move', x, y)]
        elif op_name == 'lineTo':
            x = int(args[0][0] * scale)
            y = -int(args[0][1] * scale)
            current.append(('line', x, y))
        elif op_name == 'qCurveTo':
            # Quadratic bezier — may have multiple off-curve points
            # (TrueType implicit on-curve points between consecutive off-curves)
            if len(args) >= 2:
                # Last point is the on-curve anchor
                for i in range(len(args) - 1):
                    cx = int(args[i][0] * scale)
                    cy = -int(args[i][1] * scale)
                    if i + 1 < len(args) - 1:
                        # Implicit on-curve: midpoint between consecutive off-curves
                        nx = int(args[i + 1][0] * scale)
                        ny = -int(args[i + 1][1] * scale)
                        ax = (cx + nx) // 2
                        ay = (cy + ny) // 2
                    else:
                        ax = int(args[-1][0] * scale)
                        ay = -int(args[-1][1] * scale)
                    current.append(('curve', cx, cy, ax, ay))
            elif len(args) == 1:
                # Degenerate: just a point
                x = int(args[0][0] * scale)
                y = -int(args[0][1] * scale)
                current.append(('line', x, y))
        elif op_name == 'curveTo':
            # Cubic bezier — approximate with quadratic
            if len(args) == 3:
                # Simple midpoint approximation
                cx = int((args[0][0] + args[1][0]) / 2 * scale)
                cy = -int((args[0][1] + args[1][1]) / 2 * scale)
                ax = int(args[2][0] * scale)
                ay = -int(args[2][1] * scale)
                current.append(('curve', cx, cy, ax, ay))
        elif op_name in ('closePath', 'endPath'):
            if current:
                contours.append(current)
                current = []

    if current:
        contours.append(current)

    if not contours:
        return _empty_glyph_shape()

    # ── Write SWF SHAPE ──────────────────────────────────────────
    bw = BitWriter()
    bw.write_ub(4, 1)  # NumFillBits = 1
    bw.write_ub(4, 0)  # NumLineBits = 0

    for contour in contours:
        if not contour:
            continue

        cur_x, cur_y = 0, 0

        for i, cmd in enumerate(contour):
            if cmd[0] == 'move':
                # StyleChangeRecord with MoveTo + FillStyle1=1
                bw.write_ub(1, 0)  # Non-edge
                flags = 0x01 | 0x04  # StateMoveTo + StateFillStyle1
                bw.write_ub(5, flags)
                mx, my = cmd[1], cmd[2]
                move_bits = max(_nbits_signed(mx), _nbits_signed(my), 1)
                bw.write_ub(5, move_bits)
                bw.write_sb(move_bits, mx)
                bw.write_sb(move_bits, my)
                # FillStyle1 = 1
                bw.write_ub(1, 1)
                cur_x, cur_y = mx, my

            elif cmd[0] == 'line':
                dx = cmd[1] - cur_x
                dy = cmd[2] - cur_y
                if dx == 0 and dy == 0:
                    continue
                bw.write_ub(1, 1)  # Edge
                bw.write_ub(1, 1)  # Straight
                if dx == 0:
                    num_bits = max(_nbits_signed(dy), 1)
                    bw.write_ub(4, num_bits - 2)
                    bw.write_ub(1, 0)  # Not general
                    bw.write_ub(1, 1)  # Vertical
                    bw.write_sb(num_bits, dy)
                elif dy == 0:
                    num_bits = max(_nbits_signed(dx), 1)
                    bw.write_ub(4, num_bits - 2)
                    bw.write_ub(1, 0)  # Not general
                    bw.write_ub(1, 0)  # Horizontal
                    bw.write_sb(num_bits, dx)
                else:
                    num_bits = max(_nbits_signed(dx), _nbits_signed(dy), 2)
                    bw.write_ub(4, num_bits - 2)
                    bw.write_ub(1, 1)  # General line
                    bw.write_sb(num_bits, dx)
                    bw.write_sb(num_bits, dy)
                cur_x, cur_y = cmd[1], cmd[2]

            elif cmd[0] == 'curve':
                cx, cy, ax, ay = cmd[1], cmd[2], cmd[3], cmd[4]
                cx_delta = cx - cur_x
                cy_delta = cy - cur_y
                ax_delta = ax - cx
                ay_delta = ay - cy
                num_bits = max(
                    _nbits_signed(cx_delta),
                    _nbits_signed(cy_delta),
                    _nbits_signed(ax_delta),
                    _nbits_signed(ay_delta),
                    2,
                )
                bw.write_ub(1, 1)  # Edge
                bw.write_ub(1, 0)  # Curved
                bw.write_ub(4, num_bits - 2)
                bw.write_sb(num_bits, cx_delta)
                bw.write_sb(num_bits, cy_delta)
                bw.write_sb(num_bits, ax_delta)
                bw.write_sb(num_bits, ay_delta)
                cur_x, cur_y = ax, ay

    # EndShapeRecord
    bw.write_ub(1, 0)  # Non-edge
    bw.write_ub(5, 0)  # flags = 0 → end

    return bw.get_bytes()
