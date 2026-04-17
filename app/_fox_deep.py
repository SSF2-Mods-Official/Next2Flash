#!/usr/bin/env python3
"""Deep dive into fox sprite differences and root timeline differences."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from collections import Counter

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

TAG_NAMES = {0:'End', 1:'ShowFrame', 2:'DefShape', 4:'PO1', 5:'RO1',
             9:'SetBgColor', 14:'DefSound', 15:'StartSound', 18:'SndStreamHd',
             19:'SndStreamBlock', 20:'DefBitsLL', 21:'DefBitsJPEG2',
             22:'DefShape2', 24:'Protect', 26:'PO2', 28:'RO2', 32:'DefShape3',
             35:'DefBitsJPEG3', 36:'DefBitsLL2', 37:'DefEditText', 39:'DefSprite',
             43:'FrameLabel', 45:'SndStreamHd2', 46:'DefMorphShape',
             69:'FileAttrib', 70:'PO3', 73:'FontAlignZones',
             75:'DefFont3', 76:'SymbolClass', 82:'DoABC', 83:'DefShape4',
             84:'DefMorph2', 86:'SceneLabel', 88:'FontName', 74:'CSMTextSettings',
             11:'DefText'}

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS': return raw[:8] + zlib.decompress(raw[8:])
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

def parse_po(body, version=2):
    """Parse PO2 or PO3 basic fields."""
    if len(body) < 3: return {}
    if version == 3:
        # PO3 has 2-byte flags
        if len(body) < 4: return {}
        flags = struct.unpack_from('<H', body, 0)[0]
        depth = struct.unpack_from('<H', body, 2)[0]
        pos = 4
    else:
        flags = body[0]
        depth = struct.unpack_from('<H', body, 1)[0]
        pos = 3
    
    result = {'flags': flags, 'depth': depth, 'move': bool(flags & 1)}
    
    if flags & 0x02 and pos + 2 <= len(body):
        result['charId'] = struct.unpack_from('<H', body, pos)[0]
        pos += 2
    
    return result

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

def main():
    with open(OG_PATH, 'rb') as f: og_raw = f.read()
    with open(RT_PATH, 'rb') as f: rt_raw = f.read()
    
    og = decompress_swf(og_raw)
    rt = decompress_swf(rt_raw)
    og_tags = parse_tags(og, get_offset(og))
    rt_tags = parse_tags(rt, get_offset(rt))
    
    # Get SymbolClass
    og_sym = {}; rt_sym = {}
    for tt, body in og_tags:
        if tt == 76: og_sym = parse_symbol_class(body)
    for tt, body in rt_tags:
        if tt == 76: rt_sym = parse_symbol_class(body)
    og_name2cid = {v:k for k,v in og_sym.items()}
    rt_name2cid = {v:k for k,v in rt_sym.items()}
    
    # Get all sprites
    og_sprites = {}; rt_sprites = {}
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            og_sprites[struct.unpack_from('<H', body, 0)[0]] = body
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            rt_sprites[struct.unpack_from('<H', body, 0)[0]] = body
    
    # ===== FOX SPRITE DEEP DIVE =====
    fox_og_cid = og_name2cid['fox']
    fox_rt_cid = rt_name2cid['fox']
    
    og_inner = parse_sprite_inner(og_sprites[fox_og_cid])
    rt_inner = parse_sprite_inner(rt_sprites[fox_rt_cid])
    
    print("=" * 80)
    print(f"FOX SPRITE DEEP DIVE")
    print(f"  OG cid={fox_og_cid}: {len(og_inner)} inner tags, body={len(og_sprites[fox_og_cid])}B")
    print(f"  RT cid={fox_rt_cid}: {len(rt_inner)} inner tags, body={len(rt_sprites[fox_rt_cid])}B")
    print("=" * 80)
    
    # Tag type breakdown
    og_tc = Counter(tt for tt, _ in og_inner)
    rt_tc = Counter(tt for tt, _ in rt_inner)
    print(f"\n  Tag type breakdown:")
    for stt in sorted(set(og_tc) | set(rt_tc)):
        name = TAG_NAMES.get(stt, f'Tag{stt}')
        print(f"    {name:20s}: OG={og_tc.get(stt,0):3d}  RT={rt_tc.get(stt,0):3d}  {'DIFF!' if og_tc.get(stt,0)!=rt_tc.get(stt,0) else ''}")
    
    # Dump fox sprite frame-by-frame
    print(f"\n  --- OG Fox frame-by-frame ---")
    frame = 0
    for stt, sbody in og_inner:
        name = TAG_NAMES.get(stt, f'Tag{stt}')
        if stt == 1:
            print(f"    -- ShowFrame (end of frame {frame}) --")
            frame += 1
        elif stt == 43:
            label = sbody[:sbody.index(0)].decode('utf-8','replace') if 0 in sbody else '?'
            print(f"    [F{frame}] FrameLabel: '{label}'")
        elif stt == 26:
            po = parse_po(sbody, 2)
            print(f"    [F{frame}] PO2: depth={po.get('depth')} charId={po.get('charId')} move={po.get('move')} flags=0x{po.get('flags',0):02x} ({len(sbody)}B)")
        elif stt == 70:
            po = parse_po(sbody, 3)
            print(f"    [F{frame}] PO3: depth={po.get('depth')} charId={po.get('charId')} move={po.get('move')} flags=0x{po.get('flags',0):04x} ({len(sbody)}B)")
        elif stt == 28:
            d = struct.unpack_from('<H', sbody, 0)[0]
            print(f"    [F{frame}] RO2: depth={d}")
        elif stt == 15:
            sid = struct.unpack_from('<H', sbody, 0)[0] if len(sbody) >= 2 else '?'
            info = struct.unpack_from('<B', sbody, 2)[0] if len(sbody) >= 3 else 0
            print(f"    [F{frame}] StartSound: soundId={sid} info=0x{info:02x} ({len(sbody)}B)")
        else:
            print(f"    [F{frame}] {name}: {len(sbody)}B")
    
    print(f"\n  --- RT Fox frame-by-frame ---")
    frame = 0
    for stt, sbody in rt_inner:
        name = TAG_NAMES.get(stt, f'Tag{stt}')
        if stt == 1:
            print(f"    -- ShowFrame (end of frame {frame}) --")
            frame += 1
        elif stt == 43:
            label = sbody[:sbody.index(0)].decode('utf-8','replace') if 0 in sbody else '?'
            print(f"    [F{frame}] FrameLabel: '{label}'")
        elif stt == 26:
            po = parse_po(sbody, 2)
            print(f"    [F{frame}] PO2: depth={po.get('depth')} charId={po.get('charId')} move={po.get('move')} flags=0x{po.get('flags',0):02x} ({len(sbody)}B)")
        elif stt == 70:
            po = parse_po(sbody, 3)
            print(f"    [F{frame}] PO3: depth={po.get('depth')} charId={po.get('charId')} move={po.get('move')} flags=0x{po.get('flags',0):04x} ({len(sbody)}B)")
        elif stt == 28:
            d = struct.unpack_from('<H', sbody, 0)[0]
            print(f"    [F{frame}] RO2: depth={d}")
        elif stt == 15:
            sid = struct.unpack_from('<H', sbody, 0)[0] if len(sbody) >= 2 else '?'
            info = struct.unpack_from('<B', sbody, 2)[0] if len(sbody) >= 3 else 0
            print(f"    [F{frame}] StartSound: soundId={sid} info=0x{info:02x} ({len(sbody)}B)")
        else:
            print(f"    [F{frame}] {name}: {len(sbody)}B")
    
    # ===== SoundStreamHead2 =====
    print(f"\n{'='*80}")
    print(f"SOUNDSTREAMHEAD2 COMPARISON")
    for tt, body in og_tags:
        if tt == 45:
            print(f"  OG: {body.hex()}")
            # Parse: byte0=format info, byte1=format info2
            print(f"    Byte 0=0x{body[0]:02x} ({body[0]:08b})")
            print(f"    Byte 1=0x{body[1]:02x} ({body[1]:08b})")
            # Bits: playback rate(2), playback size(1), playback type(1)
            # + stream format(4), stream rate(2), stream size(1), stream type(1)
            pb_codec = (body[0] >> 4) & 0xF
            pb_rate = (body[0] >> 2) & 0x3
            pb_size = (body[0] >> 1) & 0x1
            pb_stereo = body[0] & 0x1
            st_codec = (body[1] >> 4) & 0xF
            st_rate = (body[1] >> 2) & 0x3
            st_size = (body[1] >> 1) & 0x1
            st_stereo = body[1] & 0x1
            print(f"    Playback: codec={pb_codec} rate={pb_rate} size={pb_size} stereo={pb_stereo}")
            print(f"    Stream: codec={st_codec} rate={st_rate} size={st_size} stereo={st_stereo}")
    for tt, body in rt_tags:
        if tt == 45:
            print(f"  RT: {body.hex()}")
            print(f"    Byte 0=0x{body[0]:02x} ({body[0]:08b})")
            print(f"    Byte 1=0x{body[1]:02x} ({body[1]:08b})")
            pb_codec = (body[0] >> 4) & 0xF
            pb_rate = (body[0] >> 2) & 0x3
            pb_size = (body[0] >> 1) & 0x1
            pb_stereo = body[0] & 0x1
            st_codec = (body[1] >> 4) & 0xF
            st_rate = (body[1] >> 2) & 0x3
            st_size = (body[1] >> 1) & 0x1
            st_stereo = body[1] & 0x1
            print(f"    Playback: codec={pb_codec} rate={pb_rate} size={pb_size} stereo={pb_stereo}")
            print(f"    Stream: codec={st_codec} rate={st_rate} size={st_size} stereo={st_stereo}")
    
    # ===== CHECK TAG TYPE CONVERSIONS =====
    print(f"\n{'='*80}")
    print(f"CRITICAL TAG TYPE CONVERSIONS:")
    print(f"  Shape types: OG has DefShape(659)+DefShape2(63)+DefShape3(125)+DefShape4(8)=855")
    print(f"               RT has DefShape3(855) — ALL shapes converted to DefShape3!")
    print(f"  Morph types: OG has DefMorphShape(16)+DefMorph2(5)=21")
    print(f"               RT has DefMorph2(21) — ALL morphs converted to DefMorph2!")
    print(f"  Text types:  OG has DefText(2)+CSMTextSettings(2)")
    print(f"               RT has DefEditText(2) — Static text converted to editable!")
    print(f"  Bitmap cnt:  OG has DefBitsJPEG3(2)+DefBitsLL2(625)=627")
    print(f"               RT has DefBitsLL2(1506) — ALL converted to lossless + extra bitmaps!")
    print(f"  Sounds:      OG and RT both have 64 DefSound, but ALL differ in content/size")
    print(f"  FontName:    OG has DefineFontName(1), RT has NONE — missing!")
    print(f"  Protect:     OG has password, RT has empty protect")
    print(f"  StreamHead:  OG 0x2e vs RT 0x0e — playback codec differs!")
    
    # ===== ALSO CHECK: Are there StartSound tags inside sprites being dropped? =====
    print(f"\n{'='*80}")
    print(f"STARTSOUND TAGS INSIDE SPRITES:")
    og_total_ss = 0
    rt_total_ss = 0
    ss_diffs = []
    
    for name in sorted(og_sym.values()):
        if name == 'Main': continue
        oc = og_name2cid.get(name)
        rc = rt_name2cid.get(name)
        if oc is None or rc is None: continue
        if oc not in og_sprites or rc not in rt_sprites: continue
        
        og_in = parse_sprite_inner(og_sprites[oc])
        rt_in = parse_sprite_inner(rt_sprites[rc])
        
        og_ss = sum(1 for t, _ in og_in if t == 15)
        rt_ss = sum(1 for t, _ in rt_in if t == 15)
        og_total_ss += og_ss
        rt_total_ss += rt_ss
        if og_ss != rt_ss:
            ss_diffs.append((name, og_ss, rt_ss))
    
    print(f"  Total StartSound in named sprites: OG={og_total_ss} RT={rt_total_ss}")
    if ss_diffs:
        print(f"  Sprites with StartSound count diffs:")
        for name, ogs, rts in ss_diffs[:30]:
            print(f"    {name}: OG={ogs} RT={rts}")
    
    # Check PO3 vs PO2 inside sprites
    print(f"\n{'='*80}")
    print(f"PO3 vs PO2 USAGE INSIDE ALL SPRITES:")
    og_total_po2 = 0; og_total_po3 = 0
    rt_total_po2 = 0; rt_total_po3 = 0
    po_type_diffs = []
    
    for name in sorted(og_sym.values()):
        if name == 'Main': continue
        oc = og_name2cid.get(name)
        rc = rt_name2cid.get(name)
        if oc is None or rc is None: continue
        if oc not in og_sprites or rc not in rt_sprites: continue
        
        og_in = parse_sprite_inner(og_sprites[oc])
        rt_in = parse_sprite_inner(rt_sprites[rc])
        
        og_p2 = sum(1 for t, _ in og_in if t == 26)
        og_p3 = sum(1 for t, _ in og_in if t == 70)
        rt_p2 = sum(1 for t, _ in rt_in if t == 26)
        rt_p3 = sum(1 for t, _ in rt_in if t == 70)
        og_total_po2 += og_p2; og_total_po3 += og_p3
        rt_total_po2 += rt_p2; rt_total_po3 += rt_p3
        
        if og_p3 > 0 and rt_p3 == 0:
            po_type_diffs.append((name, og_p2, og_p3, rt_p2, rt_p3))
    
    print(f"  OG: PO2={og_total_po2}, PO3={og_total_po3}")
    print(f"  RT: PO2={rt_total_po2}, PO3={rt_total_po3}")
    if po_type_diffs:
        print(f"\n  Sprites where OG has PO3 but RT has NONE:")
        for name, op2, op3, rp2, rp3 in po_type_diffs[:30]:
            print(f"    {name}: OG PO2={op2}+PO3={op3}={op2+op3}  RT PO2={rp2}+PO3={rp3}={rp2+rp3}")

if __name__ == "__main__":
    main()
