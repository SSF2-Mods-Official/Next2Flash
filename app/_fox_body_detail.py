"""Detailed tag-by-tag comparison inside the fox MC sprite body.
Figure out where the 692B size difference comes from."""
import sys, os, struct, tempfile, zipfile
sys.path.insert(0, os.path.dirname(__file__))

import msgpack
from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder
from compile_n2d import N2DCompiler

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Import + compile
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

tmpdir = tempfile.mkdtemp(prefix="fox_deep_")
n2d_path = os.path.join(tmpdir, "fox.n2d")
packed = msgpack.packb(n2d, use_bin_type=True)
with zipfile.ZipFile(n2d_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('project.msgpack', packed)
output_path = os.path.join(tmpdir, "fox_compiled.ssf")
compiler = N2DCompiler(n2d_path, tmpdir, output_path)
compiler.compile()
with open(output_path, 'rb') as f:
    rt_data = f.read()

_, rt_tags = parse_swf(rt_data)

def parse_inner(data):
    tags = []
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data): break
        hdr_pos = pos
        tc = struct.unpack_from('<H', data, pos)[0]
        tt = tc >> 6; tl = tc & 0x3F; pos += 2
        long_header = False
        if tl == 0x3F:
            if pos + 4 > len(data): break
            tl = struct.unpack_from('<I', data, pos)[0]; pos += 4
            long_header = True
        body = data[pos:pos+tl]; pos += tl
        total_len = (6 if long_header else 2) + tl
        tags.append((tt, body, total_len))
    return tags

TAG_NAMES = {
    0: "End", 1: "ShowFrame", 26: "PO2", 28: "RO2", 43: "FrameLabel",
    45: "SoundStreamHead2", 70: "PO3",
}

# Find fox MC in OG (98 frames)
og_fox = rt_fox = None
for tag in og_tags:
    if tag.tag_type == 39 and len(tag.data) >= 4:
        fc = struct.unpack_from('<H', tag.data, 2)[0]
        if fc == 98:
            og_fox = tag.data[4:]
            break
for tag in rt_tags:
    if tag.tag_type == 39 and len(tag.data) >= 4:
        fc = struct.unpack_from('<H', tag.data, 2)[0]
        if fc == 98:
            rt_fox = tag.data[4:]
            break

og_inner = parse_inner(og_fox)
rt_inner = parse_inner(rt_fox)

# Tag type totals and size
og_type_sizes = {}
rt_type_sizes = {}
for tt, body, total in og_inner:
    if tt not in og_type_sizes:
        og_type_sizes[tt] = {'count': 0, 'total_bytes': 0}
    og_type_sizes[tt]['count'] += 1
    og_type_sizes[tt]['total_bytes'] += total
for tt, body, total in rt_inner:
    if tt not in rt_type_sizes:
        rt_type_sizes[tt] = {'count': 0, 'total_bytes': 0}
    rt_type_sizes[tt]['count'] += 1
    rt_type_sizes[tt]['total_bytes'] += total

print(f"=== Fox MC inner tag breakdown ===")
print(f"  OG body: {len(og_fox)}B, RT body: {len(rt_fox)}B, diff: {len(og_fox)-len(rt_fox)}B")
print(f"  OG tags: {len(og_inner)}, RT tags: {len(rt_inner)}")
print()
all_tt = sorted(set(og_type_sizes.keys()) | set(rt_type_sizes.keys()))
print(f"{'Tag':>4} {'Name':15s} {'OG#':>5} {'OG_B':>7} {'RT#':>5} {'RT_B':>7} {'#diff':>6} {'B_diff':>7}")
for tt in all_tt:
    name = TAG_NAMES.get(tt, f"T{tt}")
    og = og_type_sizes.get(tt, {'count': 0, 'total_bytes': 0})
    rt = rt_type_sizes.get(tt, {'count': 0, 'total_bytes': 0})
    print(f"{tt:>4} {name:15s} {og['count']:>5} {og['total_bytes']:>7} {rt['count']:>5} {rt['total_bytes']:>7} {rt['count']-og['count']:>+6} {rt['total_bytes']-og['total_bytes']:>+7}")

# Now compare PO2 by frame and depth — show where the biggest byte differences are
print(f"\n=== PO2 size comparison by frame (depth 7) ===")
og_frames = []; curr = []
for tt, body, total in og_inner:
    if tt == 0: break
    if tt == 1: og_frames.append(curr); curr = []
    else: curr.append((tt, body, total))

rt_frames = []; curr = []
for tt, body, total in rt_inner:
    if tt == 0: break
    if tt == 1: rt_frames.append(curr); curr = []
    else: curr.append((tt, body, total))

# Focus on depth 7
total_og_d7 = 0
total_rt_d7 = 0
mismatched_frames = []
for f in range(min(len(og_frames), len(rt_frames))):
    og_d7 = [(tt, b, t) for tt, b, t in og_frames[f] if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] == 7]
    rt_d7 = [(tt, b, t) for tt, b, t in rt_frames[f] if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] == 7]
    
    og_b = sum(t for _, _, t in og_d7)
    rt_b = sum(t for _, _, t in rt_d7)
    total_og_d7 += og_b
    total_rt_d7 += rt_b
    
    if og_b != rt_b or len(og_d7) != len(rt_d7):
        mismatched_frames.append((f+1, len(og_d7), og_b, len(rt_d7), rt_b))
        
    # Also compare flags and body size individually 
    for i in range(min(len(og_d7), len(rt_d7))):
        og_tt, og_b_data, og_total = og_d7[i]
        rt_tt, rt_b_data, rt_total = rt_d7[i]
        og_flags = og_b_data[0]
        rt_flags = rt_b_data[0]
        if og_flags != rt_flags and f+1 <= 5:
            print(f"  Frame {f+1}: OG flags=0x{og_flags:02x} RT flags=0x{rt_flags:02x} (OG {og_total}B RT {rt_total}B)")

print(f"\n  Depth 7 total: OG={total_og_d7}B, RT={total_rt_d7}B, diff={total_og_d7-total_rt_d7}B")
print(f"  Frames with size mismatch at depth 7: {len(mismatched_frames)}")
if mismatched_frames:
    for f, oc, ob, rc, rb in mismatched_frames[:10]:
        print(f"    Frame {f}: OG {oc} tags {ob}B, RT {rc} tags {rb}B")

# Non-depth-7 comparison
print(f"\n=== Non-depth-7 PO2 sizes ===")
total_og_other = 0
total_rt_other = 0
for f in range(min(len(og_frames), len(rt_frames))):
    og_other = [(tt, b, t) for tt, b, t in og_frames[f] if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] != 7]
    rt_other = [(tt, b, t) for tt, b, t in rt_frames[f] if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] != 7]
    total_og_other += sum(t for _, _, t in og_other)
    total_rt_other += sum(t for _, _, t in rt_other)

print(f"  Other depths total: OG={total_og_other}B, RT={total_rt_other}B, diff={total_og_other-total_rt_other}B")

# Check frame 88 specifically (the one with data diff)
print(f"\n=== Frame 88 depth 7 detail ===")
if len(og_frames) >= 88 and len(rt_frames) >= 88:
    og_88_d7 = [(tt, b, t) for tt, b, t in og_frames[87] if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] == 7]
    rt_88_d7 = [(tt, b, t) for tt, b, t in rt_frames[87] if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] == 7]
    
    for i in range(max(len(og_88_d7), len(rt_88_d7))):
        if i < len(og_88_d7):
            tt, b, t = og_88_d7[i]
            flags = b[0]
            has_char = bool(flags & 0x02); has_ratio = bool(flags & 0x10); has_name = bool(flags & 0x20)
            print(f"  OG PO2[{i}]: flags=0x{flags:02x} move={bool(flags&1)} char={has_char} ratio={has_ratio} name={has_name} ({t}B)")
            print(f"    hex: {b.hex()}")
        if i < len(rt_88_d7):
            tt, b, t = rt_88_d7[i]
            flags = b[0]
            has_char = bool(flags & 0x02); has_ratio = bool(flags & 0x10); has_name = bool(flags & 0x20)
            print(f"  RT PO2[{i}]: flags=0x{flags:02x} move={bool(flags&1)} char={has_char} ratio={has_ratio} name={has_name} ({t}B)")
            print(f"    hex: {b.hex()}")

# Cleanup
import shutil
shutil.rmtree(tmpdir, ignore_errors=True)
print("\nDone.")
