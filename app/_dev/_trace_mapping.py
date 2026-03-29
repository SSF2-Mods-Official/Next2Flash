"""Trace a specific charID mapping through the roundtrip."""
import json, zipfile, struct, zlib

with zipfile.ZipFile('converted/gameandwatch_cli.n2d') as zf:
    data = json.loads(zf.read('project.json'))

# Build orig_cid -> lib mapping
orig_cid_to_lib = {}
for lib in data['libraries']:
    c = lib.get('swfCharId')
    if c is not None:
        orig_cid_to_lib[c] = lib

# Check specific problematic charIDs from the errors
problem_cids = [271, 486, 578, 568, 326, 367, 411, 421, 425, 454, 494, 501, 481]
for cid in problem_cids:
    lib = orig_cid_to_lib.get(cid)
    if lib:
        print(f"orig_cid={cid}: lib_id={lib['id']}, name={lib.get('name','?')}, type={lib.get('type','?')}, rawTagType={lib.get('rawTagType','?')}")
    else:
        print(f"orig_cid={cid}: NOT FOUND!")

# Now let's trace what _orig_to_new_id would contain for these
print("\n--- Checking compile_n2d mapping ---")
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compile_n2d import N2DCompiler

class MockCompiler(N2DCompiler):
    def compile(self): pass

mc = MockCompiler.__new__(MockCompiler)
mc.n2d_path = 'converted/gameandwatch_cli.n2d'
mc.output_path = '/dev/null'
mc.shared_dir = 'converted'
mc.sdk_path = None
mc._load_n2d()
mc._assign_ids_and_order()

print(f"_orig_to_new_id entries: {len(mc._orig_to_new_id)}")
for cid in problem_cids:
    new_id = mc._orig_to_new_id.get(cid)
    print(f"  orig={cid} -> new={new_id}")

# Also check what the NEW IDs map to in the original
print("\n--- What do the NEW charIDs refer to? ---")
# Parse the exported SWF to see what's at each new charID
def parse_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    offset = 8
    first_byte = raw[8]
    nbits = first_byte >> 3
    total_rect_bits = 5 + nbits * 4
    offset = 8 + (total_rect_bits + 7) // 8 + 4
    tag_names = {2:'DefineShape',10:'DefineFont',11:'DefineText',14:'DefineSound',
        20:'DefineBitsLossless',21:'DefineBitsJPEG2',22:'DefineShape2',
        32:'DefineShape3',33:'DefineBitsJPEG3',34:'DefineBitsLossless2',
        36:'DefineMorphShape',39:'DefineSprite',46:'DefineMorphShape2',
        48:'DefineFont3',83:'DefineShape4',88:'DefineFontName'}
    defines = {}
    while offset < len(raw):
        tc = struct.unpack_from('<H', raw, offset)[0]
        tt = tc >> 6; tl = tc & 0x3f; offset += 2
        if tl == 0x3f: tl = struct.unpack_from('<I', raw, offset)[0]; offset += 4
        if tt in tag_names and tl >= 2:
            cid = struct.unpack_from('<H', raw, offset)[0]
            defines[cid] = tag_names[tt]
        offset += tl
        if tt == 0: break
    return defines

exp_defines = parse_swf('converted/gameandwatch_cli2.swf')
orig_defines = parse_swf(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf')

for cid in problem_cids:
    new_id = mc._orig_to_new_id.get(cid)
    orig_type = orig_defines.get(cid, '?')
    if new_id:
        new_type = exp_defines.get(new_id, '?')
        print(f"  orig cid={cid} ({orig_type}) -> new cid={new_id} ({new_type})")
    else:
        print(f"  orig cid={cid} ({orig_type}) -> NO MAPPING")
