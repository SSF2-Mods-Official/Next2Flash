"""
Check the first few frames of DAir_73 in both OG and RT.
When 'replacePalette' is called right after DAir_73 is placed, it's at frame 1.
What Bitmap/MovieClip children does frame 1 have?
"""
import struct, zlib

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

def get_sym(data):
    off = skip_hdr(data); sym = {}
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

def get_tag_type(data, cid):
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt in (2,22,32,33,36,39,46,83,84,20) and len(d)>=2:
            if struct.unpack_from('<H',d,0)[0]==cid:
                return tt
        if tt==0: break
    return None

for label, path, DAIR_CID in [('OG', OG_PATH, 1471), ('RT', RT_PATH, 650)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    # Build bitmap and sprite type lookups quickly
    bitmap_cids = set()
    sprite_cids = set()
    shape_cids = set()
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==36 and len(d)>=2: bitmap_cids.add(struct.unpack_from('<H',d,0)[0])
        if tt==39 and len(d)>=2: sprite_cids.add(struct.unpack_from('<H',d,0)[0])
        if tt in (2,22,32,83) and len(d)>=2: shape_cids.add(struct.unpack_from('<H',d,0)[0])
        if tt==0: break
    
    spr = get_sprite_bytes(data, DAIR_CID)
    if not spr: continue
    
    print(f"\n[{label}] DAir_73 (cid={DAIR_CID}) — display state frames 1-5:")
    
    # Simulate display list through first 5 frames
    display = {}  # depth -> cid
    off = 0
    frame = 0
    
    while off < len(spr) and frame <= 5:
        if off+2>len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        
        if tt == 1:
            frame += 1
            if frame <= 5:
                print(f"\n  === Frame {frame} display list ===")
                # Show all items in display
                for depth in sorted(display.keys()):
                    cid = display[depth]
                    nm = cid_to_name.get(cid, '<anon>')
                    if cid in bitmap_cids:
                        kind = 'BITMAP'
                    elif cid in sprite_cids:
                        kind = 'sprite'
                    elif cid in shape_cids:
                        kind = 'shape'
                    else:
                        kind = '?'
                    print(f"    depth={depth:3d} cid={cid:5d} [{nm[:40]}] ({kind})")
        elif tt == 26:  # PO2
            flags=d[0]; depth=struct.unpack_from('<H',d,1)[0]
            has_move=bool(flags&0x01); has_char=bool(flags&0x02)
            if has_char and len(d)>=5:
                cid=struct.unpack_from('<H',d,3)[0]
                display[depth] = cid
            elif has_move and not has_char:
                pass  # transform update only
        elif tt == 70:  # PO3
            if len(d)>=4:
                f1=d[0]; f2=d[1]; depth=struct.unpack_from('<H',d,2)[0]
                has_char=bool(f1&0x02); has_img=bool(f2&0x10)
                if has_char:
                    off2=4
                    if has_img or bool(f2&0x08):
                        # Try to read ClassName
                        if d[4] != 0x00:
                            try:
                                ne=d.index(b'\x00',4)
                                off2=ne+1
                            except: pass
                    if off2+2<=len(d):
                        cid=struct.unpack_from('<H',d,off2)[0]
                    else: cid=None
                    if cid:
                        display[depth] = cid
        elif tt == 28:  # Remove2
            depth=struct.unpack_from('<H',d,0)[0]
            if depth in display: del display[depth]
        if tt==0: break
    
    # Show total bitmap count at frame 1 (what replacePalette sees)
    frame_1_bitmaps = [(depth, cid) for depth, cid in display.items() if cid in bitmap_cids]
    frame_1_sprites = [(depth, cid) for depth, cid in display.items() if cid in sprite_cids]
    print(f"\n  Frame-1 display count: {len(display)} items total")
    print(f"  Frame-1 DIRECT Bitmap children: {len(frame_1_bitmaps)}")
    for depth, cid in sorted(frame_1_bitmaps)[:5]:
        print(f"    depth={depth} cid={cid} [{cid_to_name.get(cid,'<anon>')}]")
    print(f"  Frame-1 sprite children (recursed into by replacePalette depth=2): {len(frame_1_sprites)}")
    for depth, cid in sorted(frame_1_sprites):
        # Count bitmaps in this sub-sprite's frame 1
        sub_spr = get_sprite_bytes(data, cid)
        if sub_spr:
            sub_display = {}
            off2 = 0
            frame2 = 0
            while off2 < len(sub_spr) and frame2 < 1:
                if off2+2>len(sub_spr): break
                hdr=struct.unpack_from('<H',sub_spr,off2)[0]; tt2=hdr>>6; ln2=hdr&0x3F; off2+=2
                if ln2==0x3F: ln2=struct.unpack_from('<I',sub_spr,off2)[0]; off2+=4
                d2=sub_spr[off2:off2+ln2]; off2+=ln2
                if tt2==1: frame2+=1
                elif tt2==26:
                    fl=d2[0]; dp=struct.unpack_from('<H',d2,1)[0]
                    if bool(fl&0x02) and len(d2)>=5: 
                        sub_display[dp]=struct.unpack_from('<H',d2,3)[0]
                elif tt2==70:
                    if len(d2)>=4:
                        f1=d2[0]; f2=d2[1]; dp=struct.unpack_from('<H',d2,2)[0]
                        hc=bool(f1&0x02); hi=bool(f2&0x10)
                        if hc:
                            p=4
                            if hi or bool(f2&0x08):
                                if d2[4]!=0x00:
                                    try:
                                        ne=d2.index(b'\x00',4); p=ne+1
                                    except: pass
                            if p+2<=len(d2): sub_display[dp]=struct.unpack_from('<H',d2,p)[0]
                elif tt2==28:
                    dp=struct.unpack_from('<H',d2,0)[0]
                    if dp in sub_display: del sub_display[dp]
                if tt2==0: break
            sub_bitmaps = [(d,c) for d,c in sub_display.items() if c in bitmap_cids]
            nm = cid_to_name.get(cid,'<anon>')
            print(f"    depth={depth} cid={cid}[{nm[:30]}]: frame-1 bitmaps={sub_bitmaps[:3]}")
