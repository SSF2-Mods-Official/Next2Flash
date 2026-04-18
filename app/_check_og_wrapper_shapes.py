"""
Check whether the bitmaps inside DAir_73 in the OG have companion DefineShape3 tags.
In RT we only emit LL2 tags; if OG had Shape3 wrappers (either standalone or placed)
that's what 'Attempt 1' was trying to replicate.
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

def get_all_tags(data):
    """Return list of (tt, offset, len) for all top-level tags."""
    tags = []
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        tags.append((tt, off, ln))
        off += ln
        if tt==0: break
    return tags

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

def get_bitmaps_in_sprite(spr, data):
    """Get all LL2 bitmap cids referenced via PO3+HasImage inside a sprite's inner tags."""
    bitmaps = set()
    shapes = set()
    off = 0
    while off < len(spr):
        if off+2>len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        if tt == 70:  # PO3
            flags = struct.unpack_from('<H',d,0)[0]
            has_char = bool(flags & 0x0002)
            has_image = bool(flags & 0x0010)  # bit 4 = HasImage
            if has_char and has_image:
                depth = struct.unpack_from('<H',d,2)[0]  # after flags
                # cid is next
                cid_off = 4
                if has_char and cid_off+2<=len(d):
                    cid = struct.unpack_from('<H',d,cid_off)[0]
                    bitmaps.add(cid)
        if tt == 0: break
    return bitmaps

# For DAir_73 OG, get the bitmaps (LL2 cids)
for label, path, DAIR_CID in [('OG', OG_PATH, 1471), ('RT', RT_PATH, 650)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    tags = get_all_tags(data)
    
    # Build maps: cid -> tag type (for all top-level tags)
    cid_to_tag = {}
    for tt, off, ln in tags:
        d = data[off:off+ln]
        if tt in (2,32,33,46,83,84) and ln>=2:  # DefineShape1-4
            cid = struct.unpack_from('<H',d,0)[0]
            cid_to_tag[cid] = tt
        elif tt in (20,36) and ln>=2:  # DefineBitsLossless 1/2
            cid = struct.unpack_from('<H',d,0)[0]
            cid_to_tag[cid] = tt
        elif tt==39 and ln>=2:
            cid = struct.unpack_from('<H',d,0)[0]
            cid_to_tag[cid] = tt
    
    spr = get_sprite_bytes(data, DAIR_CID)
    if not spr: print(f"[{label}] DAir_73 not found!"); continue
    
    # Get all LL2 bitmaps referenced via PO3+HasImage in DAir_73
    dair_bitmaps = get_bitmaps_in_sprite(spr, data)
    
    # Also collect ALL bitmaps referenced in sub-sprites
    # First get all DefineSprite cids referenced in DAir_73
    sub_sprite_cids = set()
    off=0
    while off<len(spr):
        if off+2>len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        if tt in (26,70):
            flags=d[0] if tt==26 else struct.unpack_from('<H',d,0)[0]
            has_char = bool((flags & 0x02) if tt==26 else (flags & 0x0002))
            if has_char:
                dep_off = 1 if tt==26 else 2
                dep_off += 2  # depth field
                if dep_off+2<=len(d):
                    cid = struct.unpack_from('<H',d,dep_off)[0]
                    if cid_to_tag.get(cid)==39:  # DefineSprite
                        sub_sprite_cids.add(cid)
        if tt==0: break
    
    print(f"\n[{label}] DAir_73 (cid={DAIR_CID})")
    print(f"  LL2 bitmaps placed via PO3+HasImage IN DAir_73 directly: {sorted(dair_bitmaps)}")
    print(f"  Sub-sprites referenced in DAir_73: {sorted(sub_sprite_cids)}")
    
    all_bmp_cids = set(dair_bitmaps)
    for ssid in sub_sprite_cids:
        subspr = get_sprite_bytes(data, ssid)
        if subspr:
            bm = get_bitmaps_in_sprite(subspr, data)
            all_bmp_cids |= bm
            print(f"    Sub-sprite cid={ssid}[{cid_to_name.get(ssid,'?')}] LL2 bitmaps via PO3: {sorted(bm)}")
    
    print(f"\n  ALL LL2 bitmap cids for DAir_73: {sorted(all_bmp_cids)}")
    
    # Now check: for each of these LL2 bitmap cids, is there a DefineShape3 with that bitmap's cid?
    # We need to scan DefineShape3 bodies to find FillStyle 0x41 (repeating) or 0x43 (clipped non-smoothed) with that cid
    # DefineShape3 = tag 32
    shape3_with_bitmap = {}  # bitmap_cid -> [shape_cids]
    for tt, off, ln in tags:
        if tt not in (2,32,33,46,83,84): continue
        d = data[off:off+ln]
        if len(d) < 2: continue
        shape_cid = struct.unpack_from('<H',d,0)[0]
        # Quick string search for the bitmap cids we care about
        body = d[2:]
        for bmp_cid in all_bmp_cids:
            cid_bytes = struct.pack('<H', bmp_cid)
            if cid_bytes in body:
                shape3_with_bitmap.setdefault(bmp_cid, []).append((tt, shape_cid))
    
    print(f"\n  DefineShape tags that reference DAir_73's bitmaps:")
    for bmp_cid in sorted(all_bmp_cids):
        nm = cid_to_name.get(bmp_cid, '<anon>')
        hits = shape3_with_bitmap.get(bmp_cid, [])
        print(f"    LL2 cid={bmp_cid}[{nm[:40]}]: {hits if hits else 'NO SHAPE REFERENCE'}")

print("\nDone.")
