"""
Check groundRef_mc_2 (the actual m_sprite) for 'a_air_down' label and stance placement.
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

def analyze_sprite(spr_bytes, cid_to_name, sym_cids, label_prefix=""):
    """Walk the sprite timeline and for each frame label, capture all depth placements."""
    depth_state = {}
    labels_snap = {}
    current_label = None
    off = 0
    frame_n = 0
    
    while off < len(spr_bytes):
        if off+2 > len(spr_bytes): break
        hdr=struct.unpack_from('<H',spr_bytes,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr_bytes,off)[0]; off+=4
        d=spr_bytes[off:off+ln]; off+=ln
        if tt==43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            current_label = d[:null].decode('utf-8','r')
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
            frame_n += 1
            if current_label:
                labels_snap[current_label] = dict(depth_state)
        if tt==0: break
    
    return labels_snap

for label, path, main_cid in [('OG', OG_PATH, 1276), ('RT', RT_PATH, 200)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())
    
    spr = get_sprite_bytes(data, main_cid)
    if not spr:
        # Try to find groundRef_mc_2
        off2 = skip_hdr(data)
        while off2 < len(data):
            hdr = struct.unpack_from('<H',data,off2)[0]; tt=hdr>>6; ln=hdr&0x3F; off2+=2
            if ln==0x3F: ln=struct.unpack_from('<I',data,off2)[0]; off2+=4
            d=data[off2:off2+ln]; off2+=ln
            if tt==76:
                num=struct.unpack_from('<H',d,0)[0]; o=2
                for _ in range(num):
                    c=struct.unpack_from('<H',d,o)[0]; o+=2
                    ne=d.index(b'\x00',o); n2=d[o:ne].decode('utf-8','r'); o=ne+1
                    if 'groundRef' in n2: print(f"  groundRef: {n2} → cid={c}")
            if tt==0: break
        continue
    
    snaps = analyze_sprite(spr, cid_to_name, sym_cids)
    all_labels = list(snaps.keys())
    print(f"\n[{label}] groundRef_mc_2 cid={main_cid}, total labels: {len(all_labels)}")
    print(f"  'a_air_down' found: {'a_air_down' in snaps}")
    
    # DAir_73 cid
    dair_cid = sym.get('blackmage_fla.DAir_73')
    dair_label = [l for l, snap in snaps.items() if any(c == dair_cid for c in snap.values())]
    print(f"  DAir_73 cid={dair_cid}")
    print(f"  Labels where DAir_73 is placed: {dair_label[:5]}")
    
    # Check a_air_down frame
    if 'a_air_down' in snaps:
        snap = snaps['a_air_down']
        print(f"  'a_air_down' depths ({len(snap)}):")
        for dep in sorted(snap.keys()):
            cid = snap[dep]
            nm = cid_to_name.get(cid, '<anon>')
            sf = '✓' if cid in sym_cids else '✗'
            print(f"    depth={dep}: cid={cid} [{nm}] {sf}")
    
    # Check: unique depth=1 cids
    d1s = set(s.get(1) for s in snaps.values() if s.get(1))
    d1_names = {c: cid_to_name.get(c, '<anon>') for c in d1s}
    print(f"  Unique depth=1 cids: {len(d1s)}")
    print(f"  Depth-1 cids: {list(d1_names.items())[:10]}")
