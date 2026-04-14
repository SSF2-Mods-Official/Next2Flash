"""
swf_font_to_ttf.py — Convert DefineFont3/DefineFont2 SWF data to TrueType/WOFF.

Parses glyph outlines from SWF font tags and builds a valid TTF using fontTools.
SWF glyph shapes use quadratic bezier curves — same as TrueType — so the
conversion is direct with only coordinate-system differences:
  - SWF: Y increases downward, units in twips (1/20 px)
  - TTF: Y increases upward, units in font units (upem)
"""

from __future__ import annotations

import io
import logging
import struct
from typing import List, Optional, Tuple

log = logging.getLogger(__name__)


def _parse_define_font3_full(raw_body: bytes, tag_type: int = 75):
    """Parse DefineFont3 (or DefineFont2) body (after charID) into structured data.

    Returns dict with:
      font_name, bold, italic, num_glyphs, code_table, glyph_shapes,
      has_layout, ascent, descent, leading, advance_table, bounds_table
    """
    flags = raw_body[0]
    has_layout = bool(flags & 0x80)
    wide_offsets = bool(flags & 0x08)
    wide_codes = bool(flags & 0x04) if tag_type == 48 else True  # Font3 always wide
    italic = bool(flags & 0x02)
    bold = bool(flags & 0x01)

    lang_code = raw_body[1]
    name_len = raw_body[2]
    font_name = raw_body[3:3 + name_len].rstrip(b'\x00').decode('utf-8', errors='replace')
    offset = 3 + name_len

    num_glyphs = struct.unpack_from('<H', raw_body, offset)[0]
    offset += 2

    if num_glyphs == 0:
        return {
            'font_name': font_name, 'bold': bold, 'italic': italic,
            'num_glyphs': 0, 'code_table': [], 'glyph_shapes': [],
            'has_layout': has_layout, 'ascent': 0, 'descent': 0,
            'leading': 0, 'advance_table': [], 'bounds_table': [],
        }

    # Read offset table to locate each glyph shape
    ot_start = offset
    offsets = []
    if wide_offsets:
        for i in range(num_glyphs):
            offsets.append(struct.unpack_from('<I', raw_body, offset)[0])
            offset += 4
        code_table_offset_val = struct.unpack_from('<I', raw_body, offset)[0]
        offset += 4
    else:
        for i in range(num_glyphs):
            offsets.append(struct.unpack_from('<H', raw_body, offset)[0])
            offset += 2
        code_table_offset_val = struct.unpack_from('<H', raw_body, offset)[0]
        offset += 2

    # Glyph shape data starts at ot_start
    shape_data_start = ot_start

    # Parse each glyph shape
    glyph_shapes = []
    for i in range(num_glyphs):
        shape_start = shape_data_start + offsets[i]
        if i + 1 < num_glyphs:
            shape_end = shape_data_start + offsets[i + 1]
        else:
            shape_end = shape_data_start + code_table_offset_val
        shape_bytes = raw_body[shape_start:shape_end]
        try:
            contours = _parse_glyph_shape(shape_bytes)
        except Exception as e:
            log.debug("Glyph %d parse error: %s", i, e)
            contours = []
        glyph_shapes.append(contours)

    # Read code table
    ct_start = shape_data_start + code_table_offset_val
    code_table = []
    for i in range(num_glyphs):
        if wide_codes:
            cp = struct.unpack_from('<H', raw_body, ct_start + i * 2)[0]
            code_table.append(cp)
        else:
            code_table.append(raw_body[ct_start + i])

    # Layout info (if present)
    ascent = 0
    descent = 0
    leading = 0
    advance_table = []
    bounds_table = []

    if has_layout:
        layout_offset = ct_start + num_glyphs * (2 if wide_codes else 1)
        if layout_offset + 4 <= len(raw_body):
            ascent = struct.unpack_from('<H', raw_body, layout_offset)[0]
            descent = struct.unpack_from('<H', raw_body, layout_offset + 2)[0]
            leading = struct.unpack_from('<h', raw_body, layout_offset + 4)[0]
            layout_offset += 6

            # Advance width table
            for i in range(num_glyphs):
                if layout_offset + 2 <= len(raw_body):
                    adv = struct.unpack_from('<H', raw_body, layout_offset)[0]
                    advance_table.append(adv)
                    layout_offset += 2
                else:
                    advance_table.append(1024)  # default

            # Bounds table (RECT per glyph) — skip for now, we use shape bounds
            # Each is a variable-length RECT

    return {
        'font_name': font_name,
        'bold': bold,
        'italic': italic,
        'num_glyphs': num_glyphs,
        'code_table': code_table,
        'glyph_shapes': glyph_shapes,
        'has_layout': has_layout,
        'ascent': ascent,
        'descent': descent,
        'leading': leading,
        'advance_table': advance_table,
        'bounds_table': bounds_table,
    }


def _parse_glyph_shape(data: bytes) -> List[List[Tuple]]:
    """Parse a SWF glyph SHAPE into contour lists.

    SWF font glyph shapes have:
    - No fill/line style arrays (they're implied)
    - NumFillBits and NumLineBits in the first byte
    - Shape records: StyleChange, StraightEdge, CurvedEdge, EndShape

    Returns list of contours, where each contour is a list of tuples:
      ('move', x, y)
      ('line', x, y)
      ('curve', cx, cy, ax, ay)  # control point, anchor point
    """
    from swf_binary_io import BitReader

    if not data or len(data) < 1:
        return []

    br = BitReader(data, 0)

    # NumFillBits, NumLineBits
    num_fill_bits = br.read_ub(4)
    num_line_bits = br.read_ub(4)

    contours = []
    current_contour = []
    cur_x = 0
    cur_y = 0

    while True:
        if br.byte_pos >= len(data):
            break

        type_flag = br.read_ub(1)
        if type_flag == 0:
            # Non-edge record
            flags = br.read_ub(5)
            if flags == 0:
                # EndShapeRecord
                if current_contour:
                    contours.append(current_contour)
                break

            # StyleChangeRecord
            if flags & 0x01:  # StateMoveTo
                move_bits = br.read_ub(5)
                cur_x = br.read_sb(move_bits)
                cur_y = br.read_sb(move_bits)
                if current_contour:
                    contours.append(current_contour)
                current_contour = [('move', cur_x, cur_y)]
            if flags & 0x02:  # StateFillStyle0
                br.read_ub(num_fill_bits)
            if flags & 0x04:  # StateFillStyle1
                br.read_ub(num_fill_bits)
            if flags & 0x08:  # StateLineStyle
                br.read_ub(num_line_bits)
            # Font glyphs don't have StateNewStyles (flags & 0x10)
        else:
            # Edge record
            straight = br.read_ub(1)
            if straight:
                # StraightEdgeRecord
                num_bits = br.read_ub(4) + 2
                general_line = br.read_ub(1)
                if general_line:
                    dx = br.read_sb(num_bits)
                    dy = br.read_sb(num_bits)
                else:
                    vert_line = br.read_ub(1)
                    if vert_line:
                        dx = 0
                        dy = br.read_sb(num_bits)
                    else:
                        dx = br.read_sb(num_bits)
                        dy = 0
                cur_x += dx
                cur_y += dy
                current_contour.append(('line', cur_x, cur_y))
            else:
                # CurvedEdgeRecord (quadratic bezier)
                num_bits = br.read_ub(4) + 2
                cx_delta = br.read_sb(num_bits)
                cy_delta = br.read_sb(num_bits)
                ax_delta = br.read_sb(num_bits)
                ay_delta = br.read_sb(num_bits)
                ctrl_x = cur_x + cx_delta
                ctrl_y = cur_y + cy_delta
                cur_x = ctrl_x + ax_delta
                cur_y = ctrl_y + ay_delta
                current_contour.append(('curve', ctrl_x, ctrl_y, cur_x, cur_y))

    if current_contour and current_contour not in contours:
        contours.append(current_contour)

    return contours


def swf_font_to_ttf(raw_body: bytes, tag_type: int = 75) -> bytes:
    """Convert a DefineFont3/DefineFont2 raw body (after 2-byte charID) to TTF bytes.

    Args:
        raw_body: DefineFont3 tag body after the charID
        tag_type: 75 for DefineFont3, 48 for DefineFont2

    Returns:
        TTF font file bytes
    """
    from fontTools.fontBuilder import FontBuilder

    font_data = _parse_define_font3_full(raw_body, tag_type)

    font_name = font_data['font_name'] or 'SWFFont'
    bold = font_data['bold']
    italic = font_data['italic']
    num_glyphs = font_data['num_glyphs']
    code_table = font_data['code_table']
    glyph_shapes = font_data['glyph_shapes']
    advance_table = font_data['advance_table']
    ascent = font_data['ascent']
    descent = font_data['descent']

    # SWF uses twips (1/20 pixel) at 72 DPI for font glyphs.
    # DefineFont3 uses EM square of 20480 twips (1024 * 20).
    # TrueType uses units per em (typically 1024 or 2048).
    # We'll use upem=1024 and scale from SWF twips to font units.
    UPEM = 1024
    # DefineFont3: coords are in 1/20 of an EM unit → scale factor:
    # SWF EM = 20 * 1024 = 20480 twips
    # TTF EM = 1024 units
    # scale = 1024 / 20480 = 1/20
    SCALE = UPEM / 20480.0

    if not num_glyphs or not code_table:
        # Empty font — build minimal valid TTF
        fb = FontBuilder(UPEM, isTTF=True)
        fb.setupGlyphOrder(['.notdef'])
        fb.setupCharacterMap({})
        fb.setupGlyf({'.notdef': {}})
        fb.setupHorizontalMetrics({'.notdef': (500, 0)})
        fb.setupHorizontalHeader(ascent=800, descent=-200)
        fb.setupNameTable({'familyName': font_name, 'styleName': 'Regular'})
        fb.setupOs2(sTypoAscender=800, sTypoDescender=-200)
        fb.setupPost()
        buf = io.BytesIO()
        fb.font.save(buf)
        return buf.getvalue()

    # Build glyph names and char map
    glyph_names = ['.notdef']
    char_map = {}  # unicode → glyph name
    metrics = {'.notdef': (UPEM // 2, 0)}

    for i, cp in enumerate(code_table):
        gname = f'uni{cp:04X}'
        # Ensure unique names
        if gname in metrics:
            gname = f'uni{cp:04X}.{i}'
        glyph_names.append(gname)
        char_map[cp] = gname

        # Advance width
        if i < len(advance_table) and advance_table[i] > 0:
            adv = int(advance_table[i] * SCALE)
        else:
            # Estimate from glyph bounds
            adv = _estimate_advance(glyph_shapes[i], SCALE) if i < len(glyph_shapes) else UPEM // 2
        metrics[gname] = (max(adv, 1), 0)

    # Scale ascent/descent
    ttf_ascent = int(ascent * SCALE) if ascent else int(UPEM * 0.8)
    ttf_descent = -int(descent * SCALE) if descent else -int(UPEM * 0.2)
    if ttf_ascent <= 0:
        ttf_ascent = int(UPEM * 0.8)
    if ttf_descent >= 0:
        ttf_descent = -int(UPEM * 0.2)

    # Build TTF
    fb = FontBuilder(UPEM, isTTF=True)
    fb.setupGlyphOrder(glyph_names)
    fb.setupCharacterMap(char_map)

    # Build glyf table
    from fontTools.ttLib import TTFont
    from fontTools.pens.pointPen import PointToSegmentPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    glyph_table = {}
    glyph_table['.notdef'] = _build_notdef_glyph(fb, UPEM)

    for i, cp in enumerate(code_table):
        gname = glyph_names[i + 1]  # +1 because .notdef is at index 0
        if i < len(glyph_shapes):
            glyph_table[gname] = _build_glyph(fb, glyph_shapes[i], SCALE)
        else:
            glyph_table[gname] = _build_empty_glyph(fb)

    fb.setupGlyf(glyph_table)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ttf_ascent, descent=ttf_descent)

    # Name table
    style = 'Regular'
    if bold and italic:
        style = 'Bold Italic'
    elif bold:
        style = 'Bold'
    elif italic:
        style = 'Italic'
    fb.setupNameTable({'familyName': font_name, 'styleName': style})
    fb.setupOS2(sTypoAscender=ttf_ascent, sTypoDescender=ttf_descent,
                sTypoLineGap=0)
    fb.setupPost()

    buf = io.BytesIO()
    fb.font.save(buf)
    return buf.getvalue()


def swf_font_to_woff(raw_body: bytes, tag_type: int = 75) -> bytes:
    """Convert DefineFont3/DefineFont2 raw body to WOFF bytes (smaller for web)."""
    from fontTools.ttLib import TTFont

    ttf_bytes = swf_font_to_ttf(raw_body, tag_type)

    # Convert TTF → WOFF
    font = TTFont(io.BytesIO(ttf_bytes))
    buf = io.BytesIO()
    font.flavor = 'woff'
    font.save(buf)
    return buf.getvalue()


def _estimate_advance(contours: List[List[Tuple]], scale: float) -> int:
    """Estimate advance width from glyph contour bounds."""
    max_x = 0
    for contour in contours:
        for cmd in contour:
            if cmd[0] == 'move':
                max_x = max(max_x, abs(cmd[1]))
            elif cmd[0] == 'line':
                max_x = max(max_x, abs(cmd[1]))
            elif cmd[0] == 'curve':
                max_x = max(max_x, abs(cmd[1]), abs(cmd[3]))
    return max(int(max_x * scale) + 50, 100)


def _build_notdef_glyph(fb, upem):
    """Build a .notdef glyph (empty rectangle)."""
    from fontTools.pens.ttGlyphPen import TTGlyphPointPen
    pen = TTGlyphPointPen(None)
    # Simple empty glyph
    pen.beginPath()
    pen.endPath()
    return pen.glyph()


def _build_empty_glyph(fb):
    """Build an empty glyph."""
    from fontTools.pens.ttGlyphPen import TTGlyphPointPen
    pen = TTGlyphPointPen(None)
    pen.beginPath()
    pen.endPath()
    return pen.glyph()


def _build_glyph(fb, contours: List[List[Tuple]], scale: float):
    """Build a TTF glyph from SWF contour data.

    SWF coordinates: Y-down, in twips (1/20 px, with EM=20480)
    TTF coordinates: Y-up, in font units (EM=1024)

    So we scale by `scale` and flip Y.
    """
    from fontTools.pens.ttGlyphPen import TTGlyphPointPen

    pen = TTGlyphPointPen(None)

    for contour in contours:
        if not contour:
            continue

        points = []
        for cmd in contour:
            if cmd[0] == 'move':
                x = int(cmd[1] * scale)
                y = -int(cmd[2] * scale)  # flip Y
                points.append((x, y, 'move'))
            elif cmd[0] == 'line':
                x = int(cmd[1] * scale)
                y = -int(cmd[2] * scale)
                points.append((x, y, 'line'))
            elif cmd[0] == 'curve':
                cx = int(cmd[1] * scale)
                cy = -int(cmd[2] * scale)
                ax = int(cmd[3] * scale)
                ay = -int(cmd[4] * scale)
                points.append((cx, cy, 'qcurve_off'))
                points.append((ax, ay, 'qcurve_on'))

        if len(points) < 2:
            continue

        pen.beginPath()
        for x, y, ptype in points:
            if ptype == 'move':
                pen.addPoint((x, y), segmentType='line')
            elif ptype == 'line':
                pen.addPoint((x, y), segmentType='line')
            elif ptype == 'qcurve_off':
                pen.addPoint((x, y))  # off-curve
            elif ptype == 'qcurve_on':
                pen.addPoint((x, y), segmentType='qcurve')
        pen.endPath()

    return pen.glyph()
