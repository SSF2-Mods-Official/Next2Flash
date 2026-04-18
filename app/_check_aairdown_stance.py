"""
For the black_mage main sprite, find what stance sprite is at 'a_air_down' frame.
Also check ALL air attack labels to find the one with DAir_73.
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

def get_labels_and_depth1(spr_bytes, cid_to_name):
    result = {}
    depth_state = {}
    current_label = None
    off = 0
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
            if current_label:
                result[current_label] = dict(depth_state)
        if tt==0: break
    return result

for label, path, main_cid in [('OG', OG_PATH, 1556), ('RT', RT_PATH, 873)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())
    
    spr = get_sprite_bytes(data, main_cid)
    if not spr:
        print(f"[{label}] main sprite not found!"); continue
    
    labels_snap = get_labels_and_depth1(spr, cid_to_name)
    
    print(f"\n[{label}] main sprite cid={main_cid}")
    
    target_labels = ['a_air_down', 'b_down_air', 'a_air_forward', 'a_air', 'stand']
    for tl in target_labels:
        snap = labels_snap.get(tl)
        if snap:
            d1 = snap.get(1)
            d1_name = cid_to_name.get(d1, '<anon>') if d1 else 'none'
            sym_flag = '✓SYM' if (d1 and d1 in sym_cids) else '✗ANON'
            print(f"  '{tl}' → depth=1: cid={d1} [{d1_name}] {sym_flag}")
        else:
            print(f"  '{tl}' → NOT FOUND")
    
    # Find what labels have DAir_73
    dair_cid = sym.get('blackmage_fla.DAir_73')
    print(f"\n  DAir_73 cid={dair_cid}")
    frames_with_dair = [lbl for lbl, snap in labels_snap.items() if snap.get(1) == dair_cid]
    print(f"  Labels where depth=1 = DAir_73: {frames_with_dair}")
    
    # Check total unique depth=1 cids (stances)
    d1_cids = set(snap.get(1) for snap in labels_snap.values() if snap.get(1))
    print(f"  Unique stance cids: {len(d1_cids)}")
