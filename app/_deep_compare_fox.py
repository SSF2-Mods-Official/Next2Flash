"""Deep comparison: OG fox.ssf vs fresh-compiled - tag-by-tag for the main fox sprite
AND the 'a' attack child sprite. Checks PO2 flags, move vs place, depth patterns."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder
from compile_n2d import to_publish, build_timeline_tags

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"


# -- helpers --
def parse_tag_stream(data):
    """Parse a byte buffer of SWF tags into [(tag_type, tag_body), ...]"""
    tags = []
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data):
            break
        tc = struct.unpack_from('<H', data, pos)[0]
        tt = tc >> 6
        tl = tc & 0x3F
        pos += 2
        if tl == 0x3F:
            if pos + 4 > len(data):
                break
            tl = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos + tl]
        pos += tl
        tags.append((tt, body))
    return tags


def frame_split(tags):
    """Split tag list into frames. Each frame ends with ShowFrame(1)."""
    frames = []
    current = []
    for tt, body in tags:
        if tt == 0:  # End
            break
        if tt == 1:  # ShowFrame
            frames.append(current)
            current = []
        else:
            current.append((tt, body))
    if current:
        frames.append(current)
    return frames


def decode_po2_summary(body):
    """Decode PO2 tag into a summary dict."""
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    off = 3
    char_id = None
    is_move = bool(flags & 0x01)
    has_char = bool(flags & 0x02)
    has_matrix = bool(flags & 0x04)
    has_cxform = bool(flags & 0x08)
    has_ratio = bool(flags & 0x10)
    has_name = bool(flags & 0x20)
    has_clip_depth = bool(flags & 0x40)
    
    if has_char:
        char_id = struct.unpack_from('<H', body, off)[0]
        off += 2
    
    return {
        'depth': depth, 'flags': flags, 'char_id': char_id,
        'move': is_move, 'has_char': has_char, 'has_matrix': has_matrix,
        'has_cxform': has_cxform, 'has_ratio': has_ratio, 'has_name': has_name,
        'has_clip_depth': has_clip_depth, 'body_len': len(body),
    }


def find_sprite_body(tags, char_id):
    """Find DefineSprite with given charId, return its inner tag bytes."""
    for tag in tags:
        tt = tag.tag_type if hasattr(tag, 'tag_type') else tag[0]
        body = tag.data if hasattr(tag, 'data') else tag[1]
        if tt == 39 and len(body) >= 4:  # DefineSprite
            cid = struct.unpack_from('<H', body, 0)[0]
            if cid == char_id:
                return body[4:]
    return None


def compare_sprite_frames(og_frames, rt_frames, label, depth_filter=None):
    """Compare two sets of frames tag-by-tag. Returns list of differences."""
    diffs = []
    max_f = max(len(og_frames), len(rt_frames))
    if len(og_frames) != len(rt_frames):
        diffs.append(f"  Frame count: OG={len(og_frames)} RT={len(rt_frames)}")
    
    for f in range(min(len(og_frames), len(rt_frames))):
        og_f_tags = og_frames[f]
        rt_f_tags = rt_frames[f]
        
        # Filter to specific depths if requested
        if depth_filter is not None:
            og_f_po2 = [(tt, b) for tt, b in og_f_tags if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] == depth_filter]
            rt_f_po2 = [(tt, b) for tt, b in rt_f_tags if tt in (26, 70) and struct.unpack_from('<H', b, 1)[0] == depth_filter]
            og_f_ro2 = [(tt, b) for tt, b in og_f_tags if tt == 28 and struct.unpack_from('<H', b, 0)[0] == depth_filter]
            rt_f_ro2 = [(tt, b) for tt, b in rt_f_tags if tt == 28 and struct.unpack_from('<H', b, 0)[0] == depth_filter]
        else:
            og_f_po2 = [(tt, b) for tt, b in og_f_tags if tt in (26, 70)]
            rt_f_po2 = [(tt, b) for tt, b in rt_f_tags if tt in (26, 70)]
            og_f_ro2 = [(tt, b) for tt, b in og_f_tags if tt == 28]
            rt_f_ro2 = [(tt, b) for tt, b in rt_f_tags if tt == 28]
        
        # Compare RO2 counts
        if len(og_f_ro2) != len(rt_f_ro2):
            diffs.append(f"  Frame {f+1}: RO2 count OG={len(og_f_ro2)} RT={len(rt_f_ro2)}")
        
        # Compare PO2 
        if len(og_f_po2) != len(rt_f_po2):
            diffs.append(f"  Frame {f+1}: PO2 count OG={len(og_f_po2)} RT={len(rt_f_po2)}")
        
        for i in range(min(len(og_f_po2), len(rt_f_po2))):
            og_s = decode_po2_summary(og_f_po2[i][1])
            rt_s = decode_po2_summary(rt_f_po2[i][1])
            
            flag_diff = []
            if og_s['move'] != rt_s['move']:
                flag_diff.append(f"move OG={og_s['move']} RT={rt_s['move']}")
            if og_s['has_char'] != rt_s['has_char']:
                flag_diff.append(f"hasChar OG={og_s['has_char']} RT={rt_s['has_char']}")
            if og_s['has_ratio'] != rt_s['has_ratio']:
                flag_diff.append(f"hasRatio OG={og_s['has_ratio']} RT={rt_s['has_ratio']}")
            if og_s['has_name'] != rt_s['has_name']:
                flag_diff.append(f"hasName OG={og_s['has_name']} RT={rt_s['has_name']}")
            if og_s['has_cxform'] != rt_s['has_cxform']:
                flag_diff.append(f"hasCxform OG={og_s['has_cxform']} RT={rt_s['has_cxform']}")
            if og_s['has_clip_depth'] != rt_s['has_clip_depth']:
                flag_diff.append(f"hasClipDepth OG={og_s['has_clip_depth']} RT={rt_s['has_clip_depth']}")
            # char_id can differ (different IDs) - skip unless one is None
            if (og_s['has_char'] and rt_s['has_char']) and (og_s['char_id'] is None) != (rt_s['char_id'] is None):
                flag_diff.append(f"charId presence differs")
            
            if flag_diff:
                dp = og_s['depth']
                diffs.append(f"  Frame {f+1} depth {dp}: " + ", ".join(flag_diff))
        
        # Also compare tag type counts (PO2 vs PO3 etc)
        og_types = {}
        rt_types = {}
        for tt, b in og_f_tags:
            og_types[tt] = og_types.get(tt, 0) + 1
        for tt, b in rt_f_tags:
            rt_types[tt] = rt_types.get(tt, 0) + 1
        
        all_types = set(og_types.keys()) | set(rt_types.keys())
        for t in sorted(all_types):
            oc = og_types.get(t, 0)
            rc = rt_types.get(t, 0)
            if oc != rc and t not in (26, 28, 70):  # already compared PO2/RO2
                diffs.append(f"  Frame {f+1}: tag {t} count OG={oc} RT={rc}")
    
    return diffs


# -- Main --
print("Loading OG SWF...")
with open(OG, 'rb') as f:
    swf_data = f.read()
header, og_tags = parse_swf(swf_data)

print("Building N2D from OG...")
validate_swf_sprites(og_tags)
builder = N2DBuilder(header, name="fox")
builder.catalog_swf_tags(og_tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(og_tags)
n2d = builder.to_n2d_json()

libs = n2d.get("libraries", [])

# Find fox MC library entry
fox_lib = None
for lib in libs:
    if lib and lib.get("type") == "container":
        for layer in lib.get("layers", []):
            if layer.get('swfDepth') == 7 and len(layer.get("characters", [])) > 80:
                fox_lib = lib
                break
        if fox_lib:
            break

lib_to_char_idx = {}
for i, lib_e in enumerate(libs):
    if lib_e:
        lib_to_char_idx[lib_e["id"]] = i
id_to_lib = {lib_e["id"]: lib_e for lib_e in libs if lib_e}

char_id_map = {}
for i, lib_e in enumerate(libs):
    if lib_e:
        char_id_map[i] = lib_e.get("swfCharId", i + 1)


# Find the OG fox sprite charId
fox_swf_id = fox_lib.get("swfCharId")
print(f"Fox MC swfCharId={fox_swf_id}")

# Get OG fox sprite body from the SWF
og_fox_body = find_sprite_body(og_tags, fox_swf_id)
if not og_fox_body:
    print("ERROR: Could not find OG fox sprite body!")
    sys.exit(1)

og_fox_tags_parsed = parse_tag_stream(og_fox_body)
og_fox_frames = frame_split(og_fox_tags_parsed)
print(f"OG fox sprite: {len(og_fox_frames)} frames, {len(og_fox_tags_parsed)} tags")

# Compile RT fox sprite
tp = to_publish(fox_lib, lib_to_char_idx, id_to_lib)
total_frames = fox_lib.get("totalFrame") or 98
labels = fox_lib.get("labels", [])
actions = fox_lib.get("actions", [])
rt_fox_bytes = build_timeline_tags(total_frames, tp, labels, actions, char_id_map)
rt_fox_tags_parsed = parse_tag_stream(rt_fox_bytes)
rt_fox_frames = frame_split(rt_fox_tags_parsed)
print(f"RT fox sprite: {len(rt_fox_frames)} frames, {len(rt_fox_tags_parsed)} tags")

# Compare fox MC at depth 7
print("\n=== FOX MC: All depths comparison ===")
diffs = compare_sprite_frames(og_fox_frames, rt_fox_frames, "Fox MC")
if diffs:
    for d in diffs[:50]:
        print(d)
    if len(diffs) > 50:
        print(f"  ... and {len(diffs)-50} more differences")
else:
    print("  PERFECT MATCH (all tags, all frames)")

print("\n=== FOX MC: Depth 7 only ===")
diffs7 = compare_sprite_frames(og_fox_frames, rt_fox_frames, "Fox MC d7", depth_filter=7)
if diffs7:
    for d in diffs7[:30]:
        print(d)
else:
    print("  PERFECT MATCH at depth 7")

# Now find 'a' child - placed at depth 7 on frame 14
# Get OG char at depth 7 on frame 14
og_a_char_id = None
for tt, body in og_fox_frames[13]:  # frame 14 (0-indexed=13)
    if tt in (26, 70):
        s = decode_po2_summary(body)
        if s['depth'] == 7 and s['has_char']:
            og_a_char_id = s['char_id']
            break

# Get RT char at depth 7 on frame 14
rt_a_char_id = None
for tt, body in rt_fox_frames[13]:
    if tt in (26, 70):
        s = decode_po2_summary(body)
        if s['depth'] == 7 and s['has_char']:
            rt_a_char_id = s['char_id']
            break

print(f"\n=== 'a' ATTACK CHILD (frame 14 of fox MC, depth 7) ===")
print(f"  OG charId={og_a_char_id}, RT charId={rt_a_char_id}")

# Get OG 'a' sprite body
og_a_body = find_sprite_body(og_tags, og_a_char_id)
if og_a_body:
    og_a_tags = parse_tag_stream(og_a_body)
    og_a_frames = frame_split(og_a_tags)
    print(f"  OG 'a' child: {len(og_a_frames)} frames, {len(og_a_tags)} tags")
else:
    print("  ERROR: Could not find OG 'a' sprite body")
    og_a_frames = []

# Find RT 'a' child lib and compile it
rt_a_lib = None
for lib_e in libs:
    if lib_e and lib_e.get("swfCharId") == rt_a_char_id and lib_e.get("type") == "container":
        rt_a_lib = lib_e
        break
# Fallback: search by name
if not rt_a_lib:
    for lib_e in libs:
        if lib_e and lib_e.get("type") == "container" and lib_e.get("name") == "a":
            # Check if it's placed at frame 14
            rt_a_lib = lib_e
            break

if rt_a_lib:
    a_tp = to_publish(rt_a_lib, lib_to_char_idx, id_to_lib)
    a_total = rt_a_lib.get("totalFrame") or len(og_a_frames)
    a_labels = rt_a_lib.get("labels", [])
    a_actions = rt_a_lib.get("actions", [])
    rt_a_bytes = build_timeline_tags(a_total, a_tp, a_labels, a_actions, char_id_map)
    rt_a_tags = parse_tag_stream(rt_a_bytes)
    rt_a_frames = frame_split(rt_a_tags)
    print(f"  RT 'a' child: {len(rt_a_frames)} frames, {len(rt_a_tags)} tags")
    
    # Compare
    print(f"\n  --- 'a' child: All depths comparison ---")
    a_diffs = compare_sprite_frames(og_a_frames, rt_a_frames, "'a' child")
    if a_diffs:
        for d in a_diffs[:50]:
            print(d)
        if len(a_diffs) > 50:
            print(f"  ... and {len(a_diffs)-50} more differences")
    else:
        print("  PERFECT MATCH (all tags, all frames)")
    
    # Also check: are there FrameLabel tags?
    og_labels = []
    rt_labels = []
    for f_idx, f_tags in enumerate(og_a_frames):
        for tt, body in f_tags:
            if tt == 43:  # FrameLabel
                name = body[:body.index(0)].decode('utf-8', errors='replace') if 0 in body else body.decode('utf-8', errors='replace')
                og_labels.append((f_idx + 1, name))
    for f_idx, f_tags in enumerate(rt_a_frames):
        for tt, body in f_tags:
            if tt == 43:
                name = body[:body.index(0)].decode('utf-8', errors='replace') if 0 in body else body.decode('utf-8', errors='replace')
                rt_labels.append((f_idx + 1, name))
    
    print(f"\n  --- 'a' child: Frame labels ---")
    print(f"  OG labels: {og_labels}")
    print(f"  RT labels: {rt_labels}")
    
    # Check for DoAction/DoABC within the sprite
    og_has_doaction = any(tt in (12, 59, 82) for tt, _ in og_a_tags)
    rt_has_doaction = any(tt in (12, 59, 82) for tt, _ in rt_a_tags)
    print(f"\n  --- 'a' child: Action tags ---")
    print(f"  OG has DoAction/DoABC/DoInitAction: {og_has_doaction}")
    print(f"  RT has DoAction/DoABC/DoInitAction: {rt_has_doaction}")
    
    # SoundStreamHead2 in child
    og_ssh = [tt for tt, _ in og_a_tags if tt in (18, 45)]  # SoundStreamHead/Head2
    rt_ssh = [tt for tt, _ in rt_a_tags if tt in (18, 45)]
    og_ssb = sum(1 for tt, _ in og_a_tags if tt == 19)  # SoundStreamBlock
    rt_ssb = sum(1 for tt, _ in rt_a_tags if tt == 19)
    print(f"  OG SoundStreamHead tags: {og_ssh}, SoundStreamBlock: {og_ssb}")
    print(f"  RT SoundStreamHead tags: {rt_ssh}, SoundStreamBlock: {rt_ssb}")
else:
    print("  ERROR: Could not find RT 'a' child library")

# Also check one more level deep - a grandchild inside 'a'
# Find what characters 'a' places
if og_a_body and rt_a_lib:
    print(f"\n=== GRANDCHILD COMPARISON (inside 'a' attack) ===")
    # Get unique charIds placed by OG 'a'
    og_a_chars = set()
    for tt, body in og_a_tags:
        if tt in (26, 70) and len(body) >= 5:
            s = decode_po2_summary(body)
            if s['has_char']:
                og_a_chars.add(s['char_id'])
    
    # Get unique charIds placed by RT 'a'
    rt_a_chars = set()
    for tt, body in rt_a_tags:
        if tt in (26, 70) and len(body) >= 5:
            s = decode_po2_summary(body)
            if s['has_char']:
                rt_a_chars.add(s['char_id'])
    
    print(f"  OG 'a' uses {len(og_a_chars)} unique characters")
    print(f"  RT 'a' uses {len(rt_a_chars)} unique characters")
    
    # For each RT child that is a sprite, compile and compare with OG counterpart
    # Map RT chars to OG chars via SymbolClass
    og_symclass = {}
    rt_symclass = {}
    for tag in og_tags:
        tt = tag.tag_type if hasattr(tag, 'tag_type') else tag[0]
        body = tag.data if hasattr(tag, 'data') else tag[1]
        if tt == 76 and len(body) >= 2:  # SymbolClass
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]
                off += 2
                end = body.index(0, off)
                name = body[off:end].decode('utf-8', errors='replace')
                off = end + 1
                og_symclass[cid] = name
    
    # Check grandchild sprite mismatches  
    mismatch_count = 0
    checked_count = 0
    for rt_cid in sorted(rt_a_chars):
        # Find RT lib
        rt_gc_lib = None
        for lib_e in libs:
            if lib_e and lib_e.get("swfCharId") == rt_cid and lib_e.get("type") == "container":
                rt_gc_lib = lib_e
                break
        if not rt_gc_lib:
            continue
        
        # Find OG counterpart by symbol name
        og_cid = None
        rt_sym = rt_gc_lib.get("symbolName", "")
        for oc, on in og_symclass.items():
            if on == rt_sym:
                og_cid = oc
                break
        
        if og_cid is None:
            continue
        
        checked_count += 1
        og_gc_body = find_sprite_body(og_tags, og_cid)
        if not og_gc_body:
            continue
        
        og_gc_tags = parse_tag_stream(og_gc_body)
        og_gc_frames = frame_split(og_gc_tags)
        
        # Compile RT grandchild
        gc_tp = to_publish(rt_gc_lib, lib_to_char_idx, id_to_lib)
        gc_total = rt_gc_lib.get("totalFrame") or len(og_gc_frames)
        gc_labels = rt_gc_lib.get("labels", [])
        gc_actions = rt_gc_lib.get("actions", [])
        rt_gc_bytes = build_timeline_tags(gc_total, gc_tp, gc_labels, gc_actions, char_id_map)
        rt_gc_tags = parse_tag_stream(rt_gc_bytes)
        rt_gc_frames = frame_split(rt_gc_tags)
        
        gc_diffs = compare_sprite_frames(og_gc_frames, rt_gc_frames, rt_sym)
        if gc_diffs:
            mismatch_count += 1
            print(f"\n  Grandchild '{rt_sym}' (OG={og_cid}, RT={rt_cid}): {len(gc_diffs)} diffs")
            for d in gc_diffs[:5]:
                print(f"    {d}")
            if len(gc_diffs) > 5:
                print(f"    ... and {len(gc_diffs)-5} more")
    
    print(f"\n  Checked {checked_count} grandchild sprites: {mismatch_count} with differences")

print("\nDone.")
