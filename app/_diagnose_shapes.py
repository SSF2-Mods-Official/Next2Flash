"""
Diagnose specific shape differences between original and roundtrip SWF.
Compares shapes 306, 183, 185, 188.
Outputs to _diagnose_shapes_output.txt
"""
import struct, sys, os, io

ORIG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
RT   = r"test_swfs\lloyd_rt.swf"
OUT  = "_diagnose_shapes_output.txt"
TARGET_CIDS = {306, 183, 185, 188}

SHAPE_TAGS = {2, 22, 32, 46, 83}  # DefineShape, DefineShape2, DefineShape3, DefineMorphShape, DefineShape4

def read_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        if sig in (b'CWS', b'FWS', b'ZWS'):
            f.seek(0)
            data = f.read()
        else:
            f.seek(0)
            data = f.read()
    if data[:3] == b'CWS':
        import zlib
        header = data[:8]
        rest = zlib.decompress(data[8:])
        data = data[:3] + data[3:8] + rest
    elif data[:3] == b'ZWS':
        import lzma
        header = data[:8]
        rest = lzma.decompress(data[12:])
        data = data[:3] + data[3:8] + rest
    return data

def parse_tags(data):
    """Parse SWF tags, return list of (tag_type, char_id_or_none, offset, length, raw_body)"""
    # Skip header: signature(3) + version(1) + fileLength(4)
    pos = 8
    # Parse RECT to find its end
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes
    # FrameRate(2) + FrameCount(2)
    pos += 4

    tags = []
    while pos < len(data):
        if pos + 2 > len(data):
            break
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        pos += 2
        if length == 0x3F:
            if pos + 4 > len(data):
                break
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        char_id = None
        if tag_type in SHAPE_TAGS and len(body) >= 2:
            char_id = struct.unpack_from('<H', body, 0)[0]
        tags.append((tag_type, char_id, pos, length, body))
        pos += length
        if tag_type == 0:
            break
    return tags

class BitReader:
    def __init__(self, data, byte_offset=0):
        self.data = data
        self.byte_pos = byte_offset
        self.bit_pos = 0

    def read_ub(self, n):
        result = 0
        for _ in range(n):
            byte_idx = self.byte_pos + (self.bit_pos >> 3)
            bit_idx = 7 - (self.bit_pos & 7)
            if byte_idx < len(self.data):
                result = (result << 1) | ((self.data[byte_idx] >> bit_idx) & 1)
            else:
                result = (result << 1)
            self.bit_pos += 1
        return result

    def read_sb(self, n):
        val = self.read_ub(n)
        if n > 0 and val & (1 << (n - 1)):
            val -= (1 << n)
        return val

    def align(self):
        if self.bit_pos & 7:
            self.bit_pos = (self.bit_pos + 7) & ~7

    @property
    def abs_bit_pos(self):
        return self.byte_pos * 8 + self.bit_pos

def parse_rect(br):
    nbits = br.read_ub(5)
    xmin = br.read_sb(nbits)
    xmax = br.read_sb(nbits)
    ymin = br.read_sb(nbits)
    ymax = br.read_sb(nbits)
    return xmin, xmax, ymin, ymax

def parse_fill_style(br, tag_type, version):
    """Parse one fill style. version: 1=DefineShape, 2=DefineShape2, 3=DefineShape3, 4=DefineShape4"""
    fill_type = br.read_ub(8)
    br.align()
    info = {"type": fill_type}
    if fill_type == 0x00:
        # Solid fill
        if version >= 3:
            r, g, b, a = br.read_ub(8), br.read_ub(8), br.read_ub(8), br.read_ub(8)
            info["color"] = (r, g, b, a)
        else:
            r, g, b = br.read_ub(8), br.read_ub(8), br.read_ub(8)
            info["color"] = (r, g, b, 255)
    elif fill_type in (0x10, 0x12, 0x13):
        # Gradient fill - skip matrix + gradient
        info["desc"] = "gradient"
        return info  # simplified
    elif fill_type in (0x40, 0x41, 0x42, 0x43):
        # Bitmap fill
        br.align()
        byte_pos = br.byte_pos + (br.bit_pos >> 3)
        bitmap_id = struct.unpack_from('<H', br.data, byte_pos)[0]
        br.bit_pos += 16
        info["bitmapId"] = bitmap_id
        info["desc"] = "bitmap"
        return info  # simplified
    return info

def parse_shape_header(body, tag_type):
    """Parse shape header: char_id, bounds, fill_styles, line_styles, then return summary info"""
    version = {2: 1, 22: 2, 32: 3, 83: 4}.get(tag_type, 3)
    result = {}
    result["charId"] = struct.unpack_from('<H', body, 0)[0]
    result["tagType"] = tag_type
    result["bodyLen"] = len(body)
    result["version"] = version

    br = BitReader(body, 2)  # skip char_id

    # Shape bounds
    xmin, xmax, ymin, ymax = parse_rect(br)
    result["bounds"] = (xmin, xmax, ymin, ymax)
    br.align()

    if tag_type == 83:
        # DefineShape4 has edge bounds + flags
        parse_rect(br)  # edge bounds
        br.align()
        br.read_ub(5)  # reserved
        br.read_ub(1)  # UsesFillWindingRule
        br.read_ub(1)  # UsesNonScalingStrokes
        br.read_ub(1)  # UsesScalingStrokes
        br.align()

    # Fill style array
    byte_off = br.byte_pos + (br.bit_pos >> 3)
    n_fills = body[byte_off] if byte_off < len(body) else 0
    br.bit_pos += 8
    if n_fills == 0xFF and version >= 2:
        byte_off2 = br.byte_pos + (br.bit_pos >> 3)
        n_fills = struct.unpack_from('<H', body, byte_off2)[0]
        br.bit_pos += 16
    result["numFills"] = n_fills

    # Skip fill styles (we just count them)
    fill_types = []
    for _ in range(n_fills):
        byte_off_cur = br.byte_pos + (br.bit_pos >> 3)
        if byte_off_cur >= len(body):
            break
        ft = body[byte_off_cur]
        fill_types.append(ft)
        # We can't easily skip arbitrary fills without full parsing, so just record the type
        break  # Only record first fill type
    result["fillTypes"] = fill_types

    return result

def count_shape_records(body, tag_type):
    """Count edge records by scanning for TypeFlag patterns. Rough heuristic."""
    return len(body)  # Return body size as proxy

def analyze_shape(tag_type, body):
    """Get a structural summary of a shape tag."""
    header = parse_shape_header(body, tag_type)
    header["rawBytes"] = body.hex()[:200] + "..." if len(body) > 100 else body.hex()
    return header

# Main
f = open(OUT, 'w')

orig_data = read_swf(ORIG)
rt_data = read_swf(RT)

orig_tags = parse_tags(orig_data)
rt_tags = parse_tags(rt_data)

# Collect shapes by char ID
orig_shapes = {}
rt_shapes = {}
for t in orig_tags:
    tag_type, cid, offset, length, body = t
    if tag_type in SHAPE_TAGS and cid is not None:
        if cid not in orig_shapes:
            orig_shapes[cid] = (tag_type, body)

for t in rt_tags:
    tag_type, cid, offset, length, body = t
    if tag_type in SHAPE_TAGS and cid is not None:
        if cid not in rt_shapes:
            rt_shapes[cid] = (tag_type, body)

f.write("=" * 80 + "\n")
f.write("SHAPE COMPARISON: Original vs Roundtrip\n")
f.write("=" * 80 + "\n\n")

for cid in sorted(TARGET_CIDS):
    f.write(f"\n{'=' * 60}\n")
    f.write(f"CharID {cid}\n")
    f.write(f"{'=' * 60}\n")

    if cid not in orig_shapes:
        f.write("  NOT FOUND in original\n")
        continue
    if cid not in rt_shapes:
        f.write("  NOT FOUND in roundtrip\n")
        continue

    o_tag, o_body = orig_shapes[cid]
    r_tag, r_body = rt_shapes[cid]

    o_info = analyze_shape(o_tag, o_body)
    r_info = analyze_shape(r_tag, r_body)

    f.write(f"\n  ORIGINAL:  tag={o_tag}, size={len(o_body)} bytes, bounds={o_info['bounds']}, fills={o_info['numFills']}\n")
    f.write(f"  ROUNDTRIP: tag={r_tag}, size={len(r_body)} bytes, bounds={r_info['bounds']}, fills={r_info['numFills']}\n")

    if o_tag != r_tag:
        f.write(f"  ** TAG TYPE CHANGED: {o_tag} -> {r_tag}\n")
    if len(o_body) != len(r_body):
        ratio = len(r_body) / max(len(o_body), 1)
        f.write(f"  ** SIZE CHANGED: {len(o_body)} -> {len(r_body)} ({ratio:.1f}x)\n")
    if o_info['bounds'] != r_info['bounds']:
        f.write(f"  ** BOUNDS DIFFER\n")

    # Byte-level diff: find first differing byte
    min_len = min(len(o_body), len(r_body))
    first_diff = None
    diff_count = 0
    for i in range(min_len):
        if o_body[i] != r_body[i]:
            diff_count += 1
            if first_diff is None:
                first_diff = i
    if len(o_body) != len(r_body):
        diff_count += abs(len(o_body) - len(r_body))

    f.write(f"  Byte diffs: {diff_count}, first at offset {first_diff}\n")

    # Dump first 100 bytes hex of each
    f.write(f"\n  ORIG hex (first 100): {o_body[:100].hex()}\n")
    f.write(f"  RT   hex (first 100): {r_body[:100].hex()}\n")

# NOW: also parse the N2D recodes for these shapes and show them
f.write(f"\n\n{'=' * 80}\n")
f.write("N2D RECODE ANALYSIS\n")
f.write(f"{'=' * 80}\n\n")

import zipfile, msgpack

n2d_path = "test_swfs/lloyd.n2d"
if os.path.exists(n2d_path):
    with zipfile.ZipFile(n2d_path) as z:
        with z.open("project.msgpack") as mf:
            project = msgpack.unpack(mf, raw=False)

    libs = project.get("libraries", [{}])[0].get("symbols", [])
    for lib in libs:
        swf_cid = lib.get("swfCharId")
        if swf_cid in TARGET_CIDS:
            recodes = lib.get("recodes", [])
            lib_type = lib.get("type", "?")
            name = lib.get("name", "?")
            raw_tag = lib.get("rawTagType", "?")

            f.write(f"\n--- CID {swf_cid}: name={name}, type={lib_type}, rawTagType={raw_tag}, recodes_len={len(recodes)} ---\n")

            # Summarize recodes: Show commands
            # Command codes from shape_converter.py
            CMD_NAMES = {
                0: "MOVE_TO",
                1: "LINE_TO",
                2: "CURVE_TO",
                3: "FILL_STYLE",     # solid fill: r,g,b,a
                4: "LINE_STYLE",     # line style
                5: "END_FILL",
                6: "BEGIN_PATH",
                7: "CLOSE_PATH",
                8: "GRADIENT_FILL",
                9: "BITMAP_FILL",
                10: "BEGIN_BITMAP_FILL",
                11: "FOCAL_GRADIENT_FILL",
                12: "LINE_GRADIENT_FILL",
            }

            i = 0
            cmd_counts = {}
            edge_count = 0
            fill_count = 0
            line_count = 0
            move_count = 0
            while i < len(recodes):
                val = recodes[i]
                if isinstance(val, bool):
                    break
                if not isinstance(val, (int, float)):
                    i += 1
                    continue
                cmd = int(val)
                cmd_name = CMD_NAMES.get(cmd, f"UNK_{cmd}")
                cmd_counts[cmd_name] = cmd_counts.get(cmd_name, 0) + 1
                i += 1
                # Skip arguments based on command
                if cmd == 0:  # MOVE_TO
                    i += 2
                    move_count += 1
                elif cmd == 1:  # LINE_TO
                    i += 2
                    edge_count += 1
                elif cmd == 2:  # CURVE_TO
                    i += 4
                    edge_count += 1
                elif cmd == 3:  # FILL_STYLE (solid)
                    i += 4
                    fill_count += 1
                elif cmd == 4:  # LINE_STYLE
                    i += 5  # width, r, g, b, a
                    line_count += 1
                elif cmd == 5:  # END_FILL
                    pass
                elif cmd == 6:  # BEGIN_PATH
                    pass
                elif cmd == 7:  # CLOSE_PATH
                    pass
                elif cmd == 8:  # GRADIENT_FILL
                    # Skip gradient data - variable length
                    # spread(1) + interpolation(1) + count(1) + entries(count*5) + matrix(6)
                    if i + 3 <= len(recodes):
                        count = int(recodes[i+2]) if isinstance(recodes[i+2], (int, float)) else 0
                        i += 3 + count * 5 + 6
                    fill_count += 1
                elif cmd == 9:  # BITMAP_FILL
                    # bitmapId/dict, then matrix(6), then repeat_mode
                    next_val = recodes[i] if i < len(recodes) else None
                    if isinstance(next_val, dict):
                        i += 1 + 6 + 1  # dict + matrix + repeat
                    else:
                        i += 1 + 6 + 1
                    fill_count += 1
                elif cmd == 10:  # BEGIN_BITMAP_FILL
                    next_val = recodes[i] if i < len(recodes) else None
                    if isinstance(next_val, dict):
                        i += 1 + 6 + 1
                    else:
                        i += 1 + 6 + 1
                    fill_count += 1
                elif cmd == 11:  # FOCAL_GRADIENT_FILL
                    if i + 4 <= len(recodes):
                        count = int(recodes[i+3]) if isinstance(recodes[i+3], (int, float)) else 0
                        i += 4 + count * 5 + 6
                    fill_count += 1
                elif cmd == 12:  # LINE_GRADIENT_FILL
                    if i + 3 <= len(recodes):
                        count = int(recodes[i+2]) if isinstance(recodes[i+2], (int, float)) else 0
                        i += 3 + count * 5 + 6
                    fill_count += 1
                else:
                    # Unknown command, try to skip cautiously
                    pass

            f.write(f"  Commands: {cmd_counts}\n")
            f.write(f"  Fills={fill_count}, Lines={line_count}, Moves={move_count}, Edges={edge_count}\n")

            # Show first 50 recode values
            f.write(f"  First 50 recodes: {recodes[:50]}\n")

    # Also: parse the original SWF's shape records properly for the target CIDs
    f.write(f"\n\n{'=' * 80}\n")
    f.write("DETAILED EDGE RECORD COMPARISON\n")
    f.write(f"{'=' * 80}\n\n")

    # Import the actual SWF shape parser
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from swf_shape_to_recodes import parse_define_shape_to_recodes

    for cid in sorted(TARGET_CIDS):
        if cid not in orig_shapes:
            continue
        o_tag, o_body = orig_shapes[cid]
        f.write(f"\n--- CID {cid} (tag {o_tag}) ORIGINAL parse ---\n")
        try:
            result = parse_define_shape_to_recodes(o_tag, o_body)
            recodes = result.get("recodes", [])
            bounds = result.get("bounds", {})
            f.write(f"  bounds: {bounds}\n")
            f.write(f"  recodes length: {len(recodes)}\n")
            f.write(f"  first 80 recodes: {recodes[:80]}\n")
        except Exception as e:
            f.write(f"  PARSE ERROR: {e}\n")

        if cid not in rt_shapes:
            continue
        r_tag, r_body = rt_shapes[cid]
        f.write(f"\n--- CID {cid} (tag {r_tag}) ROUNDTRIP parse ---\n")
        try:
            result = parse_define_shape_to_recodes(r_tag, r_body)
            recodes = result.get("recodes", [])
            bounds = result.get("bounds", {})
            f.write(f"  bounds: {bounds}\n")
            f.write(f"  recodes length: {len(recodes)}\n")
            f.write(f"  first 80 recodes: {recodes[:80]}\n")
        except Exception as e:
            f.write(f"  PARSE ERROR: {e}\n")

else:
    f.write("lloyd.n2d not found!\n")

f.close()
print(f"Output written to {OUT}")
print(f"File size: {os.path.getsize(OUT)} bytes")
