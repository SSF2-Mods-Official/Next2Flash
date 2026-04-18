"""
Compare the tag-level structure of OG vs RT blackmage.ssf.
Focus on tag ordering, DoABC placement, SymbolClass, LL2/JPEG3 differences.
"""
import struct, zlib, sys, os

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

TAG_NAMES = {
    0: "End", 1: "ShowFrame", 2: "DefineShape", 4: "PlaceObject",
    5: "RemoveObject", 6: "DefineBits", 9: "SetBackgroundColor",
    10: "DefineFont", 11: "DefineText", 12: "DoAction",
    14: "DefineSound", 15: "StartSound", 20: "DefineBitsLossless",
    21: "DefineBitsJPEG2", 22: "DefineShape2", 24: "Protect",
    26: "PlaceObject2", 28: "RemoveObject2", 32: "DefineShape3",
    33: "DefineText2", 35: "DefineBitsJPEG3", 36: "DefineBitsLossless2",
    37: "DefineEditText", 39: "DefineSprite", 43: "FrameLabel",
    46: "DefineMorphShape", 48: "DefineFont2", 56: "ExportAssets",
    69: "FileAttributes", 70: "PlaceObject3", 72: "DoABC_legacy",
    73: "DefineFontAlignZones", 74: "CSMTextSettings", 75: "DefineFont3",
    76: "SymbolClass", 77: "Metadata", 78: "DefineScalingGrid",
    82: "DoABC", 83: "DefineShape4", 84: "DefineMorphShape2",
    86: "DefineSceneAndFrameLabelData", 87: "DefineBinaryData",
    88: "DefineFontName", 89: "StartSound2", 90: "DefineBitsJPEG4",
    91: "DefineFont4",
}

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    ver = data[3]
    file_len = struct.unpack_from('<I', data, 4)[0]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
    elif sig == b'ZWS':
        import lzma
        body = lzma.decompress(data[12:])
    else:
        body = data[8:]
    return sig, ver, file_len, body

def parse_rect(body, offset=0):
    """Parse SWF RECT from body, return (nbits, xmin, xmax, ymin, ymax, bytes_consumed)"""
    first = body[offset]
    nbits = first >> 3
    total_bits = 5 + nbits * 4
    total_bytes = (total_bits + 7) // 8
    return nbits, total_bytes

def parse_tags(body):
    """Parse SWF tags from body (after header)."""
    # Skip RECT
    _, rect_bytes = parse_rect(body)
    pos = rect_bytes
    # Frame rate (2 bytes) + frame count (2 bytes)
    fps_raw = struct.unpack_from('<H', body, pos)[0]
    fps = fps_raw >> 8
    pos += 2
    frame_count = struct.unpack_from('<H', body, pos)[0]
    pos += 2
    
    tags = []
    while pos < len(body):
        if pos + 2 > len(body):
            break
        tag_code_and_len = struct.unpack_from('<H', body, pos)[0]
        tag_type = tag_code_and_len >> 6
        tag_len = tag_code_and_len & 0x3F
        pos += 2
        if tag_len == 0x3F:
            if pos + 4 > len(body):
                break
            tag_len = struct.unpack_from('<I', body, pos)[0]
            pos += 4
        tag_body = body[pos:pos + tag_len]
        tags.append((tag_type, tag_len, tag_body, pos))
        pos += tag_len
        if tag_type == 0:  # End
            break
    
    return fps, frame_count, tags

def ll2_info(body):
    """Extract LL2 info: charID, format, width, height"""
    if len(body) < 7:
        return None
    cid = struct.unpack_from('<H', body, 0)[0]
    fmt = body[2]
    w = struct.unpack_from('<H', body, 3)[0]
    h = struct.unpack_from('<H', body, 5)[0]
    return cid, fmt, w, h

def jpeg3_info(body):
    """Extract JPEG3 charID and alpha data offset"""
    if len(body) < 6:
        return None
    cid = struct.unpack_from('<H', body, 0)[0]
    alpha_off = struct.unpack_from('<I', body, 2)[0]
    return cid, alpha_off

def symbolclass_info(body):
    """Parse SymbolClass entries"""
    if len(body) < 2:
        return []
    count = struct.unpack_from('<H', body, 0)[0]
    pos = 2
    entries = []
    for _ in range(count):
        if pos + 2 > len(body):
            break
        cid = struct.unpack_from('<H', body, pos)[0]
        pos += 2
        end = body.index(0, pos)
        name = body[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
        entries.append((cid, name))
    return entries

def doabc_info(body):
    """Parse DoABC tag: flags + name"""
    if len(body) < 4:
        return "too short"
    flags = struct.unpack_from('<I', body, 0)[0]
    end = body.index(0, 4)
    name = body[4:end].decode('utf-8', errors='replace')
    abc_size = len(body) - end - 1
    return f"flags={flags}, name='{name}', abc_size={abc_size}"

def main():
    for label, path in [("OG", OG), ("RT", RT)]:
        print(f"\n{'='*70}")
        print(f"  {label}: {path}")
        print(f"{'='*70}")
        
        if not os.path.exists(path):
            print(f"  FILE NOT FOUND!")
            continue
        
        sig, ver, file_len, body = read_swf(path)
        print(f"  Signature: {sig.decode()}, Version: {ver}, FileLength: {file_len}")
        print(f"  Body length (uncompressed): {len(body)}")
        
        fps, fc, tags = parse_tags(body)
        print(f"  FPS: {fps}, Frame count: {fc}")
        print(f"  Total tags: {len(tags)}")
        
        # Collect tag type counts
        type_counts = {}
        for tt, tl, tb, tp in tags:
            type_counts[tt] = type_counts.get(tt, 0) + 1
        
        print(f"\n  Tag type summary:")
        for tt in sorted(type_counts.keys()):
            name = TAG_NAMES.get(tt, f"Unknown({tt})")
            print(f"    {name}({tt}): {type_counts[tt]}")
        
        # Show first 30 tags (high-level structure)
        print(f"\n  First 30 tags (tag order):")
        for i, (tt, tl, tb, tp) in enumerate(tags[:30]):
            name = TAG_NAMES.get(tt, f"Unknown({tt})")
            extra = ""
            if tt == 36:  # LL2
                info = ll2_info(tb)
                if info:
                    extra = f" charID={info[0]}, fmt={info[1]}, {info[2]}x{info[3]}"
            elif tt == 35:  # JPEG3
                info = jpeg3_info(tb)
                if info:
                    extra = f" charID={info[0]}, alpha_off={info[1]}"
            elif tt == 82:  # DoABC
                extra = f" {doabc_info(tb)}"
            elif tt == 76:  # SymbolClass
                entries = symbolclass_info(tb)
                extra = f" {len(entries)} entries"
            print(f"    [{i:4d}] {name}({tt}) len={tl}{extra}")
        
        # Show tags around DoABC
        print(f"\n  Tags around DoABC:")
        for i, (tt, tl, tb, tp) in enumerate(tags):
            if tt in (82, 72):  # DoABC or DoABC_legacy
                name = TAG_NAMES.get(tt, f"Unknown({tt})")
                extra = doabc_info(tb) if tt == 82 else f"len={tl}"
                print(f"    [{i:4d}] {name}({tt}) {extra}")
                # Show 3 tags before and after
                for j in range(max(0, i-3), min(len(tags), i+4)):
                    if j == i:
                        continue
                    tt2, tl2, tb2, tp2 = tags[j]
                    name2 = TAG_NAMES.get(tt2, f"Unknown({tt2})")
                    e2 = ""
                    if tt2 == 36:
                        info = ll2_info(tb2)
                        if info:
                            e2 = f" charID={info[0]}, fmt={info[1]}"
                    elif tt2 == 76:
                        entries = symbolclass_info(tb2)
                        e2 = f" {len(entries)} entries"
                    print(f"      [{j:4d}] {name2}({tt2}) len={tl2}{e2}")
        
        # Show tags around SymbolClass
        print(f"\n  Tags around SymbolClass:")
        for i, (tt, tl, tb, tp) in enumerate(tags):
            if tt == 76:
                entries = symbolclass_info(tb)
                print(f"    [{i:4d}] SymbolClass(76) {len(entries)} entries")
                for j in range(max(0, i-3), min(len(tags), i+4)):
                    if j == i:
                        continue
                    tt2, tl2, tb2, tp2 = tags[j]
                    name2 = TAG_NAMES.get(tt2, f"Unknown({tt2})")
                    print(f"      [{j:4d}] {name2}({tt2}) len={tl2}")
                # Show first 10 and last 10 entries
                print(f"    First 10 entries:")
                for cid, name in entries[:10]:
                    print(f"      charID={cid} → {name}")
                print(f"    Last 10 entries:")
                for cid, name in entries[-10:]:
                    print(f"      charID={cid} → {name}")
        
        # LL2 format comparison
        print(f"\n  LL2 bitmap formats:")
        fmt3 = []
        fmt5 = []
        for tt, tl, tb, tp in tags:
            if tt == 36:
                info = ll2_info(tb)
                if info:
                    cid, fmt, w, h = info
                    if fmt == 3:
                        fmt3.append((cid, w, h))
                    elif fmt == 5:
                        fmt5.append((cid, w, h))
        print(f"    Format=3 (indexed): {len(fmt3)}")
        print(f"    Format=5 (ARGB):    {len(fmt5)}")
    
    # Now do a detailed diff of LL2 tags between OG and RT
    print(f"\n{'='*70}")
    print(f"  DETAILED LL2 COMPARISON")
    print(f"{'='*70}")
    
    sig_og, ver_og, fl_og, body_og = read_swf(OG)
    sig_rt, ver_rt, fl_rt, body_rt = read_swf(RT)
    _, _, tags_og = parse_tags(body_og)
    _, _, tags_rt = parse_tags(body_rt)
    
    # Collect all LL2 tags by charID
    og_ll2 = {}
    rt_ll2 = {}
    for tt, tl, tb, tp in tags_og:
        if tt == 36:
            info = ll2_info(tb)
            if info:
                og_ll2[info[0]] = (info[1], info[2], info[3], tb)
    for tt, tl, tb, tp in tags_rt:
        if tt == 36:
            info = ll2_info(tb)
            if info:
                rt_ll2[info[0]] = (info[1], info[2], info[3], tb)
    
    print(f"  OG LL2 charIDs: {len(og_ll2)}")
    print(f"  RT LL2 charIDs: {len(rt_ll2)}")
    
    # CharIDs only in one
    og_only = sorted(set(og_ll2) - set(rt_ll2))
    rt_only = sorted(set(rt_ll2) - set(og_ll2))
    if og_only:
        print(f"\n  CharIDs in OG only: {og_only[:20]}{'...' if len(og_only)>20 else ''}")
    if rt_only:
        print(f"\n  CharIDs in RT only: {rt_only[:20]}{'...' if len(rt_only)>20 else ''}")
    
    # Compare matching charIDs
    common = sorted(set(og_ll2) & set(rt_ll2))
    diffs = []
    for cid in common:
        og_fmt, og_w, og_h, og_body = og_ll2[cid]
        rt_fmt, rt_w, rt_h, rt_body = rt_ll2[cid]
        if og_fmt != rt_fmt or og_w != rt_w or og_h != rt_h:
            diffs.append((cid, (og_fmt, og_w, og_h), (rt_fmt, rt_w, rt_h)))
        elif og_body != rt_body:
            diffs.append((cid, f"fmt={og_fmt} {og_w}x{og_h} BODY DIFFERS (OG={len(og_body)} RT={len(rt_body)})", ""))
    
    if diffs:
        print(f"\n  LL2 DIFFERENCES ({len(diffs)} total):")
        for d in diffs[:50]:
            if len(d) == 3 and isinstance(d[1], tuple):
                cid, og_info, rt_info = d
                print(f"    charID={cid}: OG fmt={og_info[0]} {og_info[1]}x{og_info[2]} → RT fmt={rt_info[0]} {rt_info[1]}x{rt_info[2]}")
            else:
                print(f"    charID={d[0]}: {d[1]}")
    else:
        print(f"\n  ALL {len(common)} common LL2 tags are BYTE-IDENTICAL")
    
    # JPEG3 comparison
    og_jpeg = {}
    rt_jpeg = {}
    for tt, tl, tb, tp in tags_og:
        if tt == 35:
            info = jpeg3_info(tb)
            if info:
                og_jpeg[info[0]] = (tl, tb)
    for tt, tl, tb, tp in tags_rt:
        if tt == 35:
            info = jpeg3_info(tb)
            if info:
                rt_jpeg[info[0]] = (tl, tb)
    
    print(f"\n  OG JPEG3 charIDs: {len(og_jpeg)}")
    print(f"  RT JPEG3 charIDs: {len(rt_jpeg)}")
    j_og_only = sorted(set(og_jpeg) - set(rt_jpeg))
    j_rt_only = sorted(set(rt_jpeg) - set(og_jpeg))
    if j_og_only:
        print(f"  JPEG3 in OG only: {j_og_only}")
    if j_rt_only:
        print(f"  JPEG3 in RT only: {j_rt_only}")
    
    # Compare JPEG3 sizes
    j_common = sorted(set(og_jpeg) & set(rt_jpeg))
    j_diffs = []
    for cid in j_common:
        og_len, og_body = og_jpeg[cid]
        rt_len, rt_body = rt_jpeg[cid]
        if og_body != rt_body:
            j_diffs.append((cid, og_len, rt_len))
    
    if j_diffs:
        print(f"\n  JPEG3 BODY DIFFERENCES ({len(j_diffs)} total):")
        for cid, ol, rl in j_diffs[:20]:
            print(f"    charID={cid}: OG_len={ol} RT_len={rl} (diff={rl-ol})")
    else:
        print(f"\n  ALL {len(j_common)} common JPEG3 tags are BYTE-IDENTICAL")
    
    # DoABC comparison
    print(f"\n  DoABC COMPARISON:")
    og_doabc = [(i, tb) for i, (tt, tl, tb, tp) in enumerate(tags_og) if tt in (82, 72)]
    rt_doabc = [(i, tb) for i, (tt, tl, tb, tp) in enumerate(tags_rt) if tt in (82, 72)]
    print(f"  OG: {len(og_doabc)} DoABC tag(s) at indices {[i for i,_ in og_doabc]}")
    print(f"  RT: {len(rt_doabc)} DoABC tag(s) at indices {[i for i,_ in rt_doabc]}")
    
    if len(og_doabc) == len(rt_doabc):
        for idx, ((oi, ob), (ri, rb)) in enumerate(zip(og_doabc, rt_doabc)):
            if ob == rb:
                print(f"    DoABC[{idx}]: BYTE-IDENTICAL (len={len(ob)})")
            else:
                print(f"    DoABC[{idx}]: DIFFER! OG_len={len(ob)} RT_len={len(rb)}")
                # Find first difference
                for k in range(min(len(ob), len(rb))):
                    if ob[k] != rb[k]:
                        print(f"      First diff at byte {k}: OG=0x{ob[k]:02x} RT=0x{rb[k]:02x}")
                        break
    
    # Tag order comparison (first N top-level tags)
    print(f"\n  TAG ORDER COMPARISON (definition types):")
    def tag_summary(tags_list):
        """Return list of (index, tag_type, charID_if_applicable)"""
        out = []
        for i, (tt, tl, tb, tp) in enumerate(tags_list):
            cid = None
            if tt in (36, 35, 2, 22, 32, 83, 14, 39, 46, 84, 11, 33, 37, 10, 48, 75):
                if len(tb) >= 2:
                    cid = struct.unpack_from('<H', tb, 0)[0]
            out.append((i, tt, cid))
        return out
    
    og_sum = tag_summary(tags_og)
    rt_sum = tag_summary(tags_rt)
    
    # Check relative position of DoABC vs last bitmap
    last_bmp_og = max((i for i, tt, _ in og_sum if tt in (36, 35)), default=-1)
    last_bmp_rt = max((i for i, tt, _ in rt_sum if tt in (36, 35)), default=-1)
    doabc_idx_og = min((i for i, tt, _ in og_sum if tt in (82, 72)), default=-1)
    doabc_idx_rt = min((i for i, tt, _ in rt_sum if tt in (82, 72)), default=-1)
    symcls_idx_og = min((i for i, tt, _ in og_sum if tt == 76), default=-1)
    symcls_idx_rt = min((i for i, tt, _ in rt_sum if tt == 76), default=-1)
    
    print(f"  OG: last_bitmap={last_bmp_og}, DoABC={doabc_idx_og}, SymbolClass={symcls_idx_og}")
    print(f"  RT: last_bitmap={last_bmp_rt}, DoABC={doabc_idx_rt}, SymbolClass={symcls_idx_rt}")
    
    # Are there definition tags BETWEEN DoABC and SymbolClass?
    if doabc_idx_og >= 0 and symcls_idx_og >= 0:
        between_og = [(i, tt) for i, tt, _ in og_sum if doabc_idx_og < i < symcls_idx_og and tt not in (0, 1)]
        print(f"  OG tags between DoABC and SymbolClass: {len(between_og)}")
        for i, tt in between_og[:10]:
            print(f"    [{i}] {TAG_NAMES.get(tt, tt)}")
    
    if doabc_idx_rt >= 0 and symcls_idx_rt >= 0:
        between_rt = [(i, tt) for i, tt, _ in rt_sum if doabc_idx_rt < i < symcls_idx_rt and tt not in (0, 1)]
        print(f"  RT tags between DoABC and SymbolClass: {len(between_rt)}")
        for i, tt in between_rt[:10]:
            print(f"    [{i}] {TAG_NAMES.get(tt, tt)}")
    
    # Are there any bitmap tags AFTER DoABC in OG?
    bmps_after_doabc_og = [(i, tt) for i, tt, _ in og_sum if tt in (36, 35) and i > doabc_idx_og]
    bmps_after_doabc_rt = [(i, tt) for i, tt, _ in rt_sum if tt in (36, 35) and i > doabc_idx_rt]
    print(f"\n  Bitmap tags AFTER DoABC:")
    print(f"    OG: {len(bmps_after_doabc_og)}")
    print(f"    RT: {len(bmps_after_doabc_rt)}")
    
    # SWF header comparison
    print(f"\n  SWF HEADER COMPARISON:")
    print(f"  OG: sig={sig_og} ver={ver_og} len={fl_og}")
    print(f"  RT: sig={sig_rt} ver={ver_rt} len={fl_rt}")
    
    # FileAttributes
    for label, tag_list in [("OG", tags_og), ("RT", tags_rt)]:
        for tt, tl, tb, tp in tag_list:
            if tt == 69:  # FileAttributes
                flags = struct.unpack_from('<I', tb, 0)[0] if len(tb) >= 4 else 0
                has_as3 = bool(flags & 0x08)
                has_metadata = bool(flags & 0x10)
                use_network = bool(flags & 0x01)
                print(f"  {label} FileAttributes: flags=0x{flags:08x} AS3={has_as3} metadata={has_metadata} network={use_network}")
                break
    
    # Compare SymbolClass entries
    print(f"\n  SYMBOLCLASS COMPARISON:")
    og_sc = []
    rt_sc = []
    for tt, tl, tb, tp in tags_og:
        if tt == 76:
            og_sc = symbolclass_info(tb)
    for tt, tl, tb, tp in tags_rt:
        if tt == 76:
            rt_sc = symbolclass_info(tb)
    
    print(f"  OG entries: {len(og_sc)}")
    print(f"  RT entries: {len(rt_sc)}")
    
    og_dict = {name: cid for cid, name in og_sc}
    rt_dict = {name: cid for cid, name in rt_sc}
    
    sc_og_only = sorted(set(og_dict) - set(rt_dict))
    sc_rt_only = sorted(set(rt_dict) - set(og_dict))
    if sc_og_only:
        print(f"  Names in OG only: {sc_og_only[:10]}")
    if sc_rt_only:
        print(f"  Names in RT only: {sc_rt_only[:10]}")
    
    # CharID mismatches
    sc_cid_diff = []
    for name in sorted(set(og_dict) & set(rt_dict)):
        if og_dict[name] != rt_dict[name]:
            sc_cid_diff.append((name, og_dict[name], rt_dict[name]))
    if sc_cid_diff:
        print(f"\n  SymbolClass charID MISMATCHES ({len(sc_cid_diff)}):")
        for name, og_cid, rt_cid in sc_cid_diff[:20]:
            print(f"    {name}: OG={og_cid} RT={rt_cid}")
    else:
        print(f"  All common SymbolClass entries have MATCHING charIDs")
    
    # Order comparison
    if og_sc == rt_sc:
        print(f"  SymbolClass entries are IDENTICAL (same order, same charIDs)")
    else:
        # Check if just order differs
        if sorted(og_sc) == sorted(rt_sc):
            print(f"  SymbolClass entries same content but DIFFERENT ORDER")
            # Show first few order diffs
            for i, (o, r) in enumerate(zip(og_sc, rt_sc)):
                if o != r:
                    print(f"    First order diff at position {i}: OG=({o[0]},{o[1]}) RT=({r[0]},{r[1]})")
                    break

if __name__ == '__main__':
    main()
