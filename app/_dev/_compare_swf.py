"""Compare two SWF files tag-by-tag (keyed by tag_type + charId)."""
import struct, zlib, sys

def parse_full(path):
    raw = open(path, 'rb').read()
    data = raw
    if raw[:3] == b'CWS':
        data = raw[:8] + zlib.decompress(raw[8:])
    nbits = (data[8] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
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
    return tags

DEFINE_TAGS = {2,22,32,83, 6,21,35,90, 20,36, 39, 46,84, 11,48,75, 10,14,37,87}

TAG_NAMES = {
    0:'End',1:'ShowFrame',2:'DefineShape',9:'SetBgColor',11:'DefineText',
    14:'DefineSound',20:'DefineBitsLossless',21:'DefineBitsJPEG2',
    22:'DefineShape2',24:'Protect',26:'PlaceObject2',28:'RemoveObject2',
    32:'DefineShape3',35:'DefineBitsJPEG3',36:'DefineBitsLossless2',
    39:'DefineSprite',43:'FrameLabel',45:'SoundStreamHead2',46:'MorphShape',
    48:'DefineFont2',56:'ExportAssets',69:'FileAttributes',70:'PlaceObject3',
    72:'DoABC',73:'FontAlignZones',74:'CSMTextSettings',75:'DefineFont3',
    76:'SymbolClass',77:'Metadata',82:'DoABC2',83:'DefineShape4',
    84:'MorphShape2',86:'SceneFrameLabel',87:'DefineBinaryData',
    88:'DefineFontName',
}

def tag_name(tt):
    return TAG_NAMES.get(tt, f'tag{tt}')

orig_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.ssf'
rt_path = '_roundtrip_test.swf'

orig = parse_full(orig_path)
rt = parse_full(rt_path)

# Build tag maps keyed by (tag_type, charId) for define tags
def build_tag_map(tags):
    m = {}
    for tt, body in tags:
        if tt in DEFINE_TAGS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            key = (tt, cid)
            if key in m:
                print(f"  WARNING: duplicate {tag_name(tt)} charId={cid}")
            m[key] = body
    return m

print("=== ORIGINAL ===")
orig_map = build_tag_map(orig)
print("=== ROUNDTRIP ===")
rt_map = build_tag_map(rt)

# Compare matching define tags
print("\n=== DEFINE TAG DIFFERENCES ===")
diffs = 0
for key in sorted(orig_map.keys()):
    tt, cid = key
    if key in rt_map:
        ob = orig_map[key]
        rb = rt_map[key]
        if ob != rb:
            print(f"  DIFF {tag_name(tt)}(charId={cid}): orig={len(ob)}b rt={len(rb)}b delta={len(rb)-len(ob)}")
            for i in range(min(len(ob), len(rb))):
                if ob[i] != rb[i]:
                    print(f"    First diff at byte {i}: orig=0x{ob[i]:02x} rt=0x{rb[i]:02x}")
                    ctx = min(16, len(ob)-i, len(rb)-i)
                    print(f"    orig[{i}:{i+ctx}] = {ob[i:i+ctx].hex()}")
                    print(f"    rt  [{i}:{i+ctx}] = {rb[i:i+ctx].hex()}")
                    break
            diffs += 1
    else:
        print(f"  MISSING in roundtrip: {tag_name(tt)} charId={cid} ({len(orig_map[key])}b)")
        diffs += 1

for key in sorted(rt_map.keys()):
    if key not in orig_map:
        tt, cid = key
        print(f"  EXTRA in roundtrip: {tag_name(tt)} charId={cid} ({len(rt_map[key])}b)")
        diffs += 1

print(f"\nTotal define-tag differences: {diffs}")

# Compare non-define tags by type (SymbolClass, DoABC etc.)
print("\n=== NON-DEFINE TAG COMPARISON ===")
for tt_check in [69, 9, 24, 45, 76, 82, 86]:
    orig_bodies = [body for tt, body in orig if tt == tt_check]
    rt_bodies = [body for tt, body in rt if tt == tt_check]
    if len(orig_bodies) != len(rt_bodies):
        print(f"  {tag_name(tt_check)}: count orig={len(orig_bodies)} rt={len(rt_bodies)}")
    elif orig_bodies and orig_bodies != rt_bodies:
        for i, (ob, rb) in enumerate(zip(orig_bodies, rt_bodies)):
            if ob != rb:
                print(f"  {tag_name(tt_check)}[{i}]: DIFF orig={len(ob)}b rt={len(rb)}b")
    else:
        print(f"  {tag_name(tt_check)}: OK ({len(orig_bodies)} tags, identical)")

# Font aux tags
print("\n=== FONT-RELATED TAGS ===")
for label, tags in [('ORIG', orig), ('RT', rt)]:
    font_tags = [(tt, body) for tt, body in tags if tt in (73, 74, 75, 88)]
    print(f"{label}:")
    for tt, body in font_tags:
        cid = struct.unpack_from('<H', body, 0)[0] if len(body) >= 2 else -1
        print(f"  {tag_name(tt)} charId={cid} len={len(body)}b first20={body[:20].hex()}")

# Show sprites with different nested content
print("\n=== SPRITE DIFFERENCES ===")
sprite_diffs = 0
for key in sorted(orig_map.keys()):
    tt, cid = key
    if tt != 39:
        continue
    if key not in rt_map:
        continue
    ob = orig_map[key]
    rb = rt_map[key]
    if ob != rb:
        # Parse sprite header: charId(2) + frameCount(2)
        o_fc = struct.unpack_from('<H', ob, 2)[0]
        r_fc = struct.unpack_from('<H', rb, 2)[0]
        print(f"  Sprite charId={cid}: orig={len(ob)}b(fc={o_fc}) rt={len(rb)}b(fc={r_fc}) delta={len(rb)-len(ob)}")
        sprite_diffs += 1
        if sprite_diffs > 10:
            print("  ... (truncated)")
            break
print(f"Total sprite differences: {sprite_diffs}")
