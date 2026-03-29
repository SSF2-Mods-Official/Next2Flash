"""
Focused test: check specific sprite PlaceObject2 references to verify remapping.
Pick Hurts_88 (the first error in the debug tool) and trace every PlaceObject2.
"""
import struct, zlib, json, zipfile, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ORIG_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf'
EXP_PATH = 'converted/cli3.swf'

def decompress(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = data[:8] + zlib.decompress(data[8:])
    return data

def walk_tags(data, start_offset):
    offset = start_offset
    tags = []
    while offset < len(data):
        tc = struct.unpack_from('<H', data, offset)[0]
        tt = tc >> 6; tl = tc & 0x3f; hs = 2
        if tl == 0x3f:
            tl = struct.unpack_from('<I', data, offset + 2)[0]; hs = 6
        tags.append((tt, offset + hs, tl))
        offset += hs + tl
        if tt == 0: break
    return tags

def get_header_skip(data):
    offset = 8
    nbits = data[8] >> 3
    total_bits = 5 + nbits * 4
    offset = 8 + (total_bits + 7) // 8 + 4
    return offset

def find_sprite_by_name(data, name):
    """Find DefineSprite charID by SymbolClass name."""
    offset = get_header_skip(data)
    symbols = {}
    sprite_bodies = {}
    for tt, data_off, tl in walk_tags(data, offset):
        if tt == 76:  # SymbolClass
            sym_data = data[data_off:data_off+tl]
            count = struct.unpack_from('<H', sym_data, 0)[0]
            pos = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', sym_data, pos)[0]; pos += 2
                end = sym_data.index(0, pos); nm = sym_data[pos:end].decode('utf-8'); pos = end + 1
                symbols[cid] = nm
        elif tt == 39:  # DefineSprite
            cid = struct.unpack_from('<H', data, data_off)[0]
            sprite_bodies[cid] = data[data_off+2:data_off+tl]  # frameCount + sub-tags
    
    # Find by name
    for cid, nm in symbols.items():
        if name in nm:
            return cid, sprite_bodies.get(cid), symbols
    return None, None, symbols

def extract_place_refs(sprite_body):
    """Extract all PlaceObject2/3 references from a sprite body as (depth, charId, frame)."""
    if not sprite_body or len(sprite_body) < 4:
        return []
    refs = []
    frame = 0
    offset = 2  # skip frameCount
    while offset < len(sprite_body):
        if offset + 2 > len(sprite_body): break
        tc = struct.unpack_from('<H', sprite_body, offset)[0]
        tt = tc >> 6; tl = tc & 0x3f; hs = 2
        if tl == 0x3f:
            if offset + 6 > len(sprite_body): break
            tl = struct.unpack_from('<I', sprite_body, offset + 2)[0]; hs = 6
        data_off = offset + hs
        
        if tt == 1:  # ShowFrame
            frame += 1
        elif tt == 26 and tl >= 3:  # PlaceObject2
            flags = sprite_body[data_off]
            depth = struct.unpack_from('<H', sprite_body, data_off + 1)[0]
            cid = None
            if flags & 0x02 and tl >= 5:
                cid = struct.unpack_from('<H', sprite_body, data_off + 3)[0]
            refs.append((depth, cid, frame, 'PO2'))
        elif tt == 70 and tl >= 4:  # PlaceObject3
            flags = struct.unpack_from('<H', sprite_body, data_off)[0]
            depth = struct.unpack_from('<H', sprite_body, data_off + 2)[0]
            cid = None
            if flags & 0x02 and tl >= 6:
                cid = struct.unpack_from('<H', sprite_body, data_off + 4)[0]
            refs.append((depth, cid, frame, 'PO3'))
        
        offset += hs + tl
        if tt == 0: break
    return refs

# Load N2D to get the orig_to_new_id mapping
import compile_n2d, copy
with zipfile.ZipFile('converted/gameandwatch_cli.n2d') as zf:
    n2d = json.loads(zf.read('project.json'))

c = compile_n2d.N2DCompiler.__new__(compile_n2d.N2DCompiler)
c.n2d_path = 'converted/gameandwatch_cli.n2d'
c.shared_dir = '.'; c.output_path = 'x'; c.sdk_path = None
c.data = copy.deepcopy(n2d); c.stage = c.data.get("stage",{})
c.libs = c.data.get("libraries",[]); c.id_to_lib = {lib["id"]: lib for lib in c.libs}
c._next_id = 1; c._lib_to_swf_id = {}; c._lib_to_char_idx = {}
c._char_idx_to_swf_id = {}; c._definition_tags = bytearray()
c._assign_ids()
id_map = c._orig_to_new_id

print("=== Verifying PlaceObject remapping for Hurts_88 ===\n")

# Parse both SWFs
orig_data = decompress(ORIG_PATH)
exp_data = decompress(EXP_PATH)

# Build define maps for both
def build_define_map(data):
    offset = get_header_skip(data)
    defines = {}
    for tt, data_off, tl in walk_tags(data, offset):
        DEFINE_TAGS = {2,6,10,11,14,20,21,22,32,36,37,39,46,48,83}
        if tt in DEFINE_TAGS and tl >= 2:
            cid = struct.unpack_from('<H', data, data_off)[0]
            defines[cid] = tt
        if tt == 39 and tl >= 4:  # also walk inside sprites
            sprite_cid = struct.unpack_from('<H', data, data_off)[0]
            # Sub-tags inside sprite
            sub_off = data_off + 4  # skip charId + frameCount
            while sub_off < data_off + tl:
                stc = struct.unpack_from('<H', data, sub_off)[0]
                stt = stc >> 6; stl = stc & 0x3f; shs = 2
                if stl == 0x3f:
                    stl = struct.unpack_from('<I', data, sub_off + 2)[0]; shs = 6
                sd = sub_off + shs
                if stt in DEFINE_TAGS and stl >= 2:
                    scid = struct.unpack_from('<H', data, sd)[0]
                    defines[scid] = stt
                sub_off += shs + stl
                if stt == 0: break
    return defines

orig_defines = build_define_map(orig_data)
exp_defines = build_define_map(exp_data)

TAG_NAMES = {
    2:'DefineShape', 6:'DefineBits', 11:'DefineText', 14:'DefineSound',
    20:'DefineBitsLossless', 21:'DefineBitsJPEG2', 22:'DefineShape2',
    32:'DefineShape3', 36:'DefineBitsLossless2', 37:'DefineEditText',
    39:'DefineSprite', 46:'DefineMorphShape', 48:'DefineFont3',
    83:'DefineShape4', 10:'DefineFont',
}

# Find Hurts_88 in both
for sprite_name in ['Hurts_88', 'ItemSmash_68', 'NAir_54', 'DSmash_38']:
    print(f"\n--- {sprite_name} ---")
    orig_cid, orig_body, orig_syms = find_sprite_by_name(orig_data, sprite_name)
    exp_cid, exp_body, exp_syms = find_sprite_by_name(exp_data, sprite_name)
    
    if not orig_body or not exp_body:
        print(f"  NOT FOUND (orig={orig_cid}, exp={exp_cid})")
        continue
    
    orig_refs = extract_place_refs(orig_body)
    exp_refs = extract_place_refs(exp_body)
    
    print(f"  Orig sprite cid={orig_cid}, {len(orig_refs)} PlaceObject refs")
    print(f"  Exp  sprite cid={exp_cid}, {len(exp_refs)} PlaceObject refs")
    
    # Compare ref by ref
    for i, (o_ref, e_ref) in enumerate(zip(orig_refs, exp_refs)):
        o_depth, o_cid, o_frame, o_type = o_ref
        e_depth, e_cid, e_frame, e_type = e_ref
        
        expected_cid = id_map.get(o_cid) if o_cid is not None else None
        
        o_tag = TAG_NAMES.get(orig_defines.get(o_cid, -1), f'Tag{orig_defines.get(o_cid,"?")}')
        e_tag = TAG_NAMES.get(exp_defines.get(e_cid, -1), f'Tag{exp_defines.get(e_cid,"?")}')
        
        status = "OK" if e_cid == expected_cid else "WRONG"
        if o_cid is None and e_cid is None:
            status = "OK (no charId)"
        
        if status != "OK":
            print(f"  [{status}] frame={o_frame} depth={o_depth}: "
                  f"orig_cid={o_cid}({o_tag}) -> expected={expected_cid}, got={e_cid}({e_tag})")
