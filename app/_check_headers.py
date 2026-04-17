"""Compare SWF headers and check for any runtime-relevant differences."""
import sys, os, struct, tempfile, zipfile
sys.path.insert(0, os.path.dirname(__file__))

import msgpack
from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder
from compile_n2d import N2DCompiler

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Import
with open(OG, 'rb') as f:
    og_data = f.read()
header, og_tags = parse_swf(og_data)
validate_swf_sprites(og_tags)
builder = N2DBuilder(header, name="fox")
builder.catalog_swf_tags(og_tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(og_tags)
n2d = builder.to_n2d_json()

# Compile
tmpdir = tempfile.mkdtemp(prefix="fox_hdr_")
n2d_path = os.path.join(tmpdir, "fox.n2d")
packed = msgpack.packb(n2d, use_bin_type=True)
with zipfile.ZipFile(n2d_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('project.msgpack', packed)
output_path = os.path.join(tmpdir, "fox_compiled.ssf")
compiler = N2DCompiler(n2d_path, tmpdir, output_path)
compiler.compile()
with open(output_path, 'rb') as f:
    rt_data = f.read()

# Compare headers
print("=== SWF Headers ===")
print(f"  OG: sig={og_data[:3]} version={og_data[3]} length={struct.unpack_from('<I', og_data, 4)[0]} actual={len(og_data)}")
print(f"  RT: sig={rt_data[:3]} version={rt_data[3]} length={struct.unpack_from('<I', rt_data, 4)[0]} actual={len(rt_data)}")

# Parse both headers properly
og_h, _ = parse_swf(og_data)
rt_h, _ = parse_swf(rt_data)
print(f"\n  OG header: {og_h}")
print(f"  RT header: {rt_h}")

# Compare the main timeline tag-by-tag (ignoring definition tags)
print(f"\n=== Main timeline tags (non-definition) ===")
# Definition tags are those that define characters (shapes, bitmaps, sounds, sprites, fonts, text)
DEFINITION_TAGS = {2, 6, 8, 10, 11, 13, 14, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 46, 48, 56, 62, 73, 74, 75, 83, 84, 87, 88, 91}
og_timeline = [(t.tag_type, t.data) for t in og_tags if t.tag_type not in DEFINITION_TAGS]
rt_timeline = [(t.tag_type, t.data) for t in parse_swf(rt_data)[1] if t.tag_type not in DEFINITION_TAGS]

print(f"  OG timeline tags: {len(og_timeline)}")
print(f"  RT timeline tags: {len(rt_timeline)}")

TAG_NAMES = {
    0: "End", 1: "ShowFrame", 9: "SetBgColor", 24: "Protect",
    26: "PlaceObject2", 28: "RemoveObject2", 43: "FrameLabel",
    45: "SoundStreamHead2", 69: "FileAttributes", 70: "PlaceObject3",
    76: "SymbolClass", 82: "DoABC", 86: "DefSceneAndFrameLabel",
}

for i in range(max(len(og_timeline), len(rt_timeline))):
    og_tt, og_d = og_timeline[i] if i < len(og_timeline) else (None, None)
    rt_tt, rt_d = rt_timeline[i] if i < len(rt_timeline) else (None, None)
    og_name = TAG_NAMES.get(og_tt, f"T{og_tt}") if og_tt is not None else "-"
    rt_name = TAG_NAMES.get(rt_tt, f"T{rt_tt}") if rt_tt is not None else "-"
    data_match = "DATA_MATCH" if og_d == rt_d else "DATA_DIFF"
    type_match = "OK" if og_tt == rt_tt else "TYPE_DIFF"
    status = f"{type_match} {data_match}" if og_tt == rt_tt else type_match
    print(f"  [{i:>2}] OG: {og_name:25s}  RT: {rt_name:25s}  {status}")

# Check: compare PO2 data on main timeline frame by frame
print(f"\n=== Main timeline PO2 comparison ===")
og_frame_po2s = []
rt_frame_po2s = []
current = []
for tt, d in og_timeline:
    if tt == 1:
        og_frame_po2s.append(current)
        current = []
    elif tt in (26, 70):
        flags = d[0]
        depth = struct.unpack_from('<H', d, 1)[0]
        current.append({'type': tt, 'flags': flags, 'depth': depth, 'len': len(d)})
current = []
for tt, d in rt_timeline:
    if tt == 1:
        rt_frame_po2s.append(current)
        current = []
    elif tt in (26, 70):
        flags = d[0]
        depth = struct.unpack_from('<H', d, 1)[0]
        current.append({'type': tt, 'flags': flags, 'depth': depth, 'len': len(d)})

for f in range(min(len(og_frame_po2s), len(rt_frame_po2s))):
    if len(og_frame_po2s[f]) != len(rt_frame_po2s[f]):
        print(f"  Frame {f+1}: PO2 count OG={len(og_frame_po2s[f])} RT={len(rt_frame_po2s[f])}")
    else:
        for j in range(len(og_frame_po2s[f])):
            og_po = og_frame_po2s[f][j]
            rt_po = rt_frame_po2s[f][j]
            if og_po['type'] != rt_po['type']:
                print(f"  Frame {f+1} PO2[{j}]: tag type OG={og_po['type']} RT={rt_po['type']}")
            if og_po['flags'] != rt_po['flags']:
                print(f"  Frame {f+1} PO2[{j}] depth={og_po['depth']}: flags OG=0x{og_po['flags']:02x} RT=0x{rt_po['flags']:02x}")

# Check: in the fox MC sprite, compare EVERY depth's PO2 data byte-by-byte
print(f"\n=== Fox MC: byte-level PO2 comparison ===")
# Find fox MC in both OG and RT
fox_sym_name = None
for name, cid in {n: c for t in og_tags if t.tag_type == 76 for n, c in [(lambda d: (lambda: None)())(t.data)]}.items() if False else []:
    pass  # skip fancy approach

# Just find the fox sprite - it's the one with 98 frames
og_fox_data = None
rt_fox_data = None
for tag in og_tags:
    if tag.tag_type == 39 and len(tag.data) >= 4:
        fc = struct.unpack_from('<H', tag.data, 2)[0]
        if fc == 98:
            og_fox_data = tag.data[4:]
            og_fox_cid = struct.unpack_from('<H', tag.data, 0)[0]
            break

for tag in parse_swf(rt_data)[1]:
    if tag.tag_type == 39 and len(tag.data) >= 4:
        fc = struct.unpack_from('<H', tag.data, 2)[0]
        if fc == 98:
            rt_fox_data = tag.data[4:]
            rt_fox_cid = struct.unpack_from('<H', tag.data, 0)[0]
            break

if og_fox_data and rt_fox_data:
    print(f"  OG fox cid={og_fox_cid}, body={len(og_fox_data)}B")
    print(f"  RT fox cid={rt_fox_cid}, body={len(rt_fox_data)}B")
    
    # Parse frame by frame
    def parse_inner(data):
        tags = []
        pos = 0
        while pos < len(data):
            if pos + 2 > len(data): break
            tc = struct.unpack_from('<H', data, pos)[0]
            tt = tc >> 6; tl = tc & 0x3F; pos += 2
            if tl == 0x3F:
                if pos + 4 > len(data): break
                tl = struct.unpack_from('<I', data, pos)[0]; pos += 4
            body = data[pos:pos+tl]; pos += tl
            tags.append((tt, body))
        return tags
    
    og_inner = parse_inner(og_fox_data)
    rt_inner = parse_inner(rt_fox_data)
    
    # Compare frame-by-frame
    og_frames = []; curr = []
    for tt, b in og_inner:
        if tt == 0: break
        if tt == 1: og_frames.append(curr); curr = []
        else: curr.append((tt, b))
    
    rt_frames = []; curr = []
    for tt, b in rt_inner:
        if tt == 0: break
        if tt == 1: rt_frames.append(curr); curr = []
        else: curr.append((tt, b))
    
    po2_total = 0
    po2_byte_match = 0
    po2_byte_diff = 0
    diff_details = []
    
    for f in range(min(len(og_frames), len(rt_frames))):
        og_po = [(tt, b) for tt, b in og_frames[f] if tt in (26, 70)]
        rt_po = [(tt, b) for tt, b in rt_frames[f] if tt in (26, 70)]
        og_ro = [(tt, b) for tt, b in og_frames[f] if tt == 28]
        rt_ro = [(tt, b) for tt, b in rt_frames[f] if tt == 28]
        
        if len(og_ro) != len(rt_ro):
            diff_details.append(f"  Frame {f+1}: RO2 count OG={len(og_ro)} RT={len(rt_ro)}")
        
        for j in range(min(len(og_po), len(rt_po))):
            po2_total += 1
            og_tt, og_b = og_po[j]
            rt_tt, rt_b = rt_po[j]
            og_depth = struct.unpack_from('<H', og_b, 1)[0]
            rt_depth = struct.unpack_from('<H', rt_b, 1)[0]
            
            if og_depth != rt_depth:
                diff_details.append(f"  Frame {f+1} PO[{j}]: depth OG={og_depth} RT={rt_depth}")
            
            # Compare flags
            og_flags = og_b[0]
            rt_flags = rt_b[0]
            if og_flags != rt_flags:
                diff_details.append(f"  Frame {f+1} PO depth={og_depth}: flags OG=0x{og_flags:02x} RT=0x{rt_flags:02x}")
                po2_byte_diff += 1
            elif og_b == rt_b:
                po2_byte_match += 1
            else:
                # Same flags, different data — could be char IDs (expected to differ)
                # Check if data differs ONLY in charId
                off = 3
                og_char = rt_char = None
                if og_flags & 0x02:  # HasChar
                    og_char = struct.unpack_from('<H', og_b, off)[0]
                    rt_char = struct.unpack_from('<H', rt_b, off)[0]
                    off += 2
                    # Compare rest (matrix, ratio, name, etc.)
                    og_rest = og_b[3+2:]
                    rt_rest = rt_b[3+2:]
                    if og_rest == rt_rest:
                        pass  # Only charId differs — expected
                    else:
                        diff_details.append(f"  Frame {f+1} PO depth={og_depth}: non-charId data differs ({len(og_rest)}B vs {len(rt_rest)}B)")
                        po2_byte_diff += 1
                else:
                    diff_details.append(f"  Frame {f+1} PO depth={og_depth}: data differs (no char, {len(og_b)}B vs {len(rt_b)}B)")
                    po2_byte_diff += 1
    
    print(f"  PO2 total compared: {po2_total}")
    print(f"  Byte-identical: {po2_byte_match}")
    print(f"  Flag/data differences: {po2_byte_diff}")
    if diff_details:
        for d in diff_details[:30]:
            print(d)
    else:
        print("  No flag or data differences (only char IDs differ as expected)")
else:
    print("  Could not find fox sprite in one or both SWFs")

# Cleanup
import shutil
shutil.rmtree(tmpdir, ignore_errors=True)
print("\nDone.")
