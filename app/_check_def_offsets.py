"""Check byte offsets of key chars in RT SWF."""
import struct, zlib

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

data = read_swf(RT_PATH)
root_start = skip_hdr(data)

# chars we care about
targets = {637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 873}
names = {637:'bm_dairScythe',638:'bm_dairScytheBlade',639:'sprite_639(scythe)',
         640:'sprite_640',641:'bm_dairHand',642:'bm_dair0',643:'bm_dair1',
         644:'bm_dair2',645:'bm_dair3',646:'bm_dair4',647:'bm_dair5',
         648:'bm_dair6',649:'bm_dair7',650:'DAir_73',873:'black_mage_root'}

off = root_start
root_frame_offset = None
while off < len(data):
    if off+2 > len(data): break
    hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
    body = data[off:off+ln]
    tag_off = off-hdr_sz
    
    if tt == 1 and root_frame_offset is None:  # ShowFrame in root
        root_frame_offset = tag_off
        print(f"ROOT ShowFrame at offset {tag_off}")
    
    if len(body) >= 2 and tt in (36,39,32,2,20,21,35,83):
        cid = struct.unpack_from('<H', body, 0)[0]
        if cid in targets:
            n = names.get(cid, str(cid))
            before_frame = (root_frame_offset is None) or (tag_off < root_frame_offset)
            print(f"  TT={tt:2} charId={cid:4} ({n}) at offset {tag_off} {'before_root_frame' if before_frame else 'AFTER_ROOT_FRAME'}")
    
    off += ln
    if tt == 0: break

print(f"\nRoot ShowFrame at offset: {root_frame_offset}")
