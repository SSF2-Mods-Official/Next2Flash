"""
Binary-level morph shape comparison: original vs roundtrip.
Dumps every field of a DefineMorphShape/DefineMorphShape2 tag for both files,
then shows exactly what differs.
"""
import struct, zlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader


def read_swf(path):
    """Read SWF file, return decompressed body after 8-byte header."""
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
    """Skip a RECT structure, return new byte position."""
    br = BitReader(data, pos)
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)
    br.align()
    return br.byte_pos


def parse_rect(data, pos):
    """Parse RECT, return (xmin, xmax, ymin, ymax, new_pos)."""
    br = BitReader(data, pos)
    nbits = br.read_ub(5)
    xmin = br.read_sb(nbits)
    xmax = br.read_sb(nbits)
    ymin = br.read_sb(nbits)
    ymax = br.read_sb(nbits)
    br.align()
    return (xmin, xmax, ymin, ymax), br.byte_pos


def extract_tags(swf_body):
    """Extract all tags from decompressed SWF body (after 8-byte header)."""
    # Skip movie RECT + framerate(2) + framecount(2)
    pos = skip_rect(swf_body, 0) + 4
    tags = []
    while pos < len(swf_body):
        tc = struct.unpack_from('<H', swf_body, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', swf_body, pos)[0]
            pos += 4
        tags.append((tt, swf_body[pos:pos+ll]))
        pos += ll
        if tt == 0:
            break
    return tags


def parse_fill_style_array(br, is_morph=True):
    """Parse MorphFillStyleArray. Returns list of fill style descriptions."""
    count = br.read_ui8()
    if count == 0xFF:
        count = br.read_ui16()
    fills = []
    for i in range(count):
        ftype = br.read_ui8()
        desc = f"type=0x{ftype:02X}"
        if ftype == 0x00:
            # Solid fill
            sr, sg, sb, sa = br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8()
            er, eg, eb, ea = br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8()
            desc += f" solid start=({sr},{sg},{sb},{sa}) end=({er},{eg},{eb},{ea})"
        elif ftype in (0x10, 0x12, 0x13):
            # Gradient fill - read start+end matrices and gradient
            desc += f" gradient (skipping details)"
            # Start matrix
            _skip_matrix(br)
            # End matrix
            _skip_matrix(br)
            # Gradient
            num_grad = br.read_ui8()
            for _ in range(num_grad):
                br.read_ui8()  # start ratio
                br.read_ui8(); br.read_ui8(); br.read_ui8(); br.read_ui8()  # start RGBA
                br.read_ui8()  # end ratio
                br.read_ui8(); br.read_ui8(); br.read_ui8(); br.read_ui8()  # end RGBA
        elif ftype in (0x40, 0x41, 0x42, 0x43):
            # Bitmap fill
            bitmap_id = br.read_ui16()
            desc += f" bitmap id={bitmap_id}"
            _skip_matrix(br)  # start matrix
            _skip_matrix(br)  # end matrix
        else:
            desc += " UNKNOWN"
        fills.append(desc)
    return fills


def _skip_matrix(br):
    """Skip a MATRIX structure."""
    has_scale = br.read_ub(1)
    if has_scale:
        nb = br.read_ub(5)
        br.read_sb(nb)  # scaleX (fixed)
        br.read_sb(nb)  # scaleY
    has_rotate = br.read_ub(1)
    if has_rotate:
        nb = br.read_ub(5)
        br.read_sb(nb)
        br.read_sb(nb)
    nb = br.read_ub(5)
    br.read_sb(nb)  # translateX
    br.read_sb(nb)  # translateY
    br.align()


def parse_line_style_array(br, tag_type):
    """Parse MorphLineStyleArray. Returns list of line style descriptions."""
    count = br.read_ui8()
    if count == 0xFF:
        count = br.read_ui16()
    lines = []
    for i in range(count):
        if tag_type == 46:
            # MorphLineStyle
            sw = br.read_ui16()
            ew = br.read_ui16()
            sr, sg, sb, sa = br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8()
            er, eg, eb, ea = br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8()
            lines.append(f"width start={sw} end={ew} start=({sr},{sg},{sb},{sa}) end=({er},{eg},{eb},{ea})")
        else:
            # MorphLineStyle2
            sw = br.read_ui16()
            ew = br.read_ui16()
            start_cap = br.read_ub(2)
            join_style = br.read_ub(2)
            has_fill = br.read_ub(1)
            no_hscale = br.read_ub(1)
            no_vscale = br.read_ub(1)
            pixel_hint = br.read_ub(1)
            reserved = br.read_ub(5)
            no_close = br.read_ub(1)
            end_cap = br.read_ub(2)
            if join_style == 2:
                br.read_ui16()  # miter limit (fixed8)
            desc = f"width start={sw} end={ew} caps={start_cap}/{end_cap} join={join_style} hasFill={has_fill}"
            if has_fill:
                # Read fill style (single, not array)
                fills = parse_fill_style_array(br, is_morph=True)
                desc += f" fill={fills}"
            else:
                sr, sg, sb, sa = br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8()
                er, eg, eb, ea = br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8()
                desc += f" start=({sr},{sg},{sb},{sa}) end=({er},{eg},{eb},{ea})"
            lines.append(desc)
    return lines


def parse_shape_edges(br, label, max_records=50):
    """Parse shape record bitstream. Returns list of record descriptions."""
    num_fill_bits = br.read_ub(4)
    num_line_bits = br.read_ub(4)
    records = []
    records.append(f"  [{label}] NumFillBits={num_fill_bits} NumLineBits={num_line_bits}")

    cur_fill_bits = num_fill_bits
    cur_line_bits = num_line_bits

    for _ in range(max_records):
        type_flag = br.read_ub(1)
        if type_flag == 0:
            # Non-edge
            flags = br.read_ub(5)
            if flags == 0:
                records.append(f"    EndShapeRecord")
                br.align()
                break
            desc = "    StyleChange:"
            if flags & 0x01:
                mb = br.read_ub(5)
                mx = br.read_sb(mb)
                my = br.read_sb(mb)
                desc += f" MoveTo({mx},{my})[{mb}bits]"
            if flags & 0x02:
                f0 = br.read_ub(cur_fill_bits)
                desc += f" Fill0={f0}"
            if flags & 0x04:
                f1 = br.read_ub(cur_fill_bits)
                desc += f" Fill1={f1}"
            if flags & 0x08:
                ln = br.read_ub(cur_line_bits)
                desc += f" Line={ln}"
            if flags & 0x10:
                desc += " NewStyles!"
                # Parse new fill/line style arrays and new bit counts
                # This is complex, just note it
                records.append(desc)
                records.append("    [NewStyles encountered - stopping parse]")
                break
            records.append(desc)
        else:
            # Edge record
            straight = br.read_ub(1)
            if straight:
                nb = br.read_ub(4) + 2
                gen_line = br.read_ub(1)
                if gen_line:
                    dx = br.read_sb(nb)
                    dy = br.read_sb(nb)
                    records.append(f"    StraightEdge({dx},{dy})[{nb}bits]")
                else:
                    vert = br.read_ub(1)
                    if vert:
                        dy = br.read_sb(nb)
                        records.append(f"    VLine({dy})[{nb}bits]")
                    else:
                        dx = br.read_sb(nb)
                        records.append(f"    HLine({dx})[{nb}bits]")
            else:
                nb = br.read_ub(4) + 2
                cx = br.read_sb(nb)
                cy = br.read_sb(nb)
                ax = br.read_sb(nb)
                ay = br.read_sb(nb)
                records.append(f"    CurvedEdge(ctrl={cx},{cy} anchor={ax},{ay})[{nb}bits]")
    else:
        records.append(f"    ... (truncated at {max_records} records)")
    return records


def dump_morph_tag(body, tag_type):
    """Full dump of a DefineMorphShape(2) tag body."""
    lines = []
    char_id = struct.unpack_from('<H', body, 0)[0]
    lines.append(f"CharacterID: {char_id}")
    lines.append(f"TagType: {tag_type} ({'DefineMorphShape2' if tag_type == 84 else 'DefineMorphShape'})")
    lines.append(f"Body length: {len(body)} bytes")

    br = BitReader(body, 2)

    # StartBounds
    sb, _ = parse_rect(body, br.byte_pos)
    br.byte_pos = skip_rect(body, br.byte_pos)
    lines.append(f"StartBounds: xmin={sb[0]} xmax={sb[1]} ymin={sb[2]} ymax={sb[3]}")

    # EndBounds
    eb, _ = parse_rect(body, br.byte_pos)
    br.byte_pos = skip_rect(body, br.byte_pos)
    lines.append(f"EndBounds: xmin={eb[0]} xmax={eb[1]} ymin={eb[2]} ymax={eb[3]}")

    if tag_type == 84:
        # StartEdgeBounds
        seb, _ = parse_rect(body, br.byte_pos)
        br.byte_pos = skip_rect(body, br.byte_pos)
        lines.append(f"StartEdgeBounds: xmin={seb[0]} xmax={seb[1]} ymin={seb[2]} ymax={seb[3]}")

        # EndEdgeBounds
        eeb, _ = parse_rect(body, br.byte_pos)
        br.byte_pos = skip_rect(body, br.byte_pos)
        lines.append(f"EndEdgeBounds: xmin={eeb[0]} xmax={eeb[1]} ymin={eeb[2]} ymax={eeb[3]}")

        # UsesNonScalingStrokes + UsesScalingStrokes
        flags = br.read_ui8()
        lines.append(f"MorphShape2 flags: 0x{flags:02X}")

    # Offset
    offset = struct.unpack_from('<I', body, br.byte_pos)[0]
    br.byte_pos += 4
    offset_field_pos = br.byte_pos - 4
    lines.append(f"Offset: {offset} (field at byte {offset_field_pos} in body)")
    after_offset_pos = br.byte_pos
    lines.append(f"After-offset position: {after_offset_pos}")

    # MorphFillStyleArray
    fill_start = br.byte_pos
    try:
        fills = parse_fill_style_array(br, is_morph=True)
        lines.append(f"FillStyles ({len(fills)}) starting at byte {fill_start}:")
        for i, f in enumerate(fills):
            lines.append(f"  [{i+1}] {f}")
    except Exception as e:
        lines.append(f"FillStyles: ERROR parsing: {e}")
        return lines

    # MorphLineStyleArray
    line_start = br.byte_pos
    try:
        lstyles = parse_line_style_array(br, tag_type)
        lines.append(f"LineStyles ({len(lstyles)}) starting at byte {line_start}:")
        for i, l in enumerate(lstyles):
            lines.append(f"  [{i+1}] {l}")
    except Exception as e:
        lines.append(f"LineStyles: ERROR parsing: {e}")
        return lines

    # Start edges
    start_edge_pos = br.byte_pos
    lines.append(f"StartEdges at byte {start_edge_pos}:")
    try:
        start_records = parse_shape_edges(br, "START", max_records=100)
        lines.extend(start_records)
    except Exception as e:
        lines.append(f"  ERROR parsing start edges: {e}")
        return lines

    # End edges - should be at after_offset_pos + offset
    expected_end_pos = after_offset_pos + offset
    actual_end_pos = br.byte_pos
    lines.append(f"EndEdges expected at byte {expected_end_pos}, actually at byte {actual_end_pos} (delta={actual_end_pos - expected_end_pos})")

    # Use the offset-based position
    br.byte_pos = expected_end_pos
    br.bit_pos = 0
    lines.append(f"EndEdges at byte {br.byte_pos}:")
    try:
        end_records = parse_shape_edges(br, "END", max_records=100)
        lines.extend(end_records)
    except Exception as e:
        lines.append(f"  ERROR parsing end edges: {e}")

    # Raw hex dump of first 64 and last 32 bytes
    lines.append(f"Raw hex (first 80 bytes): {body[:80].hex()}")
    lines.append(f"Raw hex (last 40 bytes): {body[-40:].hex()}")

    return lines


def get_morph_tags(swf_path):
    """Extract all morph tags from an SWF, keyed by charId."""
    body, ver = read_swf(swf_path)
    tags = extract_tags(body)
    morphs = {}
    for tt, tbody in tags:
        if tt in (46, 84):
            cid = struct.unpack_from('<H', tbody, 0)[0]
            morphs[cid] = (tt, tbody)
    return morphs


def main():
    orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
    rt = "test_swfs/lloyd_rt.swf"

    if not os.path.exists(rt):
        print("Roundtrip file not found, generating...")
        os.system(f'python swf_to_n2d.py "{orig}" "test_swfs/lloyd_rt.n2d" >NUL 2>&1')
        os.system(f'python compile_n2d.py "test_swfs/lloyd_rt.n2d" -o "{rt}" --shared . >NUL 2>&1')

    print("Loading original...")
    orig_morphs = get_morph_tags(orig)
    print(f"  Found {len(orig_morphs)} morph tags: {sorted(orig_morphs.keys())}")

    print("Loading roundtrip...")
    rt_morphs = get_morph_tags(rt)
    print(f"  Found {len(rt_morphs)} morph tags: {sorted(rt_morphs.keys())}")

    # Find common charIds
    common = sorted(set(orig_morphs.keys()) & set(rt_morphs.keys()))
    print(f"\nCommon charIds: {common}")

    if not common:
        print("\nNo common charIds! Listing all:")
        print(f"  Original: {sorted(orig_morphs.keys())}")
        print(f"  Roundtrip: {sorted(rt_morphs.keys())}")
        # Just dump the first from each
        if orig_morphs:
            cid = sorted(orig_morphs.keys())[0]
            tt, body = orig_morphs[cid]
            print(f"\n=== ORIGINAL charId={cid} ===")
            for line in dump_morph_tag(body, tt):
                print(line)
        if rt_morphs:
            cid = sorted(rt_morphs.keys())[0]
            tt, body = rt_morphs[cid]
            print(f"\n=== ROUNDTRIP charId={cid} ===")
            for line in dump_morph_tag(body, tt):
                print(line)
        return

    # Compare first common morph in detail
    cid = common[0]
    orig_tt, orig_body = orig_morphs[cid]
    rt_tt, rt_body = rt_morphs[cid]

    print(f"\n{'='*60}")
    print(f"=== COMPARING charId={cid} ===")
    print(f"{'='*60}")

    print(f"\n--- ORIGINAL (tag {orig_tt}, {len(orig_body)} bytes) ---")
    orig_lines = dump_morph_tag(orig_body, orig_tt)
    for line in orig_lines:
        print(line)

    print(f"\n--- ROUNDTRIP (tag {rt_tt}, {len(rt_body)} bytes) ---")
    rt_lines = dump_morph_tag(rt_body, rt_tt)
    for line in rt_lines:
        print(line)

    # Side-by-side diff
    print(f"\n{'='*60}")
    print("=== DIFFERENCES ===")
    print(f"{'='*60}")
    max_lines = max(len(orig_lines), len(rt_lines))
    diffs = 0
    for i in range(max_lines):
        ol = orig_lines[i] if i < len(orig_lines) else "<missing>"
        rl = rt_lines[i] if i < len(rt_lines) else "<missing>"
        if ol != rl:
            diffs += 1
            print(f"Line {i}:")
            print(f"  ORIG: {ol}")
            print(f"  RT:   {rl}")
    if diffs == 0:
        print("  No differences found!")
    else:
        print(f"\n{diffs} differences found")

    # Also compare second morph if available
    if len(common) > 1:
        cid2 = common[1]
        orig_tt2, orig_body2 = orig_morphs[cid2]
        rt_tt2, rt_body2 = rt_morphs[cid2]
        print(f"\n{'='*60}")
        print(f"=== COMPARING charId={cid2} (second morph) ===")
        print(f"{'='*60}")
        orig_lines2 = dump_morph_tag(orig_body2, orig_tt2)
        rt_lines2 = dump_morph_tag(rt_body2, rt_tt2)
        max_lines2 = max(len(orig_lines2), len(rt_lines2))
        diffs2 = 0
        for i in range(max_lines2):
            ol = orig_lines2[i] if i < len(orig_lines2) else "<missing>"
            rl = rt_lines2[i] if i < len(rt_lines2) else "<missing>"
            if ol != rl:
                diffs2 += 1
                print(f"Line {i}:")
                print(f"  ORIG: {ol}")
                print(f"  RT:   {rl}")
        if diffs2 == 0:
            print("  No differences found!")
        else:
            print(f"\n{diffs2} differences found")


if __name__ == "__main__":
    main()
