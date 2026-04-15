"""
Shape Converter — Translates Next2D shape buffer commands to SWF DefineShape tags.

Next2D shape `buffer` is a flat array of command codes and parameters.
This module parses them and produces SWF DefineShape3/4 binary tags.
"""

from __future__ import annotations

import io
import logging
import math
import struct
from typing import List, Optional, Tuple

log = logging.getLogger(__name__)

from swf_binary_io import BitWriter
from swf_constants import (
    ShapeCommand, CMD_MOVE_TO, CMD_CURVE_TO, CMD_LINE_TO, CMD_CUBIC, CMD_ARC,
    CMD_FILL_STYLE, CMD_STROKE_STYLE, CMD_END_FILL, CMD_END_STROKE, CMD_BEGIN_PATH,
    CMD_GRADIENT_FILL, CMD_GRADIENT_STROKE, CMD_CLOSE_PATH, CMD_BITMAP_FILL, CMD_BITMAP_STROKE,
    TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4, TAG_DEFINE_MORPH_SHAPE, TAG_DEFINE_MORPH_SHAPE2
)
from swf_writer import (
    build_tag,
    twips,
    write_rect,
    _nbits_signed,
    _nbits_signed_list,
    _nbits_unsigned,
)


# ── Intermediate representation ─────────────────────────────────────────

class SolidFill:
    __slots__ = ('r', 'g', 'b', 'a')
    def __init__(self, r: int, g: int, b: int, a: int):
        self.r, self.g, self.b, self.a = r, g, b, a


class GradientStop:
    __slots__ = ('ratio', 'r', 'g', 'b', 'a')
    def __init__(self, ratio: int, r: int, g: int, b: int, a: int):
        self.ratio, self.r, self.g, self.b, self.a = ratio, r, g, b, a


class GradientFill:
    __slots__ = ('grad_type', 'stops', 'matrix', 'spread', 'interpolation', 'focal')
    def __init__(self, grad_type: int, stops: List[GradientStop],
                 matrix: List[float], spread: int, interpolation: int,
                 focal: float):
        self.grad_type = grad_type       # 0=linear, 1=radial
        self.stops = stops
        self.matrix = matrix             # [a,b,c,d,tx,ty]
        self.spread = spread             # 0=pad,1=reflect,2=repeat  (SWF: 0=pad,1=reflect,2=repeat)
        self.interpolation = interpolation
        self.focal = focal


class BitmapFill:
    __slots__ = ('width', 'height', 'pixel_data', 'matrix', 'repeat', 'smooth', 'bitmap_char_id', 'bitmap_lib_id')
    def __init__(self, width: int, height: int, pixel_data: bytes,
                 matrix: List[float], repeat: bool, smooth: bool,
                 bitmap_char_id: int = 0, bitmap_lib_id: int = 0):
        self.width = width
        self.height = height
        self.pixel_data = pixel_data
        self.matrix = matrix
        self.repeat = repeat
        self.smooth = smooth
        self.bitmap_char_id = bitmap_char_id  # SWF character ID, set later
        self.bitmap_lib_id = bitmap_lib_id    # N2D library ID for resolution


class LineStyle:
    __slots__ = ('thickness', 'r', 'g', 'b', 'a', 'cap', 'join', 'miter_limit')
    def __init__(self, thickness: float, r: int, g: int, b: int, a: int,
                 cap: int = 1, join: int = 1, miter_limit: float = 3.0):
        self.thickness = thickness
        self.r, self.g, self.b, self.a = r, g, b, a
        self.cap = cap
        self.join = join
        self.miter_limit = miter_limit


class GradientLineStyle:
    __slots__ = ('thickness', 'cap', 'join', 'miter_limit', 'grad_fill')
    def __init__(self, thickness: float, cap: int, join: int, miter_limit: float,
                 grad_fill: GradientFill):
        self.thickness = thickness
        self.cap, self.join, self.miter_limit = cap, join, miter_limit
        self.grad_fill = grad_fill


class EdgeRecord:
    """One drawing edge."""
    pass


class MoveToEdge(EdgeRecord):
    __slots__ = ('x', 'y')
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y


class LineToEdge(EdgeRecord):
    __slots__ = ('x', 'y')
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y


class CurveToEdge(EdgeRecord):
    __slots__ = ('cx', 'cy', 'ax', 'ay')
    def __init__(self, cx: float, cy: float, ax: float, ay: float):
        self.cx, self.cy, self.ax, self.ay = cx, cy, ax, ay


class SubPath:
    """
    A sequence of edges sharing the same fill/stroke style.
    """
    __slots__ = ('fill_style_idx', 'line_style_idx', 'edges', 'start_x', 'start_y',
                 '_morph_use_fill0')
    def __init__(self):
        self.fill_style_idx: int = 0    # 1-based index (0 = none)
        self.line_style_idx: int = 0    # 1-based index (0 = none)
        self.edges: List[EdgeRecord] = []
        self.start_x: float = 0.0
        self.start_y: float = 0.0
        self._morph_use_fill0: bool = False


# ── Rich format helpers (string → int conversion) ───────────────────────

_CAP_MAP  = {'round': 0, 'none': 1, 'square': 2}
_JOIN_MAP = {'round': 0, 'bevel': 1, 'miter': 2}
_GRAD_TYPE_MAP  = {'linear': 0, 'radial': 1}
# Internal encoding used by _write_gradient (NOT direct SWF values):
#   spread: 0=reflect, 1=repeat, 2=pad   (SWF: 0=pad, 1=reflect, 2=repeat)
#   interp: 0=linearRGB, 1=rgb           (SWF: 0=rgb, 1=linearRGB)
_SPREAD_MAP     = {'pad': 2, 'reflect': 0, 'repeat': 1}
_INTERP_MAP     = {'rgb': 1, 'linearRGB': 0}

def _to_cap(v) -> int:
    if isinstance(v, str):
        return _CAP_MAP.get(v, 0)
    return int(v)

def _to_join(v) -> int:
    if isinstance(v, str):
        return _JOIN_MAP.get(v, 0)
    return int(v)

def _to_grad_type(v) -> int:
    if isinstance(v, str):
        return _GRAD_TYPE_MAP.get(v, 0)
    return int(v)

def _to_spread(v) -> int:
    if isinstance(v, str):
        return _SPREAD_MAP.get(v, 2)  # default 'pad' = internal 2
    return int(v)

def _to_interp(v) -> int:
    if isinstance(v, str):
        return _INTERP_MAP.get(v, 1)  # default 'rgb' = internal 1
    return int(v)


def _parse_rich_stops(stops_list: list) -> List[GradientStop]:
    """Parse gradient stops from a list of dicts {ratio, R, G, B, A}."""
    result = []
    for s in stops_list:
        ratio = int(s.get('ratio', 0))
        r = int(s.get('R', 0))
        g = int(s.get('G', 0))
        b = int(s.get('B', 0))
        a = int(s.get('A', 255))
        result.append(GradientStop(ratio, r, g, b, a))
    return result


def _parse_bitmap_data(val) -> Tuple[int, int, bytes, int]:
    """Extract (width, height, pixel_data, bitmap_lib_id) from an embedded
    bitmap dict or return a placeholder for integer bitmap refs."""
    if isinstance(val, dict):
        w = int(val.get('width', 1))
        h = int(val.get('height', 1))
        buf = val.get('buffer', [])
        if isinstance(buf, str):
            pixel_data = bytes(ord(c) for c in buf)
        elif isinstance(buf, (bytes, bytearray)):
            pixel_data = bytes(buf)
        else:
            pixel_data = bytes(int(b) for b in buf)
        lib_id = int(val.get('bitmapId', 0))
        return w, h, pixel_data, lib_id
    # Integer bitmap reference — store library ID for later resolution
    if isinstance(val, (int, float)):
        return 1, 1, b'\x00\x00\x00\xff', int(val)
    return 1, 1, b'\x00\x00\x00\xff', 0


def _to_repeat(v) -> bool:
    """Convert repeat value to bool ('repeat'→True, 'no-repeat'→False)."""
    if isinstance(v, str):
        return v == 'repeat'
    return bool(v)


# ── Parse Next2D buffer ─────────────────────────────────────────────────

def parse_next2d_shape_buffer(buf: List) -> Tuple[List, List, List[SubPath]]:
    """
    Walk the Next2D command buffer and build:
      fill_styles  — list of fill style objects
      line_styles  — list of line style objects
      sub_paths    — list of SubPath with edges

    Handles BOTH the flat-numeric format (legacy) and the rich format
    produced by swf_shape_to_recodes.py / the Next2D editor tool.

    Returns (fill_styles, line_styles, sub_paths).
    """
    log.debug("parse_next2d_shape_buffer: %d buffer entries", len(buf))
    fill_styles: list = []
    line_styles: list = []
    sub_paths: List[SubPath] = []

    cur_path: Optional[SubPath] = None
    cur_x, cur_y = 0.0, 0.0
    cur_fill_idx = 0
    cur_line_idx = 0

    i = 0
    while i < len(buf):
        # The recodes buffer may end with a trailing boolean (inBitmap flag)
        # emitted by swf_shape_to_recodes.py — skip it.
        cmd_val = buf[i]
        if isinstance(cmd_val, bool):
            break
        cmd = int(cmd_val); i += 1

        if cmd == CMD_FILL_STYLE:
            r, g, b, a = int(buf[i]), int(buf[i+1]), int(buf[i+2]), int(buf[i+3])
            i += 4
            fill_styles.append(SolidFill(r, g, b, a))
            cur_fill_idx = len(fill_styles)
            if cur_path is not None:
                cur_path.fill_style_idx = cur_fill_idx

        elif cmd == CMD_GRADIENT_FILL:
            val = buf[i]
            if isinstance(val, str):
                # Rich format: [gtype_str, [{stops}], [matrix], spread_str, interp_str, focal]
                grad_type = _to_grad_type(val); i += 1
                stops = _parse_rich_stops(buf[i]); i += 1
                mat = list(buf[i]); i += 1
                spread = _to_spread(buf[i]); i += 1
                interp = _to_interp(buf[i]); i += 1
                focal = float(buf[i]); i += 1
            else:
                # Flat format: [grad_type_int, num_stops, ratio,r,g,b,a..., m0-m5, spread, interp, focal]
                grad_type = int(val); i += 1
                num_stops = int(buf[i]); i += 1
                stops = []
                for _ in range(num_stops):
                    ratio = int(buf[i]); i += 1
                    sr, sg, sb, sa = int(buf[i]), int(buf[i+1]), int(buf[i+2]), int(buf[i+3])
                    i += 4
                    stops.append(GradientStop(ratio, sr, sg, sb, sa))
                mat = [buf[i+j] for j in range(6)]; i += 6
                spread = int(buf[i]); i += 1
                interp = int(buf[i]); i += 1
                focal = float(buf[i]); i += 1
            fill_styles.append(GradientFill(grad_type, stops, mat, spread, interp, focal))
            cur_fill_idx = len(fill_styles)
            if cur_path is not None:
                cur_path.fill_style_idx = cur_fill_idx

        elif cmd == CMD_BITMAP_FILL:
            val = buf[i]
            if isinstance(val, dict) or (isinstance(val, (int, float)) and i + 1 < len(buf) and isinstance(buf[i + 1], list)):
                # Rich format: [{buffer,width,height} or bmp_id, [matrix], repeat_str, smooth_bool]
                w, h, pixel_data, bmp_lib_id = _parse_bitmap_data(val); i += 1
                mat = list(buf[i]); i += 1
                repeat = _to_repeat(buf[i]); i += 1
                smooth = bool(buf[i]); i += 1
            else:
                # Flat format: [width, height, buf_len, pixel_data..., m0-m5, repeat, smooth]
                w = int(val); i += 1
                h = int(buf[i]); i += 1
                buf_len = int(buf[i]); i += 1
                pixel_data = bytes(int(buf[i+j]) for j in range(buf_len)); i += buf_len
                mat = [buf[i+j] for j in range(6)]; i += 6
                repeat = bool(buf[i]); i += 1
                smooth = bool(buf[i]); i += 1
                bmp_lib_id = 0
            fill_styles.append(BitmapFill(w, h, pixel_data, mat, repeat, smooth, bitmap_lib_id=bmp_lib_id))
            cur_fill_idx = len(fill_styles)
            if cur_path is not None:
                cur_path.fill_style_idx = cur_fill_idx

        elif cmd == CMD_STROKE_STYLE:
            thickness = float(buf[i]); i += 1
            cap = _to_cap(buf[i]); i += 1
            join = _to_join(buf[i]); i += 1
            miter = float(buf[i]); i += 1
            r, g, b, a = int(buf[i]), int(buf[i+1]), int(buf[i+2]), int(buf[i+3])
            i += 4
            line_styles.append(LineStyle(thickness, r, g, b, a, cap, join, miter))
            cur_line_idx = len(line_styles)
            if cur_path is not None:
                cur_path.line_style_idx = cur_line_idx

        elif cmd == CMD_GRADIENT_STROKE:
            thickness = float(buf[i]); i += 1
            cap = _to_cap(buf[i]); i += 1
            join = _to_join(buf[i]); i += 1
            miter = float(buf[i]); i += 1
            val = buf[i]
            if isinstance(val, str):
                # Rich format: [gtype_str, [{stops}], [matrix], spread_str, interp_str, focal]
                grad_type = _to_grad_type(val); i += 1
                stops = _parse_rich_stops(buf[i]); i += 1
                mat = list(buf[i]); i += 1
                spread = _to_spread(buf[i]); i += 1
                interp = _to_interp(buf[i]); i += 1
                focal = float(buf[i]); i += 1
            else:
                # Flat format: [grad_type_int, num_stops, ratio,r,g,b,a..., m0-m5, spread, interp, focal]
                grad_type = int(val); i += 1
                num_stops = int(buf[i]); i += 1
                stops = []
                for _ in range(num_stops):
                    ratio = int(buf[i]); i += 1
                    sr, sg, sb, sa = int(buf[i]), int(buf[i+1]), int(buf[i+2]), int(buf[i+3])
                    i += 4
                    stops.append(GradientStop(ratio, sr, sg, sb, sa))
                mat = [buf[i+j] for j in range(6)]; i += 6
                spread = int(buf[i]); i += 1
                interp = int(buf[i]); i += 1
                focal = float(buf[i]); i += 1
            gf = GradientFill(grad_type, stops, mat, spread, interp, focal)
            line_styles.append(GradientLineStyle(thickness, cap, join, miter, gf))
            cur_line_idx = len(line_styles)
            if cur_path is not None:
                cur_path.line_style_idx = cur_line_idx

        elif cmd == CMD_BITMAP_STROKE:
            thickness = float(buf[i]); i += 1
            cap = _to_cap(buf[i]); i += 1
            join = _to_join(buf[i]); i += 1
            miter = float(buf[i]); i += 1
            val = buf[i]
            if isinstance(val, dict) or (isinstance(val, (int, float)) and i + 1 < len(buf) and isinstance(buf[i + 1], list)):
                # Rich format: [{bmp_data}/bmp_id, [matrix], repeat_str, smooth_bool]
                # For bitmap strokes, just use a black line fallback for now
                i += 1  # bmp data or id
                i += 1  # matrix
                i += 1  # repeat
                i += 1  # smooth
            else:
                # Flat format: [width, height, buf_len, pixel_data..., m0-m5, repeat, smooth]
                w = int(val); i += 1
                h = int(buf[i]); i += 1
                buf_len = int(buf[i]); i += 1
                i += buf_len  # pixel data
                i += 6  # matrix
                i += 1  # repeat
                i += 1  # smooth
            # fallback: add a black line style
            line_styles.append(LineStyle(thickness, 0, 0, 0, 255, cap, join, miter))
            cur_line_idx = len(line_styles)
            if cur_path is not None:
                cur_path.line_style_idx = cur_line_idx

        elif cmd == CMD_BEGIN_PATH:
            cur_path = SubPath()
            cur_path.fill_style_idx = cur_fill_idx
            cur_path.line_style_idx = cur_line_idx
            cur_path.start_x = cur_x
            cur_path.start_y = cur_y
            sub_paths.append(cur_path)

        elif cmd == CMD_MOVE_TO:
            x, y = float(buf[i]), float(buf[i+1]); i += 2
            cur_x, cur_y = x, y
            if cur_path is not None:
                cur_path.edges.append(MoveToEdge(x, y))
            else:
                cur_path = SubPath()
                cur_path.fill_style_idx = cur_fill_idx
                cur_path.line_style_idx = cur_line_idx
                cur_path.start_x = x
                cur_path.start_y = y
                sub_paths.append(cur_path)

        elif cmd == CMD_LINE_TO:
            x, y = float(buf[i]), float(buf[i+1]); i += 2
            if cur_path is None:
                cur_path = SubPath()
                cur_path.fill_style_idx = cur_fill_idx
                cur_path.line_style_idx = cur_line_idx
                cur_path.start_x = cur_x
                cur_path.start_y = cur_y
                sub_paths.append(cur_path)
            cur_path.edges.append(LineToEdge(x, y))
            cur_x, cur_y = x, y

        elif cmd == CMD_CURVE_TO:
            cx, cy = float(buf[i]), float(buf[i+1]); i += 2
            ax, ay = float(buf[i]), float(buf[i+1]); i += 2
            if cur_path is None:
                cur_path = SubPath()
                cur_path.fill_style_idx = cur_fill_idx
                cur_path.line_style_idx = cur_line_idx
                cur_path.start_x = cur_x
                cur_path.start_y = cur_y
                sub_paths.append(cur_path)
            cur_path.edges.append(CurveToEdge(cx, cy, ax, ay))
            cur_x, cur_y = ax, ay

        elif cmd == CMD_CUBIC:
            # Cubic bezier → approximate with 2 quadratics
            cx1, cy1 = float(buf[i]), float(buf[i+1]); i += 2
            cx2, cy2 = float(buf[i]), float(buf[i+1]); i += 2
            ax, ay = float(buf[i]), float(buf[i+1]); i += 2
            if cur_path is None:
                cur_path = SubPath()
                cur_path.fill_style_idx = cur_fill_idx
                cur_path.line_style_idx = cur_line_idx
                cur_path.start_x = cur_x
                cur_path.start_y = cur_y
                sub_paths.append(cur_path)
            quads = _cubic_to_quadratics(cur_x, cur_y, cx1, cy1, cx2, cy2, ax, ay)
            for qcx, qcy, qax, qay in quads:
                cur_path.edges.append(CurveToEdge(qcx, qcy, qax, qay))
            cur_x, cur_y = ax, ay

        elif cmd == CMD_ARC:
            # Arc → approximate with quadratics
            cx_a, cy_a = float(buf[i]), float(buf[i+1]); i += 2
            radius = float(buf[i]); i += 1
            if cur_path is None:
                cur_path = SubPath()
                cur_path.fill_style_idx = cur_fill_idx
                cur_path.line_style_idx = cur_line_idx
                cur_path.start_x = cur_x
                cur_path.start_y = cur_y
                sub_paths.append(cur_path)
            # Approximate circle with 8-segment quadratic bezier
            quads = _arc_to_quadratics(cx_a, cy_a, radius)
            if quads:
                # Move to start of arc
                sx, sy = quads[0]
                cur_path.edges.append(MoveToEdge(sx, sy))
                for j in range(0, len(quads) - 1, 2):
                    ctrl = quads[j]
                    anch = quads[j + 1] if j + 1 < len(quads) else quads[j]
                    cur_path.edges.append(CurveToEdge(ctrl[0], ctrl[1], anch[0], anch[1]))
                cur_x, cur_y = quads[-1]

        elif cmd == CMD_CLOSE_PATH:
            if cur_path and cur_path.edges:
                # Close back to the start
                start = cur_path.edges[0] if cur_path.edges else None
                if isinstance(start, MoveToEdge):
                    cur_path.edges.append(LineToEdge(start.x, start.y))
                    cur_x, cur_y = start.x, start.y
                else:
                    cur_path.edges.append(LineToEdge(cur_path.start_x, cur_path.start_y))
                    cur_x, cur_y = cur_path.start_x, cur_path.start_y

        elif cmd == CMD_END_FILL:
            cur_fill_idx = 0
            cur_path = None

        elif cmd == CMD_END_STROKE:
            cur_line_idx = 0
            cur_path = None

        else:
            # Unknown command – skip
            pass

    return fill_styles, line_styles, sub_paths


# ── Cubic → Quadratic approximation ────────────────────────────────────

def _cubic_to_quadratics(
    x0: float, y0: float,
    cx1: float, cy1: float, cx2: float, cy2: float,
    x3: float, y3: float,
    depth: int = 0,
) -> List[Tuple[float, float, float, float]]:
    """
    Approximate a cubic Bézier with quadratic Bézier segments.
    Uses midpoint subdivision.
    """
    # Simple approximation: single quadratic through midpoint of control points
    if depth > 4:
        # Fallback: straight line
        return [(x0 + (x3 - x0) * 0.5, y0 + (y3 - y0) * 0.5, x3, y3)]

    # Try a single quadratic approximation
    qcx = (3 * (cx1 + cx2) - x0 - x3) / 4
    qcy = (3 * (cy1 + cy2) - y0 - y3) / 4

    # Check error: distance from cubic midpoint to quad midpoint
    # Cubic midpoint at t=0.5
    cm_x = 0.125 * x0 + 0.375 * cx1 + 0.375 * cx2 + 0.125 * x3
    cm_y = 0.125 * y0 + 0.375 * cy1 + 0.375 * cy2 + 0.125 * y3
    # Quad midpoint at t=0.5
    qm_x = 0.25 * x0 + 0.5 * qcx + 0.25 * x3
    qm_y = 0.25 * y0 + 0.5 * qcy + 0.25 * y3

    error = math.hypot(cm_x - qm_x, cm_y - qm_y)
    if error < 1.0:  # sub-pixel accuracy
        return [(qcx, qcy, x3, y3)]

    # Subdivide at t=0.5
    mx1 = (x0 + cx1) / 2;  my1 = (y0 + cy1) / 2
    mx2 = (cx1 + cx2) / 2; my2 = (cy1 + cy2) / 2
    mx3 = (cx2 + x3) / 2;  my3 = (cy2 + y3) / 2
    mx4 = (mx1 + mx2) / 2; my4 = (my1 + my2) / 2
    mx5 = (mx2 + mx3) / 2; my5 = (my2 + my3) / 2
    mx6 = (mx4 + mx5) / 2; my6 = (my4 + my5) / 2

    left = _cubic_to_quadratics(x0, y0, mx1, my1, mx4, my4, mx6, my6, depth + 1)
    right = _cubic_to_quadratics(mx6, my6, mx5, my5, mx3, my3, x3, y3, depth + 1)
    return left + right


def _arc_to_quadratics(
    cx: float, cy: float, radius: float, segments: int = 8
) -> List[Tuple[float, float]]:
    """
    Approximate a full-circle arc centered at (cx, cy) with given radius.
    Returns a list of (x, y) points for quadratic segments.
    """
    if radius <= 0:
        return []
    points = []
    step = 2 * math.pi / segments
    # Control point factor for quadratic approximation of circular arc
    k = 4 * math.tan(step / 4) / 3

    for i in range(segments):
        angle_start = i * step
        angle_end = (i + 1) * step

        # Start point
        if i == 0:
            sx = cx + radius * math.cos(angle_start)
            sy = cy + radius * math.sin(angle_start)
            points.append((sx, sy))

        # Control point (midpoint of tangent intersection)
        mid_angle = (angle_start + angle_end) / 2
        cos_half = math.cos(step / 2)
        ctrl_r = radius / cos_half if cos_half != 0 else radius
        ctrl_x = cx + ctrl_r * math.cos(mid_angle)
        ctrl_y = cy + ctrl_r * math.sin(mid_angle)
        points.append((ctrl_x, ctrl_y))

        # Anchor (end point)
        ex = cx + radius * math.cos(angle_end)
        ey = cy + radius * math.sin(angle_end)
        points.append((ex, ey))

    return points


# ── Encode to SWF DefineShape3 ──────────────────────────────────────────

def build_define_shape3(
    shape_id: int,
    fill_styles: list,
    line_styles: list,
    sub_paths: List[SubPath],
    bounds: Optional[dict] = None,
) -> bytes:
    """
    Build a DefineShape3 tag from parsed shape data.
    DefineShape3 supports RGBA colours.
    """
    log.debug("build_define_shape3: shape_id=%d fills=%d lines=%d paths=%d", shape_id, len(fill_styles), len(line_styles), len(sub_paths))
    # Calculate bounds
    if bounds:
        xmin = twips(bounds.get("xMin", 0))
        xmax = twips(bounds.get("xMax", 0))
        ymin = twips(bounds.get("yMin", 0))
        ymax = twips(bounds.get("yMax", 0))
    else:
        xmin, ymin = 0, 0
        xmax, ymax = twips(100), twips(100)

    body = io.BytesIO()
    body.write(struct.pack("<H", shape_id))
    body.write(write_rect(xmin, xmax, ymin, ymax))

    # ─ Fill styles ─
    _write_fill_style_array(body, fill_styles, version=3)

    # ─ Line styles ─
    _write_line_style_array(body, line_styles, version=3)

    # ─ Shape records ─
    shape_data = _encode_shape_records(fill_styles, line_styles, sub_paths)
    body.write(shape_data)

    return build_tag(TAG_DEFINE_SHAPE3, body.getvalue())


def build_define_shape4(
    shape_id: int,
    fill_styles: list,
    line_styles: list,
    sub_paths: List[SubPath],
    bounds: Optional[dict] = None,
) -> bytes:
    """Build a DefineShape4 tag from parsed shape data.

    DefineShape4 extends DefineShape3 with:
      - An additional EdgeBounds RECT (same as shape bounds here)
      - A flags byte (UsesFillWindingRule, UsesNonScalingStrokes, etc.)
      - LINESTYLE2 records (caps, joins, miter limit, fill for strokes)
    """
    log.debug("build_define_shape4: shape_id=%d fills=%d lines=%d paths=%d",
              shape_id, len(fill_styles), len(line_styles), len(sub_paths))
    if bounds:
        xmin = twips(bounds.get("xMin", 0))
        xmax = twips(bounds.get("xMax", 0))
        ymin = twips(bounds.get("yMin", 0))
        ymax = twips(bounds.get("yMax", 0))
    else:
        xmin, ymin = 0, 0
        xmax, ymax = twips(100), twips(100)

    body = io.BytesIO()
    body.write(struct.pack("<H", shape_id))
    body.write(write_rect(xmin, xmax, ymin, ymax))   # ShapeBounds
    body.write(write_rect(xmin, xmax, ymin, ymax))   # EdgeBounds (same)

    # Flags: bit 0 = UsesFillWindingRule, bit 1 = UsesNonScalingStrokes,
    #         bit 2 = UsesScalingStrokes
    body.write(struct.pack("<B", 0x04))  # UsesScalingStrokes = true

    # ─ Fill styles ─
    _write_fill_style_array(body, fill_styles, version=4)

    # ─ Line styles (LINESTYLE2 for DefineShape4) ─
    _write_line_style2_array(body, line_styles)

    # ─ Shape records ─
    shape_data = _encode_shape_records(fill_styles, line_styles, sub_paths)
    body.write(shape_data)

    return build_tag(TAG_DEFINE_SHAPE4, body.getvalue())


def _write_fill_style_array(out: io.BytesIO, fill_styles: list, version: int = 3) -> None:
    """Write FILLSTYLEARRAY."""
    count = len(fill_styles)
    if count < 0xFF:
        out.write(struct.pack("<B", count))
    else:
        out.write(struct.pack("<BH", 0xFF, count))

    for fs in fill_styles:
        if isinstance(fs, SolidFill):
            out.write(struct.pack("<B", 0x00))  # type: solid
            out.write(struct.pack("<BBBB", fs.r, fs.g, fs.b, fs.a))

        elif isinstance(fs, GradientFill):
            if fs.grad_type == 0:
                out.write(struct.pack("<B", 0x10))  # linear gradient
            else:
                if fs.focal != 0:
                    out.write(struct.pack("<B", 0x13))  # focal radial
                else:
                    out.write(struct.pack("<B", 0x12))  # radial gradient
            # Gradient matrix
            _write_gradient_matrix(out, fs.matrix)
            # Gradient record
            _write_gradient(out, fs, version)

        elif isinstance(fs, BitmapFill):
            # Choose fill type based on repeat + smoothing
            # SWF fill types:
            #   0x40 = repeating bitmap, smoothed
            #   0x41 = clipped bitmap, smoothed
            #   0x42 = repeating bitmap, non-smoothed (SWF 8+)
            #   0x43 = clipped bitmap, non-smoothed (SWF 8+)
            if fs.repeat:
                fill_type = 0x40 if fs.smooth else 0x42
            else:
                fill_type = 0x41 if fs.smooth else 0x43
            out.write(struct.pack("<B", fill_type))
            # BitmapId — use assigned char ID if available, else placeholder
            bmp_id = fs.bitmap_char_id if fs.bitmap_char_id else 0xFFFF
            out.write(struct.pack("<H", bmp_id))
            _write_bitmap_matrix(out, fs.matrix)


def _write_bitmap_matrix(out: io.BytesIO, matrix: List[float]) -> None:
    """Write a MATRIX for a bitmap fill, converting pixel-space scale back to twips.

    During import, bitmap fill matrices have their scale/rotate components
    divided by 20 (twips→pixels).  We reverse that here (* 20) so the SWF
    matrix is correct.
    """
    from swf_writer import write_matrix
    a = (matrix[0] if len(matrix) > 0 else 1.0) * 20.0
    b = (matrix[1] if len(matrix) > 1 else 0.0) * 20.0
    c = (matrix[2] if len(matrix) > 2 else 0.0) * 20.0
    d = (matrix[3] if len(matrix) > 3 else 1.0) * 20.0
    tx = matrix[4] if len(matrix) > 4 else 0.0
    ty = matrix[5] if len(matrix) > 5 else 0.0
    out.write(write_matrix(a, b, c, d, tx, ty))


def _write_gradient_matrix(out: io.BytesIO, matrix: List[float]) -> None:
    """Write a MATRIX from a 6-element array [a,b,c,d,tx,ty]."""
    from swf_writer import write_matrix
    a = matrix[0] if len(matrix) > 0 else 1.0
    b = matrix[1] if len(matrix) > 1 else 0.0
    c = matrix[2] if len(matrix) > 2 else 0.0
    d = matrix[3] if len(matrix) > 3 else 1.0
    tx = matrix[4] if len(matrix) > 4 else 0.0
    ty = matrix[5] if len(matrix) > 5 else 0.0
    out.write(write_matrix(a, b, c, d, tx, ty))


def _write_gradient(out: io.BytesIO, gf: GradientFill, version: int) -> None:
    """Write GRADIENT or FOCALGRADIENT."""
    # SpreadMode (2 bits) | InterpolationMode (2 bits) | NumGradients (4 bits)
    # Next2D spread: 0=reflect, 1=repeat, 2=pad
    # SWF spread: 0=pad, 1=reflect, 2=repeat
    spread_map = {0: 1, 1: 2, 2: 0}
    spread = spread_map.get(gf.spread, 0)
    # Next2D interp: 0=linearRGB, 1=rgb
    # SWF interp: 0=normal(rgb), 1=linearRGB
    interp_map = {0: 1, 1: 0}
    interp = interp_map.get(gf.interpolation, 0)

    num_stops = min(len(gf.stops), 15)
    header_byte = (spread << 6) | (interp << 4) | num_stops
    out.write(struct.pack("<B", header_byte))

    for stop in gf.stops[:15]:
        out.write(struct.pack("<B", stop.ratio))
        out.write(struct.pack("<BBBB", stop.r, stop.g, stop.b, stop.a))

    # Focal gradient has an extra fixed8 focal point value
    if gf.focal != 0:
        focal_fixed = int(round(gf.focal * 256)) & 0xFFFF
        out.write(struct.pack("<h", focal_fixed))


def _write_line_style_array(out: io.BytesIO, line_styles: list, version: int = 3) -> None:
    """Write LINESTYLEARRAY (version 3 = LINESTYLE with RGBA)."""
    count = len(line_styles)
    if count < 0xFF:
        out.write(struct.pack("<B", count))
    else:
        out.write(struct.pack("<BH", 0xFF, count))

    for ls in line_styles:
        if isinstance(ls, LineStyle):
            out.write(struct.pack("<H", max(twips(ls.thickness), 1)))  # Width in twips
            out.write(struct.pack("<BBBB", ls.r, ls.g, ls.b, ls.a))
        elif isinstance(ls, GradientLineStyle):
            # DefineShape3 doesn't support gradient line styles → fallback to solid black
            out.write(struct.pack("<H", max(twips(ls.thickness), 1)))
            out.write(struct.pack("<BBBB", 0, 0, 0, 255))


def _write_line_style2_array(out: io.BytesIO, line_styles: list) -> None:
    """Write LINESTYLE2ARRAY for DefineShape4.

    LINESTYLE2 adds StartCapStyle, JoinStyle, EndCapStyle, miter limit,
    and the ability to fill a stroke with a gradient or bitmap.
    """
    count = len(line_styles)
    if count < 0xFF:
        out.write(struct.pack("<B", count))
    else:
        out.write(struct.pack("<BH", 0xFF, count))

    # Cap/Join maps: Next2D values → SWF encoding
    CAP_MAP = {'round': 0, 'none': 1, 'square': 2}
    JOIN_MAP = {'round': 0, 'bevel': 1, 'miter': 2}

    for ls in line_styles:
        width_twips = max(twips(ls.thickness), 1) if isinstance(ls, (LineStyle, GradientLineStyle)) else 20
        out.write(struct.pack("<H", width_twips))

        cap_val = CAP_MAP.get(getattr(ls, 'cap', 'round'), 0)
        join_val = JOIN_MAP.get(getattr(ls, 'join', 'round'), 0)
        miter_val = getattr(ls, 'miter_limit', 3.0) if isinstance(ls, LineStyle) else 3.0
        has_fill = isinstance(ls, GradientLineStyle)

        # LINESTYLE2 flags packed in 2 bytes (big-endian bit layout):
        # StartCapStyle(2) | JoinStyle(2) | HasFillFlag(1) |
        # NoHScaleFlag(1) | NoVScaleFlag(1) | PixelHintingFlag(1) |
        # Reserved(5) | NoClose(1) | EndCapStyle(2)
        flags = 0
        flags |= (cap_val & 0x3) << 14     # StartCapStyle
        flags |= (join_val & 0x3) << 12    # JoinStyle
        flags |= (1 if has_fill else 0) << 11  # HasFillFlag
        flags |= (cap_val & 0x3)           # EndCapStyle (same as start)
        out.write(struct.pack(">H", flags))

        if join_val == 2:  # Miter join → write MiterLimitFactor (FIXED 16.16)
            out.write(struct.pack("<I", int(miter_val * 65536)))

        if has_fill:
            # Write fill style for gradient stroke
            gf = ls.gradient_fill
            if gf.grad_type == 0:
                out.write(struct.pack("<B", 0x10))
            else:
                out.write(struct.pack("<B", 0x12))
            _write_gradient_matrix(out, gf.matrix)
            _write_gradient(out, gf, 4)
        else:
            # Solid colour fill
            r, g, b, a = (ls.r, ls.g, ls.b, ls.a) if isinstance(ls, LineStyle) else (0, 0, 0, 255)
            out.write(struct.pack("<BBBB", r, g, b, a))


def _encode_shape_records(
    fill_styles: list,
    line_styles: list,
    sub_paths: List[SubPath],
) -> bytes:
    """
    Encode shape records (style changes, edges, end).
    """
    bw = BitWriter()

    # NumFillBits/NumLineBits: 0 when there are no styles (0 means no fill/line indices)
    num_fill_bits = fill_styles and max(1, _nbits_unsigned(len(fill_styles))) or 0
    num_line_bits = line_styles and max(1, _nbits_unsigned(len(line_styles))) or 0
    bw.write_ub(4, num_fill_bits)
    bw.write_ub(4, num_line_bits)

    prev_x, prev_y = 0, 0
    cur_fill1 = 0  # track active fill1 state (SWF styles are incremental)
    cur_line = 0   # track active line state

    for sp in sub_paths:
        # Style change record to set position and styles
        has_move = True  # always set initial move
        has_fill0 = False
        # Emit fill1/line when the value changes (including clearing to 0)
        has_fill1 = sp.fill_style_idx != cur_fill1
        has_line = sp.line_style_idx != cur_line
        has_new_styles = False

        # Find the first coordinate
        move_x, move_y = sp.start_x, sp.start_y
        if sp.edges and isinstance(sp.edges[0], MoveToEdge):
            move_x, move_y = sp.edges[0].x, sp.edges[0].y

        move_x_tw = twips(move_x)
        move_y_tw = twips(move_y)

        # Non-edge record (bit 0 = 0)
        bw.write_ub(1, 0)

        # StateNewStyles | StateLineStyle | StateFillStyle1 | StateFillStyle0 | StateMoveTo
        flags = 0
        if has_new_styles:
            flags |= 0x10
        if has_line:
            flags |= 0x08
        if has_fill1:
            flags |= 0x04
        if has_fill0:
            flags |= 0x02
        if has_move:
            flags |= 0x01
        bw.write_ub(5, flags)

        if has_move:
            # SWF MoveDeltaX/Y are absolute coords (not deltas from prev)
            move_bits = max(_nbits_signed_list([move_x_tw, move_y_tw]), 1)
            bw.write_ub(5, move_bits)
            bw.write_sb(move_bits, move_x_tw)
            bw.write_sb(move_bits, move_y_tw)
            prev_x, prev_y = move_x_tw, move_y_tw

        if has_fill0:
            bw.write_ub(num_fill_bits, 0)
        if has_fill1:
            bw.write_ub(num_fill_bits, sp.fill_style_idx)
            cur_fill1 = sp.fill_style_idx
        if has_line:
            bw.write_ub(num_line_bits, sp.line_style_idx)
            cur_line = sp.line_style_idx

        # Write edges
        for edge in sp.edges:
            if isinstance(edge, MoveToEdge):
                # Emit a StyleChange with MoveTo only
                ex = twips(edge.x)
                ey = twips(edge.y)
                if ex == prev_x and ey == prev_y:
                    continue
                bw.write_ub(1, 0)  # non-edge
                bw.write_ub(5, 0x01)  # StateMoveTo only
                # SWF MoveDeltaX/Y are absolute coords (not deltas)
                mbits = max(_nbits_signed_list([ex, ey]), 1)
                bw.write_ub(5, mbits)
                bw.write_sb(mbits, ex)
                bw.write_sb(mbits, ey)
                prev_x, prev_y = ex, ey

            elif isinstance(edge, LineToEdge):
                ex = twips(edge.x)
                ey = twips(edge.y)
                edx = ex - prev_x
                edy = ey - prev_y
                if edx == 0 and edy == 0:
                    continue
                # StraightEdge record
                bw.write_ub(1, 1)  # edge flag
                bw.write_ub(1, 1)  # straight edge
                nbits = max(_nbits_signed_list([edx, edy]), 2) - 2
                nbits = max(nbits, 0)
                bw.write_ub(4, nbits)
                if edx == 0:
                    bw.write_ub(1, 0)  # GeneralLine = false
                    bw.write_ub(1, 1)  # VertLine
                    bw.write_sb(nbits + 2, edy)
                elif edy == 0:
                    bw.write_ub(1, 0)  # GeneralLine = false
                    bw.write_ub(1, 0)  # HorzLine
                    bw.write_sb(nbits + 2, edx)
                else:
                    bw.write_ub(1, 1)  # GeneralLine = true
                    bw.write_sb(nbits + 2, edx)
                    bw.write_sb(nbits + 2, edy)
                prev_x, prev_y = ex, ey

            elif isinstance(edge, CurveToEdge):
                cx_tw = twips(edge.cx)
                cy_tw = twips(edge.cy)
                ax_tw = twips(edge.ax)
                ay_tw = twips(edge.ay)
                # Control deltas (relative to current)
                cdx = cx_tw - prev_x
                cdy = cy_tw - prev_y
                # Anchor deltas (relative to control)
                adx = ax_tw - cx_tw
                ady = ay_tw - cy_tw

                if cdx == 0 and cdy == 0 and adx == 0 and ady == 0:
                    continue

                bw.write_ub(1, 1)  # edge flag
                bw.write_ub(1, 0)  # curved edge
                nbits = max(_nbits_signed_list([cdx, cdy, adx, ady]), 2) - 2
                nbits = max(nbits, 0)
                bw.write_ub(4, nbits)
                bw.write_sb(nbits + 2, cdx)
                bw.write_sb(nbits + 2, cdy)
                bw.write_sb(nbits + 2, adx)
                bw.write_sb(nbits + 2, ady)
                prev_x, prev_y = ax_tw, ay_tw

    # EndShapeRecord
    bw.write_ub(6, 0)  # non-edge, all state flags = 0

    return bw.get_bytes()


# ── Encode to SWF DefineMorphShape (tag 46) ─────────────────────────────

def _write_morph_fill_style_array(
    out: io.BytesIO,
    start_fills: list,
    end_fills: list,
) -> None:
    """Write MORPHFILLSTYLEARRAY: pairs of start/end fill styles."""
    count = len(start_fills)
    if count < 0xFF:
        out.write(struct.pack("<B", count))
    else:
        out.write(struct.pack("<BH", 0xFF, count))

    for i in range(count):
        sf = start_fills[i]
        ef = end_fills[i] if i < len(end_fills) else sf

        if isinstance(sf, SolidFill) and isinstance(ef, SolidFill):
            out.write(struct.pack("<B", 0x00))  # solid fill
            out.write(struct.pack("<BBBB", sf.r, sf.g, sf.b, sf.a))  # start RGBA
            out.write(struct.pack("<BBBB", ef.r, ef.g, ef.b, ef.a))  # end RGBA
        elif isinstance(sf, GradientFill):
            # Morph gradient — write start/end gradient data
            if sf.grad_type == 0:
                out.write(struct.pack("<B", 0x10))
            else:
                out.write(struct.pack("<B", 0x12))
            # Start gradient matrix
            _write_gradient_matrix(out, sf.matrix)
            # End gradient matrix
            ef_gf = ef if isinstance(ef, GradientFill) else sf
            _write_gradient_matrix(out, ef_gf.matrix)
            # Gradient records
            num_stops = min(len(sf.stops), 8)
            ef_stops = ef_gf.stops if isinstance(ef, GradientFill) else sf.stops
            spread = 0
            interp = 0
            header_byte = (spread << 6) | (interp << 4) | num_stops
            out.write(struct.pack("<B", header_byte))
            for si in range(num_stops):
                s = sf.stops[si]
                e = ef_stops[si] if si < len(ef_stops) else s
                out.write(struct.pack("<B", s.ratio))
                out.write(struct.pack("<BBBB", s.r, s.g, s.b, s.a))
                out.write(struct.pack("<B", e.ratio))
                out.write(struct.pack("<BBBB", e.r, e.g, e.b, e.a))
        else:
            # Fallback: solid black → solid black
            out.write(struct.pack("<B", 0x00))
            out.write(struct.pack("<BBBB", 0, 0, 0, 255))
            out.write(struct.pack("<BBBB", 0, 0, 0, 255))


def _write_morph_line_style_array(
    out: io.BytesIO,
    start_lines: list,
    end_lines: list,
) -> None:
    """Write MORPHLINESTYLEARRAY: pairs of start/end line styles."""
    count = len(start_lines)
    if count < 0xFF:
        out.write(struct.pack("<B", count))
    else:
        out.write(struct.pack("<BH", 0xFF, count))

    for i in range(count):
        sl = start_lines[i]
        el = end_lines[i] if i < len(end_lines) else sl

        sw = max(twips(sl.thickness), 0) if isinstance(sl, LineStyle) else 0
        ew = max(twips(el.thickness), 0) if isinstance(el, LineStyle) else 0
        out.write(struct.pack("<H", sw))  # start width
        out.write(struct.pack("<H", ew))  # end width
        sr, sg, sb, sa = (sl.r, sl.g, sl.b, sl.a) if isinstance(sl, LineStyle) else (0, 0, 0, 0)
        er, eg, eb, ea = (el.r, el.g, el.b, el.a) if isinstance(el, LineStyle) else (0, 0, 0, 0)
        out.write(struct.pack("<BBBB", sr, sg, sb, sa))  # start RGBA
        out.write(struct.pack("<BBBB", er, eg, eb, ea))  # end RGBA


def _write_morph_line_style2_array(
    out: io.BytesIO,
    start_lines: list,
    end_lines: list,
) -> None:
    """Write MORPHLINESTYLE2ARRAY for DefineMorphShape2.

    MORPHLINESTYLE2 extends MORPHLINESTYLE with caps, joins, miter limit,
    and optional fill-based strokes (gradient/bitmap).
    """
    count = len(start_lines)
    if count < 0xFF:
        out.write(struct.pack("<B", count))
    else:
        out.write(struct.pack("<BH", 0xFF, count))

    CAP_MAP = {'round': 0, 'none': 1, 'square': 2}
    JOIN_MAP = {'round': 0, 'bevel': 1, 'miter': 2}

    for i in range(count):
        sl = start_lines[i]
        el = end_lines[i] if i < len(end_lines) else sl

        sw = max(twips(sl.thickness), 0) if isinstance(sl, LineStyle) else 0
        ew = max(twips(el.thickness), 0) if isinstance(el, LineStyle) else 0
        out.write(struct.pack("<H", sw))  # StartWidth
        out.write(struct.pack("<H", ew))  # EndWidth

        cap_val = CAP_MAP.get(getattr(sl, 'cap', 'round'), 0)
        join_val = JOIN_MAP.get(getattr(sl, 'join', 'round'), 0)
        has_fill = isinstance(sl, GradientLineStyle)

        # MORPHLINESTYLE2 flags (big-endian 2 bytes):
        # StartCapStyle(2) | JoinStyle(2) | HasFillFlag(1) |
        # NoHScaleFlag(1) | NoVScaleFlag(1) | PixelHintingFlag(1) |
        # Reserved(5) | NoClose(1) | EndCapStyle(2)
        flags = 0
        flags |= (cap_val & 0x3) << 14
        flags |= (join_val & 0x3) << 12
        flags |= (1 if has_fill else 0) << 11
        flags |= (cap_val & 0x3)  # EndCapStyle = StartCapStyle
        out.write(struct.pack(">H", flags))

        if join_val == 2:  # Miter → MiterLimitFactor FIXED 16.16
            out.write(struct.pack("<I", int(getattr(sl, 'miter_limit', 3.0) * 65536)))

        if has_fill:
            # Write start fill style + end fill style for gradient stroke
            gf = sl.gradient_fill
            if gf.grad_type == 0:
                out.write(struct.pack("<B", 0x10))
            else:
                out.write(struct.pack("<B", 0x12))
            _write_gradient_matrix(out, gf.matrix)
            _write_gradient(out, gf, 4)
            # End fill style (same type, simple RGBA fallback)
            egf = el.gradient_fill if isinstance(el, GradientLineStyle) and el.gradient_fill else gf
            if egf.grad_type == 0:
                out.write(struct.pack("<B", 0x10))
            else:
                out.write(struct.pack("<B", 0x12))
            _write_gradient_matrix(out, egf.matrix)
            _write_gradient(out, egf, 4)
        else:
            sr, sg, sb, sa = (sl.r, sl.g, sl.b, sl.a) if isinstance(sl, LineStyle) else (0, 0, 0, 0)
            er, eg, eb, ea = (el.r, el.g, el.b, el.a) if isinstance(el, LineStyle) else (0, 0, 0, 0)
            out.write(struct.pack("<BBBB", sr, sg, sb, sa))  # StartColor RGBA
            out.write(struct.pack("<BBBB", er, eg, eb, ea))  # EndColor RGBA


def _morph_collapse_fill_merge(sub_paths: List[SubPath]) -> Tuple[List[SubPath], bool]:
    """Undo the fill_merge transformation for morph shape paths.

    The _fill_merge in swf_shape_to_recodes reverses fill0 edges and merges
    them into fill1, creating two sub_paths from one:
      Path A: fill only (reversed edges, CW)
      Path B: fill + line (original edges, CCW)
    Both paths get fill1, which causes fill cancellation via winding rules
    when rendered in Flash Player → morph appears blank.

    This function detects that pattern and collapses back into a single
    sub_path using fill0 convention (the original SWF representation).

    Returns (collapsed_paths, did_collapse).
    """
    if len(sub_paths) < 2:
        return sub_paths, False

    result = []
    used = set()
    collapsed = False

    for i in range(len(sub_paths)):
        if i in used:
            continue
        a = sub_paths[i]
        matched = False

        # Look for the fill_merge pattern: fill-only path + line path
        # Pattern 1 (gradient fill): both paths have same fill_style_idx
        #   Path A: fill=N line=0; Path B: fill=N line=M
        # Pattern 2 (solid fill with END_FILL): Path B lost its fill
        #   Path A: fill=N line=0; Path B: fill=0 line=M
        if a.fill_style_idx > 0 and a.line_style_idx == 0:
            for j in range(i + 1, len(sub_paths)):
                if j in used:
                    continue
                b = sub_paths[j]
                if (b.line_style_idx > 0 and
                        (b.fill_style_idx == a.fill_style_idx or
                         b.fill_style_idx == 0)):
                    # Found the pair: keep B (the line path with original
                    # edge direction), restore fill from A, mark for fill0.
                    new_sp = SubPath()
                    new_sp.fill_style_idx = a.fill_style_idx
                    new_sp.line_style_idx = b.line_style_idx
                    new_sp.start_x = b.start_x
                    new_sp.start_y = b.start_y
                    new_sp.edges = b.edges
                    new_sp._morph_use_fill0 = True  # type: ignore[attr-defined]
                    result.append(new_sp)
                    used.add(i)
                    used.add(j)
                    matched = True
                    collapsed = True
                    break

        if not matched:
            result.append(a)
            used.add(i)

    return result, collapsed


def _encode_morph_shape_edges(
    fill_styles: list,
    line_styles: list,
    sub_paths: List[SubPath],
    is_end_state: bool = False,
) -> bytes:
    """Encode shape records for one half of a morph shape (start or end).

    Per the SWF spec, end-state edges must have NumFillBits=0 and
    NumLineBits=0 — only geometry (MoveTo + edges), no fill/line
    style change records.  Flash Player pairs end edges with start
    edges' style assignments implicitly.
    """
    bw = BitWriter()

    if is_end_state:
        # End state: no fill/line style references per SWF spec
        num_fill_bits = 0
        num_line_bits = 0
    else:
        num_fill_bits = fill_styles and max(1, _nbits_unsigned(len(fill_styles))) or 0
        num_line_bits = line_styles and max(1, _nbits_unsigned(len(line_styles))) or 0
    bw.write_ub(4, num_fill_bits)
    bw.write_ub(4, num_line_bits)

    prev_x, prev_y = 0, 0

    for sp in sub_paths:
        has_move = True
        if is_end_state:
            # End state: geometry only, no fill/line flags
            has_fill0 = False
            has_fill1 = False
            has_line = False
        else:
            use_fill0 = getattr(sp, '_morph_use_fill0', False)
            if use_fill0:
                # Collapsed fill_merge path: write as fill0 (original SWF convention)
                has_fill0 = sp.fill_style_idx > 0
                has_fill1 = False
            else:
                has_fill0 = False
                has_fill1 = sp.fill_style_idx > 0
            has_line = sp.line_style_idx > 0

        move_x, move_y = sp.start_x, sp.start_y
        if sp.edges and isinstance(sp.edges[0], MoveToEdge):
            move_x, move_y = sp.edges[0].x, sp.edges[0].y

        move_x_tw = twips(move_x)
        move_y_tw = twips(move_y)

        bw.write_ub(1, 0)  # non-edge
        flags = 0
        if has_line:
            flags |= 0x08
        if has_fill1:
            flags |= 0x04
        if has_fill0:
            flags |= 0x02
        if has_move:
            flags |= 0x01
        bw.write_ub(5, flags)

        if has_move:
            # SWF MoveDeltaX/Y are absolute coords (not deltas from prev)
            move_bits = max(_nbits_signed_list([move_x_tw, move_y_tw]), 1)
            bw.write_ub(5, move_bits)
            bw.write_sb(move_bits, move_x_tw)
            bw.write_sb(move_bits, move_y_tw)
            prev_x, prev_y = move_x_tw, move_y_tw

        if has_fill0:
            bw.write_ub(num_fill_bits, sp.fill_style_idx)
        if has_fill1:
            bw.write_ub(num_fill_bits, sp.fill_style_idx)
        if has_line:
            bw.write_ub(num_line_bits, sp.line_style_idx)

        for edge in sp.edges:
            if isinstance(edge, MoveToEdge):
                ex = twips(edge.x)
                ey = twips(edge.y)
                if ex == prev_x and ey == prev_y:
                    continue
                bw.write_ub(1, 0)
                bw.write_ub(5, 0x01)
                # SWF MoveDeltaX/Y are absolute coords (not deltas)
                mbits = max(_nbits_signed_list([ex, ey]), 1)
                bw.write_ub(5, mbits)
                bw.write_sb(mbits, ex)
                bw.write_sb(mbits, ey)
                prev_x, prev_y = ex, ey

            elif isinstance(edge, LineToEdge):
                ex = twips(edge.x)
                ey = twips(edge.y)
                edx = ex - prev_x
                edy = ey - prev_y
                if edx == 0 and edy == 0:
                    continue
                bw.write_ub(1, 1)
                bw.write_ub(1, 1)
                nbits = max(_nbits_signed_list([edx, edy]), 2) - 2
                nbits = max(nbits, 0)
                bw.write_ub(4, nbits)
                if edx == 0:
                    bw.write_ub(1, 0)
                    bw.write_ub(1, 1)
                    bw.write_sb(nbits + 2, edy)
                elif edy == 0:
                    bw.write_ub(1, 0)
                    bw.write_ub(1, 0)
                    bw.write_sb(nbits + 2, edx)
                else:
                    bw.write_ub(1, 1)
                    bw.write_sb(nbits + 2, edx)
                    bw.write_sb(nbits + 2, edy)
                prev_x, prev_y = ex, ey

            elif isinstance(edge, CurveToEdge):
                cx_tw = twips(edge.cx)
                cy_tw = twips(edge.cy)
                ax_tw = twips(edge.ax)
                ay_tw = twips(edge.ay)
                cdx = cx_tw - prev_x
                cdy = cy_tw - prev_y
                adx = ax_tw - cx_tw
                ady = ay_tw - cy_tw
                if cdx == 0 and cdy == 0 and adx == 0 and ady == 0:
                    continue
                bw.write_ub(1, 1)
                bw.write_ub(1, 0)
                nbits = max(_nbits_signed_list([cdx, cdy, adx, ady]), 2) - 2
                nbits = max(nbits, 0)
                bw.write_ub(4, nbits)
                bw.write_sb(nbits + 2, cdx)
                bw.write_sb(nbits + 2, cdy)
                bw.write_sb(nbits + 2, adx)
                bw.write_sb(nbits + 2, ady)
                prev_x, prev_y = ax_tw, ay_tw

    # EndShapeRecord
    bw.write_ub(6, 0)

    return bw.get_bytes()


def build_define_morph_shape(
    shape_id: int,
    start_fills: list,
    start_lines: list,
    start_paths: List[SubPath],
    start_bounds: Optional[dict],
    end_fills: list,
    end_lines: list,
    end_paths: List[SubPath],
    end_bounds: Optional[dict],
) -> bytes:
    """
    Build a DefineMorphShape tag (tag 46) from parsed start/end shape data.

    The tag contains:
      - StartBounds RECT
      - EndBounds RECT
      - Offset (UI32) — byte count from after Offset to end of MorphFillStyles+
        MorphLineStyles+StartEdges
      - MorphFillStyleArray (paired start/end fills)
      - MorphLineStyleArray (paired start/end lines)
      - StartEdges (shape records for start shape)
      - EndEdges (shape records for end shape)
    """
    log.debug("build_define_morph_shape: shape_id=%d start_fills=%d end_fills=%d", shape_id, len(start_fills), len(end_fills))
    from swf_writer import write_rect

    # Calculate bounds
    if start_bounds:
        sxmin = twips(start_bounds.get("xMin", 0))
        sxmax = twips(start_bounds.get("xMax", 0))
        symin = twips(start_bounds.get("yMin", 0))
        symax = twips(start_bounds.get("yMax", 0))
    else:
        sxmin, symin, sxmax, symax = 0, 0, twips(100), twips(100)

    if end_bounds:
        exmin = twips(end_bounds.get("xMin", 0))
        exmax = twips(end_bounds.get("xMax", 0))
        eymin = twips(end_bounds.get("yMin", 0))
        eymax = twips(end_bounds.get("yMax", 0))
    else:
        exmin, eymin, exmax, eymax = 0, 0, twips(100), twips(100)

    body = io.BytesIO()
    body.write(struct.pack("<H", shape_id))
    body.write(write_rect(sxmin, sxmax, symin, symax))  # StartBounds
    body.write(write_rect(exmin, exmax, eymin, eymax))  # EndBounds

    # Build the "offset block" (styles + start edges) to compute Offset value
    # First, undo fill_merge for morph shapes to avoid fill cancellation
    start_paths, _ = _morph_collapse_fill_merge(start_paths)
    end_paths, _ = _morph_collapse_fill_merge(end_paths)

    offset_block = io.BytesIO()
    _write_morph_fill_style_array(offset_block, start_fills, end_fills)
    _write_morph_line_style_array(offset_block, start_lines, end_lines)
    start_edges = _encode_morph_shape_edges(start_fills, start_lines, start_paths)
    offset_block.write(start_edges)

    offset_data = offset_block.getvalue()
    body.write(struct.pack("<I", len(offset_data)))  # Offset
    body.write(offset_data)

    # End edges — geometry only, no fill/line references per SWF spec
    end_edges = _encode_morph_shape_edges(end_fills, end_lines, end_paths, is_end_state=True)
    body.write(end_edges)

    return build_tag(TAG_DEFINE_MORPH_SHAPE, body.getvalue())


def build_define_morph_shape2(
    shape_id: int,
    start_fills: list,
    start_lines: list,
    start_paths: List[SubPath],
    start_bounds: Optional[dict],
    end_fills: list,
    end_lines: list,
    end_paths: List[SubPath],
    end_bounds: Optional[dict],
) -> bytes:
    """Build a DefineMorphShape2 tag (tag 84).

    Extends DefineMorphShape with:
      - StartEdgeBounds RECT, EndEdgeBounds RECT
      - UI8 flags (UsesNonScalingStrokes, UsesScalingStrokes)
      - MORPHLINESTYLE2 records (caps, joins, fill for strokes)
    """
    log.debug("build_define_morph_shape2: shape_id=%d start_fills=%d end_fills=%d",
              shape_id, len(start_fills), len(end_fills))
    from swf_writer import write_rect

    if start_bounds:
        sxmin = twips(start_bounds.get("xMin", 0))
        sxmax = twips(start_bounds.get("xMax", 0))
        symin = twips(start_bounds.get("yMin", 0))
        symax = twips(start_bounds.get("yMax", 0))
    else:
        sxmin, symin, sxmax, symax = 0, 0, twips(100), twips(100)

    if end_bounds:
        exmin = twips(end_bounds.get("xMin", 0))
        exmax = twips(end_bounds.get("xMax", 0))
        eymin = twips(end_bounds.get("yMin", 0))
        eymax = twips(end_bounds.get("yMax", 0))
    else:
        exmin, eymin, exmax, eymax = 0, 0, twips(100), twips(100)

    body = io.BytesIO()
    body.write(struct.pack("<H", shape_id))
    body.write(write_rect(sxmin, sxmax, symin, symax))  # StartBounds
    body.write(write_rect(exmin, exmax, eymin, eymax))  # EndBounds
    body.write(write_rect(sxmin, sxmax, symin, symax))  # StartEdgeBounds (same)
    body.write(write_rect(exmin, exmax, eymin, eymax))  # EndEdgeBounds (same)

    # Flags: bit 0 = UsesNonScalingStrokes, bit 1 = UsesScalingStrokes
    body.write(struct.pack("<B", 0x02))  # UsesScalingStrokes

    # Build offset block (styles + start edges)
    # First, undo fill_merge for morph shapes to avoid fill cancellation
    start_paths, _ = _morph_collapse_fill_merge(start_paths)
    end_paths, _ = _morph_collapse_fill_merge(end_paths)

    offset_block = io.BytesIO()
    _write_morph_fill_style_array(offset_block, start_fills, end_fills)
    _write_morph_line_style2_array(offset_block, start_lines, end_lines)
    start_edges = _encode_morph_shape_edges(start_fills, start_lines, start_paths)
    offset_block.write(start_edges)

    offset_data = offset_block.getvalue()
    body.write(struct.pack("<I", len(offset_data)))  # Offset
    body.write(offset_data)

    # End edges — geometry only, no fill/line references per SWF spec
    end_edges = _encode_morph_shape_edges(end_fills, end_lines, end_paths, is_end_state=True)
    body.write(end_edges)

    return build_tag(TAG_DEFINE_MORPH_SHAPE2, body.getvalue())
