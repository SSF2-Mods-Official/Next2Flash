"""Full structural comparison: OG fox.ssf vs a fresh import+compile output.
Compares all tag types, counts, ordering, and key structural properties."""
import sys, os, struct, tempfile, json
sys.path.insert(0, os.path.dirname(__file__))

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Do a fresh import → save as N2D → full compile
from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder

print("=== Step 1: Import SWF to N2D ===")
with open(OG, 'rb') as f:
    swf_data = f.read()
header, og_tags = parse_swf(swf_data)
validate_swf_sprites(og_tags)
builder = N2DBuilder(header, name="fox")
builder.catalog_swf_tags(og_tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(og_tags)
n2d = builder.to_n2d_json()

# Save N2D as zip with msgpack inside (as expected by full pipeline)
import msgpack, zlib, zipfile
tmpdir = tempfile.mkdtemp(prefix="fox_compare_")
n2d_path = os.path.join(tmpdir, "fox.n2d")
packed = msgpack.packb(n2d, use_bin_type=True)
with zipfile.ZipFile(n2d_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('project.msgpack', packed)
print(f"  N2D saved to: {n2d_path}")

# Full compile
print("\n=== Step 2: Full compile N2D → SWF ===")
from compile_n2d import N2DCompiler
output_path = os.path.join(tmpdir, "fox_compiled.ssf")
compiler = N2DCompiler(n2d_path, tmpdir, output_path)
compiler.compile()

if not os.path.exists(output_path):
    print("ERROR: Compile produced no output!")
    sys.exit(1)

with open(output_path, 'rb') as f:
    rt_data = f.read()
print(f"  Compiled: {len(rt_data)} bytes (OG: {len(swf_data)} bytes)")

# Parse both
print("\n=== Step 3: Parse and compare ===")
_, rt_tags = parse_swf(rt_data)

# Tag type summary
og_type_count = {}
rt_type_count = {}
for t in og_tags:
    og_type_count[t.tag_type] = og_type_count.get(t.tag_type, 0) + 1
for t in rt_tags:
    rt_type_count[t.tag_type] = rt_type_count.get(t.tag_type, 0) + 1

TAG_NAMES = {
    0: "End", 1: "ShowFrame", 2: "DefShape", 4: "PlaceObject",
    6: "DefBits", 8: "DefBitsJPEG", 9: "SetBgColor",
    10: "DefFont", 11: "DefText", 12: "DoAction",
    13: "DefFontInfo", 14: "DefSound", 15: "StartSound",
    18: "SoundStreamHead", 19: "SoundStreamBlock",
    20: "DefBitsLossless", 21: "DefBitsJPEG2",
    22: "DefShape2", 24: "Protect", 26: "PlaceObject2",
    28: "RemoveObject2", 32: "DefShape3", 33: "DefText2",
    34: "DefButton2", 35: "DefBitsJPEG3", 36: "DefBitsLossless2",
    37: "DefEditText", 39: "DefineSprite",
    43: "FrameLabel", 45: "SoundStreamHead2",
    46: "DefMorphShape", 48: "DefFont2", 56: "ExportAssets",
    57: "ImportAssets", 59: "DoInitAction",
    62: "DefFontInfo2", 69: "FileAttributes",
    70: "PlaceObject3", 73: "DefFontAlignZones",
    75: "DefFont3", 76: "SymbolClass", 77: "Metadata",
    78: "DefScalingGrid", 82: "DoABC",
    83: "DefShape4", 84: "DefMorphShape2",
    86: "DefSceneAndFrameLabel", 87: "DefBinaryData",
    88: "DefFontName", 91: "DefFont4",
}

all_types = sorted(set(og_type_count.keys()) | set(rt_type_count.keys()))
print(f"\n{'Tag':>3}  {'Name':<25} {'OG':>5} {'RT':>5} {'Match':>5}")
print("-" * 55)
mismatches = []
for t in all_types:
    oc = og_type_count.get(t, 0)
    rc = rt_type_count.get(t, 0)
    name = TAG_NAMES.get(t, f"Tag_{t}")
    match = "OK" if oc == rc else "DIFF"
    if oc != rc:
        mismatches.append((t, name, oc, rc))
    print(f"{t:>3}  {name:<25} {oc:>5} {rc:>5} {match:>5}")

print(f"\nTag count mismatches: {len(mismatches)}")
for t, name, oc, rc in mismatches:
    print(f"  {name} (tag {t}): OG={oc} RT={rc} (diff={rc-oc:+d})")

# Compare SymbolClass
print(f"\n=== SymbolClass comparison ===")
og_sym = {}
rt_sym = {}
for tag in og_tags:
    if tag.tag_type == 76:
        data = tag.data
        count = struct.unpack_from('<H', data, 0)[0]
        off = 2
        for _ in range(count):
            cid = struct.unpack_from('<H', data, off)[0]
            off += 2
            end = data.index(0, off)
            name = data[off:end].decode('utf-8', errors='replace')
            off = end + 1
            og_sym[name] = cid
for tag in rt_tags:
    if tag.tag_type == 76:
        data = tag.data
        count = struct.unpack_from('<H', data, 0)[0]
        off = 2
        for _ in range(count):
            cid = struct.unpack_from('<H', data, off)[0]
            off += 2
            end = data.index(0, off)
            name = data[off:end].decode('utf-8', errors='replace')
            off = end + 1
            rt_sym[name] = cid
print(f"  OG symbols: {len(og_sym)}, RT symbols: {len(rt_sym)}")
missing = set(og_sym.keys()) - set(rt_sym.keys())
extra = set(rt_sym.keys()) - set(og_sym.keys())
if missing:
    print(f"  MISSING in RT: {missing}")
if extra:
    print(f"  EXTRA in RT: {extra}")
if not missing and not extra:
    print(f"  All {len(og_sym)} symbols present in both")

# Compare DoABC
print(f"\n=== DoABC comparison ===")
og_abc = [t.data for t in og_tags if t.tag_type == 82]
rt_abc = [t.data for t in rt_tags if t.tag_type == 82]
print(f"  OG DoABC tags: {len(og_abc)}, RT: {len(rt_abc)}")
if len(og_abc) == len(rt_abc):
    for i in range(len(og_abc)):
        if og_abc[i] == rt_abc[i]:
            print(f"  DoABC[{i}]: IDENTICAL ({len(og_abc[i])} bytes)")
        else:
            print(f"  DoABC[{i}]: DIFFERENT (OG={len(og_abc[i])}, RT={len(rt_abc[i])})")

# Compare main timeline structure
print(f"\n=== Main timeline comparison ===")
og_main_tags = []
rt_main_tags = []
for tag in og_tags:
    if tag.tag_type in (1, 26, 70, 28, 43, 45, 15, 19, 12, 82, 76, 69):
        og_main_tags.append((tag.tag_type, len(tag.data)))
for tag in rt_tags:
    if tag.tag_type in (1, 26, 70, 28, 43, 45, 15, 19, 12, 82, 76, 69):
        rt_main_tags.append((tag.tag_type, len(tag.data)))
print(f"  OG main timeline key tags: {len(og_main_tags)}")
print(f"  RT main timeline key tags: {len(rt_main_tags)}")

# Compare sprite frame counts
print(f"\n=== Sprite frame count comparison ===")
og_sprites = {}
rt_sprites = {}
for tag in og_tags:
    if tag.tag_type == 39 and len(tag.data) >= 4:
        cid = struct.unpack_from('<H', tag.data, 0)[0]
        fc = struct.unpack_from('<H', tag.data, 2)[0]
        og_sprites[cid] = fc
for tag in rt_tags:
    if tag.tag_type == 39 and len(tag.data) >= 4:
        cid = struct.unpack_from('<H', tag.data, 0)[0]
        fc = struct.unpack_from('<H', tag.data, 2)[0]
        rt_sprites[cid] = fc

# Map by symbol name
og_sprite_by_sym = {}
for name, cid in og_sym.items():
    if cid in og_sprites:
        og_sprite_by_sym[name] = og_sprites[cid]
rt_sprite_by_sym = {}
for name, cid in rt_sym.items():
    if cid in rt_sprites:
        rt_sprite_by_sym[name] = rt_sprites[cid]

frame_mismatches = []
for name in sorted(set(og_sprite_by_sym.keys()) & set(rt_sprite_by_sym.keys())):
    if og_sprite_by_sym[name] != rt_sprite_by_sym[name]:
        frame_mismatches.append((name, og_sprite_by_sym[name], rt_sprite_by_sym[name]))
if frame_mismatches:
    print(f"  Frame count mismatches: {len(frame_mismatches)}")
    for name, og_fc, rt_fc in frame_mismatches[:20]:
        print(f"    {name}: OG={og_fc} RT={rt_fc}")
else:
    print(f"  All sprite frame counts match ({len(og_sprite_by_sym)} checked)")

# FileAttributes
print(f"\n=== FileAttributes ===")
for tag in og_tags:
    if tag.tag_type == 69:
        print(f"  OG: {tag.data.hex()}")
for tag in rt_tags:
    if tag.tag_type == 69:
        print(f"  RT: {tag.data.hex()}")

# Tag ordering (first 30 tags)
print(f"\n=== Tag ordering (first 30) ===")
for i in range(min(30, max(len(og_tags), len(rt_tags)))):
    og_t = og_tags[i].tag_type if i < len(og_tags) else "-"
    rt_t = rt_tags[i].tag_type if i < len(rt_tags) else "-"
    og_n = TAG_NAMES.get(og_tags[i].tag_type, f"T{og_tags[i].tag_type}") if i < len(og_tags) else "-"
    rt_n = TAG_NAMES.get(rt_tags[i].tag_type, f"T{rt_tags[i].tag_type}") if i < len(rt_tags) else "-"
    match = "OK" if og_t == rt_t else "**"
    print(f"  [{i:>3}] OG: {og_n:25s}({og_t})  RT: {rt_n:25s}({rt_t})  {match}")

# Cleanup
import shutil
shutil.rmtree(tmpdir, ignore_errors=True)
print(f"\nCleaned up {tmpdir}")
print("Done.")
