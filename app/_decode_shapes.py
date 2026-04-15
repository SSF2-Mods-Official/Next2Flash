"""
Decode the structure of specific shape tags from original and roundtrip SWFs.
Shows fill styles, line styles, and edge records in human-readable form.
"""
import struct, sys, os, io

ORIG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
RT   = r"test_swfs\lloyd_rt.swf"
TARGET_CIDS = [183, 185, 188, 306]

SHAPE_TAG_IDS = {2, 22, 32, 83}

def read_swf_data(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        import zlib
        data = data[:8] + zlib.decompress(data[8:])
    elif data[:3] == b'ZWS':
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    return data

def parse_tags(data):
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4
    tags = []
    while pos < len(data) - 1:
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        cid = None
        if tag_type in SHAPE_TAG_IDS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
        tags.append((tag_type, cid, body))
        pos += length
        if tag_type == 0:
            break
    return tags

class BitReader:
    def __init__(self, data, byte_offset=0):
        self.data = data
        self.pos = byte_offset * 8  # bit position

    def read_ub(self, n):
        result = 0
        for _ in range(n):
            byte_idx = self.pos >> 3
            bit_idx = 7 - (self.pos & 7)
            if byte_idx < len(self.data):
                result = (result << 1) | ((self.data[byte_idx] >> bit_idx) & 1)
            self.pos += 1
        return result

    def read_sb(self, n):
        val = self.read_ub(n)
        if n > 0 and val & (1 << (n - 1)):
            val -= (1 << n)
        return val

    def read_ui8(self):
        self.align()
        byte_idx = self.pos >> 3
        val = self.data[byte_idx]
        self.pos += 8
        return val

    def read_ui16(self):
        self.align()
        byte_idx = self.pos >> 3
        val = struct.unpack_from('<H', self.data, byte_idx)[0]
        self.pos += 16
        return val

    def align(self):
        if self.pos & 7:
            self.pos = ((self.pos >> 3) + 1) << 3

    @property
    def byte_offset(self):
        return self.pos >> 3

def read_rect(br):
    nbits = br.read_ub(5)
    xmin = br.read_sb(nbits) / 20.0
    xmax = br.read_sb(nbits) / 20.0
    ymin = br.read_sb(nbits) / 20.0
    ymax = br.read_sb(nbits) / 20.0
    return {"xMin": xmin, "xMax": xmax, "yMin": ymin, "yMax": ymax}

def read_matrix(br):
    has_scale = br.read_ub(1)
    sx, sy = 1.0, 1.0
    if has_scale:
        nbits = br.read_ub(5)
        sx = br.read_sb(nbits) / 65536.0
        sy = br.read_sb(nbits) / 65536.0
    has_rotate = br.read_ub(1)
    r0, r1 = 0.0, 0.0
    if has_rotate:
        nbits = br.read_ub(5)
        r0 = br.read_sb(nbits) / 65536.0
        r1 = br.read_sb(nbits) / 65536.0
    has_translate = br.read_ub(1)
    tx, ty = 0, 0
    if has_translate:
        nbits = br.read_ub(5)
        tx = br.read_sb(nbits) / 20.0
        ty = br.read_sb(nbits) / 20.0
    return {"sx": sx, "sy": sy, "r0": r0, "r1": r1, "tx": tx, "ty": ty}

def read_rgb(br):
    r = br.read_ui8()
    g = br.read_ui8()
    b = br.read_ui8()
    return (r, g, b, 255)

def read_rgba(br):
    r = br.read_ui8()
    g = br.read_ui8()
    b = br.read_ui8()
    a = br.read_ui8()
    return (r, g, b, a)

def read_fill_style(br, version):
    ft = br.read_ui8()
    if ft == 0x00:
        color = read_rgba(br) if version >= 3 else read_rgb(br)
        return {"type": "solid", "color": color}
    elif ft in (0x10, 0x12, 0x13):
        mtx = read_matrix(br)
        br.align()
        # Read gradient
        num_stops = br.read_ui8()
        stops = []
        for _ in range(num_stops):
            ratio = br.read_ui8()
            color = read_rgba(br) if version >= 3 else read_rgb(br)
            stops.append({"ratio": ratio, "color": color})
        if ft == 0x13:
            focal = br.read_sb(16) / 256.0
            return {"type": f"gradient_0x{ft:02x}", "matrix": mtx, "stops": stops, "focal": focal}
        return {"type": f"gradient_0x{ft:02x}", "matrix": mtx, "stops": stops}
    elif ft in (0x40, 0x41, 0x42, 0x43):
        bitmap_id = br.read_ui16()
        mtx = read_matrix(br)
        repeat = "repeat" if ft in (0x40, 0x42) else "no-repeat"
        smooth = ft in (0x40, 0x41)
        return {"type": "bitmap", "bitmapId": bitmap_id, "matrix": mtx, "repeat": repeat, "smooth": smooth, "fillType": f"0x{ft:02x}"}
    else:
        return {"type": f"unknown_0x{ft:02x}"}

def read_line_style(br, version):
    width = br.read_ui16() / 20.0
    if version == 4:
        # DefineShape4 LINESTYLE2
        br.read_ub(2)  # StartCapStyle
        join = br.read_ub(2)
        has_fill = br.read_ub(1)
        br.read_ub(1)  # NoHScaleFlag
        br.read_ub(1)  # NoVScaleFlag
        br.read_ub(1)  # PixelHintingFlag
        br.read_ub(5)  # Reserved
        br.read_ub(1)  # NoClose
        br.read_ub(2)  # EndCapStyle
        if join == 2:
            br.read_ui16()  # MiterLimitFactor
        if has_fill:
            fill = read_fill_style(br, version)
            return {"width": width, "fill": fill}
        else:
            color = read_rgba(br)
            return {"width": width, "color": color}
    else:
        if version >= 3:
            color = read_rgba(br)
        else:
            color = read_rgb(br)
        return {"width": width, "color": color}

def decode_shape(tag_type, body, f):
    version = {2: 1, 22: 2, 32: 3, 83: 4}.get(tag_type, 3)
    cid = struct.unpack_from('<H', body, 0)[0]

    br = BitReader(body, 2)
    bounds = read_rect(br)
    br.align()

    f.write(f"  CharID: {cid}\n")
    f.write(f"  Tag: {tag_type}, Version: {version}\n")
    f.write(f"  Bounds: {bounds}\n")

    if tag_type == 83:
        edge_bounds = read_rect(br)
        br.align()
        flags = br.read_ui8()
        f.write(f"  EdgeBounds: {edge_bounds}\n")
        f.write(f"  Flags: 0x{flags:02x}\n")

    # Fill style array
    n_fills = br.read_ui8()
    if n_fills == 0xFF and version >= 2:
        n_fills = br.read_ui16()
    f.write(f"  FillStyles ({n_fills}):\n")
    fills = []
    for i in range(n_fills):
        fill = read_fill_style(br, version)
        fills.append(fill)
        f.write(f"    [{i+1}] {fill}\n")

    # Line style array
    br.align()
    n_lines = br.read_ui8()
    if n_lines == 0xFF and version >= 2:
        n_lines = br.read_ui16()
    f.write(f"  LineStyles ({n_lines}):\n")
    for i in range(n_lines):
        line = read_line_style(br, version)
        f.write(f"    [{i+1}] {line}\n")

    # Shape records
    num_fill_bits = br.read_ub(4)
    num_line_bits = br.read_ub(4)
    f.write(f"  NumFillBits={num_fill_bits}, NumLineBits={num_line_bits}\n")
    f.write(f"  Shape Records:\n")

    cur_x, cur_y = 0, 0
    rec_count = 0
    max_recs = 100  # safety limit

    while rec_count < max_recs:
        type_flag = br.read_ub(1)
        if type_flag == 0:
            # Non-edge record
            flags = br.read_ub(5)
            if flags == 0:
                f.write(f"    EndShape\n")
                break
            has_new_styles = (flags >> 4) & 1
            has_line = (flags >> 3) & 1
            has_fill1 = (flags >> 2) & 1
            has_fill0 = (flags >> 1) & 1
            has_move = flags & 1

            parts = []
            if has_move:
                move_bits = br.read_ub(5)
                mx = br.read_sb(move_bits) / 20.0
                my = br.read_sb(move_bits) / 20.0
                cur_x, cur_y = mx, my
                parts.append(f"move=({mx:.2f},{my:.2f})")
            if has_fill0:
                f0 = br.read_ub(num_fill_bits)
                parts.append(f"fill0={f0}")
            if has_fill1:
                f1 = br.read_ub(num_fill_bits)
                parts.append(f"fill1={f1}")
            if has_line:
                ls = br.read_ub(num_line_bits)
                parts.append(f"line={ls}")
            if has_new_styles:
                # Read new style arrays (only in DefineShape2+)
                new_n_fills = br.read_ui8()
                if new_n_fills == 0xFF and version >= 2:
                    new_n_fills = br.read_ui16()
                for _ in range(new_n_fills):
                    read_fill_style(br, version)
                br.align()
                new_n_lines = br.read_ui8()
                if new_n_lines == 0xFF and version >= 2:
                    new_n_lines = br.read_ui16()
                for _ in range(new_n_lines):
                    read_line_style(br, version)
                num_fill_bits = br.read_ub(4)
                num_line_bits = br.read_ub(4)
                parts.append(f"newStyles(fills={new_n_fills},lines={new_n_lines})")

            f.write(f"    StyleChange: {' '.join(parts)}\n")
        else:
            # Edge record
            straight = br.read_ub(1)
            if straight:
                nbits = br.read_ub(4) + 2
                general_line = br.read_ub(1)
                if general_line:
                    dx = br.read_sb(nbits) / 20.0
                    dy = br.read_sb(nbits) / 20.0
                else:
                    vert = br.read_ub(1)
                    if vert:
                        dx = 0
                        dy = br.read_sb(nbits) / 20.0
                    else:
                        dx = br.read_sb(nbits) / 20.0
                        dy = 0
                cur_x += dx
                cur_y += dy
                f.write(f"    Line: dx={dx:.2f} dy={dy:.2f} → ({cur_x:.2f},{cur_y:.2f})\n")
            else:
                nbits = br.read_ub(4) + 2
                cx = br.read_sb(nbits) / 20.0
                cy = br.read_sb(nbits) / 20.0
                ax = br.read_sb(nbits) / 20.0
                ay = br.read_sb(nbits) / 20.0
                cur_x += cx + ax
                cur_y += cy + ay
                f.write(f"    Curve: ctrl=({cx:.2f},{cy:.2f}) anc=({ax:.2f},{ay:.2f}) → ({cur_x:.2f},{cur_y:.2f})\n")
        rec_count += 1

    return bounds, fills

# --- Main ---
f = open("_shape_decode_output.txt", 'w', encoding='utf-8')

orig_data = read_swf_data(ORIG)
orig_tags = parse_tags(orig_data)
orig_shapes = {}
for tag_type, cid, body in orig_tags:
    if tag_type in SHAPE_TAG_IDS and cid is not None:
        if cid not in orig_shapes:
            orig_shapes[cid] = (tag_type, body)

for cid in TARGET_CIDS:
    f.write(f"\n{'='*70}\n")
    f.write(f"  ORIGINAL SHAPE CID {cid}\n")
    f.write(f"{'='*70}\n\n")
    if cid in orig_shapes:
        tag_type, body = orig_shapes[cid]
        try:
            decode_shape(tag_type, body, f)
        except Exception as e:
            import traceback
            f.write(f"  DECODE ERROR: {e}\n")
            traceback.print_exc(file=f)
    else:
        f.write("  NOT FOUND\n")

f.close()
print(f"Done. Output: _shape_decode_output.txt ({os.path.getsize('_shape_decode_output.txt')} bytes)")
