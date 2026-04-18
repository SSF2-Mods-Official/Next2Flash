"""
Find the actual 'stance' depth in the black_mage sprite by finding
which depth contains DAir_73 / other animation sprites.
Check all depths for all frame labels.
"""
import struct, zlib

RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

def get_sprite_bytes(data, target_cid):
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==39 and len(d)>=4 and struct.unpack_from('<H',d,0)[0]==target_cid:
            return d[4:]
        if tt==0: break
    return None

def get_sym(data):
    off = skip_hdr(data)
    sym = {}
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
        if tt==0: break
    return sym

def analyze_all_depths(spr_bytes, cid_to_name, sym_cids, dair_cid):
    """Walk timeline, for each frame label, record all depth→cid mappings. Find which depth has DAir_73."""
    depth_state = {}
    snaps = {}
    label = None
    off = 0
    
    while off < len(spr_bytes):
        if off+2 > len(spr_bytes): break
        hdr=struct.unpack_from('<H',spr_bytes,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr_bytes,off)[0]; off+=4
        d=spr_bytes[off:off+ln]; off+=ln
        if tt==43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            label = d[:null].decode('utf-8','r')
        elif tt==70 and len(d)>=4:
            flags1=d[0]; has_char=bool(flags1&0x02); has_move=bool(flags1&0x01)
            depth=struct.unpack_from('<H',d,2)[0]
            cid=struct.unpack_from('<H',d,4)[0] if (has_char and len(d)>=6) else None
            if cid: depth_state[depth] = cid
            elif not has_move: depth_state.pop(depth, None)
        elif tt==26 and len(d)>=3:
            flags=d[0]; has_char=bool(flags&0x02); has_move=bool(flags&0x01)
            depth=struct.unpack_from('<H',d,1)[0]
            cid=struct.unpack_from('<H',d,3)[0] if (has_char and len(d)>=5) else None
            if cid: depth_state[depth] = cid
            elif not has_move: depth_state.pop(depth, None)
        elif tt==28 and len(d)>=2:
            depth_state.pop(struct.unpack_from('<H',d,0)[0], None)
        elif tt==1:
            if label:
                snaps[label] = dict(depth_state)
        if tt==0: break
    
    # Find which depth contains DAir_73 in any label
    stance_depths = set()
    for lname, snap in snaps.items():
        for depth, cid in snap.items():
            if cid == dair_cid:
                stance_depths.add(depth)
    
    return snaps, stance_depths

for label, path, main_cid in [('OG', OG_PATH, 1556), ('RT', RT_PATH, 873)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())
    dair_cid = sym.get('blackmage_fla.DAir_73')
    
    spr = get_sprite_bytes(data, main_cid)
    if not spr: print(f"[{label}] sprite not found!"); continue
    
    snaps, stance_depths = analyze_all_depths(spr, cid_to_name, sym_cids, dair_cid)
    
    print(f"\n[{label}] black_mage cid={main_cid}, DAir_73 cid={dair_cid}")
    print(f"  Depths where DAir_73 appears: {stance_depths}")
    
    if stance_depths:
        # For the "stance" depth, show what's present at each animation label
        stance_depth = min(stance_depths)
        print(f"\n  Depth={stance_depth} across all labels:")
        for lname in sorted(snaps.keys()):
            cid = snaps[lname].get(stance_depth)
            nm = cid_to_name.get(cid, '<anon>') if cid else 'none'
            in_sym = '✓' if (cid and cid in sym_cids) else '✗'
            # Show only air/attack labels and a few others to reduce output
            if any(x in lname for x in ['air', 'stand', 'run', 'dair', 'atk']):
                print(f"    {lname}: cid={cid} [{nm}] {in_sym}")
    else:
        print(f"  DAir_73 NOT found in any frame labels!")
        # Check how many unique depth cids are in the main sprite
        all_cids = set()
        for snap in snaps.values():
            all_cids.update(snap.values())
        print(f"  Total unique cids across all labels: {len(all_cids)}")
        print(f"  Sample: {[(c, cid_to_name.get(c, '<anon>')) for c in list(all_cids)[:5]]}")
        
        # Check if DAir_73 is inside one of the container sprites
        for cid in all_cids:
            name = cid_to_name.get(cid, '')
            if 'dair' in name.lower() or 'DAir' in name:
                print(f"  Found DAir-related cid={cid} [{name}]")
