"""Validate all DefineBitsLossless2 tags in the RT blackmage by actually
decompressing them and checking if pixel data size matches w*h*4."""
import struct, zlib, sys, os

RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset, end=None):
    if end is None: end = len(data)
    tags = []
    while offset < end:
        if offset + 2 > end: break
        hdr = struct.unpack_from('<H', data, offset)[0]
        tt = hdr >> 6; length = hdr & 0x3F; offset += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, offset)[0]; offset += 4
        td = data[offset:offset+length]; tags.append((tt, td)); offset += length
        if tt == 0: break
    return tags

def parse_rect(data, bit_off=0):
    byte_i = bit_off // 8; bit_i = bit_off % 8
    nbits = 0
    for i in range(5):
        nbits = (nbits << 1) | ((data[byte_i + (bit_i+i)//8] >> (7-(bit_i+i)%8)) & 1)
    return (5 + nbits * 4 + 7) // 8

def skip_header(data):
    return 8 + parse_rect(data, 64) + 4

def validate_lossless2(d, label):
    """Validate a DefineBitsLossless2 tag."""
    cid = struct.unpack_from('<H', d, 0)[0]
    fmt = d[2]
    w = struct.unpack_from('<H', d, 3)[0]
    h = struct.unpack_from('<H', d, 5)[0]
    
    if fmt == 3:  # 8-bit colormapped
        color_table_size = d[7] + 1  # number of palette entries
        compressed = d[8:]
        try:
            decompressed = zlib.decompress(compressed)
        except zlib.error as e:
            return cid, w, h, fmt, f"ZLIB_ERROR: {e}"
        
        # Expected: color_table_size * 4 bytes (ARGB palette) + h rows of (padded-to-4 w bytes)
        row_bytes = (w + 3) & ~3  # pad to 4-byte alignment
        expected_size = color_table_size * 4 + row_bytes * h
        if len(decompressed) != expected_size:
            return cid, w, h, fmt, f"SIZE_MISMATCH: decompressed={len(decompressed)} expected={expected_size} (ct={color_table_size} row={row_bytes})"
        return cid, w, h, fmt, "OK"
    
    elif fmt == 5:  # 32-bit ARGB
        compressed = d[7:]
        try:
            decompressed = zlib.decompress(compressed)
        except zlib.error as e:
            return cid, w, h, fmt, f"ZLIB_ERROR: {e}"
        
        expected_size = w * h * 4
        if len(decompressed) != expected_size:
            return cid, w, h, fmt, f"SIZE_MISMATCH: decompressed={len(decompressed)} expected={expected_size}"
        return cid, w, h, fmt, "OK"
    
    else:
        return cid, w, h, fmt, f"UNKNOWN_FORMAT: {fmt}"

def validate_jpeg3(d, label):
    """Validate a DefineBitsJPEG3 tag."""
    cid = struct.unpack_from('<H', d, 0)[0]
    alpha_off = struct.unpack_from('<I', d, 2)[0]
    jpeg_data = d[6:6+alpha_off]
    compressed_alpha = d[6+alpha_off:]
    
    # Try to get JPEG dimensions
    w, h = 0, 0
    i = 0
    while i < len(jpeg_data) - 9:
        if jpeg_data[i] == 0xFF:
            marker = jpeg_data[i+1]
            if marker in (0xC0, 0xC1, 0xC2):
                h = struct.unpack_from('>H', jpeg_data, i+5)[0]
                w = struct.unpack_from('>H', jpeg_data, i+7)[0]
                break
            elif marker == 0xD8 or marker == 0xD9 or marker == 0x00:
                i += 2
            else:
                if i + 3 < len(jpeg_data):
                    seg_len = struct.unpack_from('>H', jpeg_data, i+2)[0]
                    i += 2 + seg_len
                else:
                    i += 2
        else:
            i += 1
    
    # Validate alpha
    try:
        alpha = zlib.decompress(compressed_alpha)
    except zlib.error as e:
        return cid, w, h, f"ALPHA_ZLIB_ERROR: {e}"
    
    if w > 0 and h > 0:
        expected_alpha = w * h
        if len(alpha) != expected_alpha:
            return cid, w, h, f"ALPHA_SIZE_MISMATCH: alpha={len(alpha)} expected={expected_alpha}"
    
    return cid, w, h, "OK"

def main():
    # First re-compile RT from N2D using the reverted code
    print("=== Rebuilding RT from N2D (no wrapper shapes) ===")
    sys.path.insert(0, '.')
    from compile_n2d import N2DCompiler
    import tempfile
    n2d_path = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage\project.n2d'
    compiler = N2DCompiler(n2d_path=n2d_path, shared_dir=tempfile.mkdtemp(), output_path=RT)
    compiler.compile()
    
    print("\n=== Validating RT DefineBitsLossless2 tags ===")
    rt_data = read_swf(RT)
    rt_tags = parse_tags(rt_data, skip_header(rt_data))
    
    errors = []
    ok_count = 0
    fmt_counts = {}
    for t, d in rt_tags:
        if t == 36:
            cid, w, h, fmt, status = validate_lossless2(d, "RT")
            fmt_counts[fmt] = fmt_counts.get(fmt, 0) + 1
            if status != "OK":
                errors.append((cid, w, h, fmt, status))
            else:
                ok_count += 1
    
    print(f"RT: {ok_count} OK, {len(errors)} errors")
    print(f"Format breakdown: {fmt_counts}")
    if errors:
        for cid, w, h, fmt, status in errors[:20]:
            print(f"  cid={cid} {w}x{h} fmt={fmt}: {status}")
    
    print("\n=== Validating OG bitmap tags ===")
    og_data = read_swf(OG)
    og_tags = parse_tags(og_data, skip_header(og_data))
    
    errors = []
    ok_count = 0
    fmt_counts = {}
    for t, d in og_tags:
        if t == 36:
            cid, w, h, fmt, status = validate_lossless2(d, "OG")
            fmt_counts[fmt] = fmt_counts.get(fmt, 0) + 1
            if status != "OK":
                errors.append((cid, w, h, fmt, status))
            else:
                ok_count += 1
        elif t == 35:
            cid, w, h, status = validate_jpeg3(d, "OG")
            if status != "OK":
                errors.append((cid, w, h, 'jpeg3', status))
            else:
                ok_count += 1
    
    print(f"OG: {ok_count} OK, {len(errors)} errors")
    print(f"Format breakdown: {fmt_counts}")
    if errors:
        for e in errors[:20]:
            print(f"  {e}")
    
    # Now check what happens with external bitmap files
    print("\n=== Checking external bitmap files ===")
    import os
    bmp_dir = os.path.join(r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage', 'bitmaps')
    if os.path.isdir(bmp_dir):
        files = os.listdir(bmp_dir)
        print(f"External bitmaps: {len(files)} files")
        # Check a few file sizes
        for f in files[:5]:
            fp = os.path.join(bmp_dir, f)
            print(f"  {f}: {os.path.getsize(fp)} bytes")
    else:
        print(f"No bitmaps directory at {bmp_dir}")

    # Check the N2D data for the bitmap buffers
    print("\n=== Checking N2D bitmap buffers ===")
    import msgpack
    with open(n2d_path, 'rb') as f:
        # It's a zip
        import zipfile
        with zipfile.ZipFile(f) as zf:
            # Find the data file
            for name in zf.namelist():
                if name.endswith('.msgpack') or name.endswith('.n2d'):
                    print(f"  Found: {name}")
            # Read the msgpack
            for name in zf.namelist():
                if name.endswith('.msgpack'):
                    data = msgpack.unpackb(zf.read(name), raw=False)
                    break
    
    libs = data.get('libraries', [])
    bitmaps = [l for l in libs if l.get('type') == 'bitmap']
    print(f"Total bitmap entries: {len(bitmaps)}")
    
    # Check which ones have buffer vs externalFile
    has_buffer = sum(1 for b in bitmaps if b.get('buffer'))
    has_external = sum(1 for b in bitmaps if b.get('externalFile'))
    no_data = sum(1 for b in bitmaps if not b.get('buffer') and not b.get('externalFile'))
    print(f"  With buffer: {has_buffer}")
    print(f"  With externalFile: {has_external}")
    print(f"  No data: {no_data}")
    
    # Check buffer sizes vs expected w*h*4
    size_mismatches = []
    for b in bitmaps:
        w = b.get('width', 0)
        h = b.get('height', 0)
        buf = b.get('buffer', '')
        if buf:
            if isinstance(buf, str):
                if buf.startswith('b64:'):
                    import base64
                    raw = base64.b64decode(buf[4:])
                else:
                    raw = buf.encode('latin-1')
            else:
                raw = buf
            expected = w * h * 4
            if len(raw) != expected:
                size_mismatches.append((b['id'], w, h, len(raw), expected))
    
    if size_mismatches:
        print(f"\n  Buffer size mismatches: {len(size_mismatches)}")
        for bid, w, h, actual, expected in size_mismatches[:10]:
            print(f"    id={bid} {w}x{h}: buffer={actual} expected={expected}")
    else:
        print(f"  All buffers match expected size (w*h*4)")

if __name__ == '__main__':
    main()
