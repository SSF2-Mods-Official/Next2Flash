"""
Examine the main blackmage sprite (root of character MC):
1. Find which sprite is placed at depth "stance" in the "dair" frame
2. Compare OG vs RT
3. Check ALL portrait / charHead related bitmaps placed via PO3
"""
import struct, zlib, sys
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d, bo=0):
    bi = bo//8; bi2 = bo%8; nb = 0
    for i in range(5): nb = (nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

def parse_tags(d, off=None, end=None):
    if off is None: off = skip_hdr(d)
    if end is None: end = len(d)
    r = []
    while off < end:
        if off+2 > end: break
        hdr = struct.unpack_from('<H',d,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',d,off)[0]; off+=4
        r.append((tt,d[off:off+ln])); off+=ln
        if tt==0: break
    return r

def get_po_name(d, tt):
    """Extract instance name from PO2/PO3 tag data, if any."""
    try:
        if tt == 26:  # PO2
            flags = d[0]
            has_char = bool(flags & 0x02)
            has_name = bool(flags & 0x20)
            has_move = bool(flags & 0x01)
            depth = struct.unpack_from('<H', d, 1)[0]
            off = 3
            cid = None
            if has_char: cid = struct.unpack_from('<H', d, off)[0]; off += 2
            if flags & 0x04: off += 2  # matrix present? actually need to parse matrix
            # can't easily parse past here without full matrix reader
            return depth, cid, None  # name extraction too complex
        elif tt == 70:  # PO3
            flags1 = d[0]; flags2 = d[1]
            has_char = bool(flags1 & 0x02)
            has_name = bool(flags2 & 0x02)
            depth = struct.unpack_from('<H', d, 2)[0]
            cid = struct.unpack_from('<H', d, 4)[0] if has_char else None
            return depth, cid, None
    except:
        pass
    return None, None, None

def analyze_main_sprite(path, label):
    data = read_swf(path)
    tags = parse_tags(data)
    sym = {}; sprites = {}; bitmaps = set()
    for tt, d in tags:
        if tt in (35,36,20) and len(d)>=2: bitmaps.add(struct.unpack_from('<H',d,0)[0])
        elif tt==39 and len(d)>=4: sprites[struct.unpack_from('<H',d,0)[0]] = d[4:]
        elif tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
    
    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())
    
    # Find the main blackmage character sprite.
    # It's the one SymbolClass-linked to the "document class" or "blackmage" class.
    # The root sprite in a character SSF is usually placed at depth 1 in the root timeline.
    # Let's find what's placed in the root timeline.
    root_tags = parse_tags(data)
    root_placements = []
    for tt, d in root_tags:
        if tt in (26, 70) and len(d) >= 4:
            has_char = bool(d[0] & 0x02)
            if has_char:
                cid = struct.unpack_from('<H', d, 3 if tt==26 else 4)[0]
                root_placements.append(cid)
        if tt == 1: break  # ShowFrame
    
    if not root_placements:
        print(f"[{label}] No root placements found.")
        return
    
    main_cid = root_placements[0]
    main_name = cid_to_name.get(main_cid, '<anon>')
    print(f"\n[{label}] Root placement: cid={main_cid} [{main_name}]")
    
    # Parse the main sprite's inner timeline
    main_bytes = sprites.get(main_cid, b'')
    if not main_bytes:
        print(f"  Main sprite has no inner bytes!")
        return
    
    # Parse inner tags: track current state per depth across frames
    off = 0; frame = 1; current_label = None
    depth_to_cid = {}  # depth -> cid currently at that depth
    frames_with_label = {}  # label -> frame_num
    placements_in_label = {}  # label -> {depth: latest_cid}
    
    # Find all frame labels and what's placed in them
    inner = []
    while off < len(main_bytes):
        if off+2 > len(main_bytes): break
        hdr = struct.unpack_from('<H',main_bytes,off)[0]; tt2=hdr>>6; ln2=hdr&0x3F; off+=2
        if ln2==0x3F: ln2=struct.unpack_from('<I',main_bytes,off)[0]; off+=4
        inner.append((tt2, main_bytes[off:off+ln2])); off+=ln2
        if tt2==0: break
    
    # Walk through looking for "dair" label and surrounding labels
    # Track at each frame what is at "stance" depth
    # First, find what depth "stance" is at
    # We'll look for PO3 tags with name="stance"
    # Actually PO3 has HasName flag... let me check HAS_NAME bit in PO3
    
    stance_depth = None
    frame_num = 0
    label_frame_map = {}  # label -> frame_num
    depth_state = {}  # depth -> current cid
    label_depth_snapshot = {}  # label -> depth_state copy
    
    for tt2, d in inner:
        if tt2 == 43:  # FrameLabel
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            lbl = d[:null].decode('utf-8','r')
            label_frame_map[lbl] = frame_num
        elif tt2 == 1:  # ShowFrame
            frame_num += 1
        elif tt2 == 70:  # PO3 - PlaceObject3
            if len(d) < 6: continue
            flags1 = d[0]; flags2 = d[1]
            has_char = bool(flags1 & 0x02)
            has_name = bool(flags2 & 0x02)
            has_move = bool(flags1 & 0x01)
            depth = struct.unpack_from('<H', d, 2)[0]
            cid = struct.unpack_from('<H', d, 4)[0] if has_char else None
            
            # Try to extract name if present
            name = None
            if has_name:
                # PO3 structure: flags1, flags2, depth (2), [cid (2)], 
                # [matrix], [cxform], [ratio], [name], ...
                off3 = 6 if has_char else 4
                # Skip optional fields in order: HasMatrix, HasColorTransform, HasRatio before HasName
                has_matrix = bool(flags1 & 0x04)
                has_cxform = bool(flags1 & 0x08)
                has_ratio = bool(flags1 & 0x10)
                # Actually parsing matrices is complex. Let's just look for known stance names.
                pass
            
            if cid:
                depth_state[depth] = cid
            elif not has_move:
                depth_state.pop(depth, None)
        elif tt2 == 26:  # PO2
            if len(d) < 3: continue
            flags = d[0]
            has_char = bool(flags & 0x02)
            depth = struct.unpack_from('<H', d, 1)[0]
            cid = struct.unpack_from('<H', d, 3)[0] if (has_char and len(d)>=5) else None
            if cid:
                depth_state[depth] = cid
        elif tt2 == 28:  # RO2
            if len(d) >= 2:
                depth = struct.unpack_from('<H', d, 0)[0]
                depth_state.pop(depth, None)
    
    print(f"  Frame labels found: {sorted(label_frame_map.keys())[:30]}")
    print(f"  Total frames: {frame_num}")
    
    # Now find "dair" frame and what's at each depth
    # Let me replay the timeline to capture depth_state at each label
    frame_num2 = 0
    depth_state2 = {}
    label_snapshots = {}
    
    for tt2, d in inner:
        if tt2 == 1: frame_num2 += 1
        elif tt2 == 43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            lbl = d[:null].decode('utf-8','r')
            label_snapshots[lbl] = dict(depth_state2)  # snapshot BEFORE ShowFrame
        elif tt2 == 70 and len(d) >= 4:
            flags1 = d[0]; flags2 = d[1] if len(d)>1 else 0
            has_char = bool(flags1 & 0x02)
            has_move = bool(flags1 & 0x01)
            depth = struct.unpack_from('<H', d, 2)[0]
            cid = struct.unpack_from('<H', d, 4)[0] if (has_char and len(d)>=6) else None
            if cid: depth_state2[depth] = cid
            elif not has_move: depth_state2.pop(depth, None)
        elif tt2 == 26 and len(d) >= 3:
            flags = d[0]; has_char = bool(flags & 0x02)
            depth = struct.unpack_from('<H', d, 1)[0]
            cid = struct.unpack_from('<H', d, 3)[0] if (has_char and len(d)>=5) else None
            if cid: depth_state2[depth] = cid
        elif tt2 == 28 and len(d) >= 2:
            depth = struct.unpack_from('<H', d, 0)[0]
            depth_state2.pop(depth, None)
    
    # Show "dair" snapshot
    dair_snap = label_snapshots.get('dair')
    if dair_snap:
        print(f"\n  Depths active at 'dair' frame label:")
        for dep in sorted(dair_snap.keys()):
            cid = dair_snap[dep]
            name = cid_to_name.get(cid, '<anon>')
            in_sym = '✓' if cid in sym_cids else '✗'
            has_img = cid in bitmaps
            print(f"    depth={dep}: cid={cid} [{name}] sym={in_sym} is_bmp={has_img}")
    else:
        print(f"  'dair' frame label NOT FOUND in main sprite!")
        print(f"  Available labels: {list(label_frame_map.keys())[:10]}")
    
    # Show all labels that contain bitmaps via PO3+HasImage
    print(f"\n  Labels that directly place PO3+HasImage bitmaps:")
    placed_bitmaps_per_label = {}
    frame_num3 = 0
    current_labels_so_far = []
    for tt2, d in inner:
        if tt2 == 43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            lbl = d[:null].decode('utf-8','r')
            current_labels_so_far.append(lbl)
        elif tt2 == 70 and len(d) >= 6:
            flags2 = d[1] if len(d)>1 else 0
            has_img = bool(flags2 & 0x10)
            has_char = bool(d[0] & 0x02)
            if has_img and has_char:
                cid = struct.unpack_from('<H', d, 4)[0]
                name = cid_to_name.get(cid, '<anon>')
                lbl = current_labels_so_far[-1] if current_labels_so_far else '<start>'
                if lbl not in placed_bitmaps_per_label:
                    placed_bitmaps_per_label[lbl] = []
                placed_bitmaps_per_label[lbl].append((cid, name))
        elif tt2 == 1:
            frame_num3 += 1
    
    for lbl, bmps in sorted(placed_bitmaps_per_label.items())[:20]:
        sym_ok = all(c in sym_cids for c, n in bmps)
        flag = '✓' if sym_ok else '✗ANON!'
        print(f"    {flag} label={lbl}: {[(n,c) for c,n in bmps[:3]]}{'...' if len(bmps)>3 else ''}")

analyze_main_sprite(OG, 'OG')
analyze_main_sprite(RT, 'RT')
