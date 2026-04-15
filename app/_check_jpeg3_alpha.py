"""Precisely compare the 4 problematic 244x244 JPEG3 bitmaps."""
import struct, zlib, zipfile, io, base64, msgpack
from PIL import Image

def read_swf_tags(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        flen = struct.unpack_from('<I', data, 4)[0]
        body = zlib.decompress(data[8:])
        data = b'FWS' + data[3:8] + body[:flen-8]
    pos = 8
    from swf_binary_io import BitReader
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

# Load N2D
with zipfile.ZipFile('test_swfs/lloyd.n2d') as zf:
    with zf.open('project.msgpack') as f:
        project = msgpack.unpack(f, raw=False)

# Get N2D 244x244 bitmaps
n2d_bmps = {}
for lib in project.get('libraries', []):
    if isinstance(lib, dict) and lib.get('type') == 'bitmap':
        if lib.get('width') == 244 and lib.get('height') == 244:
            cid = lib['swfCharId']
            buf = lib.get('buffer', '')
            if isinstance(buf, str) and buf.startswith('b64:'):
                rgba = base64.b64decode(buf[4:])
            else:
                rgba = buf
            # Extract just alpha channel
            alpha = bytearray(244*244)
            for i in range(244*244):
                alpha[i] = rgba[i*4+3]
            n2d_bmps[cid] = {'rgba': rgba, 'alpha': bytes(alpha)}

print(f"N2D 244x244 bitmaps: {list(n2d_bmps.keys())}")

# Get RT 244x244 JPEG3 bitmaps
rt_tags = read_swf_tags('test_swfs/lloyd_rt.swf')
rt_bmps = {}
for tt, body in rt_tags:
    if tt == 35 and len(body) >= 6:
        cid = struct.unpack_from('<H', body, 0)[0]
        ao = struct.unpack_from('<I', body, 2)[0]
        jpeg_data = body[6:6+ao]
        alpha_data = body[6+ao:]
        try:
            img = Image.open(io.BytesIO(jpeg_data))
            w, h = img.size
        except:
            continue
        if w == 244 and h == 244:
            try:
                alpha_raw = zlib.decompress(alpha_data)
            except:
                alpha_raw = None
            img_rgba = img.convert('RGBA')
            rt_bmps[cid] = {
                'jpeg_rgb': img_rgba.tobytes(),
                'alpha': alpha_raw,
                'w': w, 'h': h
            }

print(f"RT 244x244 JPEG3 bitmaps: {list(rt_bmps.keys())}")

# Compare alpha channels to find correct mapping
print("\n=== Alpha Channel Matching ===")
for n2d_cid, n2d in sorted(n2d_bmps.items()):
    n2d_alpha = n2d['alpha']
    print(f"\nN2D CID {n2d_cid}:")
    for rt_cid, rt in sorted(rt_bmps.items()):
        rt_alpha = rt['alpha']
        if rt_alpha is None or len(rt_alpha) != len(n2d_alpha):
            print(f"  RT CID {rt_cid}: alpha size mismatch")
            continue
        max_d = 0
        diff_count = 0
        for i in range(len(n2d_alpha)):
            d = abs(n2d_alpha[i] - rt_alpha[i])
            if d > 0:
                diff_count += 1
                max_d = max(max_d, d)
        if max_d == 0:
            print(f"  RT CID {rt_cid}: ALPHA IDENTICAL <<<")
        else:
            print(f"  RT CID {rt_cid}: alpha max_diff={max_d} diff_pixels={diff_count}/{244*244}")

# Now compare full RGBA for correct pairs
print("\n=== Full RGBA for matching alpha pairs ===")
for n2d_cid, n2d in sorted(n2d_bmps.items()):
    n2d_rgba = n2d['rgba']
    n2d_alpha = n2d['alpha']
    for rt_cid, rt in sorted(rt_bmps.items()):
        rt_alpha = rt['alpha']
        if rt_alpha is None or len(rt_alpha) != len(n2d_alpha):
            continue
        # Check if alpha matches
        if n2d_alpha == rt_alpha:
            # This is the correct pair! Compare RGB
            rt_full_rgba = bytearray(rt['jpeg_rgb'])
            # Apply the correct alpha
            for i in range(244*244):
                rt_full_rgba[i*4+3] = rt_alpha[i]
            # Compare
            max_r = max_g = max_b = max_a = 0
            for i in range(244*244):
                off = i*4
                dr = abs(n2d_rgba[off] - rt_full_rgba[off])
                dg = abs(n2d_rgba[off+1] - rt_full_rgba[off+1])
                db = abs(n2d_rgba[off+2] - rt_full_rgba[off+2])
                da = abs(n2d_rgba[off+3] - rt_full_rgba[off+3])
                max_r = max(max_r, dr)
                max_g = max(max_g, dg)
                max_b = max(max_b, db)
                max_a = max(max_a, da)
            print(f"  CID {n2d_cid} -> RT {rt_cid}: R={max_r} G={max_g} B={max_b} A={max_a}")
