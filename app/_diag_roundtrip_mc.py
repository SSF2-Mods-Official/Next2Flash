#!/usr/bin/env python3
"""
Diagnostic: full roundtrip analysis of fox.ssf MovieClips.

Parses original SWF → N2D → recompiles to SWF → compares:
  - DefineSprite frame counts (original vs recompiled)
  - PlaceObject matrix values (positioning accuracy)
  - Timeline display lists per frame (what's on screen)
  - Character counts per sprite

Prints a detailed diff report.
"""

import json
import os
import struct
import sys
import zlib
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Add app dir to path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from swf_to_n2d import (
    parse_swf, parse_tags, parse_define_sprite, parse_place_object2,
    parse_place_object3, N2DBuilder, read_matrix, read_cxform_with_alpha,
    save_n2d, decompile_all_scripts,
)
from swf_binary_io import BitReader
from swf_constants import (
    TAG_DEFINE_SPRITE, TAG_PLACE_OBJECT2, TAG_PLACE_OBJECT3,
    TAG_REMOVE_OBJECT2, TAG_SHOW_FRAME, TAG_FRAME_LABEL,
    TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2, TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4,
    TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2,
    TAG_DEFINE_BITS_JPEG2, TAG_DEFINE_BITS_JPEG3,
    TAG_DEFINE_MORPH_SHAPE, TAG_DEFINE_MORPH_SHAPE2,
    TAG_DEFINE_EDIT_TEXT, TAG_DEFINE_TEXT, TAG_DEFINE_TEXT2,
    TAG_END,
)

SWF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"


def parse_raw_swf(path: str):
    """Parse SWF and return (header_info, tags as (type, data) tuples)."""
    with open(path, 'rb') as f:
        raw = f.read()

    sig = raw[:3]
    if sig in (b'CWS', b'ZWS'):
        header = raw[:8]
        version = raw[3]
        file_len = struct.unpack_from('<I', raw, 4)[0]
        if sig == b'CWS':
            body = zlib.decompress(raw[8:])
        else:
            import lzma
            body = lzma.decompress(raw[12:])
        full = header + body
    elif sig == b'FWS':
        full = raw
        version = raw[3]
        file_len = struct.unpack_from('<I', raw, 4)[0]
    else:
        raise ValueError(f"Not a SWF: {sig}")

    # Parse rect
    br = BitReader(full, 8)
    nbits = br.read_ub(5)
    br.read_sb(nbits)  # xmin
    br.read_sb(nbits)  # xmax
    br.read_sb(nbits)  # ymin
    br.read_sb(nbits)  # ymax
    br.align()
    rect_end = br.byte_pos

    frame_rate = struct.unpack_from('<H', full, rect_end)[0]
    frame_count = struct.unpack_from('<H', full, rect_end + 2)[0]

    tags = parse_tags_raw(full, rect_end + 4)

    return {
        'version': version,
        'frameRate': frame_rate,
        'frameCount': frame_count,
    }, tags


def parse_tags_raw(data: bytes, offset: int):
    """Parse SWF tags from raw bytes. Return list of (tag_type, tag_data)."""
    tags = []
    pos = offset
    while pos < len(data):
        if pos + 2 > len(data):
            break
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        pos += 2
        if tag_length == 0x3F:
            if pos + 4 > len(data):
                break
            tag_length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        tag_data = data[pos:pos + tag_length]
        pos += tag_length
        tags.append((tag_type, tag_data))
        if tag_type == 0:  # End
            break
    return tags


def analyze_sprite(nested_tags) -> dict:
    """Analyze a DefineSprite's nested tags to extract per-frame display list."""
    frames = []
    current_display = {}  # depth -> {charId, matrix, name, clipDepth, ratio, ...}
    frame_num = 0
    frame_label = None
    frame_places = []
    frame_removes = []

    for tag_type, tag_data in nested_tags:
        if tag_type == TAG_PLACE_OBJECT2:
            po = _parse_po2(tag_data)
            frame_places.append(po)
        elif tag_type == TAG_PLACE_OBJECT3:
            po = _parse_po3(tag_data)
            frame_places.append(po)
        elif tag_type == TAG_REMOVE_OBJECT2:
            depth = struct.unpack_from('<H', tag_data, 0)[0]
            frame_removes.append(depth)
        elif tag_type == TAG_FRAME_LABEL:
            frame_label = tag_data.split(b'\x00')[0].decode('utf-8', errors='replace')
        elif tag_type == TAG_SHOW_FRAME:
            frame_num += 1
            # Apply removes
            for d in frame_removes:
                current_display.pop(d, None)
            # Apply places
            for po in frame_places:
                d = po['depth']
                if po.get('move') and d in current_display:
                    # Move: update existing
                    existing = current_display[d].copy()
                    if po.get('charId') is not None:
                        existing['charId'] = po['charId']
                    if po.get('matrix') is not None:
                        existing['matrix'] = po['matrix']
                    if po.get('colorTransform') is not None:
                        existing['colorTransform'] = po['colorTransform']
                    if po.get('name') is not None:
                        existing['name'] = po['name']
                    if po.get('ratio') is not None:
                        existing['ratio'] = po['ratio']
                    current_display[d] = existing
                else:
                    # Place new
                    current_display[d] = po.copy()

            frames.append({
                'frame': frame_num,
                'label': frame_label,
                'display': dict(current_display),
                'removes': list(frame_removes),
                'places': [p.copy() for p in frame_places],
            })
            frame_removes = []
            frame_places = []
            frame_label = None
        elif tag_type == TAG_END:
            break

    return {
        'frameCount': frame_num,
        'frames': frames,
    }


def _parse_po2(tag_data: bytes) -> dict:
    """Minimal PlaceObject2 parser."""
    flags = tag_data[0]
    has_clip_depth = bool(flags & 0x40)
    has_name = bool(flags & 0x20)
    has_ratio = bool(flags & 0x10)
    has_cx = bool(flags & 0x08)
    has_matrix = bool(flags & 0x04)
    has_character = bool(flags & 0x02)
    is_move = bool(flags & 0x01)

    depth = struct.unpack_from('<H', tag_data, 1)[0]
    result = {'depth': depth, 'move': is_move, 'charId': None,
              'matrix': None, 'colorTransform': None, 'name': None,
              'ratio': None, 'clipDepth': None, 'blendMode': None}

    try:
        br = BitReader(tag_data, 3)
        if has_character:
            result['charId'] = br.read_ui16()
        if has_matrix:
            result['matrix'] = _read_mat(br)
            br.align()
        if has_cx:
            result['colorTransform'] = _read_cx(br)
            br.align()
        if has_ratio:
            result['ratio'] = br.read_ui16()
        if has_name:
            result['name'] = br.read_string()
        if has_clip_depth:
            result['clipDepth'] = br.read_ui16()
    except Exception:
        pass
    return result


def _parse_po3(tag_data: bytes) -> dict:
    """Minimal PlaceObject3 parser."""
    flags1 = tag_data[0]
    flags2 = tag_data[1]
    has_clip_depth = bool(flags1 & 0x40)
    has_name = bool(flags1 & 0x20)
    has_ratio = bool(flags1 & 0x10)
    has_cx = bool(flags1 & 0x08)
    has_matrix = bool(flags1 & 0x04)
    has_character = bool(flags1 & 0x02)
    is_move = bool(flags1 & 0x01)
    has_filter = bool(flags2 & 0x01)
    has_blend = bool(flags2 & 0x02)
    has_image = bool(flags2 & 0x10)

    depth = struct.unpack_from('<H', tag_data, 2)[0]
    result = {'depth': depth, 'move': is_move, 'charId': None,
              'matrix': None, 'colorTransform': None, 'name': None,
              'ratio': None, 'clipDepth': None, 'blendMode': None}

    try:
        br = BitReader(tag_data, 4)
        if has_character:
            result['charId'] = br.read_ui16()
        if has_matrix:
            result['matrix'] = _read_mat(br)
            br.align()
        if has_cx:
            result['colorTransform'] = _read_cx(br)
            br.align()
        if has_ratio:
            result['ratio'] = br.read_ui16()
        if has_name:
            result['name'] = br.read_string()
        if has_clip_depth:
            result['clipDepth'] = br.read_ui16()
        if has_filter:
            pass  # skip
        if has_blend:
            result['blendMode'] = br.read_ui8()
    except Exception:
        pass
    return result


def _read_mat(br: BitReader):
    """Read SWF MATRIX record."""
    has_scale = br.read_ub(1)
    sx, sy = 1.0, 1.0
    if has_scale:
        nb = br.read_ub(5)
        sx = br.read_fb(nb)
        sy = br.read_fb(nb)
    has_rotate = br.read_ub(1)
    r0, r1 = 0.0, 0.0
    if has_rotate:
        nb = br.read_ub(5)
        r0 = br.read_fb(nb)
        r1 = br.read_fb(nb)
    nb = br.read_ub(5)
    tx = br.read_sb(nb) / 20.0 if nb else 0.0  # twips to pixels
    ty = br.read_sb(nb) / 20.0 if nb else 0.0

    return [sx, r0, r1, sy, tx, ty]


def _read_cx(br: BitReader):
    """Read CXFORMWITHALPHA."""
    has_add = br.read_ub(1)
    has_mul = br.read_ub(1)
    nb = br.read_ub(4)
    rm, gm, bm, am = 1.0, 1.0, 1.0, 1.0
    if has_mul:
        rm = br.read_sb(nb) / 256.0
        gm = br.read_sb(nb) / 256.0
        bm = br.read_sb(nb) / 256.0
        am = br.read_sb(nb) / 256.0
    ra, ga, ba, aa = 0, 0, 0, 0
    if has_add:
        ra = br.read_sb(nb)
        ga = br.read_sb(nb)
        ba = br.read_sb(nb)
        aa = br.read_sb(nb)
    return [rm, gm, bm, am, ra, ga, ba, aa]


# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("MOVIECLIP ROUNDTRIP DIAGNOSTIC")
    print("=" * 80)
    print(f"Source: {SWF_PATH}")
    print()

    # ── Step 1: Parse original SWF ──
    print("--- Step 1: Parsing original SWF ---")
    header, all_tags = parse_raw_swf(SWF_PATH)
    print(f"  SWF version: {header['version']}")
    print(f"  Main timeline frames: {header['frameCount']}")

    # Gather sprites and char types from original
    og_sprites: Dict[int, dict] = {}  # charId -> analysis
    og_sprite_frame_counts: Dict[int, int] = {}
    og_char_types: Dict[int, str] = {}  # charId -> type name
    
    tag_type_names = {
        TAG_DEFINE_SHAPE: 'Shape', TAG_DEFINE_SHAPE2: 'Shape2',
        TAG_DEFINE_SHAPE3: 'Shape3', TAG_DEFINE_SHAPE4: 'Shape4',
        TAG_DEFINE_BITS_LOSSLESS: 'BitmapLossless', TAG_DEFINE_BITS_LOSSLESS2: 'BitmapLossless2',
        TAG_DEFINE_BITS_JPEG2: 'BitmapJPEG2', TAG_DEFINE_BITS_JPEG3: 'BitmapJPEG3',
        TAG_DEFINE_MORPH_SHAPE: 'MorphShape', TAG_DEFINE_MORPH_SHAPE2: 'MorphShape2',
        TAG_DEFINE_EDIT_TEXT: 'EditText', TAG_DEFINE_TEXT: 'Text', TAG_DEFINE_TEXT2: 'Text2',
    }

    for tag_type, tag_data in all_tags:
        if tag_type == TAG_DEFINE_SPRITE:
            char_id = struct.unpack_from('<H', tag_data, 0)[0]
            frame_count = struct.unpack_from('<H', tag_data, 2)[0]
            nested = parse_tags_raw(tag_data, 4)
            analysis = analyze_sprite(nested)
            og_sprites[char_id] = analysis
            og_sprite_frame_counts[char_id] = frame_count
            og_char_types[char_id] = 'Sprite'
        elif tag_type in tag_type_names:
            char_id = struct.unpack_from('<H', tag_data, 0)[0]
            og_char_types[char_id] = tag_type_names[tag_type]

    # Also analyze main timeline
    main_analysis = analyze_sprite(all_tags)
    
    print(f"  Total sprites: {len(og_sprites)}")
    print(f"  Total defined characters: {len(og_char_types)}")
    print()

    # ── Step 2: Convert SWF → N2D ──
    print("--- Step 2: Converting SWF -> N2D ---")
    
    with open(SWF_PATH, 'rb') as f:
        swf_data = f.read()
    
    swf_header, swf_tags = parse_swf(swf_data)
    sname = os.path.splitext(os.path.basename(SWF_PATH))[0]
    builder = N2DBuilder(swf_header, name=sname)
    builder.catalog_swf_tags(swf_tags)
    
    # Decompile scripts
    scripts, frame_scripts = decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
    if scripts:
        builder.scripts.extend(scripts)
    
    builder.build_all()
    builder.build_main_timeline(swf_tags)
    builder._embed_bitmap_data_in_recodes()
    
    n2d_json_obj = builder.to_n2d_json()
    
    # Save to temp for compilation
    import tempfile
    n2d_temp = os.path.join(tempfile.gettempdir(), 'fox_diag.n2d')
    save_n2d(n2d_json_obj, n2d_temp)
    n2d_data = open(n2d_temp, 'rb').read()

    # Get the libraries
    libs = n2d_json_obj.get('libraries', [])
    
    # Build a map of SWF charId -> N2D library via swfCharId
    swf_to_n2d_map = {}
    n2d_containers = {}
    for i, lib in enumerate(libs):
        if not isinstance(lib, dict):
            continue
        swf_cid = lib.get('swfCharId')
        if swf_cid is not None:
            swf_to_n2d_map[swf_cid] = i
        if lib.get('layers') is not None:
            n2d_containers[i] = lib

    print(f"  N2D libraries: {len(libs)}")
    print(f"  N2D containers (MovieClips): {len(n2d_containers)}")
    print(f"  SWF charId → N2D mapped: {len(swf_to_n2d_map)}")
    print()

    # ── Step 3: Analyze N2D frame counts vs original ──
    print("--- Step 3: Frame count comparison ---")
    from compile_n2d import _compute_total_frames

    mismatches = []
    for swf_cid, og_fc in sorted(og_sprite_frame_counts.items()):
        n2d_idx = swf_to_n2d_map.get(swf_cid)
        if n2d_idx is None:
            mismatches.append((swf_cid, og_fc, None, "NOT IN N2D"))
            continue
        lib = libs[n2d_idx]
        # Check what totalFrame the N2D has
        n2d_total = lib.get('totalFrame')
        computed = _compute_total_frames(lib)
        
        if n2d_total is not None and n2d_total != og_fc:
            mismatches.append((swf_cid, og_fc, n2d_total, f"N2D totalFrame={n2d_total} computed={computed}"))
        elif computed != og_fc:
            mismatches.append((swf_cid, og_fc, computed, f"computed={computed} (totalFrame absent)"))

    if mismatches:
        print(f"  FRAME COUNT MISMATCHES: {len(mismatches)}")
        for swf_cid, og, n2d, note in mismatches[:30]:
            char_name = ""
            n2d_idx = swf_to_n2d_map.get(swf_cid)
            if n2d_idx is not None:
                char_name = libs[n2d_idx].get('name', '')
            print(f"    charId={swf_cid:4d} OG={og:4d} N2D={n2d if n2d else '?':>4}  {note}  name={char_name}")
        if len(mismatches) > 30:
            print(f"    ... and {len(mismatches) - 30} more")
    else:
        print("  All frame counts match!")
    print()

    # ── Step 4: Analyze per-sprite display list / PlaceObject accuracy ──
    print("--- Step 4: PlaceObject / positioning analysis ---")
    print("  Sampling first 10 sprites with >1 frame for display list comparison...")
    
    sampled = 0
    for swf_cid in sorted(og_sprites.keys()):
        if sampled >= 10:
            break
        og = og_sprites[swf_cid]
        if og['frameCount'] <= 1:
            continue
        
        n2d_idx = swf_to_n2d_map.get(swf_cid)
        if n2d_idx is None:
            continue
        lib = libs[n2d_idx]
        
        print(f"\n  Sprite charId={swf_cid} name='{lib.get('name', '')}' OG frames={og['frameCount']}")
        
        # Show the N2D layer structure
        layers = lib.get('layers', [])
        print(f"    N2D layers: {len(layers)}")
        for li, layer in enumerate(layers):
            chars = layer.get('characters', [])
            mode = layer.get('mode', 0)
            swf_d = layer.get('swfDepth', '?')
            mode_name = {0: 'NORMAL', 1: 'MASK', 2: 'MASK_IN', 3: 'GUIDE'}.get(mode, f'?{mode}')
            print(f"      Layer {li}: mode={mode_name} swfDepth={swf_d} chars={len(chars)}")
            for ci, char in enumerate(chars):
                places = char.get('places', [])
                sf = char.get('startFrame', '?')
                ef = char.get('endFrame', '?')
                lid = char.get('libraryId', '?')
                print(f"        Char {ci}: libId={lid} frames={sf}-{ef} places={len(places)}")
                for pi, pl in enumerate(places[:3]):
                    mat = pl.get('matrix', [])
                    f = pl.get('frame', '?')
                    print(f"          Place {pi}: frame={f} matrix={[round(v, 3) for v in mat]}")
                if len(places) > 3:
                    print(f"          ... +{len(places)-3} more places")
        
        # Show OG frame 1 display list
        if og['frames']:
            f1 = og['frames'][0]
            print(f"    OG Frame 1 display: {len(f1['display'])} chars at depths:")
            for d in sorted(f1['display'].keys()):
                entry = f1['display'][d]
                mat_str = ""
                if entry.get('matrix'):
                    mat_str = f" matrix={[round(v, 3) for v in entry['matrix']]}"
                cid = entry.get('charId', '?')
                ctype = og_char_types.get(cid, '?')
                print(f"      depth={d}: charId={cid} ({ctype}){mat_str}")
        
        sampled += 1

    print()

    # ── Step 5: Full roundtrip compile and compare ──
    print("--- Step 5: Full roundtrip compile ---")
    from compile_n2d import N2DCompiler
    
    # n2d_temp was already saved in Step 2
    swf_out = os.path.join(tempfile.gettempdir(), 'fox_diag_rt.swf')
    shared_dir = os.path.join(tempfile.gettempdir(), 'fox_diag_shared')
    os.makedirs(shared_dir, exist_ok=True)
    try:
        compiler = N2DCompiler(n2d_temp, shared_dir, swf_out)
        compiler.compile()
        print(f"  Compiled to: {swf_out}")
        print(f"  Output size: {os.path.getsize(swf_out)} bytes")
    except Exception as e:
        print(f"  COMPILATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    # Parse the recompiled SWF
    print("  Parsing recompiled SWF...")
    rt_header, rt_tags = parse_raw_swf(swf_out)
    
    rt_sprites: Dict[int, dict] = {}
    rt_sprite_frame_counts: Dict[int, int] = {}
    
    for tag_type, tag_data in rt_tags:
        if tag_type == TAG_DEFINE_SPRITE:
            char_id = struct.unpack_from('<H', tag_data, 0)[0]
            frame_count = struct.unpack_from('<H', tag_data, 2)[0]
            nested = parse_tags_raw(tag_data, 4)
            analysis = analyze_sprite(nested)
            rt_sprites[char_id] = analysis
            rt_sprite_frame_counts[char_id] = frame_count

    print(f"  Recompiled sprites: {len(rt_sprites)}")
    print(f"  RT main timeline frames: {rt_header['frameCount']}")
    print()

    # ── Step 6: Compare sprite frame counts (using names) ──
    print("--- Step 6: Recompiled frame count accuracy ---")
    
    # Build OG name->frameCount map
    og_name_fc = {}
    for swf_cid, fc in og_sprite_frame_counts.items():
        n2d_idx = swf_to_n2d_map.get(swf_cid)
        if n2d_idx is not None:
            name = libs[n2d_idx].get('name', f'_anon_{swf_cid}')
            og_name_fc[name] = (swf_cid, fc)
    
    # For the roundtrip, match by examining the N2D compilation order
    # The compiler assigns new charIds, so we compare by library name
    
    # Print summary statistics
    og_fc_values = sorted(og_sprite_frame_counts.values())
    rt_fc_values = sorted(rt_sprite_frame_counts.values())
    
    print(f"  OG sprite count: {len(og_sprite_frame_counts)}")
    print(f"  RT sprite count: {len(rt_sprite_frame_counts)}")
    print(f"  OG total frames across sprites: {sum(og_fc_values)}")
    print(f"  RT total frames across sprites: {sum(rt_fc_values)}")
    
    # Distribution comparison
    og_dist = defaultdict(int)
    rt_dist = defaultdict(int)
    for fc in og_fc_values:
        og_dist[fc] += 1
    for fc in rt_fc_values:
        rt_dist[fc] += 1
    
    all_fcs = sorted(set(list(og_dist.keys()) + list(rt_dist.keys())))
    print(f"\n  Frame count distribution (OG vs RT):")
    for fc in all_fcs:
        og_n = og_dist.get(fc, 0)
        rt_n = rt_dist.get(fc, 0)
        marker = " <-- DIFF" if og_n != rt_n else ""
        if fc <= 5 or og_n != rt_n or fc > 50:
            print(f"    {fc:4d} frames: OG={og_n:3d} sprites, RT={rt_n:3d} sprites{marker}")
    
    print()

    # ── Step 7: Detailed sprite-by-sprite comparison ──
    print("--- Step 7: Sprite-by-sprite roundtrip comparison ---")
    
    # Since charIds are reassigned, we need to match by examining the timeline structure
    # Strategy: for each OG sprite, find an RT sprite with matching frame count and similar structure
    # Better strategy: use the N2D library order since compiler processes them in order
    
    # Build char_id_to_lib_idx for the recompiled SWF by parsing the SymbolClass
    # or by simply matching the compilation order
    
    # Let's directly compare frame counts from the N2D perspective
    print("  Comparing _compute_total_frames vs OG DefineSprite.frameCount:")
    n2d_fc_mismatches = 0
    for swf_cid, og_fc in sorted(og_sprite_frame_counts.items()):
        n2d_idx = swf_to_n2d_map.get(swf_cid)
        if n2d_idx is None:
            continue
        lib = libs[n2d_idx]
        computed_fc = _compute_total_frames(lib)
        stored_fc = lib.get('totalFrame')
        
        if computed_fc != og_fc:
            n2d_fc_mismatches += 1
            name = lib.get('name', '')
            layers = lib.get('layers', [])
            # Dig into why
            max_ef = 0
            for layer in layers:
                for ch in layer.get('characters', []):
                    ef = ch.get('endFrame', 0)
                    if ef > max_ef:
                        max_ef = ef
                for ch in layer.get('emptyCharacters', []):
                    ef = ch.get('endFrame', 0)
                    if ef > max_ef:
                        max_ef = ef
            print(f"    MISMATCH charId={swf_cid} name='{name}': OG={og_fc} computed={computed_fc} "
                  f"stored_totalFrame={stored_fc} max_endFrame={max_ef}")
    
    if n2d_fc_mismatches == 0:
        print("    All computed frame counts match OG!")
    else:
        print(f"    Total mismatches: {n2d_fc_mismatches}")
    
    print()
    
    # ── Step 8: Check for empty/missing timeline data ──
    print("--- Step 8: Sprites with unusual timeline data ---")
    
    for swf_cid in sorted(og_sprites.keys()):
        og = og_sprites[swf_cid]
        n2d_idx = swf_to_n2d_map.get(swf_cid)
        if n2d_idx is None:
            continue
        lib = libs[n2d_idx]
        layers = lib.get('layers', [])
        
        # Check: OG has characters on display but N2D has no layers
        if og['frameCount'] > 1 and len(layers) == 0:
            print(f"  charId={swf_cid} name='{lib.get('name', '')}': "
                  f"OG has {og['frameCount']} frames but N2D has 0 layers!")
        
        # Check: OG frame 1 has N characters but N2D layers have different count
        if og['frames']:
            og_f1_chars = len(og['frames'][0]['display'])
            n2d_total_chars = sum(len(layer.get('characters', [])) for layer in layers)
            if og['frameCount'] > 1 and n2d_total_chars == 0 and og_f1_chars > 0:
                print(f"  charId={swf_cid} name='{lib.get('name', '')}': "
                      f"OG frame 1 has {og_f1_chars} chars, N2D has 0 total characters!")

    # ── Step 9: Matrix precision comparison ──
    print("\n--- Step 9: Matrix value analysis ---")
    # Compare first few sprites in detail
    sampled2 = 0
    matrix_issues = 0
    for swf_cid in sorted(og_sprites.keys()):
        if sampled2 >= 5:
            break
        og = og_sprites[swf_cid]
        if og['frameCount'] <= 2:
            continue
        n2d_idx = swf_to_n2d_map.get(swf_cid)
        if n2d_idx is None:
            continue

        lib = libs[n2d_idx]
        name = lib.get('name', '')
        
        # Compare OG frame 1 matrices with N2D place matrices
        if not og['frames']:
            continue
        
        og_f1 = og['frames'][0]
        if not og_f1['display']:
            continue
            
        print(f"\n  Sprite '{name}' (charId={swf_cid}, {og['frameCount']} frames):")
        
        for depth in sorted(og_f1['display'].keys())[:5]:
            entry = og_f1['display'][depth]
            og_mat = entry.get('matrix')
            og_cid = entry.get('charId')
            if og_mat is None:
                continue
            
            # Find corresponding N2D place
            found_n2d_mat = None
            for layer in lib.get('layers', []):
                if layer.get('swfDepth') == depth:
                    for char in layer.get('characters', []):
                        # Check if startFrame <= 1 < endFrame
                        sf = char.get('startFrame', 0)
                        ef = char.get('endFrame', 0)
                        if sf <= 1 and ef > 1:
                            for pl in char.get('places', []):
                                if pl.get('frame', 0) <= 1:
                                    found_n2d_mat = pl.get('matrix')
                                    break
                            break
                    break
            
            if found_n2d_mat:
                # Compare
                diffs = [abs(a - b) for a, b in zip(og_mat, found_n2d_mat)]
                max_diff = max(diffs)
                if max_diff > 0.01:
                    matrix_issues += 1
                    print(f"    depth={depth} charId={og_cid}: MATRIX DIFF max={max_diff:.4f}")
                    print(f"      OG:  {[round(v, 4) for v in og_mat]}")
                    print(f"      N2D: {[round(v, 4) for v in found_n2d_mat]}")
                else:
                    print(f"    depth={depth} charId={og_cid}: matrix OK (max_diff={max_diff:.6f})")
            else:
                print(f"    depth={depth} charId={og_cid}: N2D match not found at depth")
        
        sampled2 += 1
    
    if matrix_issues == 0:
        print("\n  All sampled matrices match within tolerance!")
    else:
        print(f"\n  Matrix issues found: {matrix_issues}")

    # ── Step 10: Main timeline comparison ──
    print("\n--- Step 10: Main timeline comparison ---")
    print(f"  OG main timeline: {header['frameCount']} frames, {len(main_analysis['frames'])} ShowFrames")
    
    rt_main = analyze_sprite(rt_tags)
    print(f"  RT main timeline: {rt_header['frameCount']} frames, {len(rt_main['frames'])} ShowFrames")
    
    if main_analysis['frames'] and rt_main['frames']:
        og_f1 = main_analysis['frames'][0]
        rt_f1 = rt_main['frames'][0]
        print(f"  OG frame 1 display: {len(og_f1['display'])} chars")
        print(f"  RT frame 1 display: {len(rt_f1['display'])} chars")
    
    print()
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
