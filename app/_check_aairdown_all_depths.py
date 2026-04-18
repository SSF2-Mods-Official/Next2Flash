"""
Show ALL depths at 'a_air_down' in the black_mage sprite for both OG and RT.
Look for any PO3+HasImage bitmaps directly placed in black_mage at non-stance depths.
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

def get_sym_and_bitmaps(data):
    off = skip_hdr(data)
    sym = {}; bitmaps = set()
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt in (35,36,20) and len(d)>=2: bitmaps.add(struct.unpack_from('<H',d,0)[0])
        elif tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
        if tt==0: break
    return sym, bitmaps

for label, path, main_cid in [('OG', OG_PATH, 1556), ('RT', RT_PATH, 873)]:
    data = read_swf(path)
    sym, bitmaps = get_sym_and_bitmaps(data)
    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())
    
    spr = get_sprite_bytes(data, main_cid)
    if not spr: continue
    
    # Walk timeline to get snapshot at a_air_down
    depth_state = {}
    current_label = None
    aair_snap = None
    off = 0
    
    while off < len(spr):
        if off+2 > len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        if tt==43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            current_label = d[:null].decode('utf-8','r')
        elif tt==70 and len(d)>=4:
            flags1=d[0]; has_char=bool(flags1&0x02); has_move=bool(flags1&0x01)
            depth=struct.unpack_from('<H',d,2)[0]
            cid=struct.unpack_from('<H',d,4)[0] if (has_char and len(d)>=6) else None
            has_img = bool(d[1] & 0x10) if len(d)>1 else False
            if cid: depth_state[depth] = (cid, 'PO3', has_img)
            elif not has_move: depth_state.pop(depth, None)
        elif tt==26 and len(d)>=3:
            flags=d[0]; has_char=bool(flags&0x02); has_move=bool(flags&0x01)
            depth=struct.unpack_from('<H',d,1)[0]
            cid=struct.unpack_from('<H',d,3)[0] if (has_char and len(d)>=5) else None
            if cid: depth_state[depth] = (cid, 'PO2', False)
            elif not has_move: depth_state.pop(depth, None)
        elif tt==28 and len(d)>=2:
            depth_state.pop(struct.unpack_from('<H',d,0)[0], None)
        elif tt==1:
            if current_label == 'a_air_down':
                aair_snap = dict(depth_state)
        if tt==0: break
    
    print(f"\n[{label}] all depths at 'a_air_down' label:")
    if aair_snap:
        for dep in sorted(aair_snap.keys()):
            cid, po_type, has_img = aair_snap[dep]
            nm = cid_to_name.get(cid, '<anon>')
            is_bmp = cid in bitmaps
            in_sym = '✓SYM' if cid in sym_cids else '✗ANON'
            print(f"  depth={dep}: cid={cid} [{nm}] {po_type} has_img={has_img} is_bmp={is_bmp} {in_sym}")
