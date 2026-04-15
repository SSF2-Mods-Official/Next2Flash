"""
Diagnose specific shape differences between original and roundtrip SWF.
Maps shapes through N2D to handle possible CID renumbering.
"""
import struct, sys, os, io, zipfile, msgpack

ORIG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
RT   = r"test_swfs\lloyd_rt.swf"
N2D  = r"test_swfs\lloyd.n2d"
OUT  = "_diagnose_shapes_output.txt"
TARGET_CIDS = {306, 183, 185, 188}

SHAPE_TAG_IDS = {2, 22, 32, 83}

def read_swf_data(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        import zlib
        rest = zlib.decompress(data[8:])
        data = data[:8] + rest
    elif data[:3] == b'ZWS':
        import lzma
        rest = lzma.decompress(data[12:])
        data = data[:8] + rest
    return data

def parse_tags(data):
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4  # skip rect + frame rate + frame count

    tags = []
    while pos < len(data) - 1:
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        cid = None
        if tag_type in SHAPE_TAG_IDS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
        tags.append((tag_type, cid, body))
        pos += length
        if tag_type == 0:
            break
    return tags

def get_shapes_by_cid(tags):
    shapes = {}
    for tag_type, cid, body in tags:
        if tag_type in SHAPE_TAG_IDS and cid is not None:
            if cid not in shapes:
                shapes[cid] = (tag_type, body)
    return shapes

# --- Main ---
f = open(OUT, 'w')

# 1. Parse original
orig_data = read_swf_data(ORIG)
orig_tags = parse_tags(orig_data)
orig_shapes = get_shapes_by_cid(orig_tags)

# 2. Parse roundtrip
rt_data = read_swf_data(RT)
rt_tags = parse_tags(rt_data)
rt_shapes = get_shapes_by_cid(rt_tags)

# 3. Parse N2D to find mapping
with zipfile.ZipFile(N2D) as z:
    with z.open("project.msgpack") as mf:
        project = msgpack.unpack(mf, raw=False)

libs = project.get("libraries", [{}])[0].get("symbols", [])
n2d_by_origcid = {}
for lib in libs:
    swf_cid = lib.get("swfCharId")
    if swf_cid is not None and swf_cid in TARGET_CIDS:
        n2d_by_origcid[swf_cid] = lib

f.write("=" * 80 + "\n")
f.write("TARGET SHAPES IN N2D\n")
f.write("=" * 80 + "\n\n")

for cid in sorted(TARGET_CIDS):
    if cid in n2d_by_origcid:
        lib = n2d_by_origcid[cid]
        f.write(f"CID {cid}: N2D id={lib.get('id')}, name={lib.get('name','?')}, type={lib.get('type','?')}, rawTagType={lib.get('rawTagType','?')}\n")
        f.write(f"  recodes length: {len(lib.get('recodes', []))}\n")
        f.write(f"  bounds: {lib.get('bounds')}\n")
        # Check if it's morph
        if lib.get('endRecodes'):
            f.write(f"  ** HAS endRecodes — this is a MORPH SHAPE\n")
        if lib.get('isMorphShape'):
            f.write(f"  ** isMorphShape=True\n")
    else:
        f.write(f"CID {cid}: NOT FOUND in N2D by swfCharId\n")

# Check if these CIDs exist as shapes in original
f.write(f"\n{'=' * 80}\n")
f.write("TARGET SHAPES IN ORIGINAL SWF\n")
f.write(f"{'=' * 80}\n\n")

for cid in sorted(TARGET_CIDS):
    if cid in orig_shapes:
        tag_type, body = orig_shapes[cid]
        f.write(f"CID {cid}: tag={tag_type}, size={len(body)} bytes\n")
    else:
        f.write(f"CID {cid}: NOT a shape tag in original. Checking all tags...\n")
        for tag_type, t_cid, body in orig_tags:
            if t_cid == cid:
                f.write(f"  Found as tag type {tag_type}, size={len(body)}\n")

# Check roundtrip - scan all shapes
f.write(f"\n{'=' * 80}\n")
f.write("ALL SHAPE CIDS IN ROUNDTRIP (first 300)\n")
f.write(f"{'=' * 80}\n\n")
rt_cids_sorted = sorted(rt_shapes.keys())
f.write(f"Total shape tags in roundtrip: {len(rt_cids_sorted)}\n")
for cid in rt_cids_sorted[:300]:
    tag_type, body = rt_shapes[cid]
    f.write(f"  CID {cid}: tag={tag_type}, size={len(body)}\n")

# Find roundtrip shapes that match the N2D entries
# The compile process maps N2D lib id → swf id. Let's check how.
f.write(f"\n{'=' * 80}\n")
f.write("N2D LIB SCAN - Finding shapes near target CIDs\n")
f.write(f"{'=' * 80}\n\n")

# Show ALL N2D entries with type=shape and swfCharId near our targets
for lib in libs:
    swf_cid = lib.get("swfCharId")
    if swf_cid is None:
        continue
    if lib.get("type") != "shape":
        continue
    if swf_cid in range(180, 195) or swf_cid in range(300, 310):
        f.write(f"  N2D lib id={lib.get('id')}: swfCharId={swf_cid}, name={lib.get('name','?')}, rawTagType={lib.get('rawTagType','?')}, recodes={len(lib.get('recodes',[]))}\n")

# The key issue: compile_n2d allocates NEW char IDs. Let me check if
# the roundtrip preserves original CIDs or reassigns.
f.write(f"\n{'=' * 80}\n")
f.write("CID PRESERVATION CHECK\n")
f.write(f"{'=' * 80}\n\n")

# Check a few known original CIDs
orig_cids = sorted(orig_shapes.keys())[:20]
for cid in orig_cids:
    in_rt = "YES" if cid in rt_shapes else "NO"
    o_tag, o_body = orig_shapes[cid]
    r_info = ""
    if cid in rt_shapes:
        r_tag, r_body = rt_shapes[cid]
        r_info = f"tag={r_tag}, size={len(r_body)}"
    f.write(f"  Orig CID {cid} (tag={o_tag}, size={len(o_body)}): in RT={in_rt}  {r_info}\n")

# Also show CID ranges
f.write(f"\n  Original CID range: {min(orig_shapes.keys())} - {max(orig_shapes.keys())}\n")
f.write(f"  Roundtrip CID range: {min(rt_shapes.keys())} - {max(rt_shapes.keys())}\n")
f.write(f"  Original count: {len(orig_shapes)}\n")
f.write(f"  Roundtrip count: {len(rt_shapes)}\n")

# Check specifically: does CID 183 exist as any tag type in roundtrip?
f.write(f"\n{'=' * 80}\n")
f.write("CHECKING ALL TAG TYPES FOR TARGET CIDS IN ROUNDTRIP\n")
f.write(f"{'=' * 80}\n\n")

for cid in sorted(TARGET_CIDS):
    found = False
    for tag_type, t_cid, body in rt_tags:
        if len(body) >= 2:
            body_cid = struct.unpack_from('<H', body, 0)[0]
            if body_cid == cid:
                f.write(f"CID {cid}: Found as tag type {tag_type}, size={len(body)}\n")
                found = True
    if not found:
        f.write(f"CID {cid}: NOT found in any roundtrip tag\n")

f.close()
print(f"Done. Output: {OUT} ({os.path.getsize(OUT)} bytes)")
