"""Deep-dive into what's different about pichuidle_* sprites in OG vs RT."""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\pichu.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\pichu.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] in (b'CWS', b'ZWS'):
        data = data[:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset=0):
    tags = []; pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        tt = h >> 6; length = h & 0x3F; pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]; pos += 4
        tags.append((tt, data[pos:pos+length]))
        pos += length
        if tt == 0: break
    return tags

def skip_header(data):
    pos = 8; nbits = data[pos] >> 3
    pos += (5 + nbits * 4 + 7) // 8 + 4
    return pos

def parse_symbol_class(data):
    pos = 0; count = struct.unpack_from('<H', data, pos)[0]; pos += 2
    symbols = {}
    for _ in range(count):
        cid = struct.unpack_from('<H', data, pos)[0]; pos += 2
        end = data.index(0, pos)
        symbols[data[pos:end].decode('utf-8')] = cid; pos = end + 1
    return symbols

TAG_NAMES = {
    0:'End', 1:'ShowFrame', 2:'DefineShape', 26:'PO2', 28:'RemoveObject2',
    32:'DefineShape3', 39:'DefineSprite', 37:'DefineSprite37', 
    43:'FrameLabel', 45:'SSH2', 46:'SSBlock', 70:'PO3',
    4:'PlaceObject', 5:'RemoveObject', 14:'DefineSound',
    36:'DefineEditText', 83:'DefineShape4', 84:'DefineMorphShape2',
}

og = read_swf(OG); rt = read_swf(RT)
og_tags = parse_tags(og, skip_header(og)); rt_tags = parse_tags(rt, skip_header(rt))
og_sym = rt_sym = None
for t, d in og_tags:
    if t == 76: og_sym = parse_symbol_class(d)
for t, d in rt_tags:
    if t == 76: rt_sym = parse_symbol_class(d)

og_cid_to_name = {v: k for k, v in og_sym.items()}
rt_cid_to_name = {v: k for k, v in rt_sym.items()}

# Collect all definitions (not just sprites)
og_defs = {}  # cid -> tag_type
rt_defs = {}
for t, d in og_tags:
    if t in (2, 22, 32, 83) and len(d) >= 2:  # shape tags
        cid = struct.unpack_from('<H', d, 0)[0]
        og_defs[cid] = t
    elif t in (39, 37) and len(d) >= 4:  # sprite tags
        cid = struct.unpack_from('<H', d, 0)[0]
        og_defs[cid] = t
    elif t in (36,) and len(d) >= 2:  # edit text
        cid = struct.unpack_from('<H', d, 0)[0]
        og_defs[cid] = t
    elif t in (84,) and len(d) >= 2:  # morph shape
        cid = struct.unpack_from('<H', d, 0)[0]
        og_defs[cid] = t

for t, d in rt_tags:
    if t in (2, 22, 32, 83) and len(d) >= 2:
        cid = struct.unpack_from('<H', d, 0)[0]
        rt_defs[cid] = t
    elif t in (39, 37) and len(d) >= 4:
        cid = struct.unpack_from('<H', d, 0)[0]
        rt_defs[cid] = t
    elif t in (36,) and len(d) >= 2:
        cid = struct.unpack_from('<H', d, 0)[0]
        rt_defs[cid] = t
    elif t in (84,) and len(d) >= 2:
        cid = struct.unpack_from('<H', d, 0)[0]
        rt_defs[cid] = t

# Check all pichuidle_* symbols
print("=== pichuidle_* symbols ===")
for name in sorted(og_sym):
    if 'pichuidle' in name:
        og_cid = og_sym[name]
        rt_cid = rt_sym.get(name)
        og_type = og_defs.get(og_cid, 'MISSING')
        rt_type = rt_defs.get(rt_cid, 'MISSING') if rt_cid else 'NO_SYM'
        og_type_name = TAG_NAMES.get(og_type, str(og_type)) if isinstance(og_type, int) else og_type
        rt_type_name = TAG_NAMES.get(rt_type, str(rt_type)) if isinstance(rt_type, int) else rt_type
        match = "OK" if og_type_name == rt_type_name else "MISMATCH"
        if match == "MISMATCH":
            print(f"  **{name}: OG=CID{og_cid}({og_type_name}) RT=CID{rt_cid}({rt_type_name}) *** {match}")
        else:
            print(f"  {name}: OG=CID{og_cid}({og_type_name}) RT=CID{rt_cid}({rt_type_name})")

# Check ALL symbols for definition type mismatches
print("\n=== ALL symbols with definition type mismatches ===")
mismatches = []
for name in sorted(og_sym):
    og_cid = og_sym[name]
    rt_cid = rt_sym.get(name)
    if rt_cid is None:
        print(f"  MISSING from RT: {name}")
        continue
    og_type = og_defs.get(og_cid)
    rt_type = rt_defs.get(rt_cid)
    if og_type != rt_type:
        og_tn = TAG_NAMES.get(og_type, str(og_type)) if og_type else 'NOT_DEFINED'
        rt_tn = TAG_NAMES.get(rt_type, str(rt_type)) if rt_type else 'NOT_DEFINED'
        mismatches.append((name, og_cid, og_tn, rt_cid, rt_tn))
        print(f"  {name}: OG=CID{og_cid}({og_tn}) RT=CID{rt_cid}({rt_tn})")

print(f"\nTotal type mismatches: {len(mismatches)}")

# Check for symbols in RT but not in OG
for name in sorted(rt_sym):
    if name not in og_sym:
        print(f"  EXTRA in RT: {name} CID={rt_sym[name]}")
