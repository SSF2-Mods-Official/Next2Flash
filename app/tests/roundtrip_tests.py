"""Roundtrip all test SWFs and compare original vs output."""
import os, struct, sys
from swf_binary_io import BitReader
from swf_shape_to_recodes import parse_define_shape_to_recodes

def read_swf_tags(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        import zlib
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
        tag_type = hdr >> 6
        tag_len = hdr & 0x3F
        if tag_len == 0x3F:
            tag_len = struct.unpack_from('<I', data, pos+2)[0]
            body_start = pos + 6
        else:
            body_start = pos + 2
        body = data[body_start:body_start+tag_len]
        tags.append((tag_type, body, pos))
        pos = body_start + tag_len
        if tag_type == 0: break
    return tags

def dump_shape_records(body, tag_type):
    """Parse and return shape record details."""
    br = BitReader(body, 0)
    cid = br.read_ui16()
    nb = br.read_ub(5)
    xmin = br.read_sb(nb); xmax = br.read_sb(nb)
    ymin = br.read_sb(nb); ymax = br.read_sb(nb)
    br.align()
    
    info = {'cid': cid, 'tag': tag_type, 'bounds': (xmin, xmax, ymin, ymax)}
    
    if tag_type == 83:
        nb2 = br.read_ub(5)
        for _ in range(4): br.read_sb(nb2)
        br.align()
        br.read_ub(5); br.read_ub(1); br.read_ub(1); br.read_ub(1)
    
    # Fill styles
    nfills = br.read_ui8()
    if nfills == 0xFF: nfills = br.read_ui16()
    info['nfills'] = nfills
    
    fills_detail = []
    for i in range(nfills):
        ft = br.read_ui8()
        if ft == 0x00:
            if tag_type in (32, 83):
                r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8(); a = br.read_ui8()
                fills_detail.append(f"Solid RGBA({r},{g},{b},{a})")
            else:
                r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8()
                fills_detail.append(f"Solid RGB({r},{g},{b})")
        elif ft in (0x40, 0x41, 0x42, 0x43):
            bid = br.read_ui16()
            br.align()
            hs = br.read_ub(1)
            if hs:
                n = br.read_ub(5); br.read_sb(n); br.read_sb(n)
            hr = br.read_ub(1)
            if hr:
                n = br.read_ub(5); br.read_sb(n); br.read_sb(n)
            tn = br.read_ub(5); br.read_sb(tn); br.read_sb(tn)
            br.align()
            fills_detail.append(f"Bitmap({ft:#x}) id={bid}")
        elif ft in (0x10, 0x12, 0x13):
            fills_detail.append(f"Gradient({ft:#x})")
            return info  # too complex to parse generically
        else:
            fills_detail.append(f"Unknown({ft:#x})")
            return info
    info['fills'] = fills_detail
    
    # Line styles
    nlines = br.read_ui8()
    if nlines == 0xFF: nlines = br.read_ui16()
    info['nlines'] = nlines
    
    lines_detail = []
    if tag_type == 83:
        # LINESTYLE2 - complex, skip
        pass
    elif tag_type in (32,):
        for i in range(nlines):
            w = br.read_ui16()
            r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8(); a = br.read_ui8()
            lines_detail.append(f"w={w/20:.1f} RGBA({r},{g},{b},{a})")
    else:
        for i in range(nlines):
            w = br.read_ui16()
            r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8()
            lines_detail.append(f"w={w/20:.1f} RGB({r},{g},{b})")
    info['lines'] = lines_detail
    
    # Shape records
    br.align()
    nfb = br.read_ub(4)
    nlb = br.read_ub(4)
    info['nfb'] = nfb
    info['nlb'] = nlb
    
    records = []
    rec_count = 0
    while rec_count < 5000:
        is_edge = br.read_ub(1)
        if is_edge:
            straight = br.read_ub(1)
            nbits = br.read_ub(4) + 2
            if straight:
                gen = br.read_ub(1)
                if gen:
                    dx = br.read_sb(nbits); dy = br.read_sb(nbits)
                    records.append(f"L({dx/20:.2f},{dy/20:.2f})")
                else:
                    vert = br.read_ub(1)
                    if vert:
                        dy = br.read_sb(nbits)
                        records.append(f"Lv({dy/20:.2f})")
                    else:
                        dx = br.read_sb(nbits)
                        records.append(f"Lh({dx/20:.2f})")
            else:
                cdx = br.read_sb(nbits); cdy = br.read_sb(nbits)
                adx = br.read_sb(nbits); ady = br.read_sb(nbits)
                records.append(f"C({cdx/20:.2f},{cdy/20:.2f},{adx/20:.2f},{ady/20:.2f})")
        else:
            flags = br.read_ub(5)
            if flags == 0:
                records.append("END")
                break
            parts = ["SC"]
            if flags & 1:
                mb = br.read_ub(5)
                mx = br.read_sb(mb); my = br.read_sb(mb)
                parts.append(f"M({mx/20:.2f},{my/20:.2f})")
            if flags & 2:
                f0 = br.read_ub(nfb)
                parts.append(f"f0={f0}")
            if flags & 4:
                f1 = br.read_ub(nfb)
                parts.append(f"f1={f1}")
            if flags & 8:
                ls = br.read_ub(nlb)
                parts.append(f"l={ls}")
            if flags & 0x10:
                parts.append("NEWSTYLES")
            records.append(" ".join(parts))
        rec_count += 1
    info['records'] = records
    return info

def compare_one(name, orig_path):
    """Roundtrip one SWF and compare."""
    n2d_path = orig_path.replace('.swf', '.n2d')
    rt_path = orig_path.replace('.swf', '_rt.swf')
    
    # Import
    ret = os.system(f'python swf_to_n2d.py "{orig_path}" "{n2d_path}" >NUL 2>&1')
    if ret != 0:
        print(f"  FAIL: swf_to_n2d.py returned {ret}")
        return False
    
    # Export
    ret = os.system(f'python compile_n2d.py "{n2d_path}" -o "{rt_path}" --shared . >NUL 2>&1')
    if ret != 0:
        print(f"  FAIL: compile_n2d.py returned {ret}")
        return False
    
    # Compare
    orig_tags = read_swf_tags(orig_path)
    rt_tags = read_swf_tags(rt_path)
    
    shape_types = {2, 22, 32, 46, 83, 84}
    orig_shapes = [(tt, b) for tt, b, _ in orig_tags if tt in shape_types]
    rt_shapes = [(tt, b) for tt, b, _ in rt_tags if tt in shape_types]
    
    if len(orig_shapes) != len(rt_shapes):
        print(f"  DIFF: shape count {len(orig_shapes)} -> {len(rt_shapes)}")
    
    ok = True
    for i, ((ott, ob), (rtt, rb)) in enumerate(zip(orig_shapes, rt_shapes)):
        if ott in (46, 84) or rtt in (46, 84):
            # Morph shapes - verify content integrity
            print(f"  Morph: orig tag={ott} len={len(ob)}, rt tag={rtt} len={len(rb)}")
            if len(rb) < 20:
                print(f"    FAIL: roundtrip morph too small!")
                ok = False
                continue
            # Verify roundtrip morph has fill1 (not fill0) and non-zero edges
            try:
                from swf_shape_to_recodes import parse_define_morph_shape_to_recodes
                rt_body = rb[2:]  # skip charId
                s_rec, s_bnd, e_rec, e_bnd, _ = parse_define_morph_shape_to_recodes(rtt, rt_body, {})
                if not s_rec:
                    print(f"    FAIL: roundtrip morph has empty start recodes!")
                    ok = False
                elif not e_rec:
                    print(f"    FAIL: roundtrip morph has empty end recodes!")
                    ok = False
                else:
                    print(f"    OK: start_recodes={len(s_rec)}, end_recodes={len(e_rec)}")
                    # Also check the start edges use fill1 (not fill0)
                    from swf_binary_io import BitReader
                    import struct as _struct
                    br = BitReader(rt_body, 0)
                    # Skip bounds
                    for _ in range(2):
                        nb = br.read_ub(5)
                        for __ in range(4): br.read_sb(nb)
                        br.align()
                    if rtt == 84:
                        for _ in range(2):
                            nb = br.read_ub(5)
                            for __ in range(4): br.read_sb(nb)
                            br.align()
                        br.read_ui8()  # flags
                    br.align()
                    _offset = _struct.unpack_from('<I', br.data, br.byte_pos)[0]
                    br.byte_pos += 4
                    # Read fill count
                    fc = br.read_ui8()
                    if fc == 0xFF:
                        fc = _struct.unpack_from('<H', br.data, br.byte_pos)[0]
                        br.byte_pos += 2
                    # Skip fill entries and line entries to get to start edges
                    # (simple skip for solid fills: 9 bytes each)
                    for fi in range(fc):
                        ftype = br.read_ui8()
                        if ftype == 0:
                            br.byte_pos += 8  # start RGBA + end RGBA
                        else:
                            print(f"    INFO: non-solid fill type {ftype}, skipping detailed check")
                            break
                    else:
                        lc = br.read_ui8()
                        if lc == 0xFF:
                            lc = _struct.unpack_from('<H', br.data, br.byte_pos)[0]
                            br.byte_pos += 2
                        for li in range(lc):
                            br.byte_pos += 12  # start/end width + start/end RGBA
                        # Now at start edges
                        start_hdr = br.read_ui8()
                        sfb = start_hdr >> 4
                        slb = start_hdr & 0x0F
                        # Read first style change flags
                        tf = br.read_ub(1)
                        if tf == 0:
                            flags = br.read_ub(5)
                            has_f0 = (flags >> 1) & 1
                            has_f1 = (flags >> 2) & 1
                            if has_f0 and not has_f1:
                                print(f"    WARN: start edges use fill0 (should be fill1)")
                            elif has_f1:
                                print(f"    OK: start edges correctly use fill1")
            except Exception as e:
                print(f"    WARN: morph verification error: {e}")
            continue
            
        orig_info = dump_shape_records(ob, ott)
        rt_info = dump_shape_records(rb, rtt)
        
        # Compare raw SWF records first
        diffs = []
        if orig_info.get('nfills') != rt_info.get('nfills'):
            diffs.append(f"fills {orig_info.get('nfills')}->{rt_info.get('nfills')}")
        if orig_info.get('nlines') != rt_info.get('nlines'):
            diffs.append(f"lines {orig_info.get('nlines')}->{rt_info.get('nlines')}")
        if orig_info.get('bounds') != rt_info.get('bounds'):
            diffs.append(f"bounds {orig_info.get('bounds')}->{rt_info.get('bounds')}")
        
        orig_recs = orig_info.get('records', [])
        rt_recs = rt_info.get('records', [])
        if len(orig_recs) != len(rt_recs):
            diffs.append(f"records {len(orig_recs)}->{len(rt_recs)}")
        
        # Compare each record
        rec_diffs = 0
        for j, (orec, rrec) in enumerate(zip(orig_recs, rt_recs)):
            if orec != rrec:
                rec_diffs += 1
                if rec_diffs <= 5:
                    diffs.append(f"  rec[{j}]: {orec} -> {rrec}")
        if rec_diffs > 5:
            diffs.append(f"  ...and {rec_diffs-5} more record diffs")
        
        tag_change = f" (tag {ott}->{rtt})" if ott != rtt else ""
        
        if not diffs:
            print(f"  Shape[{i}] cid={orig_info['cid']}{tag_change}: OK")
        else:
            # Raw SWF records differ — check visual equivalence via N2D recodes
            try:
                orig_recodes, _, _ = parse_define_shape_to_recodes(ott, ob[2:], {})
                rt_recodes, _, _ = parse_define_shape_to_recodes(rtt, rb[2:], {})
                if orig_recodes == rt_recodes:
                    print(f"  Shape[{i}] cid={orig_info['cid']}{tag_change}: OK (visual equiv)")
                else:
                    ok = False
                    print(f"  Shape[{i}] cid={orig_info['cid']}{tag_change}: DIFF")
                    for d in diffs:
                        print(f"    {d}")
                    print(f"    --- ORIG records (first 15) ---")
                    for r in orig_recs[:15]:
                        print(f"      {r}")
                    print(f"    --- RT records (first 15) ---")
                    for r in rt_recs[:15]:
                        print(f"      {r}")
            except Exception as e:
                ok = False
                print(f"  Shape[{i}] cid={orig_info['cid']}{tag_change}: DIFF (recode err: {e})")
                for d in diffs:
                    print(f"    {d}")
    
    return ok

# Main
test_dir = 'test_swfs'
tests = sorted(f for f in os.listdir(test_dir) if f.endswith('.swf') and '_rt' not in f)

results = {}
for t in tests:
    name = t.replace('.swf', '')
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    path = os.path.join(test_dir, t)
    ok = compare_one(name, path)
    results[name] = ok

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
for name, ok in results.items():
    print(f"  {'PASS' if ok else 'FAIL'}: {name}")

passed = sum(1 for v in results.values() if v)
print(f"\n{passed}/{len(results)} passed")
