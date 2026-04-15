"""Compare bitmaps: RT SWF vs N2D stored RGBA (export check)."""
import struct, zlib, sys, os, zipfile, io, base64
from swf_binary_io import BitReader

try:
    import msgpack
except:
    os.system('pip install msgpack')
    import msgpack

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
    cid = struct.unpack_from('<H', body, 0)[0]
    fmt = body[2]
    w = struct.unpack_from('<H', body, 3)[0]
    h = struct.unpack_from('<H', body, 5)[0]
    if fmt == 3:
        psize = body[7] + 1
        raw = zlib.decompress(body[8:])
        is_rgba = (tag_type == 36)
        bpp = 4 if is_rgba else 3
        palette = []
        for i in range(psize):
            off = i * bpp
            if is_rgba:
                palette.append((raw[off], raw[off+1], raw[off+2], raw[off+3]))
            else:
                palette.append((raw[off], raw[off+1], raw[off+2], 255))
        idx_start = psize * bpp
        row_stride = (w + 3) & ~3
        rgba = bytearray(w * h * 4)
        for y in range(h):
            row_off = idx_start + y * row_stride
            for x in range(w):
                pi = raw[row_off + x]
                r, g, b, a = palette[pi] if pi < psize else (0, 0, 0, 0)
                base = (y * w + x) * 4
                rgba[base] = r; rgba[base+1] = g; rgba[base+2] = b; rgba[base+3] = a
        return cid, w, h, bytes(rgba)
    elif fmt == 5:
        raw = zlib.decompress(body[7:])
        rgba = bytearray(w * h * 4)
        if tag_type == 20:
            for i in range(w * h):
                off = i * 4
                rgba[i*4] = raw[off+1]; rgba[i*4+1] = raw[off+2]; rgba[i*4+2] = raw[off+3]; rgba[i*4+3] = 255
        else:
            for i in range(w * h):
                off = i * 4
                a = raw[off]
                if a == 0:
                    rgba[i*4:i*4+4] = b'\x00\x00\x00\x00'
                elif a == 255:
                    rgba[i*4] = raw[off+1]; rgba[i*4+1] = raw[off+2]; rgba[i*4+2] = raw[off+3]; rgba[i*4+3] = 255
                else:
                    rgba[i*4] = min(255, (raw[off+1] * 255 + a // 2) // a)
                    rgba[i*4+1] = min(255, (raw[off+2] * 255 + a // 2) // a)
                    rgba[i*4+2] = min(255, (raw[off+3] * 255 + a // 2) // a)
                    rgba[i*4+3] = a
        return cid, w, h, bytes(rgba)
    return cid, w, h, None

def decode_jpeg_rgba(tag_type, body):
    from PIL import Image
    cid = struct.unpack_from('<H', body, 0)[0]
    if tag_type == 35:
        alpha_offset = struct.unpack_from('<I', body, 2)[0]
        jpeg_data = body[6:6+alpha_offset]
        alpha_data = body[6+alpha_offset:]
    elif tag_type == 90:
        alpha_offset = struct.unpack_from('<I', body, 2)[0]
        jpeg_data = body[8:8+alpha_offset]
        alpha_data = body[8+alpha_offset:]
    else:
        jpeg_data = body[2:]
        alpha_data = None
    if len(jpeg_data) >= 4 and jpeg_data[:4] == b'\xff\xd9\xff\xd8':
        jpeg_data = jpeg_data[2:]
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

# Load N2D
n2d_path = 'test_swfs/lloyd.n2d'
with zipfile.ZipFile(n2d_path) as zf:
    with zf.open('project.msgpack') as f:
        project = msgpack.unpack(f, raw=False)

libs = project.get('libraries', [])
bitmap_libs = {}
for lib in libs:
    if isinstance(lib, dict) and lib.get('type') == 'bitmap' and 'swfCharId' in lib:
        bitmap_libs[lib['swfCharId']] = lib

# The compiler assigns new CIDs. We need to figure out the mapping.
# During compilation, bitmaps are emitted in a specific order.
# Let's look at how compile_n2d.py assigns IDs.
# Instead, let's match RT bitmaps by dimensions+content to N2D.

# Load RT SWF
rt_tags = read_swf_tags('test_swfs/lloyd_rt.swf')
bitmap_types = {20, 21, 35, 36, 90}

rt_bmps_by_cid = {}
rt_bmps_ordered = []
for tt, body in rt_tags:
    if tt in bitmap_types and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        rt_bmps_by_cid[cid] = (tt, body)
        rt_bmps_ordered.append((cid, tt, body))

print(f"RT SWF has {len(rt_bmps_by_cid)} bitmaps")

# Match N2D bitmaps to RT bitmaps by dims
# First build RT dim index
rt_by_dims = {}
for cid, tt, body in rt_bmps_ordered:
    if tt in (20, 36):
        w = struct.unpack_from('<H', body, 3)[0]
        h = struct.unpack_from('<H', body, 5)[0]
    else:
        from PIL import Image
        if tt == 35:
            ao = struct.unpack_from('<I', body, 2)[0]
            jdata = body[6:6+ao]
        elif tt == 90:
            ao = struct.unpack_from('<I', body, 2)[0]
            jdata = body[8:8+ao]
        else:
            jdata = body[2:]
        if jdata[:4] == b'\xff\xd9\xff\xd8':
            jdata = jdata[2:]
        try:
            img = Image.open(io.BytesIO(jdata))
            w, h = img.size
        except:
            w, h = 0, 0
    key = (w, h)
    if key not in rt_by_dims:
        rt_by_dims[key] = []
    rt_by_dims[key].append((cid, tt, body))

# Compare each N2D bitmap to its matching RT bitmap 
stats = {'identical': 0, 'minor': 0, 'major': 0, 'dim_diff': 0, 'no_match': 0, 'decode_fail': 0}
issues = []

checked_rt_cids = set()
for orig_cid, lib in sorted(bitmap_libs.items()):
    nw = lib['width']
    nh = lib['height']
    
    buf = lib.get('buffer', '')
    if isinstance(buf, str) and buf.startswith('b64:'):
        n2d_rgba = base64.b64decode(buf[4:])
    elif isinstance(buf, bytes):
        n2d_rgba = buf
    else:
        stats['decode_fail'] += 1
        continue
    
    key = (nw, nh)
    candidates = rt_by_dims.get(key, [])
    
    if not candidates:
        stats['no_match'] += 1
        issues.append(f"  NO_RT CID {orig_cid}: {nw}x{nh} rawTagType={lib.get('rawTagType')}")
        continue
    
    # Find best match among candidates
    best_cid = None
    best_diff = float('inf')
    best_rgba = None
    
    for rcid, rtt, rbody in candidates:
        if rcid in checked_rt_cids:
            continue
        try:
            if rtt in (20, 36):
                _, rw, rh, rrgba = decode_lossless_rgba(rtt, rbody)
            else:
                _, rw, rh, rrgba = decode_jpeg_rgba(rtt, rbody)
        except:
            continue
        if rrgba is None or rw != nw or rh != nh:
            continue
        if len(rrgba) != len(n2d_rgba):
            continue
        if rrgba == n2d_rgba:
            best_cid = rcid
            best_diff = 0
            best_rgba = rrgba
            break
        # Quick diff
        d = sum(abs(rrgba[i] - n2d_rgba[i]) for i in range(min(100, len(rrgba))))
        if d < best_diff:
            best_diff = d
            best_cid = rcid
            best_rgba = rrgba
    
    if best_cid is None:
        stats['no_match'] += 1
        issues.append(f"  NO_MATCH CID {orig_cid}: {nw}x{nh} ({len(candidates)} candidates all checked)")
        continue
    
    checked_rt_cids.add(best_cid)
    
    if best_rgba == n2d_rgba:
        stats['identical'] += 1
        continue
    
    # Full diff
    max_d = 0
    diff_px = 0
    ch_max = [0, 0, 0, 0]
    total_px = nw * nh
    for i in range(total_px):
        off = i * 4
        px_diff = False
        for c in range(4):
            d = abs(n2d_rgba[off+c] - best_rgba[off+c])
            if d > 0:
                px_diff = True
                ch_max[c] = max(ch_max[c], d)
                max_d = max(max_d, d)
        if px_diff:
            diff_px += 1
    
    rtt_for_match = None
    for rcid2, rtt2, _ in candidates:
        if rcid2 == best_cid:
            rtt_for_match = rtt2
            break
    
    if max_d <= 2:
        stats['minor'] += 1
    else:
        stats['major'] += 1
        issues.append(f"  PIXEL CID {orig_cid}->RT {best_cid}: {nw}x{nh} tag={lib.get('rawTagType')}->{rtt_for_match} max={max_d} ch_max=R{ch_max[0]}G{ch_max[1]}B{ch_max[2]}A{ch_max[3]} diffpx={diff_px}/{total_px}")

print(f"\n=== Export Check: N2D vs RT SWF ===")
for k, v in stats.items():
    print(f"  {k}: {v}")

if issues:
    print(f"\n=== Issues ({len(issues)}) ===")
    for i in issues[:60]:
        print(i)
    if len(issues) > 60:
        print(f"  ...and {len(issues)-60} more")
