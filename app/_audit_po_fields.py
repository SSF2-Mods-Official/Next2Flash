#!/usr/bin/env python3
"""
Quantify EXACTLY what PO fields exist in fox.ssf but are lost in roundtrip.
Check: className, visible flag, clipActions, blendMode, cacheAsBitmap.
"""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS':
        return raw[:8] + zlib.decompress(raw[8:])
    return raw

def get_tag_start_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nb)
    br.align()
    return br.byte_pos + 4

def parse_tags_from_data(data, offset):
    tags = []
    pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        tcl = struct.unpack_from('<H', data, pos)[0]
        tt = tcl >> 6; tl = tcl & 0x3F; pos += 2
        if tl == 0x3F:
            if pos + 4 > len(data): break
            tl = struct.unpack_from('<I', data, pos)[0]; pos += 4
        body = data[pos:pos+tl]; tags.append((tt, body)); pos += tl
        if tt == 0: break
    return tags

def analyze_po3_flags(body):
    """Parse PO3 and return which optional fields are present."""
    if len(body) < 4:
        return None
    flags1 = body[0]
    flags2 = body[1]
    depth = struct.unpack_from('<H', body, 2)[0]
    
    result = {
        'depth': depth,
        'hasMove': bool(flags1 & 0x01),
        'hasCharacter': bool(flags1 & 0x02),
        'hasMatrix': bool(flags1 & 0x04),
        'hasClassName': bool(flags1 & 0x08),
        'hasCxform': bool(flags1 & 0x10),
        'hasRatio': bool(flags1 & 0x20),
        'hasName': bool(flags1 & 0x40),
        'hasClipDepth': bool(flags1 & 0x80),
        # flags2
        'hasFilters': bool(flags2 & 0x01),
        'hasBlendMode': bool(flags2 & 0x02),
        'hasCacheAsBitmap': bool(flags2 & 0x04),
        'hasVisible': bool(flags2 & 0x08),
        'hasOpaqueBackground': bool(flags2 & 0x10),
        'hasClipActions': bool(flags2 & 0x20),
    }
    
    # Parse className if present
    pos = 4
    if result['hasClassName']:
        end = body.index(0, pos)
        result['className'] = body[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
    
    if result['hasCharacter']:
        if pos + 2 <= len(body):
            result['charId'] = struct.unpack_from('<H', body, pos)[0]
            pos += 2
    
    return result

def analyze_po2_flags(body):
    """Parse PO2 flags."""
    if len(body) < 3:
        return None
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    return {
        'depth': depth,
        'hasMove': bool(flags & 0x01),
        'hasCharacter': bool(flags & 0x02),
        'hasMatrix': bool(flags & 0x04),
        'hasCxform': bool(flags & 0x08),
        'hasRatio': bool(flags & 0x10),
        'hasName': bool(flags & 0x20),
        'hasClipDepth': bool(flags & 0x40),
        'hasClipActions': bool(flags & 0x80),
    }

def main():
    with open(SSF_PATH, 'rb') as f:
        raw = f.read()
    data = decompress_swf(raw)
    offset = get_tag_start_offset(data)
    all_tags = parse_tags_from_data(data, offset)
    
    print("=" * 80)
    print("OG fox.ssf PlaceObject FIELD AUDIT")
    print("=" * 80)
    
    # Collect ALL PO tags: root level + inside sprites
    po_entries = []  # (context, tag_type, analysis_dict)
    
    for tt, body in all_tags:
        if tt == 26:
            a = analyze_po2_flags(body)
            if a: po_entries.append(('root', 'PO2', a))
        elif tt == 70:
            a = analyze_po3_flags(body)
            if a: po_entries.append(('root', 'PO3', a))
        elif tt == 39 and len(body) >= 4:
            sprite_cid = struct.unpack_from('<H', body, 0)[0]
            nested = parse_tags_from_data(body, 4)
            for ntt, nbody in nested:
                if ntt == 26:
                    a = analyze_po2_flags(nbody)
                    if a: po_entries.append((f'sprite:{sprite_cid}', 'PO2', a))
                elif ntt == 70:
                    a = analyze_po3_flags(nbody)
                    if a: po_entries.append((f'sprite:{sprite_cid}', 'PO3', a))
    
    print(f"\nTotal PlaceObject tags: {len(po_entries)}")
    po2_count = sum(1 for _, t, _ in po_entries if t == 'PO2')
    po3_count = sum(1 for _, t, _ in po_entries if t == 'PO3')
    print(f"  PO2: {po2_count}, PO3: {po3_count}")
    
    # === Check each problematic field ===
    
    print("\n--- Fields that are LOST in roundtrip ---")
    
    # 1. className (PO3 only)
    with_classname = [(ctx, a) for ctx, t, a in po_entries if t == 'PO3' and a.get('hasClassName')]
    print(f"\n  [className] PO3 with className: {len(with_classname)}")
    for ctx, a in with_classname[:20]:
        print(f"    {ctx} depth={a['depth']} className='{a.get('className', '?')}' charId={a.get('charId', '?')}")
    
    # 2. visible flag
    with_visible = [(ctx, a) for ctx, t, a in po_entries if a.get('hasVisible')]
    print(f"\n  [visible] PO tags with visible flag: {len(with_visible)}")
    for ctx, a in with_visible[:20]:
        print(f"    {ctx} depth={a['depth']}")
    
    # 3. cacheAsBitmap
    with_cache = [(ctx, a) for ctx, t, a in po_entries if a.get('hasCacheAsBitmap')]
    print(f"\n  [cacheAsBitmap] PO tags with cacheAsBitmap: {len(with_cache)}")
    for ctx, a in with_cache[:20]:
        print(f"    {ctx} depth={a['depth']}")
    
    # 4. opaqueBackground
    with_opaque = [(ctx, a) for ctx, t, a in po_entries if a.get('hasOpaqueBackground')]
    print(f"\n  [opaqueBackground] PO tags with opaqueBackground: {len(with_opaque)}")
    
    # 5. clipActions (AVM1 only, shouldn't matter for AS3)
    with_clip_actions = [(ctx, a) for ctx, t, a in po_entries if a.get('hasClipActions')]
    print(f"\n  [clipActions] PO tags with clipActions: {len(with_clip_actions)}")
    
    # === Check fields that ARE preserved but may have issues ===
    
    print("\n--- Fields presence summary (all POs) ---")
    fields = ['hasMove', 'hasCharacter', 'hasMatrix', 'hasCxform', 'hasRatio',
              'hasName', 'hasClipDepth', 'hasFilters', 'hasBlendMode']
    for f in fields:
        count = sum(1 for _, _, a in po_entries if a.get(f))
        print(f"  {f}: {count}")
    
    # === Specific analysis: PO3 tags with special features ===
    print("\n--- PO3 detailed breakdown ---")
    for ctx, t, a in po_entries:
        if t != 'PO3':
            continue
        special = []
        for f in ['hasClassName', 'hasVisible', 'hasCacheAsBitmap', 'hasOpaqueBackground',
                  'hasClipActions', 'hasFilters', 'hasBlendMode', 'hasClipDepth', 'hasRatio']:
            if a.get(f):
                special.append(f.replace('has', ''))
        if special:
            charId = a.get('charId', '?')
            cn = a.get('className', '')
            cn_str = f" className='{cn}'" if cn else ""
            print(f"  {ctx} depth={a['depth']} charId={charId}{cn_str}: {', '.join(special)}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
