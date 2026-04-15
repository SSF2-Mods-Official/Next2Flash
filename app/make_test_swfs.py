"""Generate minimal test SWF files with single shapes for roundtrip debugging."""
import struct, io, zlib

# ── SWF primitives ──────────────────────────────────────────────

class BitWriter:
    def __init__(self):
        self.bits = []
    def write_ub(self, n, val):
        for i in range(n - 1, -1, -1):
            self.bits.append((val >> i) & 1)
    def write_sb(self, n, val):
        if val < 0:
            val = val + (1 << n)
        self.write_ub(n, val)
    def align(self):
        while len(self.bits) % 8:
            self.bits.append(0)
    def get_bytes(self):
        self.align()
        out = bytearray()
        for i in range(0, len(self.bits), 8):
            b = 0
            for j in range(8):
                if i + j < len(self.bits):
                    b = (b << 1) | self.bits[i + j]
                else:
                    b <<= 1
            out.append(b)
        return bytes(out)

def nbits_signed(val):
    if val == 0: return 1
    if val < 0: val = ~val
    return val.bit_length() + 1

def nbits_signed_list(vals):
    return max(nbits_signed(v) for v in vals)

def nbits_unsigned(val):
    if val == 0: return 1
    return val.bit_length()

def twips(px):
    return int(round(px * 20))

def write_rect(xmin, xmax, ymin, ymax):
    bw = BitWriter()
    nb = nbits_signed_list([xmin, xmax, ymin, ymax])
    bw.write_ub(5, nb)
    bw.write_sb(nb, xmin)
    bw.write_sb(nb, xmax)
    bw.write_sb(nb, ymin)
    bw.write_sb(nb, ymax)
    return bw.get_bytes()

def build_tag(tag_type, body):
    length = len(body)
    if length < 0x3F:
        hdr = (tag_type << 6) | length
        return struct.pack('<H', hdr) + body
    else:
        hdr = (tag_type << 6) | 0x3F
        return struct.pack('<HI', hdr, length) + body

def write_swf(filename, tags, width=200, height=200, fps=24, frame_count=1):
    """Write a complete SWF file."""
    body = io.BytesIO()
    # Stage rect
    body.write(write_rect(0, twips(width), 0, twips(height)))
    # FPS (8.8 fixed)
    body.write(struct.pack('<BB', 0, fps))
    # Frame count
    body.write(struct.pack('<H', frame_count))
    # Tags
    for t in tags:
        body.write(t)
    # ShowFrame
    body.write(build_tag(1, b''))
    # End
    body.write(build_tag(0, b''))
    
    raw = body.getvalue()
    file_length = 8 + len(raw)
    
    with open(filename, 'wb') as f:
        f.write(b'FWS')       # uncompressed
        f.write(struct.pack('<B', 10))  # version
        f.write(struct.pack('<I', file_length))
        f.write(raw)
    print(f"  Written: {filename} ({file_length} bytes)")

# ── Shape builders ──────────────────────────────────────────────

def make_solid_fill_rgb(r, g, b):
    return struct.pack('<BBBB', 0x00, r, g, b)  # type + RGB

def make_solid_fill_rgba(r, g, b, a):
    return struct.pack('<BBBBB', 0x00, r, g, b, a)  # type + RGBA

def make_line_style_rgb(width_px, r, g, b):
    return struct.pack('<HBBB', twips(width_px), r, g, b)

def make_line_style_rgba(width_px, r, g, b, a):
    return struct.pack('<HBBBB', twips(width_px), r, g, b, a)

def encode_edges_simple(fills, lines, edges, num_fill_bits, num_line_bits):
    """Encode shape records from a simple list of dicts."""
    bw = BitWriter()
    bw.write_ub(4, num_fill_bits)
    bw.write_ub(4, num_line_bits)
    
    prev_x, prev_y = 0, 0
    for rec in edges:
        if rec['type'] == 'style':
            bw.write_ub(1, 0)  # non-edge
            flags = 0
            if 'move' in rec: flags |= 0x01
            if 'fill0' in rec: flags |= 0x02
            if 'fill1' in rec: flags |= 0x04
            if 'line' in rec: flags |= 0x08
            bw.write_ub(5, flags)
            if 'move' in rec:
                mx, my = twips(rec['move'][0]), twips(rec['move'][1])
                # SWF MoveDeltaX/Y are absolute coords (not deltas)
                nb = max(nbits_signed_list([mx, my]), 1)
                bw.write_ub(5, nb)
                bw.write_sb(nb, mx)
                bw.write_sb(nb, my)
                prev_x, prev_y = mx, my
            if 'fill0' in rec:
                bw.write_ub(num_fill_bits, rec['fill0'])
            if 'fill1' in rec:
                bw.write_ub(num_fill_bits, rec['fill1'])
            if 'line' in rec:
                bw.write_ub(num_line_bits, rec['line'])
        elif rec['type'] == 'line':
            ex, ey = twips(rec['to'][0]), twips(rec['to'][1])
            dx, dy = ex - prev_x, ey - prev_y
            if dx == 0 and dy == 0:
                continue
            bw.write_ub(1, 1)  # edge
            bw.write_ub(1, 1)  # straight
            nb = max(nbits_signed_list([dx, dy]), 2) - 2
            nb = max(nb, 0)
            bw.write_ub(4, nb)
            if dx == 0:
                bw.write_ub(1, 0)  # not general
                bw.write_ub(1, 1)  # vertical
                bw.write_sb(nb + 2, dy)
            elif dy == 0:
                bw.write_ub(1, 0)
                bw.write_ub(1, 0)  # horizontal
                bw.write_sb(nb + 2, dx)
            else:
                bw.write_ub(1, 1)  # general
                bw.write_sb(nb + 2, dx)
                bw.write_sb(nb + 2, dy)
            prev_x, prev_y = ex, ey
        elif rec['type'] == 'curve':
            cx, cy = twips(rec['ctrl'][0]), twips(rec['ctrl'][1])
            ax, ay = twips(rec['anchor'][0]), twips(rec['anchor'][1])
            cdx, cdy = cx - prev_x, cy - prev_y
            adx, ady = ax - cx, ay - cy
            bw.write_ub(1, 1)  # edge
            bw.write_ub(1, 0)  # curved
            nb = max(nbits_signed_list([cdx, cdy, adx, ady]), 2) - 2
            nb = max(nb, 0)
            bw.write_ub(4, nb)
            bw.write_sb(nb + 2, cdx)
            bw.write_sb(nb + 2, cdy)
            bw.write_sb(nb + 2, adx)
            bw.write_sb(nb + 2, ady)
            prev_x, prev_y = ax, ay
    
    # EndShape
    bw.write_ub(1, 0)
    bw.write_ub(5, 0)
    return bw.get_bytes()

def build_define_shape(char_id, tag_type, xmin, ymin, xmax, ymax,
                       fill_data, line_data, num_fills, num_lines, edge_data):
    """Build a raw DefineShape tag (type 2, 22, 32, or 83)."""
    body = io.BytesIO()
    body.write(struct.pack('<H', char_id))
    body.write(write_rect(twips(xmin), twips(xmax), twips(ymin), twips(ymax)))
    
    if tag_type == 83:
        # DefineShape4: edge bounds + flags before styles
        body.write(write_rect(twips(xmin), twips(xmax), twips(ymin), twips(ymax)))
        body.write(struct.pack('<B', 0x00))  # reserved + flags (no scale/fill)
    
    # Fill style array
    if num_fills < 0xFF:
        body.write(struct.pack('<B', num_fills))
    else:
        body.write(struct.pack('<BH', 0xFF, num_fills))
    body.write(fill_data)
    
    # Line style array
    if num_lines < 0xFF:
        body.write(struct.pack('<B', num_lines))
    else:
        body.write(struct.pack('<BH', 0xFF, num_lines))
    body.write(line_data)
    
    # Shape records
    body.write(edge_data)
    
    return build_tag(tag_type, body.getvalue())

def place_object(char_id, depth):
    """PlaceObject2 tag."""
    body = struct.pack('<BHH', 0x02, depth, char_id)  # flags=HasCharacter, depth, charId
    return build_tag(26, body)

# ── Test 1: Simple rectangle with fill0 only ───────────────────

def test1_fill0_rect():
    """Rectangle using fill0 (right-side fill). Tests fill0 preservation."""
    edges = encode_edges_simple(1, 0, [
        {'type': 'style', 'move': (10, 10), 'fill0': 1},
        {'type': 'line', 'to': (90, 10)},
        {'type': 'line', 'to': (90, 90)},
        {'type': 'line', 'to': (10, 90)},
        {'type': 'line', 'to': (10, 10)},
    ], num_fill_bits=1, num_line_bits=0)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             make_solid_fill_rgb(255, 0, 0),
                             b'', 1, 0, edges)
    write_swf('test_swfs/test1_fill0_rect.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 2: Simple rectangle with fill1 only ───────────────────

def test2_fill1_rect():
    """Rectangle using fill1 (left-side fill). Tests fill1 preservation."""
    edges = encode_edges_simple(1, 0, [
        {'type': 'style', 'move': (10, 10), 'fill1': 1},
        {'type': 'line', 'to': (90, 10)},
        {'type': 'line', 'to': (90, 90)},
        {'type': 'line', 'to': (10, 90)},
        {'type': 'line', 'to': (10, 10)},
    ], num_fill_bits=1, num_line_bits=0)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             make_solid_fill_rgb(0, 255, 0),
                             b'', 1, 0, edges)
    write_swf('test_swfs/test2_fill1_rect.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 3: Two sub-paths: fill0 outer + fill1 hole ───────────

def test3_fill0_fill1_donut():
    """Outer path (fill0) with inner cutout (fill1). Tests both fills."""
    edges = encode_edges_simple(1, 0, [
        # Outer rectangle CW - fill0=1
        {'type': 'style', 'move': (10, 10), 'fill0': 1},
        {'type': 'line', 'to': (90, 10)},
        {'type': 'line', 'to': (90, 90)},
        {'type': 'line', 'to': (10, 90)},
        {'type': 'line', 'to': (10, 10)},
        # Inner rectangle CCW - fill1=1 (unfills)
        {'type': 'style', 'move': (30, 30), 'fill0': 0, 'fill1': 1},
        {'type': 'line', 'to': (30, 70)},
        {'type': 'line', 'to': (70, 70)},
        {'type': 'line', 'to': (70, 30)},
        {'type': 'line', 'to': (30, 30)},
    ], num_fill_bits=1, num_line_bits=0)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             make_solid_fill_rgb(0, 0, 255),
                             b'', 1, 0, edges)
    write_swf('test_swfs/test3_donut.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 4: Shape with stroke only ────────────────────────────

def test4_stroke_only():
    """Triangle with line style, no fill."""
    edges = encode_edges_simple(0, 1, [
        {'type': 'style', 'move': (50, 10), 'line': 1},
        {'type': 'line', 'to': (90, 90)},
        {'type': 'line', 'to': (10, 90)},
        {'type': 'line', 'to': (50, 10)},
    ], num_fill_bits=0, num_line_bits=1)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             b'',
                             make_line_style_rgb(2, 0, 0, 0),
                             0, 1, edges)
    write_swf('test_swfs/test4_stroke_only.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 5: Fill + stroke combined ─────────────────────────────

def test5_fill_and_stroke():
    """Square with red fill and black stroke. Tests fill+line combo."""
    edges = encode_edges_simple(1, 1, [
        {'type': 'style', 'move': (20, 20), 'fill1': 1, 'line': 1},
        {'type': 'line', 'to': (80, 20)},
        {'type': 'line', 'to': (80, 80)},
        {'type': 'line', 'to': (20, 80)},
        {'type': 'line', 'to': (20, 20)},
    ], num_fill_bits=1, num_line_bits=1)
    
    tag = build_define_shape(1, 2, 20, 20, 80, 80,
                             make_solid_fill_rgb(255, 0, 0),
                             make_line_style_rgb(3, 0, 0, 0),
                             1, 1, edges)
    write_swf('test_swfs/test5_fill_stroke.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 6: DefineShape3 (RGBA) rectangle ─────────────────────

def test6_shape3_rgba():
    """DefineShape3 with semi-transparent fill."""
    edges = encode_edges_simple(1, 0, [
        {'type': 'style', 'move': (10, 10), 'fill1': 1},
        {'type': 'line', 'to': (90, 10)},
        {'type': 'line', 'to': (90, 90)},
        {'type': 'line', 'to': (10, 90)},
        {'type': 'line', 'to': (10, 10)},
    ], num_fill_bits=1, num_line_bits=0)
    
    tag = build_define_shape(1, 32, 10, 10, 90, 90,
                             make_solid_fill_rgba(0, 128, 255, 128),
                             b'', 1, 0, edges)
    write_swf('test_swfs/test6_shape3_rgba.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 7: Multiple fills (2 adjacent rects) ─────────────────

def test7_two_fills():
    """Two adjacent rectangles with different fills sharing an edge."""
    fill_data = make_solid_fill_rgb(255, 0, 0) + make_solid_fill_rgb(0, 0, 255)
    edges = encode_edges_simple(2, 0, [
        # Left rect: fill1=1 (red)
        {'type': 'style', 'move': (10, 10), 'fill1': 1},
        {'type': 'line', 'to': (50, 10)},
        {'type': 'line', 'to': (50, 90)},
        {'type': 'line', 'to': (10, 90)},
        {'type': 'line', 'to': (10, 10)},
        # Right rect: fill1=2 (blue)
        {'type': 'style', 'move': (50, 10), 'fill1': 2},
        {'type': 'line', 'to': (90, 10)},
        {'type': 'line', 'to': (90, 90)},
        {'type': 'line', 'to': (50, 90)},
        {'type': 'line', 'to': (50, 10)},
    ], num_fill_bits=2, num_line_bits=0)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             fill_data,
                             b'', 2, 0, edges)
    write_swf('test_swfs/test7_two_fills.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 8: Shared edge with fill0+fill1 ──────────────────────

def test8_shared_edge():
    """Two rects sharing an edge using fill0+fill1 on the shared edge."""
    fill_data = make_solid_fill_rgb(255, 0, 0) + make_solid_fill_rgb(0, 0, 255)
    edges = encode_edges_simple(2, 0, [
        # Top edge of left rect
        {'type': 'style', 'move': (10, 10), 'fill1': 1},
        {'type': 'line', 'to': (50, 10)},
        # Shared edge: fill0=1 (red on right), fill1=2 (blue on left)
        {'type': 'style', 'fill0': 1, 'fill1': 2},
        {'type': 'line', 'to': (50, 90)},
        # Bottom of right rect
        {'type': 'style', 'fill0': 0, 'fill1': 2},
        {'type': 'line', 'to': (90, 90)},
        # Right side
        {'type': 'line', 'to': (90, 10)},
        {'type': 'line', 'to': (50, 10)},
        # Bottom-left
        {'type': 'style', 'move': (50, 90), 'fill0': 0, 'fill1': 1},
        {'type': 'line', 'to': (10, 90)},
        {'type': 'line', 'to': (10, 10)},
    ], num_fill_bits=2, num_line_bits=0)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             fill_data,
                             b'', 2, 0, edges)
    write_swf('test_swfs/test8_shared_edge.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 9: Curve shape (circle approximation) ────────────────

def test9_circle():
    """Circle approximation using curves with fill0."""
    r = 40
    cx, cy = 50, 50
    # 4-point bezier circle approximation
    k = 0.5522847498  # magic number for cubic->quad approx
    # Using quadratic beziers (SWF native)
    edges = encode_edges_simple(1, 0, [
        {'type': 'style', 'move': (cx, cy - r), 'fill0': 1},
        # Top-right quadrant
        {'type': 'curve', 'ctrl': (cx + r, cy - r), 'anchor': (cx + r, cy)},
        # Bottom-right
        {'type': 'curve', 'ctrl': (cx + r, cy + r), 'anchor': (cx, cy + r)},
        # Bottom-left
        {'type': 'curve', 'ctrl': (cx - r, cy + r), 'anchor': (cx - r, cy)},
        # Top-left
        {'type': 'curve', 'ctrl': (cx - r, cy - r), 'anchor': (cx, cy - r)},
    ], num_fill_bits=1, num_line_bits=0)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             make_solid_fill_rgb(255, 128, 0),
                             b'', 1, 0, edges)
    write_swf('test_swfs/test9_circle.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 10: Simple DefineMorphShape ───────────────────────────

def test10_morph_shape():
    """Simple morph: rectangle morphing to smaller rectangle."""
    body = io.BytesIO()
    body.write(struct.pack('<H', 1))  # charId
    
    # Start bounds
    body.write(write_rect(twips(10), twips(90), twips(10), twips(90)))
    # End bounds
    body.write(write_rect(twips(30), twips(70), twips(30), twips(70)))
    
    # Build start shape + end shape
    start_shape = io.BytesIO()
    end_shape = io.BytesIO()
    
    # Start fill styles
    start_shape.write(struct.pack('<B', 1))  # 1 fill
    start_shape.write(struct.pack('<B', 0x00))  # solid
    start_shape.write(struct.pack('<BBBB', 255, 0, 0, 255))  # start RGBA
    start_shape.write(struct.pack('<BBBB', 0, 0, 255, 255))  # end RGBA
    
    # Start line styles
    start_shape.write(struct.pack('<B', 0))  # no lines
    
    # Start shape records
    bw = BitWriter()
    bw.write_ub(4, 1)  # nFillBits
    bw.write_ub(4, 0)  # nLineBits
    # StyleChange: move + fill1
    bw.write_ub(1, 0); bw.write_ub(5, 0x05)  # move + fill1
    nb = nbits_signed_list([twips(10), twips(10)])
    bw.write_ub(5, nb)
    bw.write_sb(nb, twips(10))
    bw.write_sb(nb, twips(10))
    bw.write_ub(1, 1)  # fill1=1
    # Straight edges CW
    for (dx, dy) in [(80, 0), (0, 80), (-80, 0), (0, -80)]:
        bw.write_ub(1, 1)  # edge
        bw.write_ub(1, 1)  # straight
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw.write_ub(4, nbe)
        if dxt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 1)
            bw.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 0)
            bw.write_sb(nbe + 2, dxt)
        else:
            bw.write_ub(1, 1)
            bw.write_sb(nbe + 2, dxt)
            bw.write_sb(nbe + 2, dyt)
    bw.write_ub(1, 0); bw.write_ub(5, 0)  # EndShape
    start_shape.write(bw.get_bytes())
    
    # Offset (distance from after offset field to end edges)
    start_data = start_shape.getvalue()
    
    # End shape records (geometry only, no styles)
    bw2 = BitWriter()
    bw2.write_ub(4, 0)  # nFillBits=0 (end state has no style refs)
    bw2.write_ub(4, 0)  # nLineBits=0
    # StyleChange: move
    bw2.write_ub(1, 0); bw2.write_ub(5, 0x01)  # move only
    nb2 = nbits_signed_list([twips(30), twips(30)])
    bw2.write_ub(5, nb2)
    bw2.write_sb(nb2, twips(30))
    bw2.write_sb(nb2, twips(30))
    # Edges: smaller rectangle
    for (dx, dy) in [(40, 0), (0, 40), (-40, 0), (0, -40)]:
        bw2.write_ub(1, 1)
        bw2.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw2.write_ub(4, nbe)
        if dxt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 1)
            bw2.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 0)
            bw2.write_sb(nbe + 2, dxt)
        else:
            bw2.write_ub(1, 1)
            bw2.write_sb(nbe + 2, dxt)
            bw2.write_sb(nbe + 2, dyt)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0)  # EndShape
    end_data = bw2.get_bytes()
    
    # Full morph body: charId + startBounds + endBounds + offset + start + end
    full_body = io.BytesIO()
    full_body.write(struct.pack('<H', 1))  # charId
    full_body.write(write_rect(twips(10), twips(90), twips(10), twips(90)))
    full_body.write(write_rect(twips(30), twips(70), twips(30), twips(70)))
    
    # Offset = byte length of start shape data
    full_body.write(struct.pack('<I', len(start_data)))
    full_body.write(start_data)
    full_body.write(end_data)
    
    tag = build_tag(46, full_body.getvalue())  # DefineMorphShape
    write_swf('test_swfs/test10_morph.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 11: Multiple disconnected sub-paths same fill ─────────

def test11_multi_subpath():
    """Two separate triangles with same fill. Tests sub-path handling."""
    edges = encode_edges_simple(1, 0, [
        # Triangle 1
        {'type': 'style', 'move': (20, 10), 'fill0': 1},
        {'type': 'line', 'to': (40, 40)},
        {'type': 'line', 'to': (10, 40)},
        {'type': 'line', 'to': (20, 10)},
        # Triangle 2 - separate sub-path, same fill
        {'type': 'style', 'move': (60, 60), 'fill0': 1},
        {'type': 'line', 'to': (90, 90)},
        {'type': 'line', 'to': (60, 90)},
        {'type': 'line', 'to': (60, 60)},
    ], num_fill_bits=1, num_line_bits=0)
    
    tag = build_define_shape(1, 2, 10, 10, 90, 90,
                             make_solid_fill_rgb(128, 0, 128),
                             b'', 1, 0, edges)
    write_swf('test_swfs/test11_multi_subpath.swf',
              [tag, place_object(1, 1)],
              width=100, height=100)

# ── Test 12: Morph with fill0 (left-side fill) ────────────────
def test12_morph_fill0():
    """Morph using fill0 instead of fill1. Tests fill_merge reversal on import."""
    start_shape = io.BytesIO()
    start_shape.write(struct.pack('<B', 1))  # 1 fill
    start_shape.write(struct.pack('<B', 0x00))  # solid
    start_shape.write(struct.pack('<BBBB', 0, 200, 0, 255))  # start green
    start_shape.write(struct.pack('<BBBB', 200, 200, 0, 255))  # end yellow
    start_shape.write(struct.pack('<B', 0))  # no lines

    bw = BitWriter()
    bw.write_ub(4, 1); bw.write_ub(4, 0)
    # StyleChange: move + fill0 (flag 0x03) — CCW winding
    bw.write_ub(1, 0); bw.write_ub(5, 0x03)
    nb = nbits_signed_list([twips(10), twips(10)])
    bw.write_ub(5, nb)
    bw.write_sb(nb, twips(10)); bw.write_sb(nb, twips(10))
    bw.write_ub(1, 1)  # fill0=1
    # CCW rectangle (fill0 = left side = inside for CCW)
    for (dx, dy) in [(0, 80), (80, 0), (0, -80), (-80, 0)]:
        bw.write_ub(1, 1); bw.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw.write_ub(4, nbe)
        if dxt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 1); bw.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 0); bw.write_sb(nbe + 2, dxt)
        else:
            bw.write_ub(1, 1); bw.write_sb(nbe + 2, dxt); bw.write_sb(nbe + 2, dyt)
    bw.write_ub(1, 0); bw.write_ub(5, 0)
    start_shape.write(bw.get_bytes())
    start_data = start_shape.getvalue()

    bw2 = BitWriter()
    bw2.write_ub(4, 0); bw2.write_ub(4, 0)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0x01)
    nb2 = nbits_signed_list([twips(20), twips(20)])
    bw2.write_ub(5, nb2)
    bw2.write_sb(nb2, twips(20)); bw2.write_sb(nb2, twips(20))
    for (dx, dy) in [(0, 60), (60, 0), (0, -60), (-60, 0)]:
        bw2.write_ub(1, 1); bw2.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw2.write_ub(4, nbe)
        if dxt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 0); bw2.write_sb(nbe + 2, dxt)
        else:
            bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dxt); bw2.write_sb(nbe + 2, dyt)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0)
    end_data = bw2.get_bytes()

    full = io.BytesIO()
    full.write(struct.pack('<H', 1))
    full.write(write_rect(twips(10), twips(90), twips(10), twips(90)))
    full.write(write_rect(twips(20), twips(80), twips(20), twips(80)))
    full.write(struct.pack('<I', len(start_data)))
    full.write(start_data)
    full.write(end_data)
    tag = build_tag(46, full.getvalue())
    write_swf('test_swfs/test12_morph_fill0.swf', [tag, place_object(1, 1)], width=100, height=100)


# ── Test 13: Morph with stroke only ───────────────────────────
def test13_morph_stroke():
    """Morph with line style only (no fill). Tests line roundtrip."""
    start_shape = io.BytesIO()
    start_shape.write(struct.pack('<B', 0))  # 0 fills
    start_shape.write(struct.pack('<B', 1))  # 1 line
    start_shape.write(struct.pack('<H', twips(3)))  # start width
    start_shape.write(struct.pack('<H', twips(1)))  # end width
    start_shape.write(struct.pack('<BBBB', 255, 0, 0, 255))  # start RGBA
    start_shape.write(struct.pack('<BBBB', 0, 255, 0, 255))  # end RGBA

    bw = BitWriter()
    bw.write_ub(4, 0); bw.write_ub(4, 1)
    bw.write_ub(1, 0); bw.write_ub(5, 0x09)  # move + line
    nb = nbits_signed_list([twips(10), twips(10)])
    bw.write_ub(5, nb)
    bw.write_sb(nb, twips(10)); bw.write_sb(nb, twips(10))
    bw.write_ub(1, 1)  # line=1
    for (dx, dy) in [(80, 0), (0, 80), (-80, 0), (0, -80)]:
        bw.write_ub(1, 1); bw.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw.write_ub(4, nbe)
        if dxt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 1); bw.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 0); bw.write_sb(nbe + 2, dxt)
        else:
            bw.write_ub(1, 1); bw.write_sb(nbe + 2, dxt); bw.write_sb(nbe + 2, dyt)
    bw.write_ub(1, 0); bw.write_ub(5, 0)
    start_shape.write(bw.get_bytes())
    start_data = start_shape.getvalue()

    bw2 = BitWriter()
    bw2.write_ub(4, 0); bw2.write_ub(4, 0)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0x01)
    nb2 = nbits_signed_list([twips(30), twips(30)])
    bw2.write_ub(5, nb2)
    bw2.write_sb(nb2, twips(30)); bw2.write_sb(nb2, twips(30))
    for (dx, dy) in [(40, 0), (0, 40), (-40, 0), (0, -40)]:
        bw2.write_ub(1, 1); bw2.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw2.write_ub(4, nbe)
        if dxt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 0); bw2.write_sb(nbe + 2, dxt)
        else:
            bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dxt); bw2.write_sb(nbe + 2, dyt)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0)
    end_data = bw2.get_bytes()

    full = io.BytesIO()
    full.write(struct.pack('<H', 1))
    full.write(write_rect(twips(5), twips(95), twips(5), twips(95)))
    full.write(write_rect(twips(25), twips(75), twips(25), twips(75)))
    full.write(struct.pack('<I', len(start_data)))
    full.write(start_data)
    full.write(end_data)
    tag = build_tag(46, full.getvalue())
    write_swf('test_swfs/test13_morph_stroke.swf', [tag, place_object(1, 1)], width=100, height=100)


# ── Test 14: Morph with fill AND stroke ────────────────────────
def test14_morph_fill_stroke():
    """Morph with both fill and stroke. Tests combined fill/line handling."""
    start_shape = io.BytesIO()
    start_shape.write(struct.pack('<B', 1))  # 1 fill
    start_shape.write(struct.pack('<B', 0x00))  # solid
    start_shape.write(struct.pack('<BBBB', 100, 100, 255, 255))  # start blue
    start_shape.write(struct.pack('<BBBB', 255, 100, 100, 255))  # end red
    start_shape.write(struct.pack('<B', 1))  # 1 line
    start_shape.write(struct.pack('<H', twips(2)))  # start width
    start_shape.write(struct.pack('<H', twips(4)))  # end width
    start_shape.write(struct.pack('<BBBB', 0, 0, 0, 255))  # start black
    start_shape.write(struct.pack('<BBBB', 255, 255, 0, 255))  # end yellow

    bw = BitWriter()
    bw.write_ub(4, 1); bw.write_ub(4, 1)
    bw.write_ub(1, 0); bw.write_ub(5, 0x0D)  # move + fill1 + line
    nb = nbits_signed_list([twips(10), twips(10)])
    bw.write_ub(5, nb)
    bw.write_sb(nb, twips(10)); bw.write_sb(nb, twips(10))
    bw.write_ub(1, 1)  # fill1=1
    bw.write_ub(1, 1)  # line=1
    for (dx, dy) in [(80, 0), (0, 80), (-80, 0), (0, -80)]:
        bw.write_ub(1, 1); bw.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw.write_ub(4, nbe)
        if dxt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 1); bw.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 0); bw.write_sb(nbe + 2, dxt)
        else:
            bw.write_ub(1, 1); bw.write_sb(nbe + 2, dxt); bw.write_sb(nbe + 2, dyt)
    bw.write_ub(1, 0); bw.write_ub(5, 0)
    start_shape.write(bw.get_bytes())
    start_data = start_shape.getvalue()

    bw2 = BitWriter()
    bw2.write_ub(4, 0); bw2.write_ub(4, 0)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0x01)
    nb2 = nbits_signed_list([twips(20), twips(20)])
    bw2.write_ub(5, nb2)
    bw2.write_sb(nb2, twips(20)); bw2.write_sb(nb2, twips(20))
    for (dx, dy) in [(60, 0), (0, 60), (-60, 0), (0, -60)]:
        bw2.write_ub(1, 1); bw2.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw2.write_ub(4, nbe)
        if dxt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 0); bw2.write_sb(nbe + 2, dxt)
        else:
            bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dxt); bw2.write_sb(nbe + 2, dyt)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0)
    end_data = bw2.get_bytes()

    full = io.BytesIO()
    full.write(struct.pack('<H', 1))
    full.write(write_rect(twips(10), twips(90), twips(10), twips(90)))
    full.write(write_rect(twips(20), twips(80), twips(20), twips(80)))
    full.write(struct.pack('<I', len(start_data)))
    full.write(start_data)
    full.write(end_data)
    tag = build_tag(46, full.getvalue())
    write_swf('test_swfs/test14_morph_fill_stroke.swf', [tag, place_object(1, 1)], width=100, height=100)


# ── Test 15: DefineMorphShape2 (tag 84) ───────────────────────
def test15_morph_shape2():
    """DefineMorphShape2 with edge bounds."""
    full = io.BytesIO()
    full.write(struct.pack('<H', 1))
    full.write(write_rect(twips(10), twips(90), twips(10), twips(90)))  # StartBounds
    full.write(write_rect(twips(30), twips(70), twips(30), twips(70)))  # EndBounds
    full.write(write_rect(twips(10), twips(90), twips(10), twips(90)))  # StartEdgeBounds
    full.write(write_rect(twips(30), twips(70), twips(30), twips(70)))  # EndEdgeBounds
    full.write(struct.pack('<B', 0x02))  # flags: UsesScalingStrokes

    offset_block = io.BytesIO()
    offset_block.write(struct.pack('<B', 1))  # 1 fill
    offset_block.write(struct.pack('<B', 0x00))  # solid
    offset_block.write(struct.pack('<BBBB', 255, 128, 0, 255))  # start orange
    offset_block.write(struct.pack('<BBBB', 0, 128, 255, 255))  # end cyan
    offset_block.write(struct.pack('<B', 0))  # 0 lines

    bw = BitWriter()
    bw.write_ub(4, 1); bw.write_ub(4, 0)
    bw.write_ub(1, 0); bw.write_ub(5, 0x05)  # move + fill1
    nb = nbits_signed_list([twips(10), twips(10)])
    bw.write_ub(5, nb)
    bw.write_sb(nb, twips(10)); bw.write_sb(nb, twips(10))
    bw.write_ub(1, 1)  # fill1=1
    for (dx, dy) in [(80, 0), (0, 80), (-80, 0), (0, -80)]:
        bw.write_ub(1, 1); bw.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw.write_ub(4, nbe)
        if dxt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 1); bw.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw.write_ub(1, 0); bw.write_ub(1, 0); bw.write_sb(nbe + 2, dxt)
        else:
            bw.write_ub(1, 1); bw.write_sb(nbe + 2, dxt); bw.write_sb(nbe + 2, dyt)
    bw.write_ub(1, 0); bw.write_ub(5, 0)
    offset_block.write(bw.get_bytes())
    offset_data = offset_block.getvalue()

    full.write(struct.pack('<I', len(offset_data)))
    full.write(offset_data)

    bw2 = BitWriter()
    bw2.write_ub(4, 0); bw2.write_ub(4, 0)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0x01)
    nb2 = nbits_signed_list([twips(30), twips(30)])
    bw2.write_ub(5, nb2)
    bw2.write_sb(nb2, twips(30)); bw2.write_sb(nb2, twips(30))
    for (dx, dy) in [(40, 0), (0, 40), (-40, 0), (0, -40)]:
        bw2.write_ub(1, 1); bw2.write_ub(1, 1)
        dxt, dyt = twips(dx), twips(dy)
        nbe = max(nbits_signed_list([dxt, dyt]), 2) - 2
        bw2.write_ub(4, nbe)
        if dxt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dyt)
        elif dyt == 0:
            bw2.write_ub(1, 0); bw2.write_ub(1, 0); bw2.write_sb(nbe + 2, dxt)
        else:
            bw2.write_ub(1, 1); bw2.write_sb(nbe + 2, dxt); bw2.write_sb(nbe + 2, dyt)
    bw2.write_ub(1, 0); bw2.write_ub(5, 0)
    full.write(bw2.get_bytes())

    tag = build_tag(84, full.getvalue())
    write_swf('test_swfs/test15_morph_shape2.swf', [tag, place_object(1, 1)], width=100, height=100)


# ── Test 16: Morph with many-sided polygon ────────────────────
def test16_morph_polygon():
    """Morph polygon (8-gon → smaller 8-gon). Tests multi-edge morphs."""
    import math

    def polygon_pts(cx, cy, r, n=8):
        return [(cx + r * math.cos(2*math.pi*i/n), cy + r * math.sin(2*math.pi*i/n)) for i in range(n)]

    start_pts = polygon_pts(50, 50, 40, 8)
    end_pts = polygon_pts(50, 50, 20, 8)

    def build_polygon_edges(pts, fill_bits, line_bits, with_fill1=True):
        bw = BitWriter()
        bw.write_ub(4, fill_bits); bw.write_ub(4, line_bits)
        flags = 0x01  # move
        if with_fill1: flags |= 0x04
        bw.write_ub(1, 0); bw.write_ub(5, flags)
        sx, sy = twips(pts[0][0]), twips(pts[0][1])
        nb = nbits_signed_list([sx, sy])
        bw.write_ub(5, nb)
        bw.write_sb(nb, sx); bw.write_sb(nb, sy)
        if with_fill1:
            bw.write_ub(fill_bits, 1)
        # Edges
        prev = (twips(pts[0][0]), twips(pts[0][1]))
        all_pts = list(pts[1:]) + [pts[0]]
        for p in all_pts:
            px, py = twips(p[0]), twips(p[1])
            dx, dy = px - prev[0], py - prev[1]
            if dx == 0 and dy == 0: continue
            bw.write_ub(1, 1); bw.write_ub(1, 1)
            nbe = max(nbits_signed_list([dx, dy]), 2) - 2
            bw.write_ub(4, nbe)
            if dx == 0:
                bw.write_ub(1, 0); bw.write_ub(1, 1); bw.write_sb(nbe + 2, dy)
            elif dy == 0:
                bw.write_ub(1, 0); bw.write_ub(1, 0); bw.write_sb(nbe + 2, dx)
            else:
                bw.write_ub(1, 1); bw.write_sb(nbe + 2, dx); bw.write_sb(nbe + 2, dy)
            prev = (px, py)
        bw.write_ub(1, 0); bw.write_ub(5, 0)
        return bw.get_bytes()

    start_shape = io.BytesIO()
    start_shape.write(struct.pack('<B', 1))  # 1 fill
    start_shape.write(struct.pack('<B', 0x00))
    start_shape.write(struct.pack('<BBBB', 128, 0, 255, 255))  # purple
    start_shape.write(struct.pack('<BBBB', 0, 255, 128, 255))  # mint
    start_shape.write(struct.pack('<B', 0))  # no lines
    start_shape.write(build_polygon_edges(start_pts, 1, 0, True))
    start_data = start_shape.getvalue()

    end_data = build_polygon_edges(end_pts, 0, 0, False)

    full = io.BytesIO()
    full.write(struct.pack('<H', 1))
    full.write(write_rect(twips(10), twips(90), twips(10), twips(90)))
    full.write(write_rect(twips(30), twips(70), twips(30), twips(70)))
    full.write(struct.pack('<I', len(start_data)))
    full.write(start_data)
    full.write(end_data)
    tag = build_tag(46, full.getvalue())
    write_swf('test_swfs/test16_morph_polygon.swf', [tag, place_object(1, 1)], width=100, height=100)


# ── Main ────────────────────────────────────────────────────────

import os
os.makedirs('test_swfs', exist_ok=True)

print("Generating test SWFs...")
test1_fill0_rect()
test2_fill1_rect()
test3_fill0_fill1_donut()
test4_stroke_only()
test5_fill_and_stroke()
test6_shape3_rgba()
test7_two_fills()
test8_shared_edge()
test9_circle()
test10_morph_shape()
test11_multi_subpath()
test12_morph_fill0()
test13_morph_stroke()
test14_morph_fill_stroke()
test15_morph_shape2()
test16_morph_polygon()
print("Done!")
