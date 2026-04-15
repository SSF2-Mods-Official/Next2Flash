"""Debug: examine original shape cid=235 vs roundtrip equivalent."""
from swf_binary_io import BitReader
import struct

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        import zlib
        body = zlib.decompress(data[8:])
        flen = struct.unpack_from('<I', data, 4)[0]
        data = b'FWS' + data[3:8] + body[:flen-8]
    elif data[:3] == b'ZWS':
        import lzma
        body = lzma.decompress(data[12:])
        flen = struct.unpack_from('<I', data, 4)[0]
        data = b'FWS' + data[3:8] + body[:flen-8]
    return data

def get_tags(data):
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
        tag_type = hdr >> 6
        tag_len = hdr & 0x3F
        if tag_len == 0x3F:
            tag_len = struct.unpack_from('<I', data, pos+2)[0]
            body_start = pos + 6
        else:
            body_start = pos + 2
        body = data[body_start:body_start+tag_len]
        tags.append((tag_type, body))
        pos = body_start + tag_len
        if tag_type == 0: break
    return tags

def dump_shape(body, tag_type, label):
    print(f"\n=== {label}: tag={tag_type} bodyLen={len(body)} ===")
    br = BitReader(body, 0)
    cid = br.read_ui16()
    print(f"CharId: {cid}")
    nb = br.read_ub(5)
    xmin = br.read_sb(nb); xmax = br.read_sb(nb)
    ymin = br.read_sb(nb); ymax = br.read_sb(nb)
    br.align()
    print(f"Bounds: ({xmin/20:.1f},{ymin/20:.1f})-({xmax/20:.1f},{ymax/20:.1f})")

    if tag_type == 83:
        nb2 = br.read_ub(5)
        for _ in range(4): br.read_sb(nb2)
        br.align()
        br.read_ub(5)  # reserved + flags
        br.read_ub(1)
        br.read_ub(1)
        br.read_ub(1)

    nfills = br.read_ui8()
    if nfills == 0xFF: nfills = br.read_ui16()
    print(f"NumFillStyles: {nfills}")
    
    for i in range(nfills):
        ft = br.read_ui8()
        if ft == 0x00:
            if tag_type in (32, 83):
                r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8(); a = br.read_ui8()
                print(f"  Fill[{i+1}]: Solid RGBA({r},{g},{b},{a})")
            else:
                r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8()
                print(f"  Fill[{i+1}]: Solid RGB({r},{g},{b})")
        elif ft in (0x40, 0x41, 0x42, 0x43):
            bid = br.read_ui16()
            br.align()
            hs = br.read_ub(1)
            if hs:
                n = br.read_ub(5)
                sa = br.read_sb(n)/65536
                sd = br.read_sb(n)/65536
            else:
                sa = 1.0; sd = 1.0
            hr = br.read_ub(1)
            if hr:
                n = br.read_ub(5)
                sb = br.read_sb(n)/65536
                sc = br.read_sb(n)/65536
            else:
                sb = 0; sc = 0
            tn = br.read_ub(5)
            tx = br.read_sb(tn)
            ty = br.read_sb(tn)
            br.align()
            print(f"  Fill[{i+1}]: Bitmap type={ft:#x} bitmapId={bid} scale=({sa:.2f},{sd:.2f}) rot=({sb:.2f},{sc:.2f}) translate=({tx/20:.1f},{ty/20:.1f})")
        elif ft in (0x10, 0x12, 0x13):
            print(f"  Fill[{i+1}]: Gradient type={ft:#x} (skipping parse)")
            break
        else:
            print(f"  Fill[{i+1}]: Unknown type={ft:#x}")
            break

    nlines = br.read_ui8()
    if nlines == 0xFF: nlines = br.read_ui16()
    print(f"NumLineStyles: {nlines}")

    if tag_type in (2, 22):
        for i in range(nlines):
            w = br.read_ui16()
            r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8()
            print(f"  Line[{i+1}]: width={w/20:.1f}px RGB({r},{g},{b})")
    elif tag_type in (32,):
        for i in range(nlines):
            w = br.read_ui16()
            r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8(); a = br.read_ui8()
            print(f"  Line[{i+1}]: width={w/20:.1f}px RGBA({r},{g},{b},{a})")

    br.align()
    nfb = br.read_ub(4)
    nlb = br.read_ub(4)
    print(f"NumFillBits={nfb} NumLineBits={nlb}")

    count = 0
    while count < 60:
        is_edge = br.read_ub(1)
        if is_edge:
            straight = br.read_ub(1)
            nbits = br.read_ub(4) + 2
            if straight:
                gen = br.read_ub(1)
                if gen:
                    dx = br.read_sb(nbits)
                    dy = br.read_sb(nbits)
                    print(f"  StraightEdge dx={dx/20:.1f} dy={dy/20:.1f}")
                else:
                    vert = br.read_ub(1)
                    if vert:
                        dy = br.read_sb(nbits)
                        print(f"  StraightEdge dy={dy/20:.1f}")
                    else:
                        dx = br.read_sb(nbits)
                        print(f"  StraightEdge dx={dx/20:.1f}")
            else:
                cdx = br.read_sb(nbits)
                cdy = br.read_sb(nbits)
                adx = br.read_sb(nbits)
                ady = br.read_sb(nbits)
                print(f"  CurveEdge c=({cdx/20:.1f},{cdy/20:.1f}) a=({adx/20:.1f},{ady/20:.1f})")
        else:
            flags = br.read_ub(5)
            if flags == 0:
                print(f"  EndShape")
                break
            has_move = flags & 1
            has_f0 = (flags >> 1) & 1
            has_f1 = (flags >> 2) & 1
            has_line = (flags >> 3) & 1
            has_new_styles = (flags >> 4) & 1
            parts = []
            if has_move:
                mb = br.read_ub(5)
                mx = br.read_sb(mb)
                my = br.read_sb(mb)
                parts.append(f"move=({mx/20:.1f},{my/20:.1f})")
            if has_f0:
                f0 = br.read_ub(nfb)
                parts.append(f"fill0={f0}")
            if has_f1:
                f1 = br.read_ub(nfb)
                parts.append(f"fill1={f1}")
            if has_line:
                ls = br.read_ub(nlb)
                parts.append(f"line={ls}")
            if has_new_styles:
                parts.append("NEW_STYLES!")
                # read new style arrays
                nf2 = br.read_ui8()
                if nf2 == 0xFF: nf2 = br.read_ui16()
                parts.append(f"newFills={nf2}")
                # skip for now
            print(f"  StyleChange: {' '.join(parts)}")
        count += 1

# Original
orig = read_swf(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf')
orig_tags = get_tags(orig)

# Find shape 235
for tt, body in orig_tags:
    if tt in (2, 22, 32, 83):
        cid = struct.unpack_from('<H', body, 0)[0]
        if cid == 235:
            dump_shape(body, tt, "ORIGINAL cid=235")
            break

# Now find the equivalent in roundtrip
# The shape with bounds (-15.65, -18.95) to (31.30, 37.96) 
rt = read_swf('lloyd_roundtrip.swf')
rt_tags = get_tags(rt)

# Find shape 288 (from screenshot)
for tt, body in rt_tags:
    if tt in (2, 22, 32, 83):
        cid = struct.unpack_from('<H', body, 0)[0]
        if cid == 288:
            dump_shape(body, tt, "ROUNDTRIP cid=288")
            break
