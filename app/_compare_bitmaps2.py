"""Compare bitmaps via N2D library mapping."""
import struct, zlib, sys, os, zipfile, io
from swf_binary_io import BitReader

try:
    import msgpack
except ImportError:
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
    """Decode DefineBitsLossless/2 to RGBA. Returns (cid, w, h, rgba)."""
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
    elif fmt == 4:
        raw = zlib.decompress(body[7:])
        rgba = bytearray(w * h * 4)
        row_stride = ((w * 2) + 3) & ~3
        for y in range(h):
            for x in range(w):
                off = y * row_stride + x * 2
                val = (raw[off] << 8) | raw[off+1]
                r = ((val >> 10) & 0x1F) * 255 // 31
                g = ((val >> 5) & 0x1F) * 255 // 31
                b = (val & 0x1F) * 255 // 31
                base = (y * w + x) * 4
                rgba[base] = r; rgba[base+1] = g; rgba[base+2] = b; rgba[base+3] = 255
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

def decode_swf_bitmap(tt, body):
    if tt in (20, 36):
        return decode_lossless_rgba(tt, body)
    else:
        return decode_jpeg_rgba(tt, body)

# Load N2D to get swfCharId → library ID mapping
n2d_path = 'test_swfs/lloyd.n2d'
with zipfile.ZipFile(n2d_path) as zf:
    with zf.open('project.msgpack') as f:
        project = msgpack.unpack(f, raw=False)

libs = project.get('libraries', [])
print(f"N2D has {len(libs)} library entries")

# Build swfCharId → lib entry for bitmaps
bitmap_libs = {}
for lib in libs:
    if isinstance(lib, dict) and lib.get('type') == 'bitmap' and 'swfCharId' in lib:
        bitmap_libs[lib['swfCharId']] = lib

print(f"N2D has {len(bitmap_libs)} bitmap entries with swfCharId")

# Check a sample: what does the N2D store for bitmap dimensions?
sample_cids = list(bitmap_libs.keys())[:5]
for cid in sample_cids:
    lib = bitmap_libs[cid]
    buf = lib.get('buffer', '')
    if isinstance(buf, str) and buf.startswith('b64:'):
        import base64
        raw = base64.b64decode(buf[4:])
        expected = lib.get('width', 0) * lib.get('height', 0) * 4
        print(f"  CID {cid}: {lib.get('width')}x{lib.get('height')} rawTagType={lib.get('rawTagType')} buf_len={len(raw)} expected_rgba={expected} match={len(raw)==expected}")
    else:
        print(f"  CID {cid}: {lib.get('width')}x{lib.get('height')} buf type={type(buf).__name__}")

# Now load original SWF bitmaps
orig_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf'
orig_tags = read_swf_tags(orig_path)
bitmap_types = {20, 21, 35, 36, 90}

orig_bmps = {}
for tt, body in orig_tags:
    if tt in bitmap_types and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        orig_bmps[cid] = (tt, body)

print(f"\nOriginal SWF has {len(orig_bmps)} bitmaps")

# Compare: N2D stored RGBA vs original SWF decoded RGBA
import base64

stats = {'identical': 0, 'minor': 0, 'major': 0, 'dim_diff': 0, 'missing': 0, 'decode_fail': 0}
issues = []

for cid, lib in sorted(bitmap_libs.items()):
    if cid not in orig_bmps:
        stats['missing'] += 1
        continue
    
    tt, body = orig_bmps[cid]
    try:
        _, ow, oh, orgba = decode_swf_bitmap(tt, body)
    except Exception as e:
        stats['decode_fail'] += 1
        continue
    if orgba is None:
        stats['decode_fail'] += 1
        continue
    
    nw = lib.get('width', 0)
    nh = lib.get('height', 0)
    
    if ow != nw or oh != nh:
        stats['dim_diff'] += 1
        issues.append(f"  DIM CID {cid}: orig={ow}x{oh} n2d={nw}x{nh} tag={tt} rawTagType={lib.get('rawTagType')}")
        continue
    
    buf = lib.get('buffer', '')
    if isinstance(buf, str) and buf.startswith('b64:'):
        nrgba = base64.b64decode(buf[4:])
    elif isinstance(buf, bytes):
        nrgba = buf
    else:
        stats['decode_fail'] += 1
        continue
    
    if len(nrgba) != len(orgba):
        stats['dim_diff'] += 1
        issues.append(f"  SIZE CID {cid}: orig_buf={len(orgba)} n2d_buf={len(nrgba)} dims={ow}x{oh}")
        continue
    
    if nrgba == orgba:
        stats['identical'] += 1
        continue
    
    # Find max diff
    max_d = 0
    for i in range(len(orgba)):
        d = abs(orgba[i] - nrgba[i])
        max_d = max(max_d, d)
    
    if max_d <= 2:
        stats['minor'] += 1
    else:
        stats['major'] += 1
        issues.append(f"  PIXEL CID {cid}: {ow}x{oh} tag={tt} max_diff={max_d}")

print(f"\n=== N2D vs Original SWF (Import Check) ===")
for k, v in stats.items():
    print(f"  {k}: {v}")

if issues:
    print(f"\n=== Issues ({len(issues)}) ===")
    for i in issues[:60]:
        print(i)
    if len(issues) > 60:
        print(f"  ...and {len(issues)-60} more")
