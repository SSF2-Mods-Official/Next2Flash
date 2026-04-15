"""
swf_shape_to_recodes.py — Parse SWF DefineShape binary data and convert
to Next2D recodes (flat command array) for display in the Next2D Animation Tool.

This module replicates the logic from the Next2D tool's built-in SWF shape parser
($vtc.convert) in Python, enabling direct SWF → recodes conversion without
needing JPEXS SVG intermediary.

Supports DefineShape through DefineShape4 (tags 2, 22, 32, 83).
Handles: solid fills, gradient fills (linear/radial/focal), bitmap fills,
         solid line styles, gradient/bitmap strokes (Shape4).
"""

from __future__ import annotations

import copy
import logging
import struct
from typing import Dict, List, Optional, Tuple

from swf_binary_io import BitReader
from swf_constants import ShapeCommand, MOVE_TO, CURVE_TO, LINE_TO, CUBIC, ARC, FILL_STYLE, STROKE_STYLE, END_FILL, END_STROKE, BEGIN_PATH, GRADIENT_FILL, GRADIENT_STROKE, CLOSE_PATH, BITMAP_FILL, BITMAP_STROKE

log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  SWF PRIMITIVE READERS
# ═══════════════════════════════════════════════════════════════════════════

def _read_rgb(br: BitReader) -> dict:
    return {'R': br.read_ui8(), 'G': br.read_ui8(), 'B': br.read_ui8(), 'A': 1.0}


def _read_rgba(br: BitReader) -> dict:
    r = br.read_ui8()
    g = br.read_ui8()
    b = br.read_ui8()
    a = br.read_ui8() / 255.0
    return {'R': r, 'G': g, 'B': b, 'A': a}


def _read_matrix(br: BitReader) -> List[float]:
    """Read MATRIX → [scaleX, rotSkew0, rotSkew1, scaleY, translateX, translateY]."""
    br.align()
    t = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    if br.read_ub(1):  # HasScale
        n = br.read_ub(5)
        t[0] = br.read_sb(n) / 65536.0
        t[3] = br.read_sb(n) / 65536.0
    if br.read_ub(1):  # HasRotate
        n = br.read_ub(5)
        t[1] = br.read_sb(n) / 65536.0
        t[2] = br.read_sb(n) / 65536.0
    n = br.read_ub(5)
    t[4] = br.read_sb(n) / 20.0
    t[5] = br.read_sb(n) / 20.0
    return t


def _read_gradient(br: BitReader, tag_type: int) -> dict:
    """Read GRADIENT structure.  Must be called byte-aligned (matches JS byteAlign before gradient)."""
    br.align()
    spread = br.read_ub(2)
    interp = br.read_ub(2)
    count = br.read_ub(4)
    records = []
    for _ in range(count):
        ratio = br.read_ui8()
        color = _read_rgba(br) if tag_type in (32, 83) else _read_rgb(br)
        records.append({'Ratio': ratio, 'Color': color})
    return {
        'SpreadMode': spread, 'InterpolationMode': interp,
        'GradientRecords': records, 'FocalPoint': 0.0,
    }


def _read_focal_gradient(br: BitReader, tag_type: int) -> dict:
    """Read FOCALGRADIENT (DefineShape4)."""
    grad = _read_gradient(br, tag_type)
    grad['FocalPoint'] = br.read_si16() / 256.0
    return grad


def _read_fill_style(br: BitReader, tag_type: int) -> dict:
    """Read a single FILLSTYLE."""
    ft = br.read_ui8()
    style: dict = {'fillStyleType': ft}
    if ft == 0:
        style['Color'] = _read_rgba(br) if tag_type in (32, 83) else _read_rgb(br)
    elif ft in (16, 18):
        style['gradientMatrix'] = _read_matrix(br)
        style['gradient'] = _read_gradient(br, tag_type)
    elif ft == 19:
        style['gradientMatrix'] = _read_matrix(br)
        style['gradient'] = _read_focal_gradient(br, tag_type)
    elif ft in (64, 65, 66, 67):
        style['bitmapId'] = br.read_ui16()
        style['bitmapMatrix'] = _read_matrix(br)
    return style


def _read_fill_style_array(br: BitReader, tag_type: int) -> List[dict]:
    count = br.read_ui8()
    if tag_type > 2 and count == 255:
        count = br.read_ui16()
    return [_read_fill_style(br, tag_type) for _ in range(count)]


def _read_line_style(br: BitReader, tag_type: int) -> dict:
    """Read LINESTYLE / LINESTYLE2."""
    style: dict = {'fillStyleType': 0}
    if tag_type == 83:  # DefineShape4 → LINESTYLE2
        style['Width'] = br.read_ui16() / 20.0
        style['StartCapStyle'] = br.read_ub(2)
        style['JoinStyle'] = br.read_ub(2)
        style['HasFillFlag'] = br.read_ub(1)
        style['NoHScaleFlag'] = br.read_ub(1)
        style['NoVScaleFlag'] = br.read_ub(1)
        style['PixelHintingFlag'] = br.read_ub(1)
        br.read_ub(5)  # Reserved
        style['NoClose'] = br.read_ub(1)
        style['EndCapStyle'] = br.read_ub(2)
        if style['JoinStyle'] == 2:
            style['MiterLimitFactor'] = br.read_ui16()
        if style['HasFillFlag']:
            style['FillType'] = _read_fill_style(br, tag_type)
        else:
            style['Color'] = _read_rgba(br)
    elif tag_type == 32:  # DefineShape3 → RGBA
        style['Width'] = br.read_ui16() / 20.0
        style['Color'] = _read_rgba(br)
        style['JoinStyle'] = 0
        style['StartCapStyle'] = 0
        style['EndCapStyle'] = 0
    else:  # DefineShape1/2 → RGB
        style['Width'] = br.read_ui16() / 20.0
        style['Color'] = _read_rgb(br)
        style['JoinStyle'] = 0
        style['StartCapStyle'] = 0
        style['EndCapStyle'] = 0
    return style


def _read_line_style_array(br: BitReader, tag_type: int) -> List[dict]:
    count = br.read_ui8()
    if tag_type > 2 and count == 255:
        count = br.read_ui16()
    return [_read_line_style(br, tag_type) for _ in range(count)]


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def parse_define_shape_to_recodes(
    tag_type: int,
    body_after_char_id: bytes,
    swf_bitmap_id_to_n2d_id: Optional[Dict[int, int]] = None,
) -> Tuple[List, dict, bool]:
    """
    Parse a DefineShape tag body (after the 2-byte charId) and produce
    Next2D recodes array.

    Args:
        tag_type: SWF tag type (2, 22, 32, or 83)
        body_after_char_id: raw bytes AFTER the 2-byte character ID
        swf_bitmap_id_to_n2d_id: mapping SWF bitmap charId → N2D library index

    Returns:
        (recodes, bounds, has_bitmap_fill)
    """
    log.debug("parse_define_shape_to_recodes: tag_type=%d body_len=%d", tag_type, len(body_after_char_id))
    if swf_bitmap_id_to_n2d_id is None:
        swf_bitmap_id_to_n2d_id = {}

    br = BitReader(body_after_char_id, 0)

    # ── Skip shape bounds RECT ──
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)

    # DefineShape4: extra edge-bounds RECT + flags
    if tag_type == 83:
        br.align()
        nbits2 = br.read_ub(5)
        for _ in range(4):
            br.read_sb(nbits2)
        br.align()
        br.read_ub(8)  # 5 reserved + 3 flag bits

    # ── Read initial style arrays ──
    fill_styles = _read_fill_style_array(br, tag_type)
    line_styles = _read_line_style_array(br, tag_type)

    nb = br.read_ui8()
    fill_bits = nb >> 4
    line_bits = nb & 0x0F

    # ── Walk shape records ──
    # Port of Next2D's $vtc.convert(): accumulate edges into per-style
    # buckets, then merge fill0/fill1 and chain into recodes.

    cur_x = cur_y = 0          # current position (twips)
    prev_x = prev_y = 0        # position at last style change (twips)
    edge_prev_x = edge_prev_y = 0  # position before current edge (twips)

    cur_fill0 = 0               # 1-based fill style index, 0 = none
    cur_fill1 = 0
    cur_line = 0

    # fill buckets: {style_idx: {edge_group: {obj, startX, startY, endX, endY, cache}}}
    fill0_buckets: Dict[int, Dict[int, dict]] = {}
    fill1_buckets: Dict[int, Dict[int, dict]] = {}
    # line buckets:  {style_idx: {obj, cache: [[cmd_type, coords...], ...]}}
    line_buckets: Dict[int, dict] = {}

    stacks: List[dict] = []
    edge_group = 0  # incremented on each style change record

    while br.remaining > 0:
        type_flag = br.read_ub(1)

        if type_flag == 1:
            # ── Edge record ──
            straight = br.read_ub(1)
            nbits_e = br.read_ub(4) + 2

            if straight:
                gen = br.read_ub(1)
                if gen:
                    dx = br.read_sb(nbits_e)
                    dy = br.read_sb(nbits_e)
                else:
                    vert = br.read_ub(1)
                    dx = 0 if vert else br.read_sb(nbits_e)
                    dy = br.read_sb(nbits_e) if vert else 0
                ax = cur_x + dx
                ay = cur_y + dy
                cur_x, cur_y = ax, ay
                edge = {
                    'isCurved': False,
                    'ControlX': 0.0, 'ControlY': 0.0,
                    'AnchorX': ax / 20.0, 'AnchorY': ay / 20.0,
                }
            else:
                cdx = br.read_sb(nbits_e)
                cdy = br.read_sb(nbits_e)
                adx = br.read_sb(nbits_e)
                ady = br.read_sb(nbits_e)
                cx = cur_x + cdx
                cy = cur_y + cdy
                ax = cx + adx
                ay = cy + ady
                cur_x, cur_y = ax, ay
                edge = {
                    'isCurved': True,
                    'ControlX': cx / 20.0, 'ControlY': cy / 20.0,
                    'AnchorX': ax / 20.0, 'AnchorY': ay / 20.0,
                }

            # Distribute edge to active fill0 bucket
            if cur_fill0:
                _add_fill_edge(fill0_buckets, cur_fill0 - 1, edge_group,
                               fill_styles, prev_x / 20.0, prev_y / 20.0, edge)
            # … and fill1
            if cur_fill1:
                _add_fill_edge(fill1_buckets, cur_fill1 - 1, edge_group,
                               fill_styles, prev_x / 20.0, prev_y / 20.0, edge)
            # … and line
            if cur_line:
                _add_line_edge(line_buckets, cur_line - 1, line_styles,
                               edge_prev_x / 20.0, edge_prev_y / 20.0, edge)

            edge_prev_x, edge_prev_y = cur_x, cur_y

        else:
            # ── Non-edge record ──
            flags = br.read_ub(5)
            if flags == 0:
                # End of shape records
                _flush(stacks, fill0_buckets, fill1_buckets, line_buckets)
                br.align()
                break

            edge_group += 1

            has_new    = (flags >> 4) & 1
            has_line   = (flags >> 3) & 1
            has_fill1  = (flags >> 2) & 1
            has_fill0  = (flags >> 1) & 1
            has_move   = flags & 1

            if has_new:
                _flush(stacks, fill0_buckets, fill1_buckets, line_buckets)
                cur_x = cur_y = 0
                fill0_buckets = {}
                fill1_buckets = {}
                line_buckets = {}

            if has_move:
                mb = br.read_ub(5)
                cur_x = br.read_sb(mb)
                cur_y = br.read_sb(mb)

            prev_x, prev_y = cur_x, cur_y
            edge_prev_x, edge_prev_y = cur_x, cur_y

            if has_fill0:
                cur_fill0 = br.read_ub(fill_bits)
            if has_fill1:
                cur_fill1 = br.read_ub(fill_bits)
            if has_line:
                cur_line = br.read_ub(line_bits)

            if has_new:
                fill_styles = _read_fill_style_array(br, tag_type)
                line_styles = _read_line_style_array(br, tag_type)
                nb = br.read_ui8()
                fill_bits = nb >> 4
                line_bits = nb & 0x0F

    # Convert stacks → flat recodes
    recodes, has_bitmap = _stacks_to_recodes(stacks, swf_bitmap_id_to_n2d_id)
    bounds = _compute_bounds(recodes)
    return recodes, bounds, has_bitmap


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS — bucket management
# ═══════════════════════════════════════════════════════════════════════════

def _add_fill_edge(buckets, style_idx, edge_group, styles, start_x, start_y, edge):
    """Append an edge record to the correct fill bucket."""
    if style_idx not in buckets:
        buckets[style_idx] = {}
    grp = buckets[style_idx]
    if edge_group not in grp:
        grp[edge_group] = {
            'obj': styles[style_idx] if style_idx < len(styles) else None,
            'startX': start_x, 'startY': start_y,
            'endX': 0.0, 'endY': 0.0,
            'cache': [],
        }
    bucket = grp[edge_group]
    bucket['cache'].append(copy.deepcopy(edge))
    bucket['endX'] = edge['AnchorX']
    bucket['endY'] = edge['AnchorY']


def _add_line_edge(buckets, style_idx, styles, from_x, from_y, edge):
    """Append an edge to a line bucket."""
    if style_idx not in buckets:
        buckets[style_idx] = {
            'obj': styles[style_idx] if style_idx < len(styles) else None,
            'cache': [],
        }
    b = buckets[style_idx]
    # moveTo (position before edge – optimised away later if redundant)
    b['cache'].append([0, from_x, from_y])
    if edge['isCurved']:
        b['cache'].append([1, edge['ControlX'], edge['ControlY'],
                              edge['AnchorX'], edge['AnchorY']])
    else:
        b['cache'].append([2, edge['AnchorX'], edge['AnchorY']])


def _flush(stacks, f0, f1, line):
    """Merge fills, append fills + lines to stacks."""
    merged = _fill_merge(f0, f1)
    _append_buckets(stacks, merged)
    _append_buckets(stacks, line)


def _append_buckets(stacks, buckets):
    for k in sorted(buckets.keys()):
        entry = buckets[k]
        stacks.append({'object': entry.get('obj'), 'recode': entry.get('cache', [])})


# ═══════════════════════════════════════════════════════════════════════════
#  FILL MERGE — port of $vtc.fillMerge / fillReverse / coordinateAdjustment
# ═══════════════════════════════════════════════════════════════════════════

def _fill_merge(f0, f1):
    """Reverse fill0 edges, merge into fill1, then chain segments.

    Port of JS fillMerge: fill0 entries are appended AFTER fill1 entries
    (JS uses fill1[fill1.length] = ..., i.e. next sequential index).
    """
    _fill_reverse(f0)
    for key, egs in f0.items():
        if key in f1:
            # Append fill0's segments after fill1's, using new unique keys
            next_key = max(f1[key].keys()) + 1 if f1[key] else 0
            for eg_val in egs.values():
                f1[key][next_key] = eg_val
                next_key += 1
        else:
            f1[key] = egs
    return _coordinate_adjustment(f1)


def _fill_reverse(buckets):
    """Reverse direction of every segment in the fill0 buckets (in-place)."""
    for style_idx in buckets:
        for eg_key in buckets[style_idx]:
            seg = buckets[style_idx][eg_key]
            cache = seg['cache']
            if cache:
                sx, sy = seg['startX'], seg['startY']
                for edge in cache:
                    old_ax, old_ay = edge['AnchorX'], edge['AnchorY']
                    edge['AnchorX'] = sx
                    edge['AnchorY'] = sy
                    sx, sy = old_ax, old_ay
                cache.reverse()
            seg['startX'], seg['endX'] = seg['endX'], seg['startX']
            seg['startY'], seg['endY'] = seg['endY'], seg['startY']


def _coordinate_adjustment(buckets):
    """Chain edge-group segments into continuous paths per fill style.

    Port of JS coordinateAdjustment() — exact float matching, reverse search.
    Returns {style_idx: {obj, cache: [[cmd_type, coords...], ...]}}.
    """
    result = {}
    for style_idx in sorted(buckets.keys()):
        egs = buckets[style_idx]
        segments = [egs[k] for k in sorted(egs.keys())]

        # Chain segments: port of JS coordinateAdjustment inner loop
        adjustment = []
        if len(segments) > 1:
            array = list(segments)
            while array:
                fill = array.pop(0)
                # Already closed? → emit directly
                if fill['startX'] == fill['endX'] and fill['startY'] == fill['endY']:
                    adjustment.append(fill)
                    continue

                # Search backwards for a match (JS: while (length) { --length; })
                is_match = False
                j = len(array) - 1
                while j >= 0:
                    comp = array[j]
                    if comp['startX'] == fill['endX'] and comp['startY'] == fill['endY']:
                        # Merge comp into fill
                        fill['endX'] = comp['endX']
                        fill['endY'] = comp['endY']
                        fill['cache'].extend(comp['cache'])
                        array.pop(j)
                        array.insert(0, fill)  # re-queue to try chaining again
                        is_match = True
                        break
                    j -= 1

                if not is_match:
                    # No match — re-queue at front
                    array.insert(0, fill)
                    # Avoid infinite loop: if we cycled back to the same element,
                    # pop it to adjustment
                    adjustment.append(array.pop(0))
        else:
            adjustment = segments

        # Convert to flat command entries
        cmds = []
        obj = None
        for seg in adjustment:
            if seg.get('obj') is not None:
                obj = seg['obj']
            cmds.append([0, seg['startX'], seg['startY']])  # moveTo
            for edge in seg['cache']:
                if edge['isCurved']:
                    cmds.append([1, edge['ControlX'], edge['ControlY'],
                                    edge['AnchorX'], edge['AnchorY']])
                else:
                    cmds.append([2, edge['AnchorX'], edge['AnchorY']])

        result[style_idx] = {'obj': obj, 'cache': cmds}
    return result


# ═══════════════════════════════════════════════════════════════════════════
#  STACKS → FLAT RECODES   (port of $vtc.toGraphicPath)
# ═══════════════════════════════════════════════════════════════════════════

def _stacks_to_recodes(stacks, bitmap_map):
    has_bitmap = False
    recodes = []

    for entry in stacks:
        obj = entry.get('object')
        cmds = entry.get('recode', [])
        if obj is None or not cmds:
            continue

        recodes.append(BEGIN_PATH)

        # Emit path drawing commands (with moveTo optimisation for lines)
        is_line = 'Width' in obj
        pen_x = pen_y = None
        for cmd in cmds:
            if cmd[0] == 0:  # moveTo
                mx, my = cmd[1], cmd[2]
                if not is_line or pen_x is None or \
                   pen_x != mx or pen_y != my:
                    recodes.extend([MOVE_TO, mx, my])
                pen_x, pen_y = mx, my
            elif cmd[0] == 1:  # curveTo
                recodes.extend([CURVE_TO, cmd[1], cmd[2], cmd[3], cmd[4]])
                pen_x, pen_y = cmd[3], cmd[4]
            elif cmd[0] == 2:  # lineTo
                recodes.extend([LINE_TO, cmd[1], cmd[2]])
                pen_x, pen_y = cmd[1], cmd[2]

        # Emit style command
        if is_line:
            hb = _emit_stroke(recodes, obj, bitmap_map)
        else:
            hb = _emit_fill(recodes, obj, bitmap_map)
        if hb:
            has_bitmap = True

    # Trailing inBitmap flag expected by the tool
    recodes.append(has_bitmap)
    return recodes, has_bitmap


# ─── Fill emission ───

def _emit_fill(recodes, obj, bmap):
    """Append fill-style command to recodes. Returns True if bitmap fill."""
    fst = obj.get('fillStyleType', 0)

    if fst == 0:
        c = obj.get('Color', {'R': 0, 'G': 0, 'B': 0, 'A': 1.0})
        recodes.extend([FILL_STYLE, c['R'], c['G'], c['B'], _a8(c['A'])])
        recodes.append(END_FILL)
        return False

    if fst in (16, 18, 19):
        g = obj.get('gradient', {})
        stops = _gradient_stops(g)
        gtype = 'linear' if fst == 16 else 'radial'
        mtx = obj.get('gradientMatrix', [1, 0, 0, 1, 0, 0])
        spread = _spread(g)
        interp = 'linearRGB' if g.get('InterpolationMode', 0) else 'rgb'
        focal = g.get('FocalPoint', 0)
        recodes.extend([GRADIENT_FILL, gtype, stops, mtx, spread, interp, focal])
        return False

    if fst in (64, 65, 66, 67):
        bmp_id = bmap.get(obj.get('bitmapId', 0), 0)
        mtx = obj.get('bitmapMatrix', [1, 0, 0, 1, 0, 0])
        # Scale the non-translate part by 1/20 (twips → pixels)
        smtx = [mtx[0] * 0.05, mtx[1] * 0.05,
                mtx[2] * 0.05, mtx[3] * 0.05,
                mtx[4], mtx[5]]
        repeat = 'repeat' if fst in (64, 66) else 'no-repeat'
        smooth = fst in (64, 65)
        recodes.extend([BITMAP_FILL, bmp_id, smtx, repeat, smooth])
        return True

    # Unknown → solid black fallback
    recodes.extend([FILL_STYLE, 0, 0, 0, 255])
    recodes.append(END_FILL)
    return False


# ─── Stroke emission ───

def _emit_stroke(recodes, obj, bmap):
    """Append stroke-style command. Returns True if bitmap stroke."""
    width = obj.get('Width', 1.0)
    cap = {0: 'round', 1: 'none', 2: 'square'}.get(obj.get('StartCapStyle', 0), 'round')
    join = {0: 'round', 1: 'bevel', 2: 'miter'}.get(obj.get('JoinStyle', 0), 'round')
    miter = obj.get('MiterLimitFactor', 3.0)

    # Determine the actual fill inside the stroke
    if obj.get('HasFillFlag'):
        inner = obj.get('FillType', obj)
    else:
        inner = obj

    fst = inner.get('fillStyleType', 0)

    if fst == 0:
        c = inner.get('Color', obj.get('Color', {'R': 0, 'G': 0, 'B': 0, 'A': 1.0}))
        recodes.extend([STROKE_STYLE, width, cap, join, miter,
                        c['R'], c['G'], c['B'], _a8(c['A'])])
        recodes.append(END_STROKE)
        return False

    if fst in (16, 18, 19):
        g = inner.get('gradient', {})
        stops = _gradient_stops(g)
        gtype = 'linear' if fst == 16 else 'radial'
        mtx = inner.get('gradientMatrix', [1, 0, 0, 1, 0, 0])
        spread = _spread(g)
        interp = 'linearRGB' if g.get('InterpolationMode', 0) else 'rgb'
        focal = g.get('FocalPoint', 0)
        recodes.extend([GRADIENT_STROKE, width, cap, join, miter,
                        gtype, stops, mtx, spread, interp, focal])
        return False

    if fst in (64, 65, 66, 67):
        bmp_id = bmap.get(inner.get('bitmapId', 0), 0)
        mtx = inner.get('bitmapMatrix', [1, 0, 0, 1, 0, 0])
        smtx = [mtx[0] * 0.05, mtx[1] * 0.05,
                mtx[2] * 0.05, mtx[3] * 0.05,
                mtx[4], mtx[5]]
        repeat = 'repeat' if fst in (64, 66) else 'no-repeat'
        smooth = fst in (64, 65)
        recodes.extend([BITMAP_STROKE, width, cap, join, miter,
                        bmp_id, smtx, repeat, smooth])
        return True

    # Fallback
    recodes.extend([STROKE_STYLE, width, cap, join, miter, 0, 0, 0, 255])
    recodes.append(END_STROKE)
    return False


# ─── Shared helpers ───

def _a8(alpha_float):
    """Convert 0.0-1.0 alpha to 0-255."""
    return max(0, min(255, int(round(alpha_float * 255))))


def _gradient_stops(grad_dict):
    recs = grad_dict.get('GradientRecords', [])
    return [{
        'ratio': r['Ratio'],
        'R': r['Color']['R'], 'G': r['Color']['G'],
        'B': r['Color']['B'], 'A': _a8(r['Color']['A']),
    } for r in recs]


def _spread(g):
    return {0: 'pad', 1: 'reflect', 2: 'repeat'}.get(g.get('SpreadMode', 0), 'pad')


# ═══════════════════════════════════════════════════════════════════════════
#  MORPH SHAPE PARSER (DefineMorphShape / DefineMorphShape2)
# ═══════════════════════════════════════════════════════════════════════════

def _skip_rect(br: BitReader):
    """Skip a RECT structure (bit-packed)."""
    br.align()
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)


def _read_morph_fill_style_array(br: BitReader, tag_type: int) -> List[dict]:
    """Read MORPHFILLSTYLEARRAY, returning only start-state fills in
    regular DefineShape format (compatible with _emit_fill)."""
    start_fills, _ = _read_morph_fill_style_array_both(br, tag_type)
    return start_fills


def _read_morph_fill_style_array_both(
    br: BitReader, tag_type: int
) -> Tuple[List[dict], List[dict]]:
    """Read MORPHFILLSTYLEARRAY, returning (start_fills, end_fills)."""
    count = br.read_ui8()
    if count == 0xFF:
        count = br.read_ui16()
    start_fills = []
    end_fills = []
    for _ in range(count):
        ft = br.read_ui8()
        s_style: dict = {'fillStyleType': ft}
        e_style: dict = {'fillStyleType': ft}
        if ft == 0:
            # Solid: start RGBA + end RGBA
            s_style['Color'] = _read_rgba(br)
            e_style['Color'] = _read_rgba(br)
        elif ft in (16, 18):
            # Linear/radial gradient: start matrix, end matrix, paired stops
            s_style['gradientMatrix'] = _read_matrix(br)
            e_style['gradientMatrix'] = _read_matrix(br)
            br.align()
            spread = br.read_ub(2)
            interp = br.read_ub(2)
            n_recs = br.read_ub(4)
            s_records = []
            e_records = []
            for _ in range(n_recs):
                s_ratio = br.read_ui8()
                s_color = _read_rgba(br)
                e_ratio = br.read_ui8()
                e_color = _read_rgba(br)
                s_records.append({'Ratio': s_ratio, 'Color': s_color})
                e_records.append({'Ratio': e_ratio, 'Color': e_color})
            s_style['gradient'] = {
                'SpreadMode': spread, 'InterpolationMode': interp,
                'GradientRecords': s_records, 'FocalPoint': 0.0,
            }
            e_style['gradient'] = {
                'SpreadMode': spread, 'InterpolationMode': interp,
                'GradientRecords': e_records, 'FocalPoint': 0.0,
            }
        elif ft == 19:
            # Focal radial gradient (tag 84 only)
            s_style['gradientMatrix'] = _read_matrix(br)
            e_style['gradientMatrix'] = _read_matrix(br)
            br.align()
            spread = br.read_ub(2)
            interp = br.read_ub(2)
            n_recs = br.read_ub(4)
            s_records = []
            e_records = []
            for _ in range(n_recs):
                s_ratio = br.read_ui8()
                s_color = _read_rgba(br)
                e_ratio = br.read_ui8()
                e_color = _read_rgba(br)
                s_records.append({'Ratio': s_ratio, 'Color': s_color})
                e_records.append({'Ratio': e_ratio, 'Color': e_color})
            focal = br.read_si16() / 256.0
            s_style['gradient'] = {
                'SpreadMode': spread, 'InterpolationMode': interp,
                'GradientRecords': s_records, 'FocalPoint': focal,
            }
            e_style['gradient'] = {
                'SpreadMode': spread, 'InterpolationMode': interp,
                'GradientRecords': e_records, 'FocalPoint': focal,
            }
        elif ft in (64, 65, 66, 67):
            # Bitmap fill: bitmapId + start matrix + end matrix
            bid = br.read_ui16()
            s_style['bitmapId'] = bid
            e_style['bitmapId'] = bid
            s_style['bitmapMatrix'] = _read_matrix(br)
            e_style['bitmapMatrix'] = _read_matrix(br)
        start_fills.append(s_style)
        end_fills.append(e_style)
    return start_fills, end_fills


def _read_morph_line_style_array(br: BitReader, tag_type: int) -> List[dict]:
    """Read MORPHLINESTYLEARRAY (tag 46) or MORPHLINESTYLE2ARRAY (tag 84),
    returning only start-state line styles in regular DefineShape format."""
    start_lines, _ = _read_morph_line_style_array_both(br, tag_type)
    return start_lines


def _read_morph_line_style_array_both(
    br: BitReader, tag_type: int
) -> Tuple[List[dict], List[dict]]:
    """Read MORPHLINESTYLEARRAY, returning (start_lines, end_lines)."""
    count = br.read_ui8()
    if count == 0xFF:
        count = br.read_ui16()
    start_lines = []
    end_lines = []
    for _ in range(count):
        if tag_type == 84:
            # MORPHLINESTYLE2
            s_style: dict = {'fillStyleType': 0}
            e_style: dict = {'fillStyleType': 0}
            start_width = br.read_ui16() / 20.0
            end_width = br.read_ui16() / 20.0
            s_style['Width'] = start_width
            e_style['Width'] = end_width
            cap_start = br.read_ub(2)
            join = br.read_ub(2)
            has_fill = br.read_ub(1)
            no_h = br.read_ub(1)
            no_v = br.read_ub(1)
            pixel_hint = br.read_ub(1)
            br.read_ub(5)  # reserved
            no_close = br.read_ub(1)
            cap_end = br.read_ub(2)
            for st in (s_style, e_style):
                st['StartCapStyle'] = cap_start
                st['JoinStyle'] = join
                st['HasFillFlag'] = has_fill
                st['NoHScaleFlag'] = no_h
                st['NoVScaleFlag'] = no_v
                st['PixelHintingFlag'] = pixel_hint
                st['NoClose'] = no_close
                st['EndCapStyle'] = cap_end
            if join == 2:
                miter = br.read_ui16()
                s_style['MiterLimitFactor'] = miter
                e_style['MiterLimitFactor'] = miter
            if has_fill:
                s_fill, e_fill = _read_morph_single_fill_both(br)
                s_style['FillType'] = s_fill
                e_style['FillType'] = e_fill
            else:
                s_style['Color'] = _read_rgba(br)
                e_style['Color'] = _read_rgba(br)
            start_lines.append(s_style)
            end_lines.append(e_style)
        else:
            # MORPHLINESTYLE (tag 46): simple width + RGBA pairs
            s_style = {'fillStyleType': 0}
            e_style = {'fillStyleType': 0}
            start_width = br.read_ui16() / 20.0
            end_width = br.read_ui16() / 20.0
            s_style['Width'] = start_width
            e_style['Width'] = end_width
            s_style['Color'] = _read_rgba(br)
            e_style['Color'] = _read_rgba(br)
            for st in (s_style, e_style):
                st['JoinStyle'] = 0
                st['StartCapStyle'] = 0
                st['EndCapStyle'] = 0
            start_lines.append(s_style)
            end_lines.append(e_style)
    return start_lines, end_lines


def _read_morph_single_fill_both(br: BitReader) -> Tuple[dict, dict]:
    """Read a morph fill style pair for LINESTYLE2 HasFill, return (start, end)."""
    ft = br.read_ui8()
    s_style: dict = {'fillStyleType': ft}
    e_style: dict = {'fillStyleType': ft}
    if ft == 0:
        s_style['Color'] = _read_rgba(br)
        e_style['Color'] = _read_rgba(br)
    elif ft in (16, 18, 19):
        s_style['gradientMatrix'] = _read_matrix(br)
        e_style['gradientMatrix'] = _read_matrix(br)
        br.align()
        spread = br.read_ub(2)
        interp = br.read_ub(2)
        n_recs = br.read_ub(4)
        s_records = []
        e_records = []
        for _ in range(n_recs):
            s_ratio = br.read_ui8()
            s_color = _read_rgba(br)
            e_ratio = br.read_ui8()
            e_color = _read_rgba(br)
            s_records.append({'Ratio': s_ratio, 'Color': s_color})
            e_records.append({'Ratio': e_ratio, 'Color': e_color})
        focal = br.read_si16() / 256.0 if ft == 19 else 0.0
        s_style['gradient'] = {
            'SpreadMode': spread, 'InterpolationMode': interp,
            'GradientRecords': s_records, 'FocalPoint': focal,
        }
        e_style['gradient'] = {
            'SpreadMode': spread, 'InterpolationMode': interp,
            'GradientRecords': e_records, 'FocalPoint': focal,
        }
    elif ft in (64, 65, 66, 67):
        bid = br.read_ui16()
        s_style['bitmapId'] = bid
        e_style['bitmapId'] = bid
        s_style['bitmapMatrix'] = _read_matrix(br)
        e_style['bitmapMatrix'] = _read_matrix(br)
    return s_style, e_style


def _walk_edge_records(
    br: BitReader,
    end_pos: int,
    fill_styles: List[dict],
    line_styles: List[dict],
    equiv_tag: int,
    swf_bitmap_id_to_n2d_id: Dict[int, int],
    morph_start_assignments: Optional[List[tuple]] = None,
) -> Tuple[List, dict, bool]:
    """Walk shape edge records and return (recodes, bounds, has_bitmap).

    This is shared between regular shape parsing, morph START edges,
    and morph END edges.

    morph_start_assignments: if provided (for morph end-state), a list of
        (fill0, fill1, line) tuples indexed by edge_group. When fill_bits=0,
        these override the fill/line indices read from the stream.
    """
    nb = br.read_ui8()
    fill_bits = nb >> 4
    line_bits = nb & 0x0F
    # Track fill/line assignments per edge_group for morph start-state
    _is_morph_end = morph_start_assignments is not None
    _fill_assignments: List[tuple] = []  # recorded during start-state

    cur_x = cur_y = 0
    prev_x = prev_y = 0
    edge_prev_x = edge_prev_y = 0
    cur_fill0 = cur_fill1 = cur_line = 0

    fill0_buckets: Dict[int, Dict[int, dict]] = {}
    fill1_buckets: Dict[int, Dict[int, dict]] = {}
    line_buckets: Dict[int, dict] = {}
    stacks: List[dict] = []
    edge_group = 0

    while br.byte_pos < end_pos and br.remaining > 0:
        type_flag = br.read_ub(1)
        if type_flag == 1:
            # Edge record
            straight = br.read_ub(1)
            nbits_e = br.read_ub(4) + 2
            if straight:
                gen = br.read_ub(1)
                if gen:
                    dx = br.read_sb(nbits_e)
                    dy = br.read_sb(nbits_e)
                else:
                    vert = br.read_ub(1)
                    dx = 0 if vert else br.read_sb(nbits_e)
                    dy = br.read_sb(nbits_e) if vert else 0
                ax = cur_x + dx
                ay = cur_y + dy
                cur_x, cur_y = ax, ay
                edge = {
                    'isCurved': False,
                    'ControlX': 0.0, 'ControlY': 0.0,
                    'AnchorX': ax / 20.0, 'AnchorY': ay / 20.0,
                }
            else:
                cdx = br.read_sb(nbits_e)
                cdy = br.read_sb(nbits_e)
                adx = br.read_sb(nbits_e)
                ady = br.read_sb(nbits_e)
                cx = cur_x + cdx
                cy = cur_y + cdy
                ax = cx + adx
                ay = cy + ady
                cur_x, cur_y = ax, ay
                edge = {
                    'isCurved': True,
                    'ControlX': cx / 20.0, 'ControlY': cy / 20.0,
                    'AnchorX': ax / 20.0, 'AnchorY': ay / 20.0,
                }

            if cur_fill0:
                _add_fill_edge(fill0_buckets, cur_fill0 - 1, edge_group,
                               fill_styles, prev_x / 20.0, prev_y / 20.0, edge)
            if cur_fill1:
                _add_fill_edge(fill1_buckets, cur_fill1 - 1, edge_group,
                               fill_styles, prev_x / 20.0, prev_y / 20.0, edge)
            if cur_line:
                _add_line_edge(line_buckets, cur_line - 1, line_styles,
                               edge_prev_x / 20.0, edge_prev_y / 20.0, edge)
            edge_prev_x, edge_prev_y = cur_x, cur_y
        else:
            # Non-edge record
            flags = br.read_ub(5)
            if flags == 0:
                _flush(stacks, fill0_buckets, fill1_buckets, line_buckets)
                br.align()
                break

            edge_group += 1
            has_new   = (flags >> 4) & 1
            has_line  = (flags >> 3) & 1
            has_fill1 = (flags >> 2) & 1
            has_fill0 = (flags >> 1) & 1
            has_move  = flags & 1

            if has_new:
                _flush(stacks, fill0_buckets, fill1_buckets, line_buckets)
                cur_x = cur_y = 0
                fill0_buckets = {}
                fill1_buckets = {}
                line_buckets = {}

            if has_move:
                mb = br.read_ub(5)
                cur_x = br.read_sb(mb)
                cur_y = br.read_sb(mb)

            prev_x, prev_y = cur_x, cur_y
            edge_prev_x, edge_prev_y = cur_x, cur_y

            if has_fill0:
                cur_fill0 = br.read_ub(fill_bits)
            if has_fill1:
                cur_fill1 = br.read_ub(fill_bits)
            if has_line:
                cur_line = br.read_ub(line_bits)

            # Morph end-state: inherit fill/line from start-state
            if _is_morph_end and edge_group <= len(morph_start_assignments):
                sf0, sf1, sl = morph_start_assignments[edge_group - 1]
                cur_fill0 = sf0
                cur_fill1 = sf1
                cur_line = sl

            # Record fill/line assignments for morph start-state
            if not _is_morph_end:
                _fill_assignments.append((cur_fill0, cur_fill1, cur_line))

            if has_new:
                # Mid-stream new styles use regular (non-morph) format
                fill_styles = _read_fill_style_array(br, equiv_tag)
                line_styles = _read_line_style_array(br, equiv_tag)
                nb = br.read_ui8()
                fill_bits = nb >> 4
                line_bits = nb & 0x0F

    recodes, has_bitmap = _stacks_to_recodes(stacks, swf_bitmap_id_to_n2d_id)
    bounds = _compute_bounds(recodes)
    return recodes, bounds, has_bitmap, _fill_assignments


def parse_define_morph_shape_to_recodes(
    tag_type: int,
    body_after_char_id: bytes,
    swf_bitmap_id_to_n2d_id: Optional[Dict[int, int]] = None,
) -> Tuple[List, dict, List, dict, bool]:
    """
    Parse a DefineMorphShape/2 tag body (after the 2-byte charId) and produce
    Next2D recodes for both the START and END states.

    Args:
        tag_type: SWF tag type (46 or 84)
        body_after_char_id: raw bytes AFTER the 2-byte character ID
        swf_bitmap_id_to_n2d_id: mapping SWF bitmap charId → N2D library index

    Returns:
        (start_recodes, start_bounds, end_recodes, end_bounds, has_bitmap_fill)
    """
    log.debug("parse_define_morph_shape_to_recodes: tag_type=%d body_len=%d", tag_type, len(body_after_char_id))
    if swf_bitmap_id_to_n2d_id is None:
        swf_bitmap_id_to_n2d_id = {}

    br = BitReader(body_after_char_id, 0)

    # ── StartBounds RECT (skip) ──
    _skip_rect(br)
    # ── EndBounds RECT (skip) ──
    _skip_rect(br)

    # DefineMorphShape2: extra edge bounds + flags byte
    if tag_type == 84:
        _skip_rect(br)  # StartEdgeBounds
        _skip_rect(br)  # EndEdgeBounds
        br.align()
        br.read_ui8()   # flags (UsesNonScalingStrokes, UsesScalingStrokes)

    # ── Offset (UI32) ──
    br.align()
    offset = struct.unpack_from('<I', br.data, br.byte_pos)[0]
    br.byte_pos += 4
    after_offset_pos = br.byte_pos

    # ── MorphFillStyleArray → both start and end fills ──
    start_fills, end_fills = _read_morph_fill_style_array_both(br, tag_type)
    # ── MorphLineStyleArray → both start and end lines ──
    start_lines, end_lines = _read_morph_line_style_array_both(br, tag_type)

    # Map morph tag → equivalent DefineShape tag for mid-stream new styles
    equiv_tag = 83 if tag_type == 84 else 32

    # ── StartEdges ──
    start_end_pos = after_offset_pos + offset
    start_recodes, start_bounds, has_bitmap, start_assignments = _walk_edge_records(
        br, start_end_pos, start_fills, start_lines,
        equiv_tag, swf_bitmap_id_to_n2d_id,
    )

    # ── EndEdges ──
    # Position reader at start of end edges section
    br.byte_pos = start_end_pos
    br.bit_pos = 0
    end_end_pos = len(br.data)
    try:
        end_recodes, end_bounds, end_has_bitmap, _ = _walk_edge_records(
            br, end_end_pos, end_fills, end_lines,
            equiv_tag, swf_bitmap_id_to_n2d_id,
            morph_start_assignments=start_assignments,
        )
    except Exception as e:
        log.debug("MorphShape end-edges parse error: %s — using empty end recodes", e)
        end_recodes = []
        end_bounds = start_bounds.copy() if start_bounds else {'xMin': 0, 'xMax': 20, 'yMin': 0, 'yMax': 20}
        end_has_bitmap = False

    return start_recodes, start_bounds, end_recodes, end_bounds, (has_bitmap or end_has_bitmap)


# ═══════════════════════════════════════════════════════════════════════════
#  BOUNDS COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════

def _compute_bounds(recodes):
    """Compute bounding box from recodes path coordinates."""
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    def _update(x, y):
        nonlocal min_x, min_y, max_x, max_y
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            min_x = min(min_x, x); max_x = max(max_x, x)
            min_y = min(min_y, y); max_y = max(max_y, y)

    i = 0
    n = len(recodes)
    while i < n:
        c = recodes[i]
        if c in (MOVE_TO, LINE_TO):
            if i + 2 < n:
                _update(recodes[i + 1], recodes[i + 2])
            i += 3
        elif c == CURVE_TO:
            if i + 4 < n:
                _update(recodes[i + 1], recodes[i + 2])
                _update(recodes[i + 3], recodes[i + 4])
            i += 5
        elif c == FILL_STYLE:
            i += 6   # cmd + rgba + END_FILL
        elif c == STROKE_STYLE:
            i += 11  # cmd + width,cap,join,miter,rgba + END_STROKE
        elif c == GRADIENT_FILL:
            i += 7
        elif c == GRADIENT_STROKE:
            i += 11
        elif c in (BITMAP_FILL, BITMAP_STROKE):
            i += 5
        elif c in (BEGIN_PATH, END_FILL, END_STROKE, CLOSE_PATH):
            i += 1
        elif isinstance(c, bool):
            i += 1
        else:
            i += 1

    if min_x == float('inf'):
        return {'xMin': 0, 'xMax': 0, 'yMin': 0, 'yMax': 0}
    return {'xMin': min_x, 'xMax': max_x, 'yMin': min_y, 'yMax': max_y}
