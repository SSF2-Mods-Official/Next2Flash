"""Compare bitmaps between original SWF and roundtrip SWF."""
import struct, zlib, sys, os
from swf_binary_io import BitReader

def read_swf_tags(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        flen = struct.unpack_from('<I', data, 4)[0]
        body = zlib.decompress(data[8:])
        data = b'FWS' + data[3:8] + body[:flen-8]
    elif data[:3] == b'ZWS':
        import lzma
        flen = struct.unpack_from('<I', data, 4)[0]
        body = lzma.decompress(data[12:])
        data = b'FWS' + data[3:8] + body[:flen-8]
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    br.read_ui8(); br.read_ui8(); br.read_ui16()
    pos = br.byte_pos
    tags = []
    while pos < len(data):
        if pos + 2 > len(data): break
        hdr = struct.unpack_from('<H', data, pos)[0]
        tt = hdr >> 6
        tl = hdr & 0x3F
        if tl == 0x3F:
            tl = struct.unpack_from('<I', data, pos+2)[0]
            body_start = pos + 6
        else:
            body_start = pos + 2
        body = data[body_start:body_start+tl]
        tags.append((tt, body))
        pos = body_start + tl
        if tt == 0: break
    return tags

def decode_lossless_rgba(tag_type, body):
    """Decode DefineBitsLossless/2 to RGBA pixels. Returns (width, height, rgba_bytes)."""
    cid = struct.unpack_from('<H', body, 0)[0]
    fmt = body[2]
    width = struct.unpack_from('<H', body, 3)[0]
    height = struct.unpack_from('<H', body, 5)[0]
    
    if fmt == 3:
        palette_size = body[7] + 1
        raw = zlib.decompress(body[8:])
        is_rgba = (tag_type == 36)
        bpp = 4 if is_rgba else 3
        palette = []
        for i in range(palette_size):
            off = i * bpp
            if is_rgba:
                palette.append((raw[off], raw[off+1], raw[off+2], raw[off+3]))
            else:
                palette.append((raw[off], raw[off+1], raw[off+2], 255))
        
        idx_start = palette_size * bpp
        row_stride = (width + 3) & ~3  # padded to 4
        rgba = bytearray(width * height * 4)
        for y in range(height):
            row_off = idx_start + y * row_stride
            for x in range(width):
                pi = raw[row_off + x]
                if pi < palette_size:
                    r, g, b, a = palette[pi]
                else:
                    r, g, b, a = 0, 0, 0, 0
                base = (y * width + x) * 4
                rgba[base] = r; rgba[base+1] = g; rgba[base+2] = b; rgba[base+3] = a
        return cid, width, height, bytes(rgba)
    
    elif fmt == 5:
        raw = zlib.decompress(body[7:])
        rgba = bytearray(width * height * 4)
        if tag_type == 20:
            # xRGB (4 bytes: pad, R, G, B)
            for i in range(width * height):
                off = i * 4
                rgba[i*4] = raw[off+1]
                rgba[i*4+1] = raw[off+2]
                rgba[i*4+2] = raw[off+3]
                rgba[i*4+3] = 255
        else:
            # Premultiplied ARGB → RGBA
            for i in range(width * height):
                off = i * 4
                a = raw[off]
                if a == 0:
                    rgba[i*4] = 0; rgba[i*4+1] = 0; rgba[i*4+2] = 0; rgba[i*4+3] = 0
                elif a == 255:
                    rgba[i*4] = raw[off+1]; rgba[i*4+1] = raw[off+2]; rgba[i*4+2] = raw[off+3]; rgba[i*4+3] = 255
                else:
                    rgba[i*4] = min(255, (raw[off+1] * 255 + a // 2) // a)
                    rgba[i*4+1] = min(255, (raw[off+2] * 255 + a // 2) // a)
                    rgba[i*4+2] = min(255, (raw[off+3] * 255 + a // 2) // a)
                    rgba[i*4+3] = a
        return cid, width, height, bytes(rgba)
    
    elif fmt == 4:
        raw = zlib.decompress(body[7:])
        rgba = bytearray(width * height * 4)
        row_stride = ((width * 2) + 3) & ~3
        for y in range(height):
            for x in range(width):
                off = y * row_stride + x * 2
                val = (raw[off] << 8) | raw[off+1]
                r = ((val >> 10) & 0x1F) * 255 // 31
                g = ((val >> 5) & 0x1F) * 255 // 31
                b = (val & 0x1F) * 255 // 31
                base = (y * width + x) * 4
                rgba[base] = r; rgba[base+1] = g; rgba[base+2] = b; rgba[base+3] = 255
        return cid, width, height, bytes(rgba)
    
    return cid, width, height, None

def decode_jpeg_rgba(tag_type, body):
    """Decode DefineBitsJPEG2/3/4 to RGBA pixels."""
    from PIL import Image
    import io
    
    cid = struct.unpack_from('<H', body, 0)[0]
    
    if tag_type == 35:
        alpha_offset = struct.unpack_from('<I', body, 2)[0]
        jpeg_data = body[6:6+alpha_offset]
        alpha_data = body[6+alpha_offset:]
    elif tag_type == 90:
        alpha_offset = struct.unpack_from('<I', body, 2)[0]
        # deblock param at bytes 6-7
        jpeg_data = body[8:8+alpha_offset]
        alpha_data = body[8+alpha_offset:]
    else:
        jpeg_data = body[2:]
        alpha_data = None
    
    # Strip erroneous FF D9 FF D8
    if len(jpeg_data) >= 4 and jpeg_data[:4] == b'\xff\xd9\xff\xd8':
        jpeg_data = jpeg_data[2:]
    
    # Check if it's actually PNG or GIF
    if jpeg_data[:8] == b'\x89PNG\r\n\x1a\n' or jpeg_data[:3] == b'GIF':
        img = Image.open(io.BytesIO(jpeg_data)).convert('RGBA')
        return cid, img.width, img.height, img.tobytes()
    
    try:
        img = Image.open(io.BytesIO(jpeg_data)).convert('RGBA')
    except:
        return cid, 0, 0, None
    
    if alpha_data:
        try:
            alpha_raw = zlib.decompress(alpha_data)
            rgba = bytearray(img.tobytes())
            for i in range(min(len(alpha_raw), img.width * img.height)):
                rgba[i*4+3] = alpha_raw[i]
            return cid, img.width, img.height, bytes(rgba)
        except:
            pass
    
    return cid, img.width, img.height, img.tobytes()

def compare_pixels(orig_rgba, rt_rgba, width, height):
    """Compare RGBA pixel data. Returns (max_diff, avg_diff, diff_count, total_pixels)."""
    total = width * height
    max_diff = 0
    total_diff = 0
    diff_count = 0
    channel_diffs = [0, 0, 0, 0]  # R, G, B, A
    
    for i in range(total):
        off = i * 4
        for c in range(4):
            d = abs(orig_rgba[off+c] - rt_rgba[off+c])
            if d > 0:
                diff_count += 1
                total_diff += d
                max_diff = max(max_diff, d)
                channel_diffs[c] += d
                break  # count pixel, not channel
    
    # per-channel max
    ch_max = [0, 0, 0, 0]
    for i in range(total):
        off = i * 4
        for c in range(4):
            d = abs(orig_rgba[off+c] - rt_rgba[off+c])
            ch_max[c] = max(ch_max[c], d)
    
    return max_diff, total_diff / max(1, total * 4), diff_count, total, ch_max

# Main
orig_path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf'
rt_path = sys.argv[2] if len(sys.argv) > 2 else r'test_swfs/lloyd_rt.swf'

print(f"Comparing bitmaps: {os.path.basename(orig_path)} vs {os.path.basename(rt_path)}")

orig_tags = read_swf_tags(orig_path)
rt_tags = read_swf_tags(rt_path)

bitmap_types = {20, 21, 35, 36, 90}

# Extract all bitmaps by CID
def extract_bitmaps(tags):
    bitmaps = {}
    for tt, body in tags:
        if tt in bitmap_types and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            bitmaps[cid] = (tt, body)
    return bitmaps

orig_bmps = extract_bitmaps(orig_tags)
rt_bmps = extract_bitmaps(rt_tags)

print(f"Original: {len(orig_bmps)} bitmaps, RT: {len(rt_bmps)} bitmaps")

# Match by index order (CIDs are renumbered)
# Match by order of appearance (N-th bitmap in file → N-th bitmap in file)
orig_list = [(cid, tt, body) for tt, body in orig_tags if tt in bitmap_types and len(body) >= 2 for cid in [struct.unpack_from('<H', body, 0)[0]]]
rt_list = [(cid, tt, body) for tt, body in rt_tags if tt in bitmap_types and len(body) >= 2 for cid in [struct.unpack_from('<H', body, 0)[0]]]

if len(orig_list) != len(rt_list):
    print(f"WARNING: bitmap count mismatch! {len(orig_list)} vs {len(rt_list)}")

# Categorize
stats = {'identical': 0, 'minor_diff': 0, 'major_diff': 0, 'dim_mismatch': 0, 'decode_fail': 0, 'type_change': 0}
major_diffs = []
type_changes = {'20->36': 0, '21->36': 0, '35->36': 0, '36->36': 0, '20->20': 0, '35->35': 0, '36->20': 0, 'other': 0}

for idx in range(min(len(orig_list), len(rt_list))):
    ocid, ott, obody = orig_list[idx]
    rcid, rtt, rbody = rt_list[idx]
    
    tc_key = f"{ott}->{rtt}"
    type_changes[tc_key] = type_changes.get(tc_key, 0) + 1
    if ott != rtt:
        stats['type_change'] += 1
    
    # Decode
    try:
        if ott in (20, 36):
            _, ow, oh, orgba = decode_lossless_rgba(ott, obody)
        else:
            _, ow, oh, orgba = decode_jpeg_rgba(ott, obody)
    except Exception as e:
        stats['decode_fail'] += 1
        continue
    
    try:
        if rtt in (20, 36):
            _, rw, rh, rrgba = decode_lossless_rgba(rtt, rbody)
        else:
            _, rw, rh, rrgba = decode_jpeg_rgba(rtt, rbody)
    except Exception as e:
        stats['decode_fail'] += 1
        continue
    
    if orgba is None or rrgba is None:
        stats['decode_fail'] += 1
        continue
    
    if ow != rw or oh != rh:
        stats['dim_mismatch'] += 1
        major_diffs.append(f"  CID {ocid}->{rcid} tag={ott}->{rtt}: dims {ow}x{oh} -> {rw}x{rh}")
        continue
    
    if orgba == rrgba:
        stats['identical'] += 1
        continue
    
    max_d, avg_d, dcnt, total, ch_max = compare_pixels(orgba, rrgba, ow, oh)
    
    if max_d <= 2:
        stats['minor_diff'] += 1
    else:
        stats['major_diff'] += 1
        major_diffs.append(f"  CID {ocid}->{rcid} tag={ott}->{rtt} {ow}x{oh}: max={max_d} avg={avg_d:.3f} diffpx={dcnt}/{total} ch_max=R{ch_max[0]}G{ch_max[1]}B{ch_max[2]}A{ch_max[3]}")

print(f"\n=== Type Changes ===")
for k, v in sorted(type_changes.items()):
    if v > 0:
        print(f"  {k}: {v}")

print(f"\n=== Results ===")
for k, v in stats.items():
    print(f"  {k}: {v}")

if major_diffs:
    print(f"\n=== Major Diffs (max > 2) ===")
    for d in major_diffs[:50]:
        print(d)
    if len(major_diffs) > 50:
        print(f"  ...and {len(major_diffs)-50} more")
