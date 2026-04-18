"""
Targeted comparison: find the dair bitmaps and DAir_73 sprite in both OG and RT SWFs.
Key question: does OG place dair bitmaps as LL2 (Bitmap) or DefineShape3 (Shape)?
"""
import struct, zlib

def parse_swf_full(path):
    """Parse SWF, return (defs, sprites) where:
      defs[char_id] = (tag_type, extra)  e.g. (36, (width, height)) for LL2
      sprites[sprite_id] = [(depth, char_id, flags1, flags2, tag_type)]
    """
    with open(path, 'rb') as f:
        raw = f.read()
    sig = raw[:3]
    if sig == b'CWS':
        body = zlib.decompress(raw[8:])
        raw = raw[:8] + body
    elif sig != b'FWS':
        raise ValueError(f"Unknown SWF: {sig}")

    pos = 8
    nbits = (raw[pos] >> 3) & 0x1f
    pos += (5 + nbits * 4 + 7) // 8
    pos += 4

    defs = {}
    sprites = {}

    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tag_type = hdr >> 6
        short_len = hdr & 0x3f
        pos += 2
        if short_len == 0x3f:
            length = struct.unpack_from('<I', raw, pos)[0]
            pos += 4
        else:
            length = short_len
        payload = raw[pos:pos+length]

        if tag_type == 0:
            break

        if tag_type == 36:  # DefineBitsLossless2
            cid = struct.unpack_from('<H', payload)[0]
            fmt = payload[2]
            w = struct.unpack_from('<H', payload, 3)[0]
            h = struct.unpack_from('<H', payload, 5)[0]
            defs[cid] = (36, (w, h))

        elif tag_type == 32:  # DefineShape3
            cid = struct.unpack_from('<H', payload)[0]
            defs[cid] = (32, None)

        elif tag_type == 46:  # DefineShape4
            cid = struct.unpack_from('<H', payload)[0]
            defs[cid] = (46, None)

        elif tag_type == 39:  # DefineSprite
            sprite_id = struct.unpack_from('<H', payload)[0]
            defs[sprite_id] = (39, None)
            inner_pos = 4
            placements = []
            while inner_pos < length - 1:
                h2 = struct.unpack_from('<H', payload, inner_pos)[0]
                t2 = h2 >> 6
                sl2 = h2 & 0x3f
                inner_pos += 2
                if sl2 == 0x3f:
                    l2 = struct.unpack_from('<I', payload, inner_pos)[0]
                    inner_pos += 4
                else:
                    l2 = sl2
                p2 = payload[inner_pos:inner_pos+l2]
                if t2 == 26 and l2 >= 3:  # PO2
                    fl1 = p2[0]
                    depth = struct.unpack_from('<H', p2, 1)[0]
                    ci = None
                    if fl1 & 0x02 and l2 >= 5:
                        ci = struct.unpack_from('<H', p2, 3)[0]
                    placements.append((depth, ci, fl1, 0, 26))
                elif t2 == 70 and l2 >= 4:  # PO3
                    fl1 = p2[0]; fl2 = p2[1]
                    depth = struct.unpack_from('<H', p2, 2)[0]
                    p = 4
                    # HasClassName in PO3 flags2 bit3 → skip class name string
                    if fl2 & 0x08:
                        while p < l2 and p2[p] != 0:
                            p += 1
                        p += 1  # skip null terminator
                    ci = None
                    if fl1 & 0x02 and p + 2 <= l2:
                        ci = struct.unpack_from('<H', p2, p)[0]
                    placements.append((depth, ci, fl1, fl2, 70))
                elif t2 == 0:
                    break
                inner_pos += l2
            sprites[sprite_id] = placements

        pos += length

    return defs, sprites


OG_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
RT_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

print("Parsing OG...")
og_defs, og_sprites = parse_swf_full(OG_PATH)
print("Parsing RT...")
rt_defs, rt_sprites = parse_swf_full(RT_PATH)

print(f"\nOG: {len(og_defs)} defs, {len(og_sprites)} sprites")
print(f"RT: {len(rt_defs)} defs, {len(rt_sprites)} sprites")

# --- Find dair bitmap charIDs by known dimensions ---
DAIR_DIM_NAMES = {
    (25, 34): 'bm_dair0',
    (5,  5):  'bm_dairHand',
    (21, 33): 'bm_dairScythe',
    (13, 20): 'bm_dairScytheBlade',
    (55, 53): 'bm_dair1/2/3/4/6/7',
    (25, 33): 'bm_dair5',
}

print("\n=== LL2 IDs by known dair dimensions ===")
og_dair_ll2 = {}
rt_dair_ll2 = {}
for cid, (tt, extra) in sorted(og_defs.items()):
    if tt == 36 and extra in DAIR_DIM_NAMES:
        name = DAIR_DIM_NAMES[extra]
        og_dair_ll2[cid] = (extra, name)
        print(f"  OG LL2 char_id={cid} dims={extra} name={name}")
for cid, (tt, extra) in sorted(rt_defs.items()):
    if tt == 36 and extra in DAIR_DIM_NAMES:
        name = DAIR_DIM_NAMES[extra]
        rt_dair_ll2[cid] = (extra, name)
        print(f"  RT LL2 char_id={cid} dims={extra} name={name}")

# --- Find sprites that place those dair LL2s ---
print("\n=== Sprites placing dair LL2s ===")
dair_og_sprite_ids = set()
dair_rt_sprite_ids = set()

for sid, placements in og_sprites.items():
    for (depth, ci, fl1, fl2, tt) in placements:
        if ci in og_dair_ll2:
            dair_og_sprite_ids.add(sid)
for sid, placements in rt_sprites.items():
    for (depth, ci, fl1, fl2, tt) in placements:
        if ci in rt_dair_ll2:
            dair_rt_sprite_ids.add(sid)

print(f"OG sprites referencing dair LL2s: {sorted(dair_og_sprite_ids)}")
print(f"RT sprites referencing dair LL2s: {sorted(dair_rt_sprite_ids)}")

# --- Deep-dive: what does DAir_73 look like in each SWF? ---
def show_sprite(label, sid, placements, defs):
    print(f"\n  [{label}] Sprite {sid}:")
    for (depth, ci, fl1, fl2, tt) in placements:
        if ci is None:
            print(f"    depth={depth:<3} charId=None   PO_type={tt}")
            continue
        def_info = defs.get(ci)
        if def_info:
            def_type, def_extra = def_info
            type_name = {36:'LL2', 32:'DS3', 46:'DS4', 39:'Sprite'}.get(def_type, f'tag{def_type}')
            has_img = bool(fl2 & 0x10)
            print(f"    depth={depth:<3} charId={ci:<5} type={type_name:<8} has_image={has_img} f1={fl1:#04x} f2={fl2:#04x}  {def_extra or ''}")
        else:
            print(f"    depth={depth:<3} charId={ci:<5} type=UNKNOWN f1={fl1:#04x} f2={fl2:#04x}")

for sid in sorted(dair_og_sprite_ids):
    show_sprite("OG", sid, og_sprites[sid], og_defs)
for sid in sorted(dair_rt_sprite_ids):
    show_sprite("RT", sid, rt_sprites[sid], rt_defs)

# --- Also find the actual DAir_73 sprite by looking for sprites that
#     reference the scythe sub-sprite (dim-based) ---
# The scythe sub-sprite contains bm_dairScythe (21x33) and bm_dairScytheBlade (13x20)
scythe_ll2_og = {cid for cid,(tt,e) in og_defs.items() if tt==36 and e in ((21,33),(13,20))}
scythe_ll2_rt = {cid for cid,(tt,e) in rt_defs.items() if tt==36 and e in ((21,33),(13,20))}

# Find sprites that contain both scythe bitmaps
print("\n=== Sub-sprites containing both scythe bitmaps (the scythe sub-sprite) ===")
for sid, placements in og_sprites.items():
    ci_set = {ci for (_,ci,_,_,_) in placements if ci}
    if ci_set & scythe_ll2_og:
        print(f"  OG Sprite {sid} contains scythe bitmaps")
        show_sprite("OG scythe", sid, placements, og_defs)

for sid, placements in rt_sprites.items():
    ci_set = {ci for (_,ci,_,_,_) in placements if ci}
    if ci_set & scythe_ll2_rt:
        print(f"  RT Sprite {sid} contains scythe bitmaps")
        show_sprite("RT scythe", sid, placements, rt_defs)

# Then find the parent sprite (DAir_73) that contains the scythe sub-sprite
scythe_sprite_og = {sid for sid,pl in og_sprites.items() if any(ci in scythe_ll2_og for (_,ci,_,_,_) in pl)}
scythe_sprite_rt = {sid for sid,pl in rt_sprites.items() if any(ci in scythe_ll2_rt for (_,ci,_,_,_) in pl)}

print("\n=== DAir_73 parent (contains the scythe sub-sprite) ===")
# The parent contains a sprite from scythe_sprite_og/rt
for sid, placements in og_sprites.items():
    ci_set = {ci for (_,ci,_,_,_) in placements if ci}
    if ci_set & scythe_sprite_og:
        print(f"  OG DAir_73 candidate: Sprite {sid}")
        show_sprite("OG DAir_73", sid, placements, og_defs)

for sid, placements in rt_sprites.items():
    ci_set = {ci for (_,ci,_,_,_) in placements if ci}
    if ci_set & scythe_sprite_rt:
        print(f"  RT DAir_73 candidate: Sprite {sid}")
        show_sprite("RT DAir_73", sid, placements, rt_defs)
