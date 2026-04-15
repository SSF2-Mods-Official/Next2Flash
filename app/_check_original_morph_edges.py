"""Compare morph start-edge fill convention between original and roundtrip."""
import struct, zlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

def parse_morph_start_info(path):
    """Return list of (charId, tag_type, fill0, fill1, line, edge_count) for each morph."""
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('B', f.read(1))[0]
        flen = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4  # skip frame rate + frame count
    
    morphs = []
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        tag_start = pos
        if tt in (46, 84):
            body = rest[pos:pos+ll]
            cid = struct.unpack_from('<H', body, 0)[0]
            
            # Count total edges by scanning raw bits
            # We'll just record the first StyleChange flags
            br = BitReader(body, 2)
            # Skip start bounds + end bounds
            for _ in range(2):
                nb = br.read_ub(5)
                for __ in range(4): br.read_sb(nb)
                br.align()
            if tt == 84:
                for _ in range(2):
                    nb = br.read_ub(5)
                    for __ in range(4): br.read_sb(nb)
                    br.align()
                br.read_ui8()  # reserved
            br.align()
            
            offset = struct.unpack_from('<I', body, br.byte_pos)[0]
            br.byte_pos += 4
            
            # Skip fill styles
            fc = br.read_ui8()
            if fc == 0xFF: fc = br.read_ui16()
            for _ in range(fc):
                ft = br.read_ui8()
                if ft == 0x00:
                    br.byte_pos += 8  # 2x RGBA
                elif ft in (0x10, 0x12, 0x13):
                    for __ in range(2):  # 2 matrices
                        hs = br.read_ub(1)
                        if hs:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        hr = br.read_ub(1)
                        if hr:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                    ng = br.read_ui8()
                    br.byte_pos += ng * 10
                elif ft in (0x40, 0x41, 0x42, 0x43):
                    br.byte_pos += 2  # bitmap id (start+end same)
                    for __ in range(2):
                        hs = br.read_ub(1)
                        if hs:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        hr = br.read_ub(1)
                        if hr:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
            
            # Skip line styles
            lc = br.read_ui8()
            if lc == 0xFF: lc = br.read_ui16()
            if tt == 46:
                br.byte_pos += lc * 12  # 2 widths + 2x RGBA
            else:
                for _ in range(lc):
                    br.byte_pos += 4  # 2 widths
                    flags2 = struct.unpack_from('<H', body, br.byte_pos)[0]
                    br.byte_pos += 2
                    join = (flags2 >> 2) & 3
                    has_fill = (flags2 >> 4) & 1
                    if join == 2: br.byte_pos += 2  # miter
                    if has_fill:
                        sfc = br.read_ui8()
                        if sfc == 0xFF: sfc = br.read_ui16()
                        for __ in range(sfc):
                            sft = br.read_ui8()
                            if sft == 0x00: br.byte_pos += 8
                            elif sft in (0x10, 0x12, 0x13):
                                for ___ in range(2):
                                    hs = br.read_ub(1)
                                    if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    hr = br.read_ub(1)
                                    if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                                ng = br.read_ui8()
                                br.byte_pos += ng * 10
                            elif sft in (0x40, 0x41, 0x42, 0x43):
                                br.byte_pos += 2
                                for ___ in range(2):
                                    hs = br.read_ub(1)
                                    if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    hr = br.read_ub(1)
                                    if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                    else:
                        br.byte_pos += 8  # 2x RGBA
            
            # Now at start shape edges
            sfb = br.read_ub(4)
            slb = br.read_ub(4)
            
            # Count ALL edge records (not just first style change)
            edge_count = 0
            style_changes = []
            while True:
                tf = br.read_ub(1)
                if tf == 1:  # edge
                    sf = br.read_ub(1)
                    if sf == 1:  # straight
                        nb = br.read_ub(4) + 2
                        gf = br.read_ub(1)
                        if gf == 1:
                            br.read_sb(nb); br.read_sb(nb)
                        else:
                            vl = br.read_ub(1)
                            br.read_sb(nb)
                    else:  # curved
                        nb = br.read_ub(4) + 2
                        br.read_sb(nb); br.read_sb(nb)
                        br.read_sb(nb); br.read_sb(nb)
                    edge_count += 1
                else:
                    flags = br.read_ub(5)
                    if flags == 0:
                        break  # EndShapeRecord
                    has_move = flags & 0x01
                    has_f0 = (flags >> 1) & 1
                    has_f1 = (flags >> 2) & 1
                    has_ln = (flags >> 3) & 1
                    has_new = (flags >> 4) & 1
                    
                    f0v = f1v = lnv = 0
                    if has_move:
                        mb = br.read_ub(5)
                        br.read_sb(mb); br.read_sb(mb)
                    if has_f0:
                        f0v = br.read_ub(sfb)
                    if has_f1:
                        f1v = br.read_ub(sfb)
                    if has_ln:
                        lnv = br.read_ub(slb)
                    if has_new:
                        # skip new styles (shouldn't happen in morph)
                        pass
                    style_changes.append((has_f0, f0v, has_f1, f1v, has_ln, lnv))
            
            morphs.append({
                'cid': cid,
                'tag': tt,
                'fill_bits': sfb,
                'line_bits': slb,
                'edge_count': edge_count,
                'style_changes': style_changes,
            })
        pos = tag_start + ll
    return morphs

orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
rt = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd_rt.swf")

print("=== ORIGINAL ===")
orig_morphs = parse_morph_start_info(orig)
for m in orig_morphs:
    sc = m['style_changes']
    sc_str = " | ".join(f"f0={s[0]}({s[1]}) f1={s[2]}({s[3]}) ln={s[4]}({s[5]})" for s in sc)
    print(f"  cid={m['cid']:4d} tag={m['tag']} fb={m['fill_bits']} lb={m['line_bits']} edges={m['edge_count']:3d}: {sc_str}")
print(f"  Total: {len(orig_morphs)}")

print()
print("=== ROUNDTRIP ===")
rt_morphs = parse_morph_start_info(rt)
for m in rt_morphs:
    sc = m['style_changes']
    sc_str = " | ".join(f"f0={s[0]}({s[1]}) f1={s[2]}({s[3]}) ln={s[4]}({s[5]})" for s in sc)
    print(f"  cid={m['cid']:4d} tag={m['tag']} fb={m['fill_bits']} lb={m['line_bits']} edges={m['edge_count']:3d}: {sc_str}")
print(f"  Total: {len(rt_morphs)}")

# Summary comparison
print("\n=== SUMMARY ===")
print(f"Original: {len(orig_morphs)} morphs")
print(f"Roundtrip: {len(rt_morphs)} morphs")

orig_f0 = sum(1 for m in orig_morphs if all(s[0] for s in m['style_changes']) and not any(s[2] for s in m['style_changes']))
orig_f1 = sum(1 for m in orig_morphs if not any(s[0] for s in m['style_changes']) and all(s[2] for s in m['style_changes']))
rt_f0 = sum(1 for m in rt_morphs if all(s[0] for s in m['style_changes']) and not any(s[2] for s in m['style_changes']))
rt_f1 = sum(1 for m in rt_morphs if not any(s[0] for s in m['style_changes']) and all(s[2] for s in m['style_changes']))
print(f"Original:  fill0-only={orig_f0}  fill1-only={orig_f1}")
print(f"Roundtrip: fill0-only={rt_f0}  fill1-only={rt_f1}")
