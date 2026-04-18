"""
Compare OG SWF vs RT SWF DAir_73 sprite structure.
Find what tag types define the characters that DAir_73 places.
If OG puts Shapes (not Bitmaps) as children, that's why replacePalette works in OG.
"""
import struct, zlib, sys

def parse_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    sig = raw[:3]
    if sig == b'CWS':
        body = zlib.decompress(raw[8:])
        raw = raw[:8] + body
    elif sig != b'FWS':
        raise ValueError(f"Unknown SWF: {sig}")
    
    # Skip header rect
    pos = 8
    nbits = (raw[pos] >> 3) & 0x1f
    pos += (5 + nbits * 4 + 7) // 8
    pos += 4  # framerate + framecount

    defs = {}  # char_id -> tag_type
    sprites = {}  # char_id -> list of (depth, char_id, flags2)
    
    current_sprite = None
    current_sprite_placements = []
    
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
        
        if tag_type == 0:  # End
            if current_sprite is not None:
                sprites[current_sprite] = current_sprite_placements
                current_sprite = None
                current_sprite_placements = []
            break
        
        if tag_type == 39:  # DefineSprite
            if current_sprite is not None:
                # nested sprite end -- parse inner
                sprites[current_sprite] = current_sprite_placements
            sprite_id = struct.unpack_from('<H', payload)[0]
            defs[sprite_id] = 39
            # parse inner tags
            inner_pos = 4  # skip sprite_id + frame_count
            inner_placements = []
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
                if t2 == 26:  # PO2
                    fl = p2[0]
                    depth = struct.unpack_from('<H', p2, 1)[0]
                    has_char = fl & 0x02
                    ci = None
                    if has_char:
                        ci = struct.unpack_from('<H', p2, 3)[0]
                    inner_placements.append((depth, ci, 0, 26))
                elif t2 == 70:  # PO3
                    fl1 = p2[0]; fl2 = p2[1]
                    depth = struct.unpack_from('<H', p2, 2)[0]
                    has_char = fl1 & 0x02
                    has_image = fl2 & 0x10
                    ci = None
                    if has_char:
                        ci = struct.unpack_from('<H', p2, 4)[0]
                    inner_placements.append((depth, ci, has_image, 70))
                elif t2 == 1:  # ShowFrame
                    pass
                elif t2 == 0:
                    break
                inner_pos += l2
            sprites[sprite_id] = inner_placements
        elif tag_type in (36, 32, 20, 2, 22, 83, 84, 46, 78, 91, 26, 70):
            if length >= 2:
                cid = struct.unpack_from('<H', payload)[0]
                defs[cid] = tag_type
        
        pos += length
    
    return defs, sprites

TAG_NAMES = {36: 'LL2', 32: 'DS3', 20: 'LL1', 2: 'DefineShape', 22: 'DS2', 
             83: 'DefineBinaryData', 84: 'DefineFont4', 46: 'DefineShape4',
             39: 'DefineSprite'}

OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

import os
if not os.path.exists(OG):
    # try without _ORIGINAL
    OG = RT.replace('blackmage.ssf', 'blackmage_og.ssf')
if not os.path.exists(OG):
    print(f"OG SWF not found at {OG}")
    # list what's in the directory
    d = os.path.dirname(RT)
    print("Files in dir:", os.listdir(d))
    sys.exit(1)

print(f"OG: {OG}")
print(f"RT: {RT}")

og_defs, og_sprites = parse_swf(OG)
rt_defs, rt_sprites = parse_swf(RT)

print(f"\nOG: {len(og_defs)} defs, {len(og_sprites)} sprites")
print(f"RT: {len(rt_defs)} defs, {len(rt_sprites)} sprites")

# Find DAir_73 sprite in both
# In OG: look for sprite with specific placements. 
# We need to find which sprite corresponds to DAir_73.
# From previous analysis: OG DAir_73 is sprite ID 1471 (OG), RT is whatever ID was assigned.
# Let's look at a sprite that places bitmaps at depths known to be in dair.

# RT: We know DAir_73 N2D id=1471, but SWF id is different. Let's find sprites by PO3+hasImage count.
def describe_sprite(sprite_id, placements, defs):
    bitmaps_direct = [(d,c,hi) for (d,c,hi,tt) in placements if hi and c and defs.get(c) == 36]
    shapes_direct = [(d,c,hi) for (d,c,hi,tt) in placements if (not hi) and c and defs.get(c) in (32,46,2,22)]
    po3_count = sum(1 for (_,_,_,tt) in placements if tt == 70)
    return f"  total_placements={len(placements)} PO3={po3_count} bitmaps_as_LL2={len(bitmaps_direct)} shapes={len(shapes_direct)}"

# Find sprites with multiple PO3+hasImage+LL2 placements in RT (these are our bitmap sprites)
print("\n=== RT sprites with 2+ PO3+hasImage+LL2 ===")
dair_rt_id = None
for sid, placements in sorted(rt_sprites.items()):
    bitmaps = [(d,c,hi) for (d,c,hi,tt) in placements if hi and c and rt_defs.get(c) == 36]
    if len(bitmaps) >= 2:
        print(f"  Sprite {sid}: {len(bitmaps)} direct LL2 Bitmaps: {[(d,c) for (d,c,hi) in bitmaps]}")
        if len(bitmaps) >= 2 and len(placements) >= 6:  # DAir_73 has many layers
            dair_rt_id = sid

print("\n=== OG sprites with 2+ placements ===")
dair_og_id = None
for sid, placements in sorted(og_sprites.items()):
    # In OG, dair bitmaps might be placed as Shape or Bitmap
    all_chars = [(d,c,hi,defs.get(c)) for (d,c,hi,tt) in placements if c]
    # Look for sprites with >= 5 placements that include both LL2-direct and shapes
    po3_hi = [(d,c,hi) for (d,c,hi,tt) in placements if hi]
    if len(placements) >= 6:
        char_types = [og_defs.get(c, '?') for (_,c,_,_) in placements if c]
        if 36 in char_types or 32 in char_types:
            print(f"  Sprite {sid}: {len(placements)} placements, char_types={set(char_types)}")
            if 36 in char_types:
                ll2_children = [(d,c) for (d,c,hi,tt) in placements if c and og_defs.get(c) == 36]
                print(f"    LL2 children (hasImage-via-LL2 defs): {ll2_children}")
                po3_hi_list = [(d,c,hi) for (d,c,hi,tt) in placements if hi and c]
                print(f"    PO3+hasImage: {po3_hi_list}")
                # If this looks like dair (has LL2 children)
                if len(ll2_children) >= 2:
                    dair_og_id = sid
