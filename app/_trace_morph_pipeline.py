"""
Trace a single morph shape through the entire roundtrip pipeline:
1. Parse from original SWF binary
2. See what recodes the importer produces (from N2D)
3. See what the exporter encodes from those recodes
4. Compare original binary vs roundtrip binary field by field

Also checks edge counts match between start and end states.
"""
import struct, zlib, sys, os, json, msgpack
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader


def read_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('B', f.read(1))[0]
        flen = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    elif sig == b'ZWS':
        import lzma
        rest = lzma.decompress(rest)
    return rest, ver


def skip_rect(data, pos):
    br = BitReader(data, pos)
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)
    br.align()
    return br.byte_pos


def extract_morph_tags_ordered(swf_body):
    """Extract morph tags in order of appearance."""
    pos = skip_rect(swf_body, 0) + 4
    morphs = []
    while pos < len(swf_body):
        tc = struct.unpack_from('<H', swf_body, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', swf_body, pos)[0]
            pos += 4
        if tt in (46, 84):
            cid = struct.unpack_from('<H', swf_body[pos:pos+ll], 0)[0]
            morphs.append((tt, cid, swf_body[pos:pos+ll]))
        pos += ll
        if tt == 0:
            break
    return morphs


def count_shape_records(br, label=""):
    """Count edge records in a shape, return (edge_count, total_records, details)."""
    num_fill_bits = br.read_ub(4)
    num_line_bits = br.read_ub(4)
    cur_fill_bits = num_fill_bits
    cur_line_bits = num_line_bits
    
    edges = 0
    moves = 0
    style_changes = 0
    records = []
    
    for _ in range(500):
        type_flag = br.read_ub(1)
        if type_flag == 0:
            flags = br.read_ub(5)
            if flags == 0:
                records.append("EndShape")
                br.align()
                break
            desc = "SC("
            if flags & 0x01:
                mb = br.read_ub(5)
                mx = br.read_sb(mb)
                my = br.read_sb(mb)
                desc += f"mv={mx},{my} "
                moves += 1
            if flags & 0x02:
                f0 = br.read_ub(cur_fill_bits)
                desc += f"f0={f0} "
            if flags & 0x04:
                f1 = br.read_ub(cur_fill_bits)
                desc += f"f1={f1} "
            if flags & 0x08:
                ln = br.read_ub(cur_line_bits)
                desc += f"ln={ln} "
            if flags & 0x10:
                desc += "newStyles "
                records.append(desc + ")")
                records.append("[STOPPED: newStyles]")
                return edges, moves, style_changes, records, num_fill_bits, num_line_bits
            records.append(desc.strip() + ")")
            style_changes += 1
        else:
            straight = br.read_ub(1)
            if straight:
                nb = br.read_ub(4) + 2
                gen_line = br.read_ub(1)
                if gen_line:
                    dx = br.read_sb(nb)
                    dy = br.read_sb(nb)
                    records.append(f"L({dx},{dy})")
                else:
                    vert = br.read_ub(1)
                    if vert:
                        d = br.read_sb(nb)
                        records.append(f"VL({d})")
                    else:
                        d = br.read_sb(nb)
                        records.append(f"HL({d})")
            else:
                nb = br.read_ub(4) + 2
                cx = br.read_sb(nb)
                cy = br.read_sb(nb)
                ax = br.read_sb(nb)
                ay = br.read_sb(nb)
                records.append(f"C({cx},{cy},{ax},{ay})")
            edges += 1
    
    return edges, moves, style_changes, records, num_fill_bits, num_line_bits


def analyze_morph(body, tag_type, char_id, prefix=""):
    """Full analysis of a morph shape tag body."""
    br = BitReader(body, 2)
    
    # Bounds
    # StartBounds
    nb = br.read_ub(5)
    sb = [br.read_sb(nb) for _ in range(4)]
    br.align()
    # EndBounds
    nb = br.read_ub(5)
    eb = [br.read_sb(nb) for _ in range(4)]
    br.align()
    
    if tag_type == 84:
        # Edge bounds
        nb = br.read_ub(5)
        seb = [br.read_sb(nb) for _ in range(4)]
        br.align()
        nb = br.read_ub(5)
        eeb = [br.read_sb(nb) for _ in range(4)]
        br.align()
        flags = br.read_ui8()
    
    offset = struct.unpack_from('<I', br.data, br.byte_pos)[0]
    br.byte_pos += 4
    after_offset = br.byte_pos
    
    # Fill styles
    fc = br.read_ui8()
    if fc == 0xFF:
        fc = br.read_ui16()
    
    # Skip fill style bodies
    fills_start = br.byte_pos - (1 if fc < 0xFF else 3)
    for i in range(fc):
        ftype = br.read_ui8()
        if ftype == 0x00:
            br.byte_pos += 8  # 2 RGBA colors
        elif ftype in (0x10, 0x12, 0x13):
            _skip_matrix_br(br)
            _skip_matrix_br(br)
            ng = br.read_ui8()
            br.byte_pos += ng * 10  # ratio + RGBA x2
        elif ftype in (0x40, 0x41, 0x42, 0x43):
            br.byte_pos += 2  # bitmap id
            _skip_matrix_br(br)
            _skip_matrix_br(br)
    
    # Line styles
    lc = br.read_ui8()
    if lc == 0xFF:
        lc = br.read_ui16()
    for i in range(lc):
        if tag_type == 46:
            br.byte_pos += 12  # 2 widths + 2 RGBA
        else:
            br.byte_pos += 4  # 2 widths
            flags2 = br.read_ui16()
            join = (flags2 >> 2) & 3
            has_fill = (flags2 >> 4) & 1
            if join == 2:
                br.byte_pos += 2  # miter
            if has_fill:
                # Read a fill style
                sfc = br.read_ui8()
                if sfc == 0xFF:
                    sfc = br.read_ui16()
                for j in range(sfc):
                    sftype = br.read_ui8()
                    if sftype == 0x00:
                        br.byte_pos += 8
                    elif sftype in (0x10, 0x12, 0x13):
                        _skip_matrix_br(br)
                        _skip_matrix_br(br)
                        sng = br.read_ui8()
                        br.byte_pos += sng * 10
                    elif sftype in (0x40, 0x41, 0x42, 0x43):
                        br.byte_pos += 2
                        _skip_matrix_br(br)
                        _skip_matrix_br(br)
            else:
                br.byte_pos += 8  # 2 RGBA
    
    # Start edges
    start_edge_pos = br.byte_pos
    se, sm, ssc, srecs, sfb, slb = count_shape_records(br, "start")
    
    # End edges
    end_expected = after_offset + offset
    end_actual = br.byte_pos
    br.byte_pos = end_expected
    br.bit_pos = 0
    ee, em, esc, erecs, efb, elb = count_shape_records(br, "end")
    
    print(f"{prefix}charId={char_id} tag={tag_type} bodyLen={len(body)}")
    print(f"{prefix}  StartBounds: {sb}")
    print(f"{prefix}  EndBounds: {eb}")
    print(f"{prefix}  FillCount={fc} LineCount={lc} Offset={offset}")
    print(f"{prefix}  StartEdges at byte {start_edge_pos}: fill_bits={sfb} line_bits={slb}")
    print(f"{prefix}    edges={se} moves={sm} style_changes={ssc}")
    print(f"{prefix}    records: {' | '.join(srecs)}")
    print(f"{prefix}  EndEdges at byte {end_expected} (actual={end_actual}, delta={end_actual-end_expected}): fill_bits={efb} line_bits={elb}")
    print(f"{prefix}    edges={ee} moves={em} style_changes={esc}")
    print(f"{prefix}    records: {' | '.join(erecs)}")
    
    if se != ee:
        print(f"{prefix}  *** EDGE COUNT MISMATCH: start={se} end={ee} ***")
    if sm != em:
        print(f"{prefix}  *** MOVE COUNT MISMATCH: start={sm} end={em} ***")
    
    return {
        'tag': tag_type, 'body_len': len(body),
        'start_bounds': sb, 'end_bounds': eb,
        'fills': fc, 'lines': lc, 'offset': offset,
        'start_fb': sfb, 'start_lb': slb,
        'start_edges': se, 'start_moves': sm,
        'end_fb': efb, 'end_lb': elb,
        'end_edges': ee, 'end_moves': em,
        'start_records': srecs, 'end_records': erecs,
        'offset_delta': end_actual - end_expected,
    }


def _skip_matrix_br(br):
    has_scale = br.read_ub(1)
    if has_scale:
        nb = br.read_ub(5)
        br.read_sb(nb)
        br.read_sb(nb)
    has_rotate = br.read_ub(1)
    if has_rotate:
        nb = br.read_ub(5)
        br.read_sb(nb)
        br.read_sb(nb)
    nb = br.read_ub(5)
    br.read_sb(nb)
    br.read_sb(nb)
    br.align()


def main():
    orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
    n2d = "test_swfs/lloyd_rt.n2d"
    rt = "test_swfs/lloyd_rt.swf"
    
    # Always regenerate to pick up latest code
    print("Regenerating roundtrip...")
    os.system(f'python swf_to_n2d.py "{orig}" "{n2d}" >NUL 2>&1')
    os.system(f'python compile_n2d.py "{n2d}" -o "{rt}" --shared . >NUL 2>&1')
    
    print("\n=== ORIGINAL ===")
    orig_body, _ = read_swf(orig)
    orig_morphs = extract_morph_tags_ordered(orig_body)
    print(f"  {len(orig_morphs)} morph tags")
    
    print("\n=== ROUNDTRIP ===")
    rt_body, _ = read_swf(rt)
    rt_morphs = extract_morph_tags_ordered(rt_body)
    print(f"  {len(rt_morphs)} morph tags")
    
    # Compare ordinal pairs
    n = min(len(orig_morphs), len(rt_morphs))
    
    for i in range(min(n, 5)):  # Compare first 5
        print(f"\n{'='*70}")
        print(f"MORPH #{i}")
        print(f"{'='*70}")
        
        ott, ocid, obody = orig_morphs[i]
        rtt, rcid, rbody = rt_morphs[i]
        
        print(f"\n--- ORIGINAL ---")
        oinfo = analyze_morph(obody, ott, ocid, "  ")
        
        print(f"\n--- ROUNDTRIP ---")
        rinfo = analyze_morph(rbody, rtt, rcid, "  ")
        
        # Summary of differences
        print(f"\n--- DIFFERENCES ---")
        if oinfo['tag'] != rinfo['tag']:
            print(f"  TAG TYPE: {oinfo['tag']} -> {rinfo['tag']}")
        if oinfo['fills'] != rinfo['fills']:
            print(f"  FILL COUNT: {oinfo['fills']} -> {rinfo['fills']}")
        if oinfo['lines'] != rinfo['lines']:
            print(f"  LINE COUNT: {oinfo['lines']} -> {rinfo['lines']}")
        if oinfo['start_edges'] != rinfo['start_edges']:
            print(f"  START EDGE COUNT: {oinfo['start_edges']} -> {rinfo['start_edges']}")
        if oinfo['end_edges'] != rinfo['end_edges']:
            print(f"  END EDGE COUNT: {oinfo['end_edges']} -> {rinfo['end_edges']}")
        if oinfo['start_moves'] != rinfo['start_moves']:
            print(f"  START MOVE COUNT: {oinfo['start_moves']} -> {rinfo['start_moves']}")
        if oinfo['end_moves'] != rinfo['end_moves']:
            print(f"  END MOVE COUNT: {oinfo['end_moves']} -> {rinfo['end_moves']}")
        if oinfo['offset_delta'] != 0:
            print(f"  ORIG OFFSET DELTA: {oinfo['offset_delta']}")
        if rinfo['offset_delta'] != 0:
            print(f"  RT OFFSET DELTA: {rinfo['offset_delta']}")
        if oinfo['start_fb'] != rinfo['start_fb']:
            print(f"  START FILL_BITS: {oinfo['start_fb']} -> {rinfo['start_fb']}")


if __name__ == "__main__":
    main()
