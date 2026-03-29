"""
Deep charID analysis: compare original vs exported SWF tag-by-tag.
Shows every DefineXxx -> charID and every PlaceObject -> charID reference,
plus checks that each referenced charID was actually defined and maps to
the same type of asset.
"""
import struct, zlib, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ── SWF parser (minimal) ──────────────────────────────────────────────

TAG_NAMES = {
    1:'ShowFrame',2:'DefineShape',4:'PlaceObject',6:'DefineBits',7:'DefineButton',
    8:'JPEGTables',9:'SetBgColor',10:'DefineFont',11:'DefineText',12:'DoAction',
    13:'DefineFontInfo',14:'DefineSound',20:'DefineBitsLossless',21:'DefineBitsJPEG2',
    22:'DefineShape2',24:'Protect',26:'PlaceObject2',28:'RemoveObject2',
    32:'DefineShape3',33:'DefineBitsJPEG3',34:'DefineBitsLossless2',35:'DefineBitsJPEG4',
    36:'DefineMorphShape',37:'DefineFont2',39:'DefineSprite',
    45:'SoundStreamHead2',46:'DefineMorphShape2',48:'DefineFont3',
    56:'ExportAssets',59:'DoInitAction',
    69:'FileAttributes',70:'PlaceObject3',73:'DefineFontAlignZones',
    74:'CSMTextSettings',75:'DefineFont4',76:'SymbolClass',
    82:'DoABC2',83:'DefineShape4',86:'DefineSceneFrameLabel',88:'DefineFontName',
    0:'End',1:'ShowFrame',
}

DEFINE_TAGS = {2,10,11,14,20,21,22,32,33,34,35,36,37,39,46,48,83,6,7,88}
PLACE_TAGS = {4,26,70}

def decompress(data):
    sig = data[:3]
    if sig == b'CWS':
        unc = data[:8] + zlib.decompress(data[8:])
        return unc
    elif sig == b'FWS':
        return data
    raise ValueError(f"Unknown SWF signature: {sig}")

def read_rect_bits(data, bit_offset):
    byte_idx = bit_offset // 8
    bit_idx = bit_offset % 8
    nbits = 0
    for i in range(5):
        b = (data[byte_idx + (bit_idx + i) // 8] >> (7 - (bit_idx + i) % 8)) & 1
        nbits = (nbits << 1) | b
    return nbits, bit_offset + 5 + nbits * 4

def parse_tags(data):
    # Skip header: signature(3) + version(1) + length(4) + RECT + fps(2) + frameCount(2)
    offset = 8
    _, end_bit = read_rect_bits(data, offset * 8)
    offset = (end_bit + 7) // 8 + 4  # +2 fps +2 frameCount
    
    tags = []
    while offset < len(data):
        if offset + 2 > len(data):
            break
        tag_code_and_length = struct.unpack_from('<H', data, offset)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3f
        offset += 2
        if length == 0x3f:
            if offset + 4 > len(data):
                break
            length = struct.unpack_from('<I', data, offset)[0]
            offset += 4
        tag_data = data[offset:offset+length]
        tags.append((tag_type, tag_data))
        offset += length
        if tag_type == 0:
            break
    return tags

def get_define_charid(tag_type, tag_data):
    """Extract the charID from a define tag."""
    if tag_type in DEFINE_TAGS and len(tag_data) >= 2:
        return struct.unpack_from('<H', tag_data, 0)[0]
    return None

def get_place_info(tag_type, tag_data):
    """Extract depth and optional charID from PlaceObject2/3."""
    if tag_type == 26 and len(tag_data) >= 3:  # PlaceObject2
        flags = tag_data[0]
        depth = struct.unpack_from('<H', tag_data, 1)[0]
        has_char = flags & 0x02
        char_id = None
        if has_char and len(tag_data) >= 5:
            char_id = struct.unpack_from('<H', tag_data, 3)[0]
        return depth, char_id, flags
    elif tag_type == 70 and len(tag_data) >= 4:  # PlaceObject3
        flags = struct.unpack_from('<H', tag_data, 0)[0]
        depth = struct.unpack_from('<H', tag_data, 2)[0]
        has_char = flags & 0x02
        char_id = None
        if has_char and len(tag_data) >= 6:
            char_id = struct.unpack_from('<H', tag_data, 4)[0]
        return depth, char_id, flags
    return None, None, None

def parse_sprite_tags(sprite_data):
    """Parse tags inside a DefineSprite."""
    if len(sprite_data) < 4:
        return []
    # skip charID(2) + frameCount(2)
    offset = 4
    tags = []
    while offset < len(sprite_data):
        if offset + 2 > len(sprite_data):
            break
        tc = struct.unpack_from('<H', sprite_data, offset)[0]
        tt = tc >> 6
        tl = tc & 0x3f
        offset += 2
        if tl == 0x3f:
            if offset + 4 > len(sprite_data):
                break
            tl = struct.unpack_from('<I', sprite_data, offset)[0]
            offset += 4
        td = sprite_data[offset:offset+tl]
        tags.append((tt, td))
        offset += tl
        if tt == 0:
            break
    return tags

def parse_symbol_class(tag_data):
    """Parse SymbolClass tag -> dict of charID -> className."""
    if len(tag_data) < 2:
        return {}
    num = struct.unpack_from('<H', tag_data, 0)[0]
    offset = 2
    result = {}
    for _ in range(num):
        if offset + 2 > len(tag_data):
            break
        cid = struct.unpack_from('<H', tag_data, offset)[0]
        offset += 2
        end = tag_data.index(0, offset)
        name = tag_data[offset:end].decode('utf-8', errors='replace')
        offset = end + 1
        result[cid] = name
    return result

def analyze_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    data = decompress(raw)
    tags = parse_tags(data)
    
    defines = {}  # charID -> (tag_type, tag_data_len, tag_index)
    symbols = {}  # charID -> className
    root_places = []  # (depth, charID, flags)
    sprite_refs = {}  # charID -> list of (depth, referenced_charID)
    
    for i, (tt, td) in enumerate(tags):
        cid = get_define_charid(tt, td)
        if cid is not None:
            defines[cid] = (tt, len(td), i)
        
        if tt == 76:  # SymbolClass
            symbols = parse_symbol_class(td)
        
        if tt in PLACE_TAGS:
            depth, char_id, flags = get_place_info(tt, td)
            if depth is not None:
                root_places.append((depth, char_id, flags))
        
        if tt == 39:  # DefineSprite
            sprite_cid = struct.unpack_from('<H', td, 0)[0]
            sprite_tags = parse_sprite_tags(td)
            refs = []
            for st, sd in sprite_tags:
                if st in PLACE_TAGS:
                    d, c, f = get_place_info(st, sd)
                    if d is not None and c is not None:
                        refs.append((d, c))
            sprite_refs[sprite_cid] = refs
    
    return {
        'tags': tags,
        'defines': defines,
        'symbols': symbols,
        'root_places': root_places,
        'sprite_refs': sprite_refs,
    }

# ── MAIN ──────────────────────────────────────────────────────────────

orig_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf'
exp_path = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\cli3.swf'

print("Parsing original...")
orig = analyze_swf(orig_path)
print("Parsing exported...")
exp = analyze_swf(exp_path)

# Build reverse symbol maps: className -> charID
orig_class_to_id = {v: k for k, v in orig['symbols'].items()}
exp_class_to_id = {v: k for k, v in exp['symbols'].items()}

# Build charID -> tag_type maps
orig_id_type = {cid: TAG_NAMES.get(info[0], f'Tag{info[0]}') for cid, info in orig['defines'].items()}
exp_id_type = {cid: TAG_NAMES.get(info[0], f'Tag{info[0]}') for cid, info in exp['defines'].items()}

print("\n" + "="*70)
print("CHECKING: Do sprite PlaceObjects reference the right asset types?")
print("="*70)

errors = []
warnings = []

# For each sprite in exported, check that every charID it references is defined
# and maps to the same type as in the original
for exp_sprite_cid, exp_refs in sorted(exp['sprite_refs'].items()):
    sprite_name = exp['symbols'].get(exp_sprite_cid, f'(unnamed cid={exp_sprite_cid})')
    
    # Find the original sprite by class name
    orig_sprite_cid = orig_class_to_id.get(sprite_name)
    if orig_sprite_cid is None:
        # Try without dots
        continue
    
    orig_refs = orig['sprite_refs'].get(orig_sprite_cid, [])
    
    # Check each reference in exported
    for depth, ref_cid in exp_refs:
        if ref_cid not in exp['defines']:
            errors.append(f"  UNDEFINED REF: {sprite_name} depth={depth} references charID={ref_cid} which is NOT DEFINED")
            continue
        
        exp_ref_type = exp_id_type.get(ref_cid, '?')
        exp_ref_name = exp['symbols'].get(ref_cid, f'(unnamed)')
        
        # Find what the original sprite references at this depth
        orig_ref_at_depth = [(d, c) for d, c in orig_refs if d == depth]
        if orig_ref_at_depth:
            orig_ref_cid = orig_ref_at_depth[0][1]
            orig_ref_type = orig_id_type.get(orig_ref_cid, '?')
            orig_ref_name = orig['symbols'].get(orig_ref_cid, f'(unnamed)')
            
            if exp_ref_type != orig_ref_type:
                errors.append(
                    f"  TYPE MISMATCH: {sprite_name} depth={depth}: "
                    f"orig refs {orig_ref_name}({orig_ref_type} cid={orig_ref_cid}) "
                    f"but exp refs {exp_ref_name}({exp_ref_type} cid={ref_cid})"
                )
            elif exp_ref_name != orig_ref_name and exp_ref_name != '(unnamed)' and orig_ref_name != '(unnamed)':
                warnings.append(
                    f"  NAME MISMATCH: {sprite_name} depth={depth}: "
                    f"orig refs '{orig_ref_name}' but exp refs '{exp_ref_name}'"
                )

# Check root timeline
print("\n--- ROOT TIMELINE REFERENCES ---")
for i, (depth, cid, flags) in enumerate(exp['root_places']):
    if cid is not None:
        etype = exp_id_type.get(cid, '?')
        ename = exp['symbols'].get(cid, '(unnamed)')
        
        if i < len(orig['root_places']):
            od, oc, of_ = orig['root_places'][i]
            otype = orig_id_type.get(oc, '?') if oc else '?'
            oname = orig['symbols'].get(oc, '(unnamed)') if oc else '?'
            match = "OK" if etype == otype and ename == oname else "MISMATCH"
            print(f"  [{match}] depth={depth}: exp={ename}({etype} cid={cid}) orig={oname}({otype} cid={oc})")
        else:
            print(f"  [NEW] depth={depth}: exp={ename}({etype} cid={cid})")

print(f"\n--- ERRORS: {len(errors)} ---")
for e in errors[:50]:
    print(e)
if len(errors) > 50:
    print(f"  ... and {len(errors)-50} more")

print(f"\n--- WARNINGS: {len(warnings)} ---")
for w in warnings[:30]:
    print(w)
if len(warnings) > 30:
    print(f"  ... and {len(warnings)-30} more")

# Check for undefined references across ALL sprites
print("\n--- UNDEFINED REFERENCE CHECK ---")
all_defined = set(exp['defines'].keys())
undef_count = 0
for sprite_cid, refs in exp['sprite_refs'].items():
    sname = exp['symbols'].get(sprite_cid, f'cid={sprite_cid}')
    for depth, ref_cid in refs:
        if ref_cid not in all_defined:
            print(f"  {sname} depth={depth} -> charID={ref_cid} NOT DEFINED!")
            undef_count += 1
print(f"Total undefined references: {undef_count}")

# Show define order comparison (first 30)
print("\n--- DEFINE ORDER (first 30 by charID) ---")
print(f"  {'charID':>6}  {'Orig Type':<25} {'Orig Name':<40} {'Exp Type':<25} {'Exp Name'}")
for cid in sorted(set(list(orig['defines'].keys())[:30] + list(exp['defines'].keys())[:30])):
    ot = orig_id_type.get(cid, '-')
    on = orig['symbols'].get(cid, '')
    et = exp_id_type.get(cid, '-')
    en = exp['symbols'].get(cid, '')
    flag = " DIFF" if (ot != et or on != en) and ot != '-' and et != '-' else ""
    print(f"  {cid:>6}  {ot:<25} {on:<40} {et:<25} {en}{flag}")
