"""Compare morph start edges: original vs roundtrip using swf_to_n2d parser."""
import os, sys, struct, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

def iter_tags(path):
    """Yield (tag_type, tag_body_bytes) for each tag in an SWF."""
    with open(path, 'rb') as f:
        sig = f.read(3)
        f.read(1)  # version
        flen = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        body = rest[pos:pos+ll]
        pos += ll
        yield tt, body

def analyze_morph_edges_raw(body, tag_type):
    """Parse a morph tag and extract start edge fill convention flags."""
    cid = struct.unpack_from('<H', body, 0)[0]
    br = BitReader(body, 2)
    
    # Skip startBounds, endBounds
    for _ in range(2):
        nb = br.read_ub(5)
        for __ in range(4): br.read_sb(nb)
        br.align()
    
    if tag_type == 84:
        # Skip startEdgeBounds, endEdgeBounds
        for _ in range(2):
            nb = br.read_ub(5)
            for __ in range(4): br.read_sb(nb)
            br.align()
        br.read_ui8()  # reserved
    br.align()
    
    # Read offset
    offset = struct.unpack_from('<I', body, br.byte_pos)[0]
    offset_byte = br.byte_pos + 4  # byte after offset field
    br.byte_pos += 4
    
    # Instead of parsing styles, use the offset to find end of start edges,
    # then scan from after styles to find the SHAPE header
    # We need to actually skip style arrays to find the edge data
    
    # Skip MorphFillStyleArray
    try:
        fc = br.read_ui8()
        if fc == 0xFF:
            fc = br.read_ui16()
        for i in range(fc):
            ft = br.read_ui8()
            if ft == 0x00:
                br.byte_pos += 8  # 2x RGBA
            elif ft in (0x10, 0x12, 0x13):
                # 2 gradient matrices + gradient records
                for __ in range(2):
                    hs = br.read_ub(1)
                    if hs:
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                    hr = br.read_ub(1)
                    if hr:
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                    nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                    br.align()
                ng = br.read_ui8()
                br.byte_pos += ng * 10  # RGBA+ratio * 2 for each stop
            elif ft in (0x40, 0x41, 0x42, 0x43):
                br.byte_pos += 2  # bitmapId
                for __ in range(2):
                    hs = br.read_ub(1)
                    if hs:
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                    hr = br.read_ub(1)
                    if hr:
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                    nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                    br.align()
            else:
                return {'cid': cid, 'tag': tag_type, 'error': f'unknown fill type 0x{ft:02X} at fill #{i}'}
        
        # Skip MorphLineStyleArray
        lc = br.read_ui8()
        if lc == 0xFF:
            lc = br.read_ui16()
        if tag_type == 46:
            # MorphLineStyle: 2 widths + 2x RGBA = 12 bytes each
            br.byte_pos += lc * 12
        else:
            # MorphLineStyle2
            for _ in range(lc):
                sw = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2  # startWidth
                ew = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2  # endWidth
                flags = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2
                start_cap = flags & 3
                join = (flags >> 2) & 3
                has_fill = (flags >> 4) & 1
                no_hscale = (flags >> 5) & 1
                no_vscale = (flags >> 6) & 1
                pixel_hint = (flags >> 7) & 1
                no_close = (flags >> 8) & 1
                end_cap = (flags >> 10) & 3
                if join == 2:
                    br.byte_pos += 2  # miterLimitFactor (UI16 fixed 8.8)
                if has_fill:
                    # Fill style (same format as fill styles above)
                    ft = br.read_ui8()
                    if ft == 0x00:
                        br.byte_pos += 8
                    elif ft in (0x10, 0x12, 0x13):
                        for __ in range(2):
                            hs = br.read_ub(1)
                            if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                            hr = br.read_ub(1)
                            if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                            nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                        ng = br.read_ui8()
                        br.byte_pos += ng * 10
                    elif ft in (0x40, 0x41, 0x42, 0x43):
                        br.byte_pos += 2
                        for __ in range(2):
                            hs = br.read_ub(1)
                            if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                            hr = br.read_ub(1)
                            if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                            nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                else:
                    br.byte_pos += 8  # start RGBA + end RGBA
        
        # Now at start edges!
        sfb = br.read_ub(4)
        slb = br.read_ub(4)
        
        # Parse all edge records
        edge_count = 0
        style_changes = []
        while True:
            tf = br.read_ub(1)
            if tf == 1:  # edge record
                sf = br.read_ub(1)
                if sf == 1:  # straight
                    nb = br.read_ub(4) + 2
                    gf = br.read_ub(1)
                    if gf:
                        br.read_sb(nb); br.read_sb(nb)
                    else:
                        br.read_ub(1); br.read_sb(nb)
                else:  # curved
                    nb = br.read_ub(4) + 2
                    br.read_sb(nb); br.read_sb(nb)
                    br.read_sb(nb); br.read_sb(nb)
                edge_count += 1
            else:
                flags = br.read_ub(5)
                if flags == 0:
                    break
                has_move = flags & 1
                has_f0 = (flags >> 1) & 1
                has_f1 = (flags >> 2) & 1
                has_ln = (flags >> 3) & 1
                has_new = (flags >> 4) & 1
                if has_move:
                    mb = br.read_ub(5)
                    br.read_sb(mb); br.read_sb(mb)
                f0v = br.read_ub(sfb) if has_f0 else 0
                f1v = br.read_ub(sfb) if has_f1 else 0
                lnv = br.read_ub(slb) if has_ln else 0
                style_changes.append({
                    'f0': has_f0, 'f0v': f0v,
                    'f1': has_f1, 'f1v': f1v,
                    'ln': has_ln, 'lnv': lnv,
                })
        
        return {
            'cid': cid, 'tag': tag_type,
            'fill_bits': sfb, 'line_bits': slb,
            'edges': edge_count, 'style_changes': style_changes,
        }
    except Exception as e:
        return {'cid': cid, 'tag': tag_type, 'error': str(e)}

def show(label, path):
    print(f"=== {label}: {os.path.basename(path)} ===")
    morphs = []
    for tt, body in iter_tags(path):
        if tt in (46, 84):
            info = analyze_morph_edges_raw(body, tt)
            morphs.append(info)
            if 'error' in info:
                print(f"  cid={info['cid']:4d} tag={info['tag']}: ERROR: {info['error']}")
            else:
                sc_parts = []
                for s in info['style_changes']:
                    sc_parts.append(f"f0={s['f0']}({s['f0v']}) f1={s['f1']}({s['f1v']}) ln={s['ln']}({s['lnv']})")
                sc_str = " | ".join(sc_parts) if sc_parts else "(no style changes?)"
                print(f"  cid={info['cid']:4d} tag={info['tag']}  fb={info['fill_bits']} lb={info['line_bits']}  edges={info['edges']:3d}  SC: {sc_str}")
    
    # Summary
    f0_only = sum(1 for m in morphs if 'error' not in m and all(s['f0'] and not s['f1'] for s in m['style_changes']))
    f1_only = sum(1 for m in morphs if 'error' not in m and all(not s['f0'] and s['f1'] for s in m['style_changes']))
    mixed = sum(1 for m in morphs if 'error' not in m and any(s['f0'] for s in m['style_changes']) and any(s['f1'] for s in m['style_changes']))
    errors = sum(1 for m in morphs if 'error' in m)
    print(f"  Total={len(morphs)} fill0_only={f0_only} fill1_only={f1_only} mixed={mixed} errors={errors}")
    return morphs

orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
rt = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd_rt.swf")

orig_morphs = show("ORIGINAL", orig)
print()
rt_morphs = show("ROUNDTRIP", rt)
