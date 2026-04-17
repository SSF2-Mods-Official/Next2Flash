#!/usr/bin/env python3
"""Comprehensive binary diff between OG and RT fox.ssf files.
Checks EVERYTHING: headers, tag bodies, sprite internals, shape bytes, etc."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

TAG_NAMES = {0:'End', 1:'ShowFrame', 2:'DefShape', 4:'PlaceObject', 5:'RemoveObject',
             9:'SetBgColor', 14:'DefSound', 15:'StartSound', 20:'DefBitsLL', 21:'DefBitsJPEG2',
             22:'DefShape2', 24:'Protect', 26:'PO2', 28:'RO2', 32:'DefShape3',
             35:'DefBitsJPEG3', 36:'DefBitsLL2', 37:'DefEditText', 39:'DefSprite',
             43:'FrameLabel', 45:'SoundStreamHead2', 46:'DefMorphShape',
             48:'DefFont2', 56:'ExportAssets', 69:'FileAttrib', 70:'PO3',
             73:'FontAlignZones', 75:'DefFont3', 76:'SymbolClass', 77:'Metadata',
             82:'DoABC', 83:'DefShape4', 84:'DefMorph2', 86:'SceneLabel',
             87:'DefBinaryData', 88:'FontName', 89:'StartSound2'}

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS': return raw[:8] + zlib.decompress(raw[8:])
    if sig == b'ZWS':
        import lzma
        return raw[:8] + lzma.decompress(raw[12:])
    return raw

def get_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    return br.byte_pos + 4

def parse_tags(data, offset):
    tags = []; pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        tcl = struct.unpack_from('<H', data, pos)[0]
        tt = tcl >> 6; tl = tcl & 0x3F; pos += 2
        if tl == 0x3F:
            tl = struct.unpack_from('<I', data, pos)[0]; pos += 4
        body = data[pos:pos+tl]; tags.append((tt, body)); pos += tl
        if tt == 0: break
    return tags

def parse_symbol_class(body):
    if len(body) < 2: return {}
    count = struct.unpack_from('<H', body, 0)[0]
    pos = 2; result = {}
    for _ in range(count):
        cid = struct.unpack_from('<H', body, pos)[0]; pos += 2
        end = body.index(0, pos)
        name = body[pos:end].decode('utf-8','replace'); pos = end + 1
        result[cid] = name
    return result

def parse_sym_ordered(body):
    if len(body) < 2: return []
    count = struct.unpack_from('<H', body, 0)[0]
    pos = 2; result = []
    for _ in range(count):
        cid = struct.unpack_from('<H', body, pos)[0]; pos += 2
        end = body.index(0, pos)
        name = body[pos:end].decode('utf-8','replace'); pos = end + 1
        result.append((cid, name))
    return result

def get_sprite_cid(body):
    return struct.unpack_from('<H', body, 0)[0] if len(body) >= 2 else None

def get_sprite_frames(body):
    return struct.unpack_from('<H', body, 2)[0] if len(body) >= 4 else 0

def parse_sprite_inner(body):
    pos = 4; stags = []
    while pos < len(body):
        if pos + 2 > len(body): break
        tcl = struct.unpack_from('<H', body, pos)[0]
        stt = tcl >> 6; stl = tcl & 0x3F; pos += 2
        if stl == 0x3F:
            stl = struct.unpack_from('<I', body, pos)[0]; pos += 4
        sbody = body[pos:pos+stl]; stags.append((stt, sbody)); pos += stl
        if stt == 0: break
    return stags

def main():
    with open(OG_PATH, 'rb') as f: og_raw = f.read()
    with open(RT_PATH, 'rb') as f: rt_raw = f.read()
    
    print("=" * 80)
    print(f"OG: {OG_PATH}")
    print(f"    {len(og_raw)} bytes, sig={og_raw[:3]}")
    print(f"RT: {RT_PATH}")
    print(f"    {len(rt_raw)} bytes, sig={rt_raw[:3]}")
    print("=" * 80)
    
    og = decompress_swf(og_raw)
    rt = decompress_swf(rt_raw)
    
    # Header comparison
    print(f"\n--- HEADERS ---")
    print(f"  OG: ver={og[3]}, len={struct.unpack_from('<I', og, 4)[0]:,}")
    print(f"  RT: ver={rt[3]}, len={struct.unpack_from('<I', rt, 4)[0]:,}")
    
    og_off = get_offset(og)
    rt_off = get_offset(rt)
    print(f"  OG header bytes: {og[:og_off].hex()[:80]}...")
    print(f"  RT header bytes: {rt[:rt_off].hex()[:80]}...")
    if og[:og_off] == rt[:rt_off]:
        print(f"  Headers: IDENTICAL")
    else:
        print(f"  Headers: DIFFERENT!")
        for i in range(min(og_off, rt_off)):
            if og[i] != rt[i]:
                print(f"    First diff at byte {i}: OG=0x{og[i]:02x} RT=0x{rt[i]:02x}")
                break
    
    og_tags = parse_tags(og, og_off)
    rt_tags = parse_tags(rt, rt_off)
    
    print(f"\n--- TAG CENSUS ---")
    print(f"  OG: {len(og_tags)} tags")
    print(f"  RT: {len(rt_tags)} tags")
    
    from collections import Counter
    og_c = Counter(tt for tt, _ in og_tags)
    rt_c = Counter(tt for tt, _ in rt_tags)
    for tt in sorted(set(og_c) | set(rt_c)):
        oc, rc = og_c.get(tt,0), rt_c.get(tt,0)
        name = TAG_NAMES.get(tt, f'Tag{tt}')
        flag = " DIFF!" if oc != rc else ""
        print(f"    {name:25s}: OG={oc:5d}  RT={rc:5d}{flag}")
    
    # SymbolClass comparison
    og_sym = rt_sym = {}
    og_sym_ordered = rt_sym_ordered = []
    for tt, body in og_tags:
        if tt == 76:
            og_sym = parse_symbol_class(body)
            og_sym_ordered = parse_sym_ordered(body)
    for tt, body in rt_tags:
        if tt == 76:
            rt_sym = parse_symbol_class(body)
            rt_sym_ordered = parse_sym_ordered(body)
    
    print(f"\n--- SYMBOLCLASS ---")
    print(f"  OG: {len(og_sym)} entries, RT: {len(rt_sym)} entries")
    
    # Check order
    og_names = [n for _, n in og_sym_ordered]
    rt_names = [n for _, n in rt_sym_ordered]
    if og_names == rt_names:
        print(f"  Order: IDENTICAL")
    else:
        print(f"  Order: DIFFERENT!")
        for i in range(min(len(og_names), len(rt_names))):
            if og_names[i] != rt_names[i]:
                print(f"    First diff at [{i}]: OG='{og_names[i]}' RT='{rt_names[i]}'")
                break
    
    # Build name→cid maps
    og_name2cid = {n: c for c, n in og_sym.items()}
    rt_name2cid = {n: c for c, n in rt_sym.items()}
    
    # DoABC comparison
    og_abc = rt_abc = b''
    for tt, body in og_tags:
        if tt == 82: og_abc = body
    for tt, body in rt_tags:
        if tt == 82: rt_abc = body
    print(f"\n--- DoABC ---")
    print(f"  OG: {len(og_abc)} bytes")
    print(f"  RT: {len(rt_abc)} bytes")
    if og_abc == rt_abc:
        print(f"  Content: IDENTICAL")
    else:
        print(f"  Content: DIFFERENT!")
        for i in range(min(len(og_abc), len(rt_abc))):
            if og_abc[i] != rt_abc[i]:
                print(f"    First diff at byte {i}: OG=0x{og_abc[i]:02x} RT=0x{rt_abc[i]:02x}")
                break
    
    # Build sprites by charId
    og_sprites = {}; rt_sprites = {}
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            og_sprites[get_sprite_cid(body)] = body
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            rt_sprites[get_sprite_cid(body)] = body
    
    # Build shapes by charId
    og_shapes = {}; rt_shapes = {}
    for tt, body in og_tags:
        if tt in (2, 22, 32, 83) and len(body) >= 2:
            og_shapes[get_sprite_cid(body)] = (tt, body)
    for tt, body in rt_tags:
        if tt in (2, 22, 32, 83) and len(body) >= 2:
            rt_shapes[get_sprite_cid(body)] = (tt, body)
    
    # Build morphs by charId
    og_morphs = {}; rt_morphs = {}
    for tt, body in og_tags:
        if tt in (46, 84) and len(body) >= 2:
            og_morphs[get_sprite_cid(body)] = (tt, body)
    for tt, body in rt_tags:
        if tt in (46, 84) and len(body) >= 2:
            rt_morphs[get_sprite_cid(body)] = (tt, body)
    
    # Build bitmaps by charId
    og_bmps = {}; rt_bmps = {}
    for tt, body in og_tags:
        if tt in (20, 21, 35, 36) and len(body) >= 2:
            og_bmps[get_sprite_cid(body)] = (tt, body)
    for tt, body in rt_tags:
        if tt in (20, 21, 35, 36) and len(body) >= 2:
            rt_bmps[get_sprite_cid(body)] = (tt, body)
    
    # Build sounds by charId
    og_sounds = {}; rt_sounds = {}
    for tt, body in og_tags:
        if tt == 14 and len(body) >= 2:
            og_sounds[get_sprite_cid(body)] = body
    for tt, body in rt_tags:
        if tt == 14 and len(body) >= 2:
            rt_sounds[get_sprite_cid(body)] = body
    
    # Compare all named symbols
    print(f"\n--- NAMED SYMBOL COMPARISON (by class name) ---")
    sprite_diffs = []
    shape_diffs = []
    morph_diffs = []
    bmp_diffs = []
    sound_diffs = []
    missing_in_rt = []
    
    for name in og_names:
        og_cid = og_name2cid.get(name)
        rt_cid = rt_name2cid.get(name)
        if og_cid is None or rt_cid is None:
            missing_in_rt.append(name)
            continue
        
        # Sprite?
        if og_cid in og_sprites and rt_cid in rt_sprites:
            og_body = og_sprites[og_cid]
            rt_body = rt_sprites[rt_cid]
            og_fc = get_sprite_frames(og_body)
            rt_fc = get_sprite_frames(rt_body)
            og_inner = parse_sprite_inner(og_body)
            rt_inner = parse_sprite_inner(rt_body)
            
            issues = []
            if og_fc != rt_fc:
                issues.append(f"frames: {og_fc} vs {rt_fc}")
            if len(og_inner) != len(rt_inner):
                issues.append(f"inner tags: {len(og_inner)} vs {len(rt_inner)}")
            if len(og_body) != len(rt_body):
                issues.append(f"body size: {len(og_body)} vs {len(rt_body)}")
            
            # Compare tag types sequence
            og_seq = [(t,len(b)) for t,b in og_inner]
            rt_seq = [(t,len(b)) for t,b in rt_inner]
            if og_seq != rt_seq:
                issues.append("tag sequence differs")
            
            if issues:
                sprite_diffs.append((name, og_cid, rt_cid, issues))
        
        # Shape?
        if og_cid in og_shapes and rt_cid in rt_shapes:
            og_tt, og_body = og_shapes[og_cid]
            rt_tt, rt_body = rt_shapes[rt_cid]
            if og_tt != rt_tt or len(og_body) != len(rt_body):
                shape_diffs.append((name, og_cid, rt_cid, og_tt, rt_tt, len(og_body), len(rt_body)))
        
        # Morph?
        if og_cid in og_morphs and rt_cid in rt_morphs:
            og_tt, og_body = og_morphs[og_cid]
            rt_tt, rt_body = rt_morphs[rt_cid]
            if og_tt != rt_tt or len(og_body) != len(rt_body):
                morph_diffs.append((name, og_cid, rt_cid, og_tt, rt_tt, len(og_body), len(rt_body)))
        
        # Bitmap?
        if og_cid in og_bmps and rt_cid in rt_bmps:
            og_tt, og_body = og_bmps[og_cid]
            rt_tt, rt_body = rt_bmps[rt_cid]
            if og_tt != rt_tt or len(og_body) != len(rt_body):
                bmp_diffs.append((name, og_cid, rt_cid, og_tt, rt_tt, len(og_body), len(rt_body)))
        
        # Sound?
        if og_cid in og_sounds and rt_cid in rt_sounds:
            if og_sounds[og_cid] != rt_sounds[rt_cid]:
                sound_diffs.append((name, og_cid, rt_cid, len(og_sounds[og_cid]), len(rt_sounds[rt_cid])))
    
    print(f"\n  Sprite diffs: {len(sprite_diffs)}")
    for name, oc, rc, issues in sprite_diffs[:30]:
        print(f"    {name} (OG={oc}, RT={rc}): {'; '.join(issues)}")
    
    print(f"\n  Shape diffs: {len(shape_diffs)}")
    for name, oc, rc, ott, rtt, osz, rsz in shape_diffs[:20]:
        print(f"    {name}: type {ott}→{rtt}, size {osz}→{rsz}")
    
    print(f"\n  Morph diffs: {len(morph_diffs)}")
    for name, oc, rc, ott, rtt, osz, rsz in morph_diffs[:20]:
        print(f"    {name}: type {ott}→{rtt}, size {osz}→{rsz}")
    
    print(f"\n  Bitmap diffs: {len(bmp_diffs)}")
    for name, oc, rc, ott, rtt, osz, rsz in bmp_diffs[:10]:
        print(f"    {name}: type {ott}→{rtt}, size {osz}→{rsz}")
    
    print(f"\n  Sound diffs: {len(sound_diffs)}")
    for name, oc, rc, osz, rsz in sound_diffs[:10]:
        print(f"    {name}: size {osz}→{rsz}")
    
    if missing_in_rt:
        print(f"\n  Missing in RT: {missing_in_rt}")
    
    # Now compare ALL tags (not just named ones) by type
    # Compare non-named sprites too
    print(f"\n--- ALL SPRITE COMPARISON (by internal structure) ---")
    # Map OG→RT via SymbolClass names
    cid_map = {}  # og_cid → rt_cid
    for name in og_names:
        oc = og_name2cid.get(name)
        rc = rt_name2cid.get(name)
        if oc is not None and rc is not None:
            cid_map[oc] = rc
    
    # For non-named sprites, we can't directly map. Check total counts.
    print(f"  Named sprites mapped: {sum(1 for c in cid_map if c in og_sprites)}")
    print(f"  OG total sprites: {len(og_sprites)}")
    print(f"  RT total sprites: {len(rt_sprites)}")
    
    # Check if there are sprites in OG not in RT
    og_sprite_cids_mapped = set()
    rt_sprite_cids_mapped = set()
    for oc, rc in cid_map.items():
        if oc in og_sprites: og_sprite_cids_mapped.add(oc)
        if rc in rt_sprites: rt_sprite_cids_mapped.add(rc)
    
    unmapped_og = set(og_sprites.keys()) - og_sprite_cids_mapped
    unmapped_rt = set(rt_sprites.keys()) - rt_sprite_cids_mapped
    print(f"  Unmapped OG sprites (no SymbolClass name): {len(unmapped_og)}")
    print(f"  Unmapped RT sprites (no SymbolClass name): {len(unmapped_rt)}")
    
    # Compare font, edittext, and other definition tags
    print(f"\n--- FONT/TEXT TAGS ---")
    og_fonts = [(i, body) for i, (tt, body) in enumerate(og_tags) if tt in (75, 48)]
    rt_fonts = [(i, body) for i, (tt, body) in enumerate(rt_tags) if tt in (75, 48)]
    print(f"  OG fonts: {len(og_fonts)}")
    print(f"  RT fonts: {len(rt_fonts)}")
    for (oi, ob), (ri, rb) in zip(og_fonts, rt_fonts):
        oc = get_sprite_cid(ob)
        rc = get_sprite_cid(rb)
        match = "SAME" if len(ob) == len(rb) else f"DIFF ({len(ob)} vs {len(rb)})"
        print(f"    OG[{oi}] cid={oc} {len(ob)}B | RT[{ri}] cid={rc} {len(rb)}B | {match}")
    
    og_texts = [(i, body) for i, (tt, body) in enumerate(og_tags) if tt == 37]
    rt_texts = [(i, body) for i, (tt, body) in enumerate(rt_tags) if tt == 37]
    print(f"  OG edittext: {len(og_texts)}")
    print(f"  RT edittext: {len(rt_texts)}")
    
    # Check auxiliary tags (FileAttributes, Protect, SceneLabel, SoundStreamHead2)
    print(f"\n--- AUXILIARY TAGS ---")
    for check_tt, check_name in [(69,'FileAttrib'), (24,'Protect'), (86,'SceneLabel'), (45,'SoundStreamHead2')]:
        og_aux = [body for tt, body in og_tags if tt == check_tt]
        rt_aux = [body for tt, body in rt_tags if tt == check_tt]
        if len(og_aux) != len(rt_aux):
            print(f"  {check_name}: count OG={len(og_aux)} RT={len(rt_aux)} DIFF!")
        elif og_aux and og_aux[0] != rt_aux[0]:
            print(f"  {check_name}: BODY DIFFERS (OG={len(og_aux[0])}B RT={len(rt_aux[0])}B)")
            print(f"    OG: {og_aux[0][:40].hex()}")
            print(f"    RT: {rt_aux[0][:40].hex()}")
        else:
            print(f"  {check_name}: OK")
    
    # Tag-by-tag comparison at specific positions
    print(f"\n--- TAG POSITION COMPARISON (around SymbolClass/DoABC) ---")
    og_sym_pos = next((i for i, (tt, _) in enumerate(og_tags) if tt == 76), None)
    rt_sym_pos = next((i for i, (tt, _) in enumerate(rt_tags) if tt == 76), None)
    og_abc_pos = next((i for i, (tt, _) in enumerate(og_tags) if tt == 82), None)
    rt_abc_pos = next((i for i, (tt, _) in enumerate(rt_tags) if tt == 82), None)
    print(f"  OG: DoABC at [{og_abc_pos}], SymbolClass at [{og_sym_pos}]")
    print(f"  RT: DoABC at [{rt_abc_pos}], SymbolClass at [{rt_sym_pos}]")
    
    # Show tags from position max-5 to end
    start = max(0, (og_sym_pos or 0) - 3)
    end = len(og_tags)
    print(f"\n  OG tags [{start}..{end-1}]:")
    for i in range(start, end):
        tt, body = og_tags[i]
        name = TAG_NAMES.get(tt, f'Tag{tt}')
        extra = ""
        if tt == 39 and len(body) >= 4:
            extra = f" (cid={get_sprite_cid(body)}, {get_sprite_frames(body)}fr)"
        elif tt in (32, 83, 22, 2, 84, 36, 20, 35, 75, 14) and len(body) >= 2:
            extra = f" (cid={get_sprite_cid(body)}, {len(body)}B)"
        elif tt == 76:
            extra = f" ({len(parse_symbol_class(body))} entries)"
        elif tt == 82:
            extra = f" ({len(body)}B)"
        elif tt == 26 and len(body) >= 3:
            fl = body[0]; d = struct.unpack_from('<H', body, 1)[0]
            c = struct.unpack_from('<H', body, 3)[0] if fl & 2 and len(body) >= 5 else None
            extra = f" (d={d}, cid={c}, mv={bool(fl&1)})"
        print(f"    [{i:4d}] {name}{extra}")
    
    start = max(0, (rt_sym_pos or 0) - 3)
    end = len(rt_tags)
    print(f"\n  RT tags [{start}..{end-1}]:")
    for i in range(start, end):
        tt, body = rt_tags[i]
        name = TAG_NAMES.get(tt, f'Tag{tt}')
        extra = ""
        if tt == 39 and len(body) >= 4:
            extra = f" (cid={get_sprite_cid(body)}, {get_sprite_frames(body)}fr)"
        elif tt in (32, 83, 22, 2, 84, 36, 20, 35, 75, 14) and len(body) >= 2:
            extra = f" (cid={get_sprite_cid(body)}, {len(body)}B)"
        elif tt == 76:
            extra = f" ({len(parse_symbol_class(body))} entries)"
        elif tt == 82:
            extra = f" ({len(body)}B)"
        elif tt == 26 and len(body) >= 3:
            fl = body[0]; d = struct.unpack_from('<H', body, 1)[0]
            c = struct.unpack_from('<H', body, 3)[0] if fl & 2 and len(body) >= 5 else None
            extra = f" (d={d}, cid={c}, mv={bool(fl&1)})"
        print(f"    [{i:4d}] {name}{extra}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
