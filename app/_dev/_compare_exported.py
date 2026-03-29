"""Compare exported project.swf vs original gameandwatch.swf."""
import struct, zlib, sys

def parse_full(path):
    raw = open(path, 'rb').read()
    data = raw
    if raw[:3] == b'CWS':
        data = raw[:8] + zlib.decompress(raw[8:])
    elif raw[:3] == b'ZWS':
        import lzma
        data = raw[:8] + lzma.decompress(raw[12:])
    nbits = (data[8] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    fps_raw = struct.unpack_from('<H', data, rect_end)[0]
    fps = fps_raw >> 8
    frame_count = struct.unpack_from('<H', data, rect_end + 2)[0]
    tag_start = rect_end + 4
    tags = []
    i = tag_start
    while i < len(data):
        if i + 2 > len(data): break
        h = struct.unpack_from('<H', data, i)[0]
        tt = h >> 6
        ln = h & 0x3f
        hdr = 2
        if ln == 0x3f:
            ln = struct.unpack_from('<I', data, i+2)[0]
            hdr = 6
        body = data[i+hdr:i+hdr+ln]
        tags.append((tt, body))
        i += hdr + ln
        if tt == 0: break
    return tags, data, fps, frame_count

DEFINE_TAGS = {2,22,32,83, 6,21,35,90, 20,36, 39, 46,84, 11,48,75, 10,14,37,87}

TAG_NAMES = {
    0:'End',1:'ShowFrame',2:'DefineShape',4:'PlaceObject',5:'RemoveObject',
    9:'SetBgColor',10:'DefineFont',11:'DefineText',12:'DoAction',
    14:'DefineSound',15:'StartSound',20:'DefineBitsLossless',21:'DefineBitsJPEG2',
    22:'DefineShape2',24:'Protect',26:'PlaceObject2',28:'RemoveObject2',
    32:'DefineShape3',33:'DefineText2',35:'DefineBitsJPEG3',36:'DefineBitsLossless2',
    37:'DefineEditText',39:'DefineSprite',43:'FrameLabel',45:'SoundStreamHead2',
    46:'MorphShape',48:'DefineFont2',56:'ExportAssets',
    69:'FileAttributes',70:'PlaceObject3',72:'DoABC',
    73:'FontAlignZones',74:'CSMTextSettings',75:'DefineFont3',
    76:'SymbolClass',77:'Metadata',82:'DoABC2',83:'DefineShape4',
    84:'MorphShape2',86:'SceneFrameLabel',87:'DefineBinaryData',88:'DefineFontName',
}

def tag_name(tt):
    return TAG_NAMES.get(tt, f'tag{tt}')

def get_char_id(body):
    if len(body) >= 2:
        return struct.unpack_from('<H', body, 0)[0]
    return None

def parse_symbol_class(body):
    """Parse SymbolClass tag body → dict of charId → className."""
    if len(body) < 2: return {}
    count = struct.unpack_from('<H', body, 0)[0]
    i = 2
    result = {}
    for _ in range(count):
        if i + 2 > len(body): break
        cid = struct.unpack_from('<H', body, i)[0]
        i += 2
        end = body.index(0, i) if 0 in body[i:] else len(body)
        name = body[i:end].decode('utf-8', errors='replace')
        i = end + 1
        result[cid] = name
    return result

def parse_sprite_timeline(body):
    """Parse DefineSprite inner tags."""
    if len(body) < 4: return []
    cid = struct.unpack_from('<H', body, 0)[0]
    fc = struct.unpack_from('<H', body, 2)[0]
    inner = []
    i = 4
    while i < len(body):
        if i + 2 > len(body): break
        h = struct.unpack_from('<H', body, i)[0]
        tt = h >> 6
        ln = h & 0x3f
        hdr = 2
        if ln == 0x3f:
            if i + 6 > len(body): break
            ln = struct.unpack_from('<I', body, i+2)[0]
            hdr = 6
        b = body[i+hdr:i+hdr+ln]
        inner.append((tt, b))
        i += hdr + ln
        if tt == 0: break
    return cid, fc, inner

def parse_place_object(body, tag_type=26):
    """Parse PlaceObject2/3 to extract depth, charId, matrix info."""
    if not body: return {}
    flags = body[0]
    i = 1
    if tag_type == 70:
        if len(body) < 2: return {}
        flags2 = body[1]
        i = 2
    else:
        flags2 = 0
    depth = struct.unpack_from('<H', body, i)[0] if i + 2 <= len(body) else 0
    i += 2
    result = {'depth': depth, 'flags': flags}
    
    has_clip_actions = flags & 0x80
    has_clip_depth = flags & 0x40
    has_name = flags & 0x20
    has_ratio = flags & 0x10
    has_ctransform = flags & 0x08
    has_matrix = flags & 0x04
    has_char = flags & 0x02
    has_move = flags & 0x01
    
    result['hasChar'] = bool(has_char)
    result['hasMove'] = bool(has_move)
    result['hasMatrix'] = bool(has_matrix)
    result['hasCTransform'] = bool(has_ctransform)
    
    if has_char:
        if i + 2 <= len(body):
            result['charId'] = struct.unpack_from('<H', body, i)[0]
            i += 2
    
    return result

# --- MAIN ---
orig_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf'
exported_path = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\gameandwatch_cli.swf'

print("=" * 70)
print("COMPARING ORIGINAL vs EXPORTED SWF")
print("=" * 70)

orig, orig_data, orig_fps, orig_fc = parse_full(orig_path)
exp, exp_data, exp_fps, exp_fc = parse_full(exported_path)

print(f"\nOriginal: {len(orig)} tags, {len(orig_data)} bytes, fps={orig_fps}, frames={orig_fc}")
print(f"Exported: {len(exp)} tags, {len(exp_data)} bytes, fps={exp_fps}, frames={exp_fc}")

# Tag type histogram
print("\n--- TAG TYPE HISTOGRAM ---")
def tag_histogram(tags):
    h = {}
    for tt, _ in tags:
        h[tt] = h.get(tt, 0) + 1
    return h

orig_hist = tag_histogram(orig)
exp_hist = tag_histogram(exp)
all_types = sorted(set(list(orig_hist.keys()) + list(exp_hist.keys())))
for tt in all_types:
    oc = orig_hist.get(tt, 0)
    ec = exp_hist.get(tt, 0)
    marker = " ***" if oc != ec else ""
    print(f"  {tag_name(tt):25s} orig={oc:4d}  exp={ec:4d}{marker}")

# Build define tag maps
def build_tag_map(tags):
    m = {}
    for tt, body in tags:
        if tt in DEFINE_TAGS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            key = (tt, cid)
            m[key] = body
    return m

orig_map = build_tag_map(orig)
exp_map = build_tag_map(exp)

# Character IDs overview
print(f"\n--- CHARACTER ID COUNTS ---")
orig_cids = set(cid for (tt, cid) in orig_map.keys())
exp_cids = set(cid for (tt, cid) in exp_map.keys())
print(f"  Original charIds: {len(orig_cids)} (range {min(orig_cids)}-{max(orig_cids)})")
print(f"  Exported charIds: {len(exp_cids)} (range {min(exp_cids)}-{max(exp_cids)})")

# SymbolClass comparison
print("\n--- SYMBOLCLASS COMPARISON ---")
orig_symbols = {}
exp_symbols = {}
for tt, body in orig:
    if tt == 76:
        orig_symbols.update(parse_symbol_class(body))
for tt, body in exp:
    if tt == 76:
        exp_symbols.update(parse_symbol_class(body))

orig_classes = set(orig_symbols.values())
exp_classes = set(exp_symbols.values())

print(f"  Original symbols: {len(orig_symbols)} ({len(orig_classes)} unique classes)")
print(f"  Exported symbols: {len(exp_symbols)} ({len(exp_classes)} unique classes)")

missing_classes = orig_classes - exp_classes
extra_classes = exp_classes - orig_classes
if missing_classes:
    print(f"\n  MISSING classes in export ({len(missing_classes)}):")
    for c in sorted(missing_classes):
        print(f"    - {c}")
if extra_classes:
    print(f"\n  EXTRA classes in export ({len(extra_classes)}):")
    for c in sorted(extra_classes):
        print(f"    + {c}")

# DoABC2 comparison
print("\n--- DoABC2 COMPARISON ---")
orig_abc = [(tt, body) for tt, body in orig if tt in (72, 82)]
exp_abc = [(tt, body) for tt, body in exp if tt in (72, 82)]
print(f"  Original DoABC/DoABC2 tags: {len(orig_abc)}")
print(f"  Exported DoABC/DoABC2 tags: {len(exp_abc)}")
for i, (tt, body) in enumerate(orig_abc):
    print(f"    orig[{i}] type={tag_name(tt)} len={len(body)}")
for i, (tt, body) in enumerate(exp_abc):
    print(f"    exp[{i}] type={tag_name(tt)} len={len(body)}")

# Define tag differences
print("\n--- DEFINE TAG DIFFERENCES ---")
diffs = 0
matching = 0
# Compare by charId across tag types
orig_by_cid = {}
exp_by_cid = {}
for (tt, cid), body in orig_map.items():
    orig_by_cid.setdefault(cid, []).append((tt, body))
for (tt, cid), body in exp_map.items():
    exp_by_cid.setdefault(cid, []).append((tt, body))

# Since charIds are reassigned, compare by SymbolClass name mapping
print("\n--- COMPARING ASSETS BY SYMBOL NAME ---")
# Build name→body maps
orig_name_map = {}
exp_name_map = {}
for cid, name in orig_symbols.items():
    for tt, body in orig_map.items():
        if tt[1] == cid:
            orig_name_map[name] = (tt[0], body)
            break
for cid, name in exp_symbols.items():
    for tt, body in exp_map.items():
        if tt[1] == cid:
            exp_name_map[name] = (tt[0], body)
            break

common_names = set(orig_name_map.keys()) & set(exp_name_map.keys())
print(f"  Common symbol names: {len(common_names)}")

shape_diffs = 0
sprite_diffs = 0
bitmap_diffs = 0
other_diffs = 0
sprite_details = []

for name in sorted(common_names):
    o_tt, o_body = orig_name_map[name]
    e_tt, e_body = exp_name_map[name]
    
    if o_body == e_body:
        matching += 1
        continue
    
    if o_tt != e_tt:
        print(f"  TYPE MISMATCH: {name}: orig={tag_name(o_tt)} exp={tag_name(e_tt)}")
    
    if o_tt in (2, 22, 32, 83):
        shape_diffs += 1
        if shape_diffs <= 5:
            print(f"  SHAPE DIFF: {name}: orig={len(o_body)}b exp={len(e_body)}b")
    elif o_tt == 39:
        sprite_diffs += 1
        # Parse sprite details
        o_cid, o_fc, o_inner = parse_sprite_timeline(o_body)
        e_cid, e_fc, e_inner = parse_sprite_timeline(e_body)
        o_inner_hist = tag_histogram(o_inner)
        e_inner_hist = tag_histogram(e_inner)
        detail = f"  SPRITE DIFF: {name}: orig(fc={o_fc}, tags={len(o_inner)}) exp(fc={e_fc}, tags={len(e_inner)})"
        # Check PlaceObject differences
        o_places = [(tt, b) for tt, b in o_inner if tt in (26, 70)]
        e_places = [(tt, b) for tt, b in e_inner if tt in (26, 70)]
        detail += f" places: orig={len(o_places)} exp={len(e_places)}"
        sprite_details.append(detail)
        if sprite_diffs <= 10:
            print(detail)
    elif o_tt in (20, 36, 21, 35, 90):
        bitmap_diffs += 1
    else:
        other_diffs += 1
        if other_diffs <= 5:
            print(f"  OTHER DIFF: {name} ({tag_name(o_tt)}): orig={len(o_body)}b exp={len(e_body)}b")

print(f"\n  Summary: matching={matching}, shape_diffs={shape_diffs}, sprite_diffs={sprite_diffs}, bitmap_diffs={bitmap_diffs}, other_diffs={other_diffs}")

# SPRITE POSITIONING ANALYSIS
print("\n--- SPRITE POSITIONING ANALYSIS (first 5 differing sprites) ---")
for name in sorted(common_names):
    o_tt, o_body = orig_name_map[name]
    e_tt, e_body = exp_name_map[name]
    if o_tt != 39 or o_body == e_body:
        continue
    
    o_cid, o_fc, o_inner = parse_sprite_timeline(o_body)
    e_cid, e_fc, e_inner = parse_sprite_timeline(e_body)
    
    # Compare PlaceObject tags
    o_places = [(tt, b) for tt, b in o_inner if tt in (26, 70)]
    e_places = [(tt, b) for tt, b in e_inner if tt in (26, 70)]
    
    print(f"\n  Sprite: {name} (orig fc={o_fc}, exp fc={e_fc})")
    print(f"    PlaceObject tags: orig={len(o_places)} exp={len(e_places)}")
    
    # Compare depths used
    o_depths = set()
    e_depths = set()
    for tt, b in o_places:
        info = parse_place_object(b, tt)
        o_depths.add(info.get('depth', 0))
    for tt, b in e_places:
        info = parse_place_object(b, tt)
        e_depths.add(info.get('depth', 0))
    
    if o_depths != e_depths:
        print(f"    Depth difference: orig={sorted(o_depths)} exp={sorted(e_depths)}")
    
    # Compare first few PlaceObject bodies
    for i in range(min(3, len(o_places), len(e_places))):
        o_info = parse_place_object(o_places[i][1], o_places[i][0])
        e_info = parse_place_object(e_places[i][1], e_places[i][0])
        if o_places[i][1] != e_places[i][1]:
            print(f"    Place[{i}] DIFF: orig_flags=0x{o_info.get('flags',0):02x} exp_flags=0x{e_info.get('flags',0):02x}")
            print(f"      orig_depth={o_info.get('depth')} exp_depth={e_info.get('depth')}")
            print(f"      orig_charId={o_info.get('charId','N/A')} exp_charId={e_info.get('charId','N/A')}")
            print(f"      orig body({len(o_places[i][1])}b): {o_places[i][1][:30].hex()}")
            print(f"      exp  body({len(e_places[i][1])}b): {e_places[i][1][:30].hex()}")
    
    sprite_diffs -= 1
    if sprite_diffs <= 0:
        break

# ROOT TIMELINE comparison
print("\n--- ROOT TIMELINE COMPARISON ---")
# Tags that are not definitions and not in special category
orig_root_places = [(tt, body) for tt, body in orig if tt in (26, 70)]
exp_root_places = [(tt, body) for tt, body in exp if tt in (26, 70)]
orig_root_removes = [(tt, body) for tt, body in orig if tt == 28]
exp_root_removes = [(tt, body) for tt, body in exp if tt == 28]
orig_root_frames = [(tt, body) for tt, body in orig if tt == 1]
exp_root_frames = [(tt, body) for tt, body in exp if tt == 1]
orig_root_labels = [(tt, body) for tt, body in orig if tt == 43]
exp_root_labels = [(tt, body) for tt, body in exp if tt == 43]

print(f"  PlaceObject: orig={len(orig_root_places)} exp={len(exp_root_places)}")
print(f"  RemoveObject: orig={len(orig_root_removes)} exp={len(exp_root_removes)}")
print(f"  ShowFrame: orig={len(orig_root_frames)} exp={len(exp_root_frames)}")
print(f"  FrameLabel: orig={len(orig_root_labels)} exp={len(exp_root_labels)}")

print("\n  Root PlaceObject depth analysis:")
for label, places in [("orig", orig_root_places), ("exp", exp_root_places)]:
    depths = set()
    char_ids = set()
    for tt, b in places:
        info = parse_place_object(b, tt)
        depths.add(info.get('depth', 0))
        if 'charId' in info:
            char_ids.add(info['charId'])
    print(f"    {label}: depths={sorted(depths)}, charIds referenced={sorted(char_ids)}")

print("\nDone.")
