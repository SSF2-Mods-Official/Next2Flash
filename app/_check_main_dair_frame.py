"""
Check the main character sprite (cid=1311 in RT) for the dair frame label
and what stance cid is placed there.
"""
import struct, zlib, sys

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
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

def parse_inner(b):
    r = []; off = 0
    while off < len(b):
        if off+2 > len(b): break
        hdr = struct.unpack_from('<H',b,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',b,off)[0]; off+=4
        r.append((tt,b[off:off+ln])); off+=ln
        if tt==0: break
    return r

def find_root_sprites(path):
    data = read_swf(path)
    tags = parse_tags(data)
    sprites = {}
    sym = {}
    for tt, d in tags:
        if tt==39 and len(d)>=4: sprites[struct.unpack_from('<H',d,0)[0]] = d[4:]
        elif tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
    
    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())
    
    # Find root placements
    root_tags = parse_tags(data)
    root_cids = []
    for tt, d in root_tags:
        if tt == 26 and len(d) >= 5:
            has_char = bool(d[0] & 0x02)
            if has_char:
                cid = struct.unpack_from('<H', d, 3)[0]
                root_cids.append(cid)
        if tt == 1: break
    
    return root_cids, sprites, cid_to_name, sym_cids

def scan_sprite_for_dair_stance(spr_cid, sprites, cid_to_name, sym_cids, label):
    spr_bytes = sprites.get(spr_cid, b'')
    if not spr_bytes:
        print(f"  Sprite cid={spr_cid} not found!")
        return
    
    inner = parse_inner(spr_bytes)
    
    # Walk timeline to find stance cid at each frame label
    depth_state = {}  # depth -> cid
    depth_name = {}   # depth -> instance name  
    all_labels = {}
    stance_depth = None
    
    for tt, d in inner:
        if tt == 43:  # FrameLabel
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            lbl = d[:null].decode('utf-8','r')
            all_labels[lbl] = dict(depth_state)
        elif tt == 70 and len(d) >= 4:  # PO3
            flags1 = d[0]; flags2 = d[1] if len(d)>1 else 0
            has_char = bool(flags1 & 0x02)
            has_move = bool(flags1 & 0x01)
            has_name = bool(flags2 & 0x02)
            depth = struct.unpack_from('<H', d, 2)[0]
            cid = struct.unpack_from('<H', d, 4)[0] if (has_char and len(d)>=6) else None
            if cid:
                depth_state[depth] = cid
            elif not has_move:
                depth_state.pop(depth, None)
        elif tt == 26 and len(d) >= 3:  # PO2
            flags = d[0]; has_char = bool(flags & 0x02); has_move = bool(flags & 0x01)
            depth = struct.unpack_from('<H', d, 1)[0]
            cid = struct.unpack_from('<H', d, 3)[0] if (has_char and len(d)>=5) else None
            if cid:
                depth_state[depth] = cid
            elif not has_move:
                depth_state.pop(depth, None)
        elif tt == 28 and len(d) >= 2:  # RO2
            depth = struct.unpack_from('<H', d, 0)[0]
            depth_state.pop(depth, None)
    
    print(f"\n[{label}] Main sprite cid={spr_cid}: frames with label count = {len(all_labels)}")
    
    # Find dair label
    dair_snap = all_labels.get('dair')
    if dair_snap:
        print(f"  'dair' frame active depths ({len(dair_snap)} depths):")
        for dep in sorted(dair_snap.keys()):
            cid = dair_snap[dep]
            name = cid_to_name.get(cid, '<anon>')
            sym_flag = '✓SYM' if cid in sym_cids else '✗ANON'
            print(f"    depth={dep}: cid={cid} [{name}] {sym_flag}")
    else:
        print(f"  'dair' NOT FOUND. Available labels: {list(all_labels.keys())[:20]}")
    
    # Print an overview of all labels and what main sprite they contain
    # Focus on animations (labels with sprite cids similar to known animations)
    print(f"\n  All frame labels and their depth=1 cid:")
    dair_cid = sym_cids & set(sym_cids) # get the sym for dair
    for lbl, snap in sorted(all_labels.items()):
        d1_cid = snap.get(1)
        d1_name = cid_to_name.get(d1_cid, '<anon>') if d1_cid else 'none'
        # Only show a few relevant labels
        print(f"    {lbl}: depth1=cid={d1_cid}[{d1_name}]")

for path_label, path in [('OG', OG_PATH), ('RT', RT_PATH)]:
    root_cids, sprites, cid_to_name, sym_cids = find_root_sprites(path)
    data = read_swf(path)
    tags = parse_tags(data)
    
    # Find root placements (including after first frame)
    all_root_po = []
    for tt, d in tags:
        if tt==26 and len(d)>=5:
            has_char = bool(d[0]&0x02)
            if has_char:
                cid = struct.unpack_from('<H',d,3)[0]
                all_root_po.append(cid)
    
    print(f"\n[{path_label}] Root timeline PO2 cids: {all_root_po[:5]}...")
    
    # The main character sprite is typically the one with the most frames
    # Try depth=1
    depth1_cid = all_root_po[0] if all_root_po else None
    print(f"  Depth-1 sprite: cid={depth1_cid} [{cid_to_name.get(depth1_cid,'?')}]")
    
    if depth1_cid:
        scan_sprite_for_dair_stance(depth1_cid, sprites, cid_to_name, sym_cids, path_label)
