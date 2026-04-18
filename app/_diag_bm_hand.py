"""
Targeted diagnostic for the bm_dairHand (charID=1001) Error #2015 mystery.

Answers:
  Q1. Does OG have any DefineShape with a bitmap-fill reference to charID=1001?
      (Proper byte-scan — avoids imprecise matrix-skip used in _check_ds3_fills.py)
  Q2. Which charIDs were JPEG3 in OG (now LL2 in RT)?
  Q3. What tag-file index is charID=1001's LL2 tag in OG vs RT?
      (Relevant to H3 — pool-position/eviction theory)
  Q4. Are ANY other sprites (besides 1471) referencing charID=1001?
      (Double-check of previous finding)
  Q5. Does any DefineShape (any type) in OG/RT have the bytes E9 03 (= 1001 LE-uint16)?
"""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

BITMAP_FILL_TYPES  = {0x40, 0x41, 0x42, 0x43}
SHAPE_TAG_TYPES    = {2, 22, 32, 83}   # DS1, DS2, DS3, DS4
MORPH_TAG_TYPES    = {46, 84}          # DefineMorphShape, DefineMorphShape2
BUTTON_TAG_TYPES   = {7, 34}           # DefineButton, DefineButton2
SPRITE_TAG         = 39
JPEG3_TAG          = 35
LL2_TAG            = 36
DEFINE_BITS_TAG    = 6                 # raw JPEG no alpha

TARGET_CHAR_ID     = 1001
TARGET_CID_BYTES   = struct.pack('<H', TARGET_CHAR_ID)  # b'\xe9\x03'


# ─── SWF parser ─────────────────────────────────────────────────────────────

def read_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    return raw


def iter_tags(data, start=None):
    """Yield (tag_type, payload, file_offset) for every top-level SWF tag."""
    if start is None:
        # Skip SWF header: 8 bytes fixed + variable RECT + 4 bytes frame info
        pos = 8
        nb = (data[pos] >> 3) & 0x1F
        pos += (5 + nb * 4 + 7) // 8 + 4
    else:
        pos = start
    while pos + 1 < len(data):
        hdr = struct.unpack_from('<H', data, pos)[0]
        tt  = hdr >> 6
        sl  = hdr & 0x3F
        off = pos
        pos += 2
        if sl == 0x3F:
            l = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        else:
            l = sl
        payload = data[pos:pos + l]
        if tt == 0:
            break
        yield tt, payload, off
        pos += l


def iter_sprite_tags(payload):
    """Yield (tag_type, payload) for tags inside a DefineSprite body (after 4-byte header)."""
    pos = 4   # skip charID (2) + frameCount (2)
    while pos + 1 < len(payload):
        hdr = struct.unpack_from('<H', payload, pos)[0]
        tt  = hdr >> 6
        sl  = hdr & 0x3F
        pos += 2
        if sl == 0x3F:
            l = struct.unpack_from('<I', payload, pos)[0]
            pos += 4
        else:
            l = sl
        sp = payload[pos:pos + l]
        if tt == 0:
            break
        yield tt, sp
        pos += l


# ─── Q1 / Q5: raw byte scan of DefineShape payloads ─────────────────────────

def scan_shapes_for_target_cid(data, label):
    """
    For every DefineShape / DefineMorphShape / DefineButton tag,
    do a RAW BYTE SEARCH for TARGET_CID_BYTES anywhere in the payload.
    This is conservative — some matches may be false positives (e.g. part of a
    matrix bitfield), but a TRUE bitmap-fill reference WILL produce a match.
    """
    hits = []
    for tt, pay, off in iter_tags(data):
        if tt not in (SHAPE_TAG_TYPES | MORPH_TAG_TYPES | BUTTON_TAG_TYPES):
            continue
        if len(pay) < 4:
            continue
        cid = struct.unpack_from('<H', pay)[0]   # shape's own charID
        if cid == TARGET_CHAR_ID:
            # This IS bm_dairHand itself — skip
            continue
        idx = 0
        while True:
            idx = pay.find(TARGET_CID_BYTES, idx)
            if idx == -1:
                break
            hits.append((label, tt, cid, idx, off))
            idx += 1   # keep scanning for multiple occurrences
    return hits


# ─── Q2: JPEG3 charIDs in OG ────────────────────────────────────────────────

def jpeg3_charids(data):
    ids = []
    for tt, pay, _ in iter_tags(data):
        if tt == JPEG3_TAG and len(pay) >= 2:
            ids.append(struct.unpack_from('<H', pay)[0])
    return sorted(ids)


# ─── Q3: Tag-file index of charID=1001 LL2 ──────────────────────────────────

def ll2_tag_index(data):
    """Return (tag_index, total_ll2_count) for the LL2 with charID == TARGET."""
    idx = 0
    ll2_count = 0
    found_at = None
    for tt, pay, off in iter_tags(data):
        if tt == LL2_TAG:
            ll2_count += 1
            if len(pay) >= 2:
                cid = struct.unpack_from('<H', pay)[0]
                if cid == TARGET_CHAR_ID and found_at is None:
                    found_at = ll2_count   # 1-based position among LL2 tags
    return found_at, ll2_count


# ─── Q4: sprites referencing charID=1001 ────────────────────────────────────

def sprites_referencing_cid(data, target_cid):
    """Find every DefineSprite that has a PlaceObject3/2 referencing target_cid."""
    refs = {}
    for tt, pay, off in iter_tags(data):
        if tt != SPRITE_TAG:
            continue
        if len(pay) < 4:
            continue
        sp_cid = struct.unpack_from('<H', pay)[0]
        for stt, sp in iter_sprite_tags(pay):
            if stt == 70 and len(sp) >= 6:   # PlaceObject3
                flags2 = sp[1]
                has_char = (sp[0] >> 1) & 1
                has_image = (flags2 >> 4) & 1
                if has_char:
                    cid = struct.unpack_from('<H', sp, 4)[0]
                    if cid == target_cid:
                        refs.setdefault(sp_cid, []).append(('PO3', has_image))
            elif stt == 26 and len(sp) >= 3:   # PlaceObject2
                flags = sp[0]
                has_char = (flags >> 1) & 1
                if has_char and len(sp) >= 5:
                    cid = struct.unpack_from('<H', sp, 3)[0]
                    if cid == target_cid:
                        refs.setdefault(sp_cid, []).append(('PO2', 0))
    return refs


# ─── Q6: position of LL2 tag (by charID order) among ALL bitmaps ─────────────

def bitmap_order_stats(data):
    """Return a dict {charID: position} for all LL2 and JPEG3 tags, in file order."""
    order = {}
    pos_idx = 0
    for tt, pay, off in iter_tags(data):
        if tt in (LL2_TAG, JPEG3_TAG, DEFINE_BITS_TAG, 20, 21):  # bitmap tag types
            if len(pay) >= 2:
                cid = struct.unpack_from('<H', pay)[0]
                order[cid] = (pos_idx, 'LL2' if tt == LL2_TAG else 'JPEG3' if tt == JPEG3_TAG else f'tag{tt}')
            pos_idx += 1
    return order


# ─── MAIN ────────────────────────────────────────────────────────────────────

print("=" * 70)
print(f"TARGET: charID={TARGET_CHAR_ID} (bm_dairHand), bytes={TARGET_CID_BYTES.hex()}")
print("=" * 70)

og_data = read_swf(OG)
rt_data = read_swf(RT)

# --- Q1 / Q5: Shape byte scan ---
print("\n── Q1/Q5: DefineShape byte-scan for charID=1001 in payload ─────────────")
for path_data, lbl in [(og_data, 'OG'), (rt_data, 'RT')]:
    hits = scan_shapes_for_target_cid(path_data, lbl)
    if hits:
        print(f"  [{lbl}] {len(hits)} hit(s):")
        for _, tt, shape_cid, byte_idx, file_off in hits:
            tn = {2:'DS1', 22:'DS2', 32:'DS3', 83:'DS4', 46:'Morph1', 84:'Morph2', 7:'Btn1', 34:'Btn2'}.get(tt, f'tag{tt}')
            print(f"    shapeCID={shape_cid} ({tn}) bytes_in_payload={byte_idx} file_off={file_off:#x}")
    else:
        print(f"  [{lbl}] NO shapes contain charID=1001 bytes")

# --- Q2: JPEG3 charIDs in OG ---
print("\n── Q2: JPEG3 bitmap charIDs in OG ──────────────────────────────────────")
og_jpeg3 = jpeg3_charids(og_data)
print(f"  OG JPEG3 count: {len(og_jpeg3)}")
if og_jpeg3:
    print(f"  JPEG3 charIDs: {og_jpeg3}")
    near_1001 = [c for c in og_jpeg3 if abs(c - TARGET_CHAR_ID) <= 20]
    if near_1001:
        print(f"  ** JPEG3 charIDs near {TARGET_CHAR_ID} (±20): {near_1001}")
    else:
        print(f"  None within ±20 of {TARGET_CHAR_ID}")

# --- Q3: LL2 tag index ---
print("\n── Q3: LL2 file-position of charID=1001 ─────────────────────────────────")
for path_data, lbl in [(og_data, 'OG'), (rt_data, 'RT')]:
    pos, total = ll2_tag_index(path_data)
    print(f"  [{lbl}] charID=1001 is LL2 #{pos} out of {total} total LL2 tags")

# --- Q4: sprite references ---
print("\n── Q4: Sprites (any type) referencing charID=1001 ──────────────────────")
for path_data, lbl in [(og_data, 'OG'), (rt_data, 'RT')]:
    sprite_refs = sprites_referencing_cid(path_data, TARGET_CHAR_ID)
    if sprite_refs:
        for sp_cid, placements in sorted(sprite_refs.items()):
            print(f"  [{lbl}] Sprite {sp_cid}: {placements}")
    else:
        print(f"  [{lbl}] No sprites reference charID=1001 (unexpected!)")

# --- Q6: bitmap order ---
print("\n── Q6: Bitmap tag-order position (file order) ───────────────────────────")
og_order = bitmap_order_stats(og_data)
rt_order = bitmap_order_stats(rt_data)
if TARGET_CHAR_ID in og_order:
    op, ot = og_order[TARGET_CHAR_ID]
    print(f"  OG: charID=1001 is bitmap #{op} out of {len(og_order)} ({ot})")
if TARGET_CHAR_ID in rt_order:
    rp, rt_t = rt_order[TARGET_CHAR_ID]
    print(f"  RT: charID=1001 is bitmap #{rp} out of {len(rt_order)} ({rt_t})")

# Bonus: how many JPEG3 in OG come BEFORE charID=1001 in file?
if og_jpeg3 and TARGET_CHAR_ID in og_order:
    target_pos = og_order[TARGET_CHAR_ID][0]
    jpeg3_before = sum(1 for c in og_jpeg3 if c in og_order and og_order[c][0] < target_pos)
    print(f"\n  OG: JPEG3 bitmaps that appear BEFORE charID=1001 in file: {jpeg3_before}")

print()
print("Done.")
