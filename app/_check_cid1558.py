import struct, zlib

def parse_all_tags(path):
    data = open(path,'rb').read()
    sig = data[:3]
    if sig == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    off = 8
    nb = (data[off] >> 3) & 0x1f
    off += ((5 + 4*nb) + 7) // 8
    off += 4
    tags = []
    while off < len(data)-1:
        rec = struct.unpack_from('<H', data, off)[0]
        tag_type = rec >> 6
        tag_len = rec & 0x3f
        if tag_len == 0x3f:
            tag_len = struct.unpack_from('<I', data, off+2)[0]
            body_off = off + 6
            off += 6
        else:
            body_off = off + 2
            off += 2
        body = data[body_off:body_off+tag_len]
        tags.append((tag_type, body))
        off += tag_len
    return tags

og_p = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_swf = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

og_tags = parse_all_tags(og_p)
rt_tags = parse_all_tags(rt_swf)

TAG_NAMES = {2:'DefineShape',6:'DefineBits',10:'DefineFont',11:'DefineText',14:'DefineSound',
    15:'StartSound',18:'SoundStreamHead',19:'SoundStreamBlock',20:'LL1',21:'JPEG2',
    22:'DefineShape2',26:'PO2',28:'RemoveObject2',32:'DefineShape3',35:'JPEG3',
    36:'LL2',37:'DefineEditText',39:'DefineSprite',43:'FrameLabel',46:'DefineMorphShape',
    75:'DefineFont3',76:'SymbolClass',77:'Metadata',82:'DoABC',83:'DefineShape4',
    84:'DefineMorphShape2',87:'DefineBinaryData',88:'DefineFontName',90:'JPEG4'}

DEF_TYPES = {2, 10, 11, 14, 20, 21, 22, 32, 33, 35, 36, 37, 39, 46, 75, 78, 83, 84, 87, 88, 90}

print("=== OG charID=1558 definitions ===")
for i, (t, b) in enumerate(og_tags):
    if t in DEF_TYPES and len(b) >= 2:
        cid = struct.unpack_from('<H', b, 0)[0]
        if cid == 1558:
            print(f'  idx={i} type={TAG_NAMES.get(t, t)} len={len(b)} body[:12]={b[:12].hex()}')

print("\n=== RT charID=1558 definitions ===")
for i, (t, b) in enumerate(rt_tags):
    if t in DEF_TYPES and len(b) >= 2:
        cid = struct.unpack_from('<H', b, 0)[0]
        if cid == 1558:
            print(f'  idx={i} type={TAG_NAMES.get(t, t)} len={len(b)} body[:12]={b[:12].hex()}')

# Check SymbolClass for both charID=1001 and charID=1178
print("\n=== SymbolClass entries for charID=1001 and charID=1178 and charID=1558 ===")
for label, tags in [('OG', og_tags), ('RT', rt_tags)]:
    for t, b in tags:
        if t == 76:  # SymbolClass
            count = struct.unpack_from('<H', b, 0)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', b, off)[0]
                off += 2
                null_pos = b.find(b'\x00', off)
                name = b[off:null_pos].decode('utf-8', errors='replace')
                off = null_pos + 1
                if cid in (1001, 1178, 1558):
                    print(f'  {label}: charID={cid} -> "{name}"')

# Check what bitmaps charID=1178 and 1558 are
print("\n=== charID=1178 LL2 bitmap details in OG ===")
for i, (t, b) in enumerate(og_tags):
    if t == 36:  # LL2
        cid = struct.unpack_from('<H', b, 0)[0]
        if cid == 1178:
            fmt = b[2]
            w = struct.unpack_from('<H', b, 3)[0]
            h = struct.unpack_from('<H', b, 5)[0]
            print(f'  idx={i} charID={cid} fmt={fmt} w={w} h={h} tag_len={len(b)}')

print("\n=== Context: what's around charID=1558 (in OG, showing adjacent tags) ===")
for i, (t, b) in enumerate(og_tags):
    if t in DEF_TYPES and len(b) >= 2:
        cid = struct.unpack_from('<H', b, 0)[0]
        if cid == 1558:
            print(f'  Around idx={i}:')
            for j in range(max(0, i-3), min(len(og_tags), i+4)):
                jt, jb = og_tags[j]
                jcid = struct.unpack_from('<H', jb, 0)[0] if len(jb) >= 2 else 0
                print(f'    OG[{j}]: type={TAG_NAMES.get(jt, jt)} charID={jcid} len={len(jb)}')
