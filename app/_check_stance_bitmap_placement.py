"""
Investigate: in OG blackmage.ssf, how are bitmaps placed in stance sprites?
- Direct placement (PlaceObject2 with bitmap charId) → AS3 Bitmap object → threshold() works
- Via DefineShape3 wrapper  → AS3 Shape object → threshold() does NOT work

Also compare OG vs RT to see what differs.
"""
import struct, zlib, sys, io, collections
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

# ---------------------------------------------------------------------------
# SWF parsing helpers
# ---------------------------------------------------------------------------

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset=None, end=None):
    if offset is None:
        offset = skip_header(data)
    if end is None:
        end = len(data)
    tags = []
    while offset < end:
        if offset + 2 > end:
            break
        hdr = struct.unpack_from('<H', data, offset)[0]
        tt = hdr >> 6
        length = hdr & 0x3F
        offset += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, offset)[0]
            offset += 4
        td = data[offset:offset + length]
        tags.append((tt, td))
        offset += length
        if tt == 0:
            break
    return tags

def parse_rect_bits(d, bit_off=0):
    """Returns number of BITS consumed by this RECT."""
    byte_i = bit_off // 8
    bit_i  = bit_off % 8
    nbits = 0
    for i in range(5):
        nbits = (nbits << 1) | ((d[byte_i + (bit_i + i) // 8] >> (7 - (bit_i + i) % 8)) & 1)
    return 5 + nbits * 4

def skip_header(data):
    rect_bits = parse_rect_bits(data, 64)
    rect_bytes = (rect_bits + 7) // 8
    return 8 + rect_bytes + 4

# ---------------------------------------------------------------------------
# Inventory builder
# ---------------------------------------------------------------------------

def build_inventory(tags):
    """
    Returns:
      bitmaps:  {charId: 'lossless2'|'jpeg3'}
      shapes:   {charId: [bitmap_charIds_referenced]}
      sprites:  {charId: [(place_charId, depth, frame), ...]}  (PlaceObject2/3 placements)
      sym_class: {name: charId}
    """
    bitmaps = {}   # charId → tag type string
    shapes  = {}   # charId → list of bitmap cids referenced via fills
    sprites = {}   # charId → list of placement dicts
    sym_class = {} # class name → charId

    for (tt, d) in tags:
        if tt in (35, 36, 20):               # bitmap tags
            if len(d) < 2: continue
            cid = struct.unpack_from('<H', d, 0)[0]
            bitmaps[cid] = {35: 'jpeg3', 36: 'lossless2', 20: 'lossless'}[tt]

        elif tt in (2, 22, 32, 83):          # DefineShape variants
            cid = struct.unpack_from('<H', d, 0)[0]
            bitmap_refs = _parse_shape_bitmap_fills(d, tt)
            shapes[cid] = bitmap_refs

        elif tt == 39:                       # DefineSprite
            cid = struct.unpack_from('<H', d, 0)[0]
            frame_count = struct.unpack_from('<H', d, 2)[0]
            inner_tags = parse_tags(d, offset=4, end=len(d))
            placements = _parse_sprite_placements(inner_tags)
            sprites[cid] = placements

        elif tt == 76:                       # SymbolClass
            num = struct.unpack_from('<H', d, 0)[0]
            off = 2
            for _ in range(num):
                cid = struct.unpack_from('<H', d, off)[0]; off += 2
                name_end = d.index(b'\x00', off)
                name = d[off:name_end].decode('utf-8', errors='replace')
                off = name_end + 1
                sym_class[name] = cid

    return bitmaps, shapes, sprites, sym_class


def _parse_sprite_placements(inner_tags):
    """Extract all PlaceObject2/3 from a sprite's tag list."""
    placements = []
    frame = 0
    for (tt, d) in inner_tags:
        if tt == 1:   # ShowFrame
            frame += 1
        elif tt == 26:  # PlaceObject2
            if len(d) < 3: continue
            flags = d[0]
            has_char = bool(flags & 0x02)
            depth = struct.unpack_from('<H', d, 1)[0]
            off = 3
            if has_char and off + 1 < len(d):
                cid = struct.unpack_from('<H', d, off)[0]
                placements.append({'cid': cid, 'depth': depth, 'frame': frame,
                                   'tag': 'PO2', 'has_image': False})
        elif tt == 70:  # PlaceObject3
            if len(d) < 4: continue
            flags1 = d[0]; flags2 = d[1]
            has_char  = bool(flags1 & 0x02)
            has_image = bool(flags2 & 0x10)
            depth = struct.unpack_from('<H', d, 2)[0]
            off = 4
            if has_char and off + 1 < len(d):
                cid = struct.unpack_from('<H', d, off)[0]
                placements.append({'cid': cid, 'depth': depth, 'frame': frame,
                                   'tag': 'PO3', 'has_image': has_image})
    return placements


def _parse_shape_bitmap_fills(d, tag_type):
    """Return list of bitmap charIds referenced by bitmap fills in this shape tag."""
    if len(d) < 4:
        return []
    # Skip charId (2 bytes) + RECT
    bit_off = 16  # 2 bytes = 16 bits for charId
    rect_bits = parse_rect_bits(d, bit_off)
    byte_off = (bit_off + rect_bits + 7) // 8

    if tag_type == 83:  # DefineShape4 has EdgeBounds + flags
        if byte_off >= len(d): return []
        nbits2 = d[byte_off] >> 3
        byte_off += (5 + nbits2 * 4 + 7) // 8
        byte_off += 1  # flags

    if byte_off >= len(d):
        return []

    fill_count = d[byte_off]; byte_off += 1
    if fill_count == 0xFF:
        if byte_off + 1 >= len(d): return []
        fill_count = struct.unpack_from('<H', d, byte_off)[0]; byte_off += 2

    bitmap_refs = []
    for _ in range(fill_count):
        if byte_off >= len(d):
            break
        fill_type = d[byte_off]; byte_off += 1
        if fill_type == 0x00:
            byte_off += 4 if tag_type in (32, 83) else 3
        elif fill_type in (0x10, 0x12, 0x13):
            break  # gradient — variable length, just stop
        elif fill_type in (0x40, 0x41, 0x42, 0x43):
            if byte_off + 1 < len(d):
                bitmap_refs.append(struct.unpack_from('<H', d, byte_off)[0])
            break  # rough parse for fill styles — stop after first bitmap fill
        else:
            break
    return bitmap_refs

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyse(label, tags):
    bitmaps, shapes, sprites, sym_class = build_inventory(tags)

    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(f"  Bitmaps: {len(bitmaps)}, Shapes: {len(shapes)}, Sprites: {len(sprites)}")

    # Build reverse: shape_id → bitmap_ids it wraps
    shape_wraps_bitmap = {sid: refs for sid, refs in shapes.items() if refs}
    print(f"  Shapes with bitmap fills: {len(shape_wraps_bitmap)}")

    # For all sprites: classify placed charIds
    # category per placement:
    #  'direct_bitmap'  — placed charId is a known bitmap → AS3 Bitmap
    #  'shape_wrapping' — placed charId is a shape referencing bitmaps → AS3 Shape
    #  'shape_no_bmp'   — placed charId is a shape with no bitmap fill
    #  'sprite'         — nested sprite
    #  'unknown'
    def classify(cid):
        if cid in bitmaps:
            return 'direct_bitmap'
        if cid in shape_wraps_bitmap:
            return 'shape_wrapping_bitmap'
        if cid in shapes:
            return 'shape_no_bmp'
        if cid in sprites:
            return 'sprite'
        return 'unknown'

    # Count across all sprites
    cat_counts = collections.Counter()
    for sid, placements in sprites.items():
        for p in placements:
            cat_counts[classify(p['cid'])] += 1

    print("\n  All placements across all sprites:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat:30s}: {cnt:5d}")

    # Find sprites that have ANY direct bitmap placement
    sprites_with_direct_bmp = [
        sid for sid, placements in sprites.items()
        if any(classify(p['cid']) == 'direct_bitmap' for p in placements)
    ]
    print(f"\n  Sprites with direct bitmap placements: {len(sprites_with_direct_bmp)}")
    for sid in sorted(sprites_with_direct_bmp)[:20]:
        direct = [p for p in sprites[sid] if classify(p['cid']) == 'direct_bitmap']
        # Show which bitmap IDs are placed directly
        bmp_ids = sorted({p['cid'] for p in direct})
        tags_used = {p['tag'] for p in direct}
        has_imgs  = any(p.get('has_image') for p in direct)
        print(f"    sprite cid={sid:5d}  frames=~{1+max((p['frame'] for p in sprites[sid]), default=0):3d}"
              f"  direct_bitmaps={bmp_ids[:5]}  tags={tags_used}  has_image={has_imgs}")

    # SymbolClass entries
    print(f"\n  SymbolClass entries: {len(sym_class)}")
    # Find the main sprite (usually SymbolClass entry 0 maps to the root)
    if sym_class:
        # Root is typically cid=0 → 'blackmage' or similar
        # Show all entries
        for name, cid in sorted(sym_class.items()):
            print(f"    cid={cid:5d}  {name}")

    # HasImage placements (PlaceObject3 with has_image=True)
    has_image_total = sum(
        1 for sid, placements in sprites.items()
        for p in placements if p.get('has_image')
    )
    print(f"\n  PlaceObject3 with has_image=True: {has_image_total}")

    return bitmaps, shapes, sprites, sym_class, shape_wraps_bitmap


def compare_og_vs_rt(og_data, rt_data):
    og_tags = parse_tags(og_data)
    rt_tags = parse_tags(rt_data)

    og_bitmaps, og_shapes, og_sprites, og_sym, og_wrap = analyse("OG blackmage.ssf", og_tags)
    rt_bitmaps, rt_shapes, rt_sprites, rt_sym, rt_wrap = analyse("RT blackmage.ssf", rt_tags)

    # Cross-check: for the same sprite names, what do they place?
    # Use SymbolClass to align
    print(f"\n{'=' * 60}")
    print("  STANCE SPRITE ANALYSIS (depth=2 walk for replacePalette)")
    print(f"{'=' * 60}")

    # The main character sprite is the one exported by SymbolClass
    # Find an entry that looks like a character class
    def find_main_char(sym):
        for name, cid in sym.items():
            if 'blackmage' in name.lower() or 'black' in name.lower():
                return cid, name
        # Fallback: any exported symbol
        return None, None

    og_main_cid, og_main_name = find_main_char(og_sym)
    rt_main_cid, rt_main_name = find_main_char(rt_sym)
    print(f"\n  OG main cid={og_main_cid}  name={og_main_name}")
    print(f"  RT main cid={rt_main_cid}  name={rt_main_name}")

    def walk_depth2(sprites, shapes, bitmaps, shape_wrap, root_cid, label):
        """Walk the stance sprite at depth=2 like Utils.replacePalette."""
        if root_cid not in sprites:
            print(f"  [{label}] root cid={root_cid} not in sprites dict")
            return

        def classify(cid):
            if cid in bitmaps:    return 'direct_bitmap'
            if cid in shape_wrap: return 'shape_wrapping_bitmap'
            if cid in shapes:     return 'shape_no_bmp'
            if cid in sprites:    return 'sprite'
            return 'unknown'

        depth0_placements = sprites[root_cid]
        depth0_child_cids = sorted({p['cid'] for p in depth0_placements})
        print(f"\n  [{label}] depth0 (root sprite cid={root_cid}) places {len(depth0_child_cids)} unique cids")

        # Depth 1 children
        depth1_sprites = [cid for cid in depth0_child_cids if cid in sprites]
        depth1_bitmaps = [cid for cid in depth0_child_cids if classify(cid) == 'direct_bitmap']
        depth1_shapes_bmp = [cid for cid in depth0_child_cids if classify(cid) == 'shape_wrapping_bitmap']
        print(f"    depth1 sprite children: {len(depth1_sprites)}")
        print(f"    depth1 direct bitmap children: {len(depth1_bitmaps)} => {depth1_bitmaps[:10]}")
        print(f"    depth1 shape-wrapping-bitmap children: {len(depth1_shapes_bmp)} => {depth1_shapes_bmp[:10]}")

        # Depth 2: look inside depth1 sprites
        all_depth2_direct_bitmaps = []
        all_depth2_shape_bitmaps  = []
        all_depth2_sprites        = []
        for sp_cid in depth1_sprites:
            child_cids = sorted({p['cid'] for p in sprites[sp_cid]})
            for cid in child_cids:
                cat = classify(cid)
                if   cat == 'direct_bitmap':         all_depth2_direct_bitmaps.append(cid)
                elif cat == 'shape_wrapping_bitmap':  all_depth2_shape_bitmaps.append(cid)
                elif cat == 'sprite':                 all_depth2_sprites.append(cid)

        print(f"    depth2 direct bitmap children total: {len(all_depth2_direct_bitmaps)}")
        print(f"    depth2 shape-wrapping-bitmap children total: {len(all_depth2_shape_bitmaps)}")
        print(f"    depth2 sprite children total: {len(all_depth2_sprites)}")
        print(f"    replacePalette would find Bitmap objects: {len(all_depth2_direct_bitmaps) + len(depth1_bitmaps)}")

    walk_depth2(og_sprites, og_shapes, og_bitmaps, og_wrap, og_main_cid, "OG")
    walk_depth2(rt_sprites, rt_shapes, rt_bitmaps, rt_wrap, rt_main_cid, "RT")


if __name__ == '__main__':
    og_data = read_swf(OG)
    rt_data = read_swf(RT)
    compare_og_vs_rt(og_data, rt_data)
